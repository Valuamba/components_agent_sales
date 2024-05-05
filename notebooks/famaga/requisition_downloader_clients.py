import csv
import json
import logging
import threading
import requests
import concurrent
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import pandas as pd


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Thread %(thread)d] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("requisition_processing.log"),
        logging.StreamHandler()
    ]
)

HEADERS = {
    'Authorization': 'Bearer YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw',
    'Cookie': 'PHPSESSID=8gv7kd7lne3dfu5jk7kqpkfj36'
}

def fetch_offers(client_id):
    """Fetch offers for a given client ID."""
    url = f'http://api.famaga.org/requisition?client={client_id}'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_conversations(request_id):
    """Fetch conversations for a given request ID."""
    url = f'https://api.famaga.org/imap/deal/{request_id}'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def process_deal(requisition):
    """Process a single requisition."""
    request_id = requisition['request']['id']
    thread_id = threading.get_ident()
    logging.info(f"Thread {thread_id}. Fetching request ID: {request_id}")
    try:
        conversations = fetch_conversations(request_id)
        messages = conversations.get('content', [])
        total = conversations.get('total', 0)
        return {
            'request_id': request_id,
            'total': total,
            'messages': [
                {
                    'messageId': msg.get('messageId', ''),
                    'date': msg.get('date', ''),
                    'subject': msg.get('subject', ''),
                    'body': msg.get('body', ''),
                    'plain_body': msg.get('plainBody', ''),
                    'mail': msg.get('from', {}).get('mail', ''),
                    'mailbox': msg.get('from', {}).get('mailbox', ''),
                    'host': msg.get('from', {}).get('host', ''),
                    'full': msg.get('from', {}).get('full', ''),
                    'is_attachments_exists': bool(msg.get('attachments'))
                } for msg in messages
            ]
        }
    except requests.RequestException as e:
        logging.error(f"Thread {thread_id}. Error fetching request ID: {request_id}. Error: {str(e)}")
        return {
            'request_id': request_id,
            'total': 0,
            'messages': [],
            'error': str(e)
        }

def handle_result(client_id, result, csv_writer, csv_lock):
    """Handle the result of fetching conversations and write to CSV."""
    thread_id = threading.get_ident()
    error = result.get('error')
    if error:
        logging.error(f"Thread {thread_id}. Error processing request ID: {result['request_id']}. Error: {error}")
        with csv_lock:
            csv_writer.writerow({
                'client_id': client_id,
                'request_id': result['request_id'],
                'total': 0,
                'error': error,
                'messageId': '',
                'date': '',
                'subject': '',
                'body': '',
                'plain_body': '',
                'mail': '',
                'mailbox': '',
                'host': '',
                'full': '',
                'is_attachments_exists': ''
            })
    else:
        for message in result.get('messages', []):
            try:
                with csv_lock:
                    csv_writer.writerow({
                        'client_id': client_id,
                        'request_id': result['request_id'],
                        'total': result['total'],
                        'error': '',
                        'messageId': message['messageId'],
                        'date': message['date'],
                        'subject': message['subject'],
                        'body': message['body'],
                        'plain_body': message['plain_body'],
                        'mail': message['mail'],
                        'mailbox': message['mailbox'],
                        'host': message['host'],
                        'full': message['full'],
                        'is_attachments_exists': message['is_attachments_exists']
                    })
                logging.info(f"Thread {thread_id}. Successfully processed message ID: {message['messageId']}")
            except Exception as e:
                logging.error(f"Thread {thread_id}. Error processing message ID: {message['messageId']}. Error: {str(e)}")
                with csv_lock:
                    csv_writer.writerow({
                        'client_id': client_id,
                        'request_id': result['request_id'],
                        'total': result['total'],
                        'error': str(e),
                        'messageId': '',
                        'date': '',
                        'subject': '',
                        'body': '',
                        'plain_body': '',
                        'mail': '',
                        'mailbox': '',
                        'host': '',
                        'full': '',
                        'is_attachments_exists': ''
                    })

def process_client_chunk(clients, csv_writer, csv_lock):
    """Process a chunk of client IDs."""
    for client_id in clients:
        logging.info(f"Fetching offers for client ID: {client_id}")
        offers = fetch_offers(client_id)['content']
        for requisition in offers:
            result = process_deal(requisition)
            handle_result(client_id, result, csv_writer, csv_lock)

if __name__ == "__main__":
    products_path = '/Users/valuamba/Downloads/products.json'

    with open(products_path, 'r') as f:
        products_data = json.loads(f.read())

    df = pd.DataFrame(products_data)
    clients = df['client_id'].unique()

    results_path = 'requisitions_results_by_client.csv'
    max_workers = 40

    # Split clients into chunks for each worker
    chunk_size = (len(clients) // max_workers) + 1
    client_chunks = [clients[i:i + chunk_size] for i in range(0, len(clients), chunk_size)]

    with open(results_path, 'w', newline='') as csvfile:
        fieldnames = ['client_id', 'request_id', 'total', 'error', 'messageId', 'date', 'subject', 'body', 'plain_body', 'mail', 'mailbox', 'host', 'full', 'is_attachments_exists']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_lock = threading.Lock()
        executor = ThreadPoolExecutor(max_workers=max_workers)
        futures = [executor.submit(process_client_chunk, chunk, csv_writer, csv_lock) for chunk in client_chunks]

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            future.result()

    logging.info(f"Results have been written to '{results_path}'.")
