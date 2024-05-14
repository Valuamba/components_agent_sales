
from typing import List, Any
import requests
import json
import re

from bs4 import BeautifulSoup
# flake8: noqa

import itertools
import re

DAY = "(3[0-1]|[12][0-9]|0?[1-9])"
NUM_MONTH = "(1[0-2]|0?[1-9])"
MONTH_DICT = {
    "january": ["jan", "янв."],
    "february": ["feb"],
    "march": ["mar"],
    "april": ["apr"],
    "may": [],
    "june": ["jun"],
    "july": ["july", "jul"],
    "august": ["aug"],
    "september": ["sp", "sep", "sept"],
    "october": ["oct"],
    "november": ["nov"],
    "december": ["dec"],
}
ALL_YEAR = "(([0-9]{2}){1,2})"
YEAR = "([0-9]{4})"
DATE_NUM_SEPS = [r"\/", r"\.", r"\-"]
MONTH_ABBRS = "|".join(itertools.chain(*MONTH_DICT.values()))  # type: ignore
MONTH_NAMES = "|".join(MONTH_DICT.keys())
MONTH_STR_KEYWORDS = f"({MONTH_NAMES}|{MONTH_ABBRS})"
MONTH_KEYWORDS = f"({MONTH_NAMES}|{MONTH_ABBRS}|{NUM_MONTH})"

DATE_DICT = {
    "left_date_with_seps": fr'(?:^|\s)(?P<left_date_with_seps>({"|".join("(" + sep.join([DAY, MONTH_KEYWORDS, ALL_YEAR]) + ")" for sep in DATE_NUM_SEPS)}))(?=\s|$|\.)',
    "right_date_with_seps": fr'(?:^|\s)(?P<right_date_with_seps>({"|".join("(" + sep.join([YEAR, MONTH_KEYWORDS, DAY]) + ")" for sep in DATE_NUM_SEPS)}))(?=\s|$|\.)',
    "left_date_with_spaces": fr"(?:^|\s)(?P<left_date_with_spaces>({DAY}?(\s|( of ))?{MONTH_STR_KEYWORDS}(?![\/\.\-])[\s\,]?{ALL_YEAR}?))(?=\s|$|\.)",
    "right_date_with_spaces": fr"(?:^|\s)(?P<right_date_with_spaces>({YEAR}\s{MONTH_STR_KEYWORDS}\s{DAY}?))(?=\s|$|\.)",
}

HOUR = "(2[0-4]|[1][0-9]|0?[0-9])"
MINUTE = "(60|[1-5][0-9]|0?[0-9])"
SECOND = "(60|[1-5][0-9]|0?[0-9])"
TIMES = {
    "%hh:%mm:%ss AM/PM": fr"\b{HOUR}:{MINUTE}:{SECOND}(\s?am|\s?pm|)( pdt| mst| mdt| cst| cdt| est| edt| ast| adt| ndt| pt| mt| ct| et| at| ist|)\b",
    "%hh:%mm AM/PM": fr"\b{HOUR}:{MINUTE}(\s?am|\s?pm|)( pdt| mst| mdt| cst| cdt| est| edt| ast| adt| ndt| pt| mt| ct| et| at| ist|)\b",
}
TIME_ONE_SHOT = "(" + "|".join({x for _, x in TIMES.items()}) + ")"

EMAIL_ONE_SHOT = r"\b[a-z0-9._%+-]+\s?@\s?[a-z0-9.-]+\.[a-z]{2,}"

URL_ONE_SHOT = r"(?:^|\s|\/)((?i)\b((?:https?:(?:\/{1,3}|[a-z0-9%])|[a-z0-9\.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b\/?(?!@))))"

MONEY_SIGNS_DICT = {
    "€": ["eur", "euro", "euros"],
    r"\$": ["usd", "dollar", "dollars"],
    "£": ["gbp", "pound", "pounds"],
    "₣": ["chf"],
    "zł": ["pln"],
}
MONEY_NAMES = "|".join(itertools.chain(*MONEY_SIGNS_DICT.values()))
MONEY_SIGNS = "|".join(MONEY_SIGNS_DICT.keys())
MONEY_KEYWORDS = f"{MONEY_SIGNS}|{MONEY_NAMES}"
MONEY_DICT = {
    "only_left_words": rf"(?:^|\s)(?P<only_left_words>\w+\s({MONEY_NAMES}))",
    "only_left_digits": rf"(?:^|\s)(?P<only_left_digits>\-?\d+([,\.]\d+)?\s?({MONEY_KEYWORDS}))",
    "only_right_digits": rf"(?:^|\s)(?P<only_right_digits>\-?({MONEY_KEYWORDS})\s?\-?\d+([,\.]\d+)?)(?=\s|$|\.[^\d])",
    "point_and_comma": rf"(?:^|\s)(?P<point_and_comma>({MONEY_KEYWORDS})?[\s\-]*\d{{1,3}}(\.\d{{3}})+\,\d+)(?=\s|$|\.)",
}

PHONE_WORDS = [
    "phone",
    "tel",
    "call us",
    "call on",
    "call",
    "t:",
    "at",
    "ph",
    "telephone",
    "p:",
    "f:",
    "fax",
    "facsimile",
    "T",
    "F",
    "P",
]
PHONE_DICT = {
    "with_brackets_by_blocks": r"(?:^|\s)(?P<with_brackets_by_blocks>\([\+]?\d{1,3}\)(\d{1,3})?([\/\-\.\s]\d{2,4})+)(?=\s|$|\.)",
    "with_plus_by_blocks": r"(?:^|\s)(?P<with_plus_by_blocks>\+\d{1,3}([\-\.\s]?\(\d{1,3}\))?\d{1,3}?([\/\-\.\s]\d{2,4})+)(?=\s|$|\.)",
    "with_plus_continuous": r"(?:^|\s)(?P<with_plus_continuous>(\+\d{8,12}))(?=\s|$|\.)",
    # 'base': r'(?:^|\s)(?P<base>(\d[\-\.\s])?\d{3}[\-\.\s]\d{3}[\-\.\s]\d{4})(?=\s|$|\.)',
    "with_words": fr'(?:^|\s)({"|".join(PHONE_WORDS)})'
    + r"[\-\.:#\s]+[a-zA-Z]*[\-\.:\s]*(?P<with_words>(\+[\s0-9]+)?(\d{3}|[\(\[]?[0-9]+[\)\]])?([\/\.\-\s]?[0-9]){6,12})(?=\s|$|\.)",
}

PERCENT_ONE_SHOT = r"\b\d+(?:\.\d+)?\s?%"


def get_date_from_str(text):
    return [
        match.span(name)
        for name, pattern in DATE_DICT.items()
        for match in re.finditer(pattern, text.lower())
        if len(match.group(name)) > 3
    ]


def get_time_from_str(text):
    return [match.span() for match in re.finditer(TIME_ONE_SHOT, text.lower())]


def get_email_from_str(text):
    return [match.span() for match in re.finditer(EMAIL_ONE_SHOT, text.lower())]


def get_url_from_str(text):
    return [match.span(1) for match in re.finditer(URL_ONE_SHOT, text.lower().replace("@ ", "@@"))]


def get_money_from_str(text):
    return [match.span(name) for name, pattern in MONEY_DICT.items() for match in re.finditer(pattern, text.lower())]


def get_phone_from_str(text):
    return [match.span(name) for name, pattern in PHONE_DICT.items() for match in re.finditer(pattern, text.lower())] + [
        match.span("with_words") for match in re.finditer(PHONE_DICT["with_words"], text)
    ]


def get_percent_from_str(text):
    return [match.span() for match in re.finditer(PERCENT_ONE_SHOT, text.lower())]


WRONG_DATE_WORDS = [
    "today",
    "yesterday",
    "tomorrow",
    "days",
    "months",
    "years",
    "weeks",
    "daily",
    "monthly",
    "annually",
    "annual",
    "date",
]


def filter_date_field(text: str):
    if re.search(r"\d{5,}", text):
        return False
    for word in WRONG_DATE_WORDS:
        if word.lower() in text:
            return False
    return True


def filter_person_field(text: str):
    return not any(char.isdigit() for char in text) and len(text) > 1


def filter_money_field(text: str):
    if all(not char.isdigit() for char in text) and len(text.strip().split(" ")) == 1:
        return False
    return True


def filter_phone_field(text: str, acceptable_phone_range=(8, 16)):
    return acceptable_phone_range[1] > sum(c.isdigit() for c in text) >= acceptable_phone_range[0]


def filter_email_field(text: str):
    return "@" in text


def filter_url_field(text: str):
    return "@" not in text




import re
from bs4 import BeautifulSoup


FROM_PATTERN = r'From:(\s*)(.*)(\s*)Sent:(\s*)(.*)(\s*)To:(\s*)(.*)(\s*)Cc:(\s*)(.*)(\s*)Subject:(\s*)(.*)(\s*)'


def find_deepest_splitter_parent(element):
    splitter = None
    stack = [(element, None)]  # Initialize stack with root element and no parent

    while stack:
        current, parent = stack.pop(0)

        # Check if current matches the splitter pattern
        if hasattr(current, 'text') and re.search(FROM_PATTERN, current.text.strip()):
            splitter = parent  # Update current_parent to the last parent if current matches

            # Traverse children to see if deeper matches exist
            for child in current.children:
                if hasattr(child, 'text'):
                    stack.append((child, current))  # Push child and current as its parent

    # Return the parent of the deepest element that matched the splitter
    if splitter:
        return splitter.parent
    return None


def process_request(request_id, message_id = None):
    url = f'https://api.famaga.org/imap/deal/{request_id}'
    headers = {
        'Authorization': 'Bearer YXBpZmFtYWdhcnU6RHpJVFd1Lk1COUV4LjNmdERsZ01YYlcvb0VFcW9NLw',
        'Cookie': 'PHPSESSID=8gv7kd7lne3dfu5jk7kqpkfj36'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if message_id:
        return next(msg for msg in data['content'] if msg['messageId'] == message_id)

    return response.content


def is_splitter_element(text: str) -> bool:
    is_date_matched = len(get_date_from_str(text)) > 0
    is_email_with_timestamp = len(list(re.finditer(EMAIL_TIMESTEMPS, text.lower())))

    return bool(is_date_matched and is_email_with_timestamp)


QUOTE_TAG = "blockquote"
EMAIL_TIMESTEMPS_LIST = [
    "wrote:",
    "wrote ---"
]

EMAIL_TIMESTEMPS = '|'.join(EMAIL_TIMESTEMPS_LIST)

BLOCKED_TAGS = ['style']

FROM_PATTER = r'From:(\s*)(.*)(\s*)Sent:(\s*)(.*)(\s*)To:(\s*)(.*)(\s*)Cc:(\s*)(.*)(\s*)Subject:(\s*)(.*)(\s*)'

def generate_conversations(element):
    print('---- Iter ----')
    stack = [element]

    while stack:
        current_element = stack.pop(0)
        blockquote = current_element.find('blockquote')
        if blockquote and blockquote != -1:
            blockquote.extract()
            stack.append(blockquote)

        message_elements = []

        for child in current_element.descendants:
            # if (blockquote := child.find('blockquote')) not in [None, -1]:
            #     blockquote.extract()
            #     stack.append(blockquote)

            if child.text.strip() and child.name not in BLOCKED_TAGS and child.name in ['p']:
                if is_splitter_element(child.text):
                    # Yield current message and start a new one if a splitter is found
                    if message_elements:
                        yield message_elements
                        message_elements = []
                elif list(re.finditer(FROM_PATTER, child.text)):
                    if message_elements:
                        yield message_elements
                        message_elements = [child.text.strip()]
                else:
                    # Collect text parts into the current message
                    message_elements.append(child.text.strip())

        # After processing all children, yield the collected message elements
        if message_elements:
            yield message_elements


def is_splitter(text):
    # Define patterns that indicate a new message
    patterns = [
        '---- Forwarded messages ----',
        r'\d{1,2} [A-Za-z]+ \d{4}, .*? wrote:'
    ]
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False


def get_conversation(element):
    stack = [element]
    stack_ids = {id(element)}
    conversation = []
    processed_elements = set()

    def _append_nested_element(element):
        if id(element) not in stack_ids:
            print(f'Append to stack {element.name} with id {id(element)}, attribute id [{element.get('id')}]')
            stack.append(element)
            stack_ids.add(id(element))

    def _append_messages(messages):
        print(f'Append messages {len(messages)}')
        conversation.append(messages)

    while stack:
        messages = []
        current = stack.pop(0)
        stack_ids.remove(id(current))

        print(f'\n--- ITER {len(stack)} {id(current)}----')
        childrens = list(current.children)
        print(f'Childs before extracting: {len(list(current.descendants))}')

        # Convert current to a hashable type and add to the set if not already processed
        if id(current) in processed_elements:
            continue  # Skip if already processed
        processed_elements.add(id(current))

        if current.name == 'blockquote':
            print('It\'s blockquote')

        blockquote = current.find('blockquote')
        if blockquote and blockquote != -1:
            blockquote.extract()
            _append_nested_element(blockquote)

        for child in childrens:
            splitter_parent = find_deepest_splitter_parent(child)
            if splitter_parent and splitter_parent != current:
                splitter_parent.extract()
                print('Splitter')
                _append_nested_element(splitter_parent)

        print(f'After extracting {len(list(current.descendants))}')

        for child in childrens:
            if child.name not in [None, 'style'] and child.text.strip():
                if 'From:' in child.text.strip():
                    _append_messages(messages)
                    messages = []
                else:
                    print(f'Append message with parent id {child.parent.get('id')}')
                    messages.append(child.text.strip())
                # messages.append(child.text.strip())

        _append_messages(messages)

    return conversation



# def get_conversation(element, message_elements: List[Any] = []):
#     print('---- Iter ----')
#     conversation_elements: List[Any] = []
#     next_iters = []
#
#     while next_iters:
#         for child in element.children:
#             if child.name and child.name not in BLOCKED_TAGS:
#                 blockquote = child.find('blockquote')
#                 if blockquote:
#                     print('Block quote was found.')
#                     # conversation_elements.append(message_elements)
#                     blockquote.extract()
#                     # conversation_elements += get_conversation(blockquote.parent, message_elements)
#                     # message_elements = []
#                 if child.text and is_splitter_element(child.text):
#                     print('Is splitter element!')
#                     conversation_elements.append(message_elements)
#                     message_elements = []
#                 elif child.text and list(re.finditer(r'From:(\s*)(.*)(\s*)Sent:(\s*)(.*)(\s*)To:(\s*)(.*)(\s*)Cc:(\s*)(.*)(\s*)Subject:(\s*)(.*)(\s*)', child.text)):
#                     print('From, Sent, To, CC, Subject was found.')
#                     conversation_elements.append(message_elements)
#                     message_elements = [child]
#                 elif child.text and bool(re.match(r'(\s*)(-+)(\s*)Forwarded Message(\s*)(-+)(\s*)', child.text)):
#                     print('Forwarded message was found.')
#                     conversation_elements.append(message_elements)
#                     message_elements = []
#                 elif child.name == QUOTE_TAG:
#                     conversation_elements.append(message_elements)
#                     message_elements = []
#                     conversation_elements += get_conversation(child)
#                 else:
#                     if child.text.strip():
#                         message_elements.append(child)
#                         print(child.name)

    # conversation_elements.append(message_elements)
    # return conversation_elements


deal_id, message_id = (425437, 'SN7PR19MB6829ACC4384D33E775265FB9AD05A@SN7PR19MB6829.namprd19.prod.outlook.com')

body = """
<html>

    <body>
        <div id="root">
            <div id="outer-wrap">
                <div id="inner-wrap">
                    <p>
                        <span>Your prompt feedback is much highly appreciated.</span>
                    </p>
                </div>
            </div>
        </div>
        <p></p>
        <p></p>
        <p>
            On Mon, 24 Jul 2023, 13:01 sales@famaga.com, <sales@famaga.com> wrote:
        </p>
        <div id="divRplyFwdMsg" dir="ltr"><font face="Calibri, sans-serif" style="font-size:11pt" color="#000000"><b>From:</b> acc@gulffalcon.co &lt;acc@gulffalcon.co&gt;<br>
            <b>Sent:</b> 29 July 2023 21:21<br>
            <b>To:</b> pushkar@famaga.com &lt;pushkar@famaga.com&gt;; 'MUATAZ % ABBAS %' &lt;info@gulffalcon.co&gt;; 'Fadi Asmar' &lt;fadyasmar75@gmail.com&gt;<br>
            <b>Cc:</b> mataz_2022@outlook.com &lt;mataz_2022@outlook.com&gt;<br>
            <b>Subject:</b> RE: Offer №425437 26.07.2023, VibraSens || FAMAGA Group *</font>
            <div id="message-content">&nbsp;</div>
        </div>
        <div id="omega">
            <div id="sigma">
                <p>Kindly find attached file</p>
                <div id="border-wrap" style="border:none; border-top:solid #E1E1E1 1.0pt; padding:3.0pt 0in 0in 0in">
                    <p class="x_MsoNormal"><b>From:</b> pushkar@famaga.com &lt;pushkar@famaga.com&gt; <br>
                    <b>Sent:</b> Saturday, July 29, 2023 8:18 PM<br>
                    <b>To:</b> MUATAZ % ABBAS % &lt;info@gulffalcon.co&gt;; Fadi Asmar &lt;fadyasmar75@gmail.com&gt;<br>
                    <b>Cc:</b> acc@gulffalcon.co; mataz_2022@outlook.com<br>
                    <b>Subject:</b> Re: Offer №425437 26.07.2023, VibraSens || FAMAGA Group *</p>
                </div>
                <p>Please send invoice!</p>
                <p class="x_MsoNormal">10:19 pm, 29 July 2023, "MUATAZ % ABBAS %" &lt;
                    <a href="mailto:info@gulffalcon.co">info@gulffalcon.co</a>&gt;:
                </p>
                <blockquote id="main-quote">
                    <div id="quote-wrap-1">
                        <div id="quote-inner-1">
                            <p class="x_MsoNormal"><span style="font-size:12.0pt; color:black">dear puskkar&nbsp;&nbsp;</span></p>
                        </div>
                        <div id="x_f2e387f28ef856c18dfa722bbcbb9bfadivRplyFwdMsg">
                            <p class="x_MsoNormal"><b><span style="color:black">From:</span></b><span style="color:black"> Fadi Asmar &lt;<a href="mailto:fadyasmar75@gmail.com">fadyasmar75@gmail.com</a>&gt;<br>
                            <b>Sent:</b> 29 July 2023 19:45<br>
                            <b>To:</b> <a href="mailto:pushkar@famaga.com">pushkar@famaga.com</a> &lt;<a href="mailto:pushkar@famaga.com">pushkar@famaga.com</a>&gt;<br>
                            <b>Cc:</b> <a href="mailto:info@gulffalcon.co">info@gulffalcon.co</a> &lt;<a href="mailto:info@gulffalcon.co">info@gulffalcon.co</a>&gt;;
                            <a href="mailto:acc@gulffalcon.co">acc@gulffalcon.co</a> &lt;<a href="mailto:acc@gulffalcon.co">acc@gulffalcon.co</a>&gt;;
                            <a href="mailto:mataz_2022@outlook.com">mataz_2022@outlook.com</a> &lt;<a href="mailto:mataz_2022@outlook.com">mataz_2022@outlook.com</a>&gt;<br>
                            <b>Subject:</b> Re: Offer №<span class="x_1f1ea193f6735cf0wmi-callto">425437 26</span>.07.2023, VibraSens || FAMAGA Group *</span>
                            </p>
                            <div id="inner-wrap-2">
                                <p class="x_MsoNormal">&nbsp;</p>
                            </div>
                        </div>
                    </div>

                    <div id="sub-root">
                        <div id="first-message">
                            <p class="x_MsoNormal">@ Pushkar, </p>
                            <div id="first-confirmation">
                                <p class="x_MsoNormal">Thank you for your confirmation.</p>
                            </div>
                            <div id="second-message">
                                <p class="x_MsoNormal">@ Noora,</p>
                            </div>
                            <div id="payment-request">
                                <p class="x_MsoNormal">Please proceed with the payment formalities.&nbsp;</p>
                            </div>
                            <div id="gratitude-message">
                                <p class="x_MsoNormal">Thank you,</p>
                            </div>
                            <div id="best-regards">
                                <p class="x_MsoNormal">Best&nbsp;Regards,</p>
                            </div>
                            <div id="sign-off">
                                <p class="x_MsoNormal">Fady</p>
                            </div>
                        </div>
                        <div id="final-message">
                            <div id="response-wrap">
                                <p class="x_MsoNormal">On Sat, 29 Jul 2023, 15:20 , &lt;<a href="mailto:pushkar@famaga.com">pushkar@famaga.com</a>&gt; wrote:</p>
                            </div>
                            <blockquote id="nested-quote">
                                <div id="nested-quote-wrap">
                                    <div id="nested-quote-inner">
                                        <p>
                                            Sir,

                                            its not same item at all, its item with another meters. and quantity is not same.
                                            It is logical that price is depends of quantity

                                            For Pos 1 = 5mtrs
                                            For Pos 2 = 10mtrs
                                        </p>
                                    </div>
                                </div>
                            </blockquote>
                        </div>
                    </div>
                </blockquote>
            </div>
        </div>        
    </body>
</html>

"""
# msg = process_request(deal_id, message_id)
# body = msg['body']

# with open(f'/Users/valuamba/projs/components_agent_sales/notebooks/famaga/deals_html/discount_v3/425437.html', 'r') as f:
#     body = f.read()

soup = BeautifulSoup(body, "html.parser")
body_el = soup.find('body')


# conversation_el = get_conversation(body_el)

conversation_el = get_conversation(body_el)

ll = list(conversation_el)

messages = ['\n'.join([paragraph.strip() for paragraph in messages_items]) for messages_items in ll]


for idx, msg in enumerate(messages):
    msg = re.sub(r'\n+', '\n', msg)
    if msg.strip():
        # pass
        print(f'Message: {len(messages) - idx}')
        print(f'```\n' + msg + '\n```\n\n')