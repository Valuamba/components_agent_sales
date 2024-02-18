import re
import json
import hashlib


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
