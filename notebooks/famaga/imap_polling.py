import os
import csv
import re
import time
import imaplib
import email
import logging
from email.policy import SMTP
from datetime import datetime

# Email server configuration

imap_server = 'mail.famaga.de'
username = 'gk@famaga.de'
password = '78U5tV5BEhdz78q'

csv_file_path = 'emails.csv'


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Thread %(thread)d] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("./logs/imap_polling.log"),
        logging.StreamHandler()
    ]
)

# Set up logging
deal_id_patterns = [
    r"New Deal [A-Z]*?(\d+)",  # New Deal IDs with optional leading letters
    r"Request [A-Z]*?(\d+)",  # Comment IDs with optional leading letters
    r"Offer №(\d+)",  # Offer IDs
    r"№ [A-Z]*?(\d+)"  # Inquiry IDs with optional leading letters
]


def extract_deal_id(subject):
    for pattern in deal_id_patterns:
        match = re.search(pattern, subject)
        if match:
            return match.group(1)
    return None


def initialize_csv_and_load_existing(file_path):
    existing_entries = set()
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['deal_id', 'message_id', 'from', 'to', 'date', 'subject', 'content_type', 'html_content', 'plain_text',
                 'is_attachments', 'created_at'])
    else:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            for row in reader:
                existing_entries.add((row[0], row[1]))  # Tuple of (deal_id, message_id)
    return existing_entries


existing_entries = initialize_csv_and_load_existing(csv_file_path)


def fetch_emails():
    try:
        with imaplib.IMAP4_SSL(imap_server) as mail:
            mail.login(username, password)
            mail.select('inbox')
            result, data = mail.search(None, '(UNSEEN)')
            if result != 'OK':
                logging.warning('Failed to search for unseen emails.')
                return

            logging.info(f'Message count: {len(data[0].split())}')

            for num in data[0].split():
                st, dt = mail.fetch(num, '(BODY.PEEK[])')
                email_msg = email.message_from_bytes(dt[0][1], policy=SMTP)

                if email_msg:
                    message_id = email_msg['Message-ID']
                    subject = email_msg['Subject']
                    deal_id = extract_deal_id(subject)
                    if not deal_id or (deal_id, message_id) in existing_entries:
                        logging.info(f'Skipped already processed message: {message_id}')
                        continue  # Skip if already processed

                    from_email = email_msg['From']
                    to_email = email_msg['To']
                    date = email_msg['Date']
                    content_type = email_msg.get_content_type()
                    html_content = ''
                    plain_text = ''
                    is_attachments = False

                    if email_msg.is_multipart():
                        for part in email_msg.walk():
                            part_content_type = part.get_content_type()
                            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition',
                                                                                      '').startswith('attachment'):
                                continue
                            content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            if part_content_type == 'text/plain':
                                plain_text += content
                            elif part_content_type == 'text/html':
                                html_content += content
                    else:
                        content = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                        if content_type == 'text/plain':
                            plain_text = content
                        elif content_type == 'text/html':
                            html_content = content

                    created_at = datetime.utcnow().isoformat()

                    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            [deal_id, message_id, from_email, to_email, date, subject, content_type, html_content,
                             plain_text, is_attachments, created_at])
                    existing_entries.add((deal_id, message_id))
                    logging.info(f'Appended {deal_id}:{message_id}. Subject: {subject}')
    except Exception as e:
        logging.error(f'Error in fetch_emails: {e}')


# Polling loop to fetch emails every 3 seconds
while True:
    fetch_emails()
    time.sleep(5)
