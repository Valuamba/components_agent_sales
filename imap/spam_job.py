import hashlib
import imaplib
import email
import logging
from datetime import datetime
import time
from bs4 import BeautifulSoup
from langchain_community.callbacks import get_openai_callback
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import re
from sqlalchemy import create_engine, Column, String, Text, Boolean, Float, Numeric, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dateutil import parser
import traceback

load_dotenv()

IMAP_SERVER = 'mail.famaga.de'
IMAP_USER = 'sales6@famaga.com'
IMAP_PASSWORD = '5qaBz5JFlDFHVev'
MAILBOXES = ['INBOX', 'spam']  # Mailboxes to check
CHECK_INTERVAL = 5  # Check every 5 seconds
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATABASE_URL = os.getenv('FAMAGA_DB_URL')
OFFSET_DATE = datetime(2024, 5, 17)

if not os.path.exists('./logs'):
    os.makedirs('./logs')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Thread %(thread)d] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("./logs/spam_checker.log"),
        logging.StreamHandler()
    ]
)

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default='uuid_generate_v4()')
    imap_server = Column(String(255), nullable=False)
    imap_user = Column(String(255), nullable=False)
    subject = Column(Text)
    body = Column(Text)
    from_address = Column(String(255))
    to_address = Column(String(255))
    date = Column(DateTime)
    message_id = Column(String(255), unique=True)
    spam_flag = Column(Boolean)
    spam_score = Column(Float)
    gpt_spam_flag = Column(Boolean)
    cost = Column(Numeric)
    created_at = Column(DateTime, default=datetime.utcnow)
    folder = Column(String(255))
    body_hash = Column(String(255))
    is_error = Column(Boolean, default=False)
    error_msg = Column(Text)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def sha1(input_string):
    """Helper to hash input strings"""
    try:
        hash_object = hashlib.sha1()
        hash_object.update(input_string.encode('utf-8'))
        return hash_object.hexdigest()
    except Exception as e:
        raise ValueError(input_string) from e

def connect_to_imap():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(IMAP_USER, IMAP_PASSWORD)
    return mail

def fetch_messages(mail, mailbox, since_date):
    try:
        result, data = mail.select(mailbox)
        if result != 'OK':
            logging.error(f"Failed to select mailbox {mailbox}.")
            return []
        result, data = mail.search(None, f'SINCE {since_date.strftime("%d-%b-%Y")}')
        if result != 'OK':
            logging.error(f"Failed to fetch messages from {mailbox}.")
            return []
        message_ids = data[0].split()
        logging.info(f"Fetched {len(message_ids)} messages from {mailbox}.")
        return message_ids
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {str(e)}")
        return []

def extract_original_message(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition", "")
            if content_type == "message/rfc822":
                return extract_original_message(part.get_payload(0))
            elif content_type in ["text/plain", "text/html"] and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                decoded_payload = payload.decode(part.get_content_charset() or 'utf-8')
                return decoded_payload
    else:
        payload = msg.get_payload(decode=True)
        decoded_payload = payload.decode(msg.get_content_charset() or 'utf-8')
        return decoded_payload

def extract_encapsulated_message(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "message/rfc822":
                original_msg = part.get_payload(0)
                return extract_original_message(original_msg)
    return None

def extract_spam_score(msg):
    spam_status = msg.get('X-Spam-Status', '')
    score_match = re.search(r'score=([\d\.]+)', spam_status)
    return float(score_match.group(1)) if score_match else 0.0

def process_message(mailbox, message_id, llm, prompt, processed_ids):
    try:
        mail = connect_to_imap()
        mail.select(mailbox)
        result, data = mail.fetch(message_id, '(BODY.PEEK[])')
        if result != 'OK':
            logging.error(f"Failed to fetch message ID {message_id} from {mailbox}.")
            return None
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = str(email.header.make_header(email.header.decode_header(msg['subject'])))
        from_ = str(email.header.make_header(email.header.decode_header(msg['from'])))
        to = str(email.header.make_header(email.header.decode_header(msg['to'])))
        date = msg['date']
        message_id_str = message_id.decode()

        if message_id_str in processed_ids:
            return None

        encapsulated_message = extract_encapsulated_message(msg)
        body = encapsulated_message if encapsulated_message else extract_original_message(msg)

        if msg.get_content_type() == 'text/html':
            soup = BeautifulSoup(body, 'html.parser')
            body = soup.get_text()

        spam_flag = msg.get('X-Spam-Flag', 'No').lower() == 'yes'
        spam_score = extract_spam_score(msg)

        prompt_text = prompt.format(body=body)
        messages = [("human", prompt_text)]

        with get_openai_callback() as cb:
            response = llm.invoke(messages)
            completion_cost = cb.total_cost

        gpt_spam_flag = response.content.strip().lower() == 'true'

        if spam_flag and not gpt_spam_flag:
            mail.select(mailbox)
            mail.copy(message_id_str, 'INBOX')
            mail.store(message_id_str, '+FLAGS', '\\Deleted')
            mail.expunge()
            logging.info(f"Message {message_id_str} moved to INBOX.")

        created_at = datetime.now()
        body_hash = sha1(body)

        # Parse the date field, set to None if parsing fails
        try:
            date = parser.parse(date) if date else None
        except Exception as e:
            logging.error(f"Failed to parse date {date}: {str(e)}")
            date = None

        email_record = Email(
            imap_server=IMAP_SERVER,
            imap_user=IMAP_USER,
            subject=subject,
            body=body,
            from_address=from_,
            to_address=to,
            date=date,
            message_id=message_id_str,
            spam_flag=spam_flag,
            spam_score=spam_score,
            gpt_spam_flag=gpt_spam_flag,
            cost=completion_cost,
            created_at=created_at,
            folder=mailbox,
            body_hash=body_hash,
            is_error=False
        )
        session.add(email_record)
        session.commit()
        logging.info(f"Inserted message ID {message_id_str} into database.")
        return email_record
    except SQLAlchemyError as e:
        logging.error(f"SQLAlchemy error occurred: {str(e)}\n\nStack trace: {traceback.format_exc()}")
        session.rollback()  # Roll back the session
        created_at = datetime.now()
        email_record = Email(
            imap_server=IMAP_SERVER,
            imap_user=IMAP_USER,
            subject='N/A',
            body='N/A',
            from_address='N/A',
            to_address='N/A',
            date=None,
            message_id=message_id.decode(),
            spam_flag=False,
            spam_score=0.0,
            gpt_spam_flag=False,
            cost=0.0,
            created_at=created_at,
            folder=mailbox,
            body_hash='N/A',
            is_error=True,
            error_msg=str(e)
        )
        session.add(email_record)
        session.commit()
        return email_record
    except Exception as e:
        logging.error(f"Exception occurred while processing message ID {message_id} from {mailbox}: {str(e)}\n\nStack trace: {traceback.format_exc()}")
        session.rollback()  # Roll back the session in case of any other exception
        created_at = datetime.now()
        email_record = Email(
            imap_server=IMAP_SERVER,
            imap_user=IMAP_USER,
            subject='N/A',
            body='N/A',
            from_address='N/A',
            to_address='N/A',
            date=None,
            message_id=message_id.decode(),
            spam_flag=False,
            spam_score=0.0,
            gpt_spam_flag=False,
            cost=0.0,
            created_at=created_at,
            folder=mailbox,
            body_hash='N/A',
            is_error=True,
            error_msg=str(e)
        )
        session.add(email_record)
        session.commit()
        return email_record
    finally:
        mail.logout()

def get_processed_message_ids():
    try:
        processed_ids = session.query(Email.message_id).all()
        return set([msg_id[0] for msg_id in processed_ids])
    except SQLAlchemyError as e:
        logging.error(f"Failed to fetch processed message IDs from the database: {str(e)}")
        return set()

def get_latest_message_date(folder):
    latest_email = session.query(Email).filter(Email.folder == folder).order_by(Email.date.desc()).first()
    if latest_email and latest_email.date:
        return latest_email.date
    else:
        return OFFSET_DATE

def main():

    template = """
        You are a sales manager at a company that sells parts and components for manufacturers. Usually customers send requests
        with part numbers, brand, model, etc.

        But customers could ask some questions without sending parts details. Your zone of responsibility distinguishes spam messages and messages 
        from customers.

        Please detect the following message:
        {body}

        Response with short answer True/False. True - message is spam, False - message is not spam.
    """
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model='gpt-4o', temperature=0)

    while True:
        for mailbox in MAILBOXES:
            since_date = get_latest_message_date(mailbox)
            since_date = OFFSET_DATE
            mail = connect_to_imap()
            message_ids = fetch_messages(mail, mailbox, since_date)
            mail.logout()
            processed_ids = get_processed_message_ids()

            for message_id in message_ids:
                message_id_str = message_id.decode()
                if message_id_str not in processed_ids:
                    logging.info(f"Processing message ID {message_id_str} from {mailbox}.")
                    process_message(mailbox, message_id, llm, prompt, processed_ids)
                else:
                    logging.info(f"Skipping already processed message ID {message_id_str} from {mailbox}.")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
