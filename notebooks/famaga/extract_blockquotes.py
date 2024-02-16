from bs4 import BeautifulSoup, NavigableString, Tag
import email
from email.policy import default
import os

def extract_html_from_eml(file_path):
    # Read the .eml file content
    with open(file_path, 'r', encoding='utf-8') as file:
        eml_content = file.read()
    
    # Parse the email content
    message = email.message_from_string(eml_content, policy=default)
    
    # Initialize an empty string to hold the HTML part
    html_content = ""
    
    # Check if the email message is multipart
    if message.is_multipart():
        # Iterate over each part of the email
        for part in message.walk():
            # Check if the content type is HTML
            if part.get_content_type() == 'text/html':
                # Get the HTML content and break the loop
                html_content = part.get_payload(decode=True).decode(part.get_content_charset())
                break
    else:
        # If the email is not multipart, directly check if it's HTML
        if message.get_content_type() == 'text/html':
            html_content = message.get_payload(decode=True).decode(message.get_content_charset())
    
    return html_content

# Example usage (Make sure to replace 'path_to_your_eml_file.eml' with the actual file path)

def find_root_blockquotes(soup):
    """
    Find all blockquote elements that are not nested within another blockquote.
    """
    root_blockquotes = []
    for blockquote in soup.find_all("blockquote"):
        if not blockquote.find_parent("blockquote"):
            root_blockquotes.append(blockquote)
    return root_blockquotes

def extract_content_and_nested(blockquote, depth=0):
    """
    Extract content and nested blockquotes, handling various tag arrangements.
    """
    contents = []
    for element in blockquote.contents:
        if isinstance(element, NavigableString):
            if element.strip():  # Ignore empty or whitespace strings
                contents.append((depth, element.strip()))
        elif isinstance(element, Tag):
            if element.name == "blockquote":
                # Recursively process nested blockquotes
                contents.extend(extract_content_and_nested(element, depth + 1))
                break
            else:
                # Process non-blockquote tags for text
                text = element.get_text(strip=True)
                if text:
                    contents.append((depth, text))
                # Also, look for nested blockquotes within other tags like div
                nested_blockquotes = element.find_all("blockquote")
                if len(nested_blockquotes) > 0:
                    for nested_blockquote in nested_blockquotes:
                        contents.extend(extract_content_and_nested(nested_blockquote, depth + 1))
                    break

    return contents


emails_dir = r'C:\Users\MGroup\Downloads\Автоматизация-20240128T094908Z-001\Автоматизация'
file_name = 'Re ORDER_ Zamowienie Reminder FAMAGA Group GmbH _ Co. KG № KP440822 (5) (2).eml'

file_path = os.path.join(emails_dir, file_name)
html_content = extract_html_from_eml(file_path)

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Find root blockquotes
root_blockquotes = find_root_blockquotes(soup)

# Extract content and nested blockquotes
messages = []
for blockquote in root_blockquotes:
    messages.extend(extract_content_and_nested(blockquote))

# Print extracted messages
for depth, content in messages:
    print(f"Message at depth {depth}: {len(content)}")
