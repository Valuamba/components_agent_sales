import re


def normalize_text(text):
    text = re.sub(r'\W+', ' ', text).lower().strip()  # \W+ matches any non-word character
    return text


def signature_exists_in_email(signature, email):
    norm_signature = normalize_text(signature)

    norm_email = normalize_text(email)
    pattern = r'(\s*)'.join(re.escape(word) for word in norm_signature.split())

    return re.search(pattern, norm_email) is not None


def remove_sign_from_message(signature, email):
    norm_signature = normalize_text(signature)
    norm_email = normalize_text(email)
    pattern = r'(\s*)'.join(re.escape(word) for word in norm_signature.split())

    if re.search(pattern, norm_email) is not None:
        return re.sub(pattern, '', norm_email)
    else:
        print('Warn: sign was not found at message.')
        return email

