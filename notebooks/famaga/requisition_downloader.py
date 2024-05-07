import csv
import logging
import threading
import requests
import requests
import json
import pandas as pd
from tqdm import tqdm
import csv
from concurrent.futures import ThreadPoolExecutor
import concurrent
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Thread %(thread)d] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("requisition_processing.log"),
        logging.StreamHandler()
    ]
)

def fetch_requisitions(limit, page):
    url = 'http://api.famaga.org/requisition'
    headers = {
        'Authorization': 'Bearer YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw',
        'Cookie': 'PHPSESSID=8gv7kd7lne3dfu5jk7kqpkfj36'
    }
    params = {
        'limit': limit,
        'page': page
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def process_request(request_id):
    url = f'https://api.famaga.org/imap/deal/{request_id}'
    headers = {
        'Authorization': 'Bearer YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw',
        'Cookie': 'PHPSESSID=8gv7kd7lne3dfu5jk7kqpkfj36'
    }
    thread_id = threading.get_ident()
    logging.info(f"Thread {thread_id}. Fetching request ID: {request_id}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info(f"Thread {thread_id}. Successfully fetched request ID: {request_id}")
        return response.json(), request_id, None
    except requests.RequestException as e:
        logging.error(f"Thread {thread_id}. Error fetching request ID: {request_id}. Error: {str(e)}")
        return None, request_id, str(e)


def handle_result(result, csv_writer, csv_lock):
    total_result, request_id, error_message = result
    thread_id = threading.get_ident()
    if error_message:
        logging.error(f"Thread {thread_id}. Error processing request ID: {request_id}. Error: {error_message}")
        with csv_lock:
            csv_writer.writerow({
                'request_id': request_id,
                'total': 0,
                'error': error_message,
                'subject': '',
                'body': '',
                'plain_body': '',
                'mailbox': '',
                'mail': '',
                'host': '',
                'full': '',
                'date': '',
                'uid': '',
                'messageId': '',
                'is_attachments_exists': ''
            })
    else:
        for content in total_result.get('content', []):
            try:
                subject = content.get('subject', '')
                body_html = content.get('body', '')
                plain_body = content.get('plainBody', '')
                from_info = content.get('from', {})
                is_attachments_exists = bool(content.get('attachments'))
                with csv_lock:
                    csv_writer.writerow({
                        'request_id': request_id,
                        'total': total_result.get('total', 0),
                        'error': '',
                        'subject': subject,
                        'body': body_html,
                        'plain_body': plain_body,  # append plainBody in addition
                        'mailbox': from_info.get('mailbox', ''),
                        'mail': from_info.get('mail', ''),
                        'host': from_info.get('host', ''),
                        'full': from_info.get('full', ''),
                        'date': content.get('date', ''),
                        'uid': content.get('uid', ''),
                        'messageId': content.get('messageId', ''),
                        'is_attachments_exists': is_attachments_exists
                    })
                logging.info(f"Thread {thread_id}. Successfully processed request ID: {request_id}")
            except Exception as e:
                logging.error(f"Thread {thread_id}. Error processing content for request ID: {request_id}. Error: {str(e)}")
                with csv_lock:
                    csv_writer.writerow({
                        'request_id': request_id,
                        'total': total_result.get('total', 0),
                        'error': str(e),
                        'subject': '',
                        'body': '',
                        'plain_body': '',
                        'mailbox': '',
                        'mail': '',
                        'host': '',
                        'full': '',
                        'date': '',
                        'uid': '',
                        'messageId': '',
                        'is_attachments_exists': ''
                    })


if __name__ == "__main__":
    limit = 1000
    page = 1
    results_path = 'concurrent_requisition_results_v2.csv'
    csv_lock = threading.Lock()
    processed_ids = set()
    max_workers = 40

    # Set up initial CSV file with headers
    with open(results_path, 'w', newline='') as csvfile:
        fieldnames = ['request_id', 'total', 'error', 'subject', 'body', 'plain_body', 'mailbox', 'mail', 'host', 'full', 'date', 'uid', 'messageId', 'is_attachments_exists']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()

        executor = ThreadPoolExecutor(max_workers=max_workers)

        while True:
            requisitions = fetch_requisitions(limit, page)
            if not requisitions['content']:
                break
            logging.info(f'Processing requisitions from page {page}')

            content = requisitions['content']
            chunk_size = (len(content) // max_workers) + 1
            futures = []
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                futures.append(executor.submit(
                    lambda c: [
                        handle_result(process_request(item['request']['id']), csv_writer, csv_lock)
                        for item in c if item['request']['id'] not in processed_ids
                    ],
                    chunk
                ))

            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                future.result()  # wait for all threads to complete

            page += 1

    logging.info(f"Results have been written incrementally to '{results_path}'.")