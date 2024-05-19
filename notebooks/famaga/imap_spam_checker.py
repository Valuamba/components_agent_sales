import hashlib
import imaplib
import email
import csv
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
import concurrent


load_dotenv()

NUM_WORKERS = 50
IMAP_SERVER = 'mail.famaga.de'
IMAP_USER = 'sales6@famaga.com'
IMAP_PASSWORD = '5qaBz5JFlDFHVev'
MAILBOXES = ['INBOX', 'spam']  # Mailboxes to check
CHECK_INTERVAL = 5  # Check every 5 seconds
PROCESSED_IDS_FILE = 'processed_ids.txt'  # File to store processed message IDs
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CSV_FILE = 'spam_detection_results.csv'  # CSV file
OFFSET_DATE = datetime(2024, 5, 10)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Thread %(thread)d] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("./logs/spam_checker.log"),
        logging.StreamHandler()
    ]
)


def sha1(input_string):
    """Helper to hash input strings"""
    try:
        hash_object = hashlib.sha1()
        hash_object.update(input_string.encode('utf-8'))
        return hash_object.hexdigest()
    except Exception as e:
        raise ValueError(input_string) from e

# Connect to the IMAP server
def connect_to_imap():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(IMAP_USER, IMAP_PASSWORD)
    return mail

# Fetch messages from the mailbox
def fetch_messages(mail, mailbox):
    try:
        result, data = mail.select(mailbox)
        if result != 'OK':
            logging.error(f"Failed to select mailbox {mailbox}.")
            return []
        today = OFFSET_DATE.strftime("%d-%b-%Y")
        result, data = mail.search(None, f'SINCE {today}')
        if result != 'OK':
            logging.error(f"Failed to fetch messages from {mailbox}.")
            return []
        message_ids = data[0].split()
        logging.info(f"Fetched {len(message_ids)} messages from {mailbox}.")
        return message_ids
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {str(e)}")
        return []

# Extract original encapsulated message
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

# Extract encapsulated message if present
def extract_encapsulated_message(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "message/rfc822":
                original_msg = part.get_payload(0)
                return extract_original_message(original_msg)
    return None

# Extract spam score from the X-Spam-Status header
def extract_spam_score(msg):
    spam_status = msg.get('X-Spam-Status', '')
    score_match = re.search(r'score=([\d\.]+)', spam_status)
    return score_match.group(1) if score_match else '0.0'

# Process the message
def process_message(mailbox, message_id, llm, prompt, processed_ids):
    try:
        mail = connect_to_imap()
        mail.select(mailbox)
        result, data = mail.fetch(message_id, '(BODY.PEEK[])')
        mail.logout()
        if result != 'OK':
            logging.error(f"Failed to fetch message ID {message_id} from {mailbox}.")
            return None
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg['subject']
        from_ = msg['from']
        to = msg['to']
        date = msg['date']
        message_id_str = message_id.decode()

        if message_id_str in processed_ids:
            return None

        encapsulated_message = extract_encapsulated_message(msg)
        body = encapsulated_message if encapsulated_message else extract_original_message(msg)

        # Handle HTML content
        if msg.get_content_type() == 'text/html':
            soup = BeautifulSoup(body, 'html.parser')
            body = soup.get_text()

        # Extract SpamAssassin headers
        spam_flag = msg.get('X-Spam-Flag', 'No')
        spam_score = extract_spam_score(msg)

        # Custom spam check using LangChain and ChatGPT-4
        prompt_text = prompt.format(body=body)
        messages = [
            ("human", prompt_text),
        ]

        with get_openai_callback() as cb:
            response = llm.invoke(messages)
            completion_cost = cb.total_cost

        gpt_spam_flag = response.content.strip()

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body_hash = sha1(body)

        processed_ids.add(message_id_str)
        return {
            'imap_server': IMAP_SERVER,
            'imap_user': IMAP_USER,
            'subject': subject,
            'body': body,
            'from': from_,
            'to': to,
            'date': date,
            'message_id': message_id,
            'spam_flag': spam_flag,
            'spam_score': spam_score,
            'gpt_spam_flag': gpt_spam_flag,
            'cost': completion_cost,
            'created_at': created_at,
            'folder': mailbox,
            'body_hash': body_hash,
            'is_error': False
        }
    except Exception as e:
        logging.error(f"Exception occurred while processing message ID {message_id} from {mailbox}: {str(e)}")
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return {
            'imap_server': IMAP_SERVER,
            'imap_user': IMAP_USER,
            'subject': 'N/A',
            'body': 'N/A',
            'from': 'N/A',
            'to': 'N/A',
            'date': 'N/A',
            'message_id': message_id,
            'spam_flag': 'N/A',
            'spam_score': 'N/A',
            'gpt_spam_flag': 'N/A',
            'cost': 0.0,
            'created_at': created_at,
            'folder': mailbox,
            'body_hash': 'N/A',
            'is_error': True
        }

# Write data to CSV
def write_to_csv(data):
    if not data:
        return

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        if not file_exists:
            writer.writeheader()  # Write header if file does not exist
        writer.writerows(data)

# Load processed message IDs
def load_processed_ids():
    try:
        with open(PROCESSED_IDS_FILE, 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

# Save processed message IDs
def save_processed_ids(processed_ids):
    with open(PROCESSED_IDS_FILE, 'w') as file:
        for message_id in processed_ids:
            file.write(message_id + '\n')

# Main function
def main():
    processed_ids = load_processed_ids()

    # Prepare LangChain components
    template = """
        You are sales manager at company that sells parts and components for manufacturers. Usually customers sends request 
        with part number, brand, model and etc.

        But customers could ask some questions without sending parts details. Your zone of responsibility distinguishes spam messages and messages 
        from customers.

        Please detect the following message:
        {body}

        Response with short answer spam/not spam.
    """
    prompt = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model='gpt-4', temperature=0)

    while True:
        for mailbox in MAILBOXES:
            mail = connect_to_imap()
            message_ids = fetch_messages(mail, mailbox)
            mail.logout()
            chunks = [message_ids[i:i + 10] for i in range(0, len(message_ids), 10)]

            with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
                futures = []
                for chunk in chunks:
                    futures.append(executor.submit(process_chunk, mailbox, chunk, llm, prompt, processed_ids))

                for future in concurrent.futures.as_completed(futures):
                    chunk_data = future.result()
                    if chunk_data:
                        write_to_csv(chunk_data)

        save_processed_ids(processed_ids)
        time.sleep(CHECK_INTERVAL)

def process_chunk(mailbox, chunk, llm, prompt, processed_ids):
    chunk_data = []
    for message_id in chunk:
        if message_id.decode() not in processed_ids:
            message_data = process_message(mailbox, message_id, llm, prompt, processed_ids)
            if message_data:
                chunk_data.append(message_data)
                logging.info(f"Processed message ID {message_id.decode()} from {mailbox}.")
    return chunk_data

if __name__ == "__main__":
    main()