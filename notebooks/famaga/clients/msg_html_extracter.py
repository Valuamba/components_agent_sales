import copy
import re
import json
import hashlib
import email
from email.policy import default

from bs4 import BeautifulSoup



class MsgHtmlExtracter:
    @staticmethod
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
    
    @staticmethod
    def extract_messages_from_raw_html(html_content: str):
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

    @staticmethod
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
