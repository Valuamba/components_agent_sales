from typing import List

from bs4 import BeautifulSoup
import re
import json


specific_style = "border:none;border-top:solid"

keys_to_check = ['From:', 'Sent:', 'To:', 'Subject:']


# Function to check presence of keys
def check_presence_of_keys(element, keys):
    text = element.get_text()  # Extract all text from the HTML
    missing_keys = [key for key in keys if key not in text]
    return missing_keys


def select_json_block(text: str):
    match = re.search(r"```json\n([\s\S]*?)\n```", text)
    if match:
        json_data = match.group(1)
    else:
        raise ValueError("No valid JSON data found in the string.")

    return json.loads(json_data)


def get_element_messages(element) -> List[str]:
    child_elements = [desc for desc in element.children if desc.name in ['p', 'div', 'table', 'blockquote']]
    messages = []

    message = ''

    def _append_message(msg: str):
        if msg.strip():
            messages.append(msg)

    for child in child_elements:
        if child.name == 'div':
            blockquote = child.find('blockquote')
            if blockquote:
                _append_message(message)
                message = ''
                messages += get_element_messages(child)
            elif hasattr(child, 'style') and child.get('style') and specific_style in child.get('style'):
                _append_message(message)
                message = ''
            else:
                message += child.get_text(strip=True)
        elif child.name == 'p':
            if hasattr(child, 'class') and child.get('class') and child.get('class')[0] == 'moz-forward-container':
                _append_message(message)
                message = ''
            elif not check_presence_of_keys(child, keys_to_check):
                _append_message(message)
                message = ''
                message += child.get_text(strip=True)
            else:
                message += child.get_text(strip=True)
        elif child.name == 'blockquote':
            _append_message(message)
            message = ''
            messages += get_element_messages(child)
        elif child.name == 'table':
            blockquote = child.find('blockquote')
            if blockquote:
                # print('Table blockquote')
                _append_message(message)
                message = ''
                messages += get_element_messages(blockquote)
            else:
                message += child.get_text(strip=True)
        else:
            message += child.get_text(strip=True)

    _append_message(message)

    return messages


def get_messages_from_html_file(file_path: str):
    with open(file_path, 'rb') as f:
        html = f.read()
        return split_email_html_on_messages(html)


def split_email_html_on_messages(email_html) -> List[str]:
    soup = BeautifulSoup(email_html, "html.parser")
    root_element = soup.find('body') if soup.find('body') else soup
    return get_element_messages(root_element)
