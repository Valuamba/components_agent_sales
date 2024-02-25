import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import copy
import pandas as pd
import sqlite3
import threading


threadLocal = threading.local()

def get_database_connection():
    """
    Returns a thread-local SQLite connection.
    Creates a new connection if it does not exist for the current thread.
    """
    if not hasattr(threadLocal, 'connection'):
        threadLocal.connection = sqlite3.connect('extracted_deals_messaging.db', check_same_thread=False)
    return threadLocal.connection


def get_messages_from_contents(data):
    if len(data['content']) == 0:
        print('There is no items')
        return []
    html_content = data['content'][-1]['body']['html']
    soup = BeautifulSoup(html_content, "html.parser")
    messages = []
    clone_body = copy.copy(soup)

    for nested_blockquote in clone_body.find_all("blockquote"):
        nested_blockquote.decompose()

    messages.append(clone_body.get_text(strip=True))
    blockquotes = soup.find_all("blockquote")

    for blockquote in blockquotes:
        clone = copy.copy(blockquote)

        for nested_blockquote in clone.find_all("blockquote"):
            nested_blockquote.decompose()

        messages.append(clone.get_text(strip=True))
    return messages


def fetch_deals_chunk(deal_ids_chunk, headers):
    print(f'Start chunk {len(deal_ids_chunk)}')
    deals_info = {}
    error_collection = []
    for deal_id in deal_ids_chunk:
        try:
            download_url = f"https://test-api.famaga.org/imap/deal/{deal_id}"
            response = requests.get(download_url, headers=headers)
            if response.status_code != 200:
                error_text = response.text
                print(f'[{deal_id}]: {error_text[:500]}')
                # Insert error into DB
                insert_deal_into_db(deal_id, None, error_text)
            else:
                print(f'Append deal {deal_id}')
                deal_info = response.json()
                # Insert deal into DB
                insert_deal_into_db(deal_id, deal_info)
        except Exception as e:
            print(f'[{deal_id}]: 500 error - {str(e)[:500]}')
            # Insert error into DB for unexpected issues
            insert_deal_into_db(deal_id, None, f'[{deal_id}]: 500 error')


def insert_deal_into_db(deal_id, deal_info, error_msg=None):
    conn = get_database_connection()
    cursor = conn.cursor()
    if error_msg:
        cursor.execute('''INSERT INTO deals (deal_id, error_msg) VALUES (?, ?)''',
                       (deal_id, error_msg))
    else:
        parsed_messages = None
        messages_count = None
        if deal_info['total'] == 0:
            chat_history = None
        else:
            chat_history = json.dumps(deal_info)
            messages = get_messages_from_contents(deal_info)
            messages_count = len(messages)
            parsed_messages = json.dumps(messages) if deal_info else None

        cursor.execute('''INSERT INTO deals (deal_id, chat_history, parsed_messages, messages_count) VALUES (?, ?, ?, ?)''',
                       (deal_id, chat_history, parsed_messages, messages_count))
    conn.commit()


def divide_into_chunks(deals_ids, chunk_count=20):
    for i in range(0, len(deals_ids), chunk_count):
        yield deals_ids[i:i + chunk_count]


def main(deals_ids, headers):
    max_workers = 20
    chunks = list(divide_into_chunks(deals_ids, max_workers))  # Divide deals_ids into 20 chunks

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_deals_chunk, chunk, headers) for chunk in chunks]
        # Wait for all threads to complete
        as_completed(futures)


# Example usage
headers = {"Authorization": "Bearer YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw"}

df = pd.read_json(r'C:\Users\MGroup\Documents\products.json')
conn = get_database_connection()
query = "SELECT deal_id FROM deals"
existing_deal_ids_df = pd.read_sql_query(query, conn)

existing_deal_ids = existing_deal_ids_df['deal_id'].tolist()

filtered_df = df[~df['id'].isin(existing_deal_ids)]
deals_ids = filtered_df['id'].values.tolist()

main(list(dict.fromkeys(deals_ids)), headers)