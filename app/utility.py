import re
import json    


def select_json_block(text: str):
    regex = r',(?!\s*?[\{\["\'\w])'
    cleaned_input = re.sub(regex, '', text)
    match = re.search(r'```json\n([\s\S]*?)\n```', text)
    if match:
        json_data = match.group(1)
    else:
        raise ValueError("No valid JSON data found in the string.")

    return json.loads(json_data)