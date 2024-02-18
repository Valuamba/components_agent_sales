import copy
import re
import json
import hashlib
import email
from email.policy import default

from bs4 import BeautifulSoup


def extract_html_from_eml(eml_content):
    message = email.message_from_bytes(eml_content, policy=default)

    html_content = ""

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True).decode(part.get_content_charset())
                break
    else:
        if message.get_content_type() == 'text/html':
            html_content = message.get_payload(decode=True).decode(message.get_content_charset())

    return html_content


def extract_messages_from_body(html_content: str):
    soup = BeautifulSoup(html_content, "html.parser")
    messages = []
    body = soup.find_all("body")[0]
    clone_body = copy.copy(body)

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


def normalize_content(content: str) -> str:
    """
    Normalize the content for consistent hashing.
    This function can be expanded based on your normalization needs.
    """
    # Example normalization: strip leading/trailing whitespace and convert to lowercase.
    return content.strip().lower()


def content_hash(content: str) -> str:
    """
    Convert the normalized content to a SHA-256 hash.
    """
    normalized_content = normalize_content(content)
    # Encode the normalized content to a byte format as required by hashlib
    content_bytes = normalized_content.encode()
    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(content_bytes)
    # Convert the hash object to a hexadecimal string
    hash_hex = hash_obj.hexdigest()
    return hash_hex


def select_json_block(text: str):
    match = re.search(r"```json\n([\s\S]*?)\n```", text)
    if match:
        json_data = match.group(1)
    else:
        raise ValueError("No valid JSON data found in the string.")

    return json.loads(json_data)
