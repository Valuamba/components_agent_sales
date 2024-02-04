from pydantic import BaseModel
from typing import Optional, List
import json
import re
import uuid
import requests

from openai import OpenAI


import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

import json
import psycopg2
import pgvector
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
import pandas as pd

import asyncio

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

PGVECTOR_CONNECTION_STRING = "postgresql://admin:5tgb%25TGB@localhost:45048/famaga"
PGVECTOR_COLLECTION_NAME = "details"
TOP_K = 6
SIMILARITY_SEARCH_LIMIT = 0.1
EMBEDDINGS_MODEL = "text-embedding-ada-002"
INDEX_DIMENSIONS = 1536


class DetailRequest(BaseModel):
    amount: int
    brand_name: str
    part_number: str
    country: Optional[str] = None


class Detail(BaseModel):
    id: int
    brand_name: str
    part_number: str
    description: str


class SuitableDetail(BaseModel):
    id: int
    relevance: List[str]


detail_classification_schema = """
Your response should be a list of comma separated values, eg: `foo, bar, baz`

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

```json
[
{
   "amount": int // This is the amount of details
   "brand_name": string // This is thr brand  name of detail
   "part_number": string // This is the part number of detail
   "country": string // This is the country of detail
}
]
```
"""

detail_classification_few_shot = """
Answer could contain comma separated list of json objects, like in following example:

```json
[
{
   "amount": 1,
   "brand_name": "Airtac",
   "part_number": "A05-DMSE-020",
   "country": "Romania"
},
{
   "amount": 15,
   "brand_name": "Clayton",
   "part_number": "0039042",
   "country": "null
}
]
```
"""

system_prompt = """
You are manufacturer sales specialist. You know many brands, models, articles of manufacturer details.
"""


suitable_items_few_shot = """
Answer could contain comma separated list of json objects, like in following example:
```json
[
{
   "id": 0
   "relevance": [
      "equal part number",
      "has price"
   ]
},
{
   "id": 3
   "relevance": [
      "equal part number",
      "has price",
      "equal brand name",
      "equal model"
   ]
},
]
```
"""

suitable_items_schema = """
Your response should be a list of comma separated values, eg: `foo, bar, baz`

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

```json
[
{
   "id": int // This is the Id of item
   "relevance": string[] // This is relevant string array that shows relevant parameters
}
]
```
"""


class Context:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.trace_id = str(uuid.uuid4())

    def _escape_markdown_v2(self, text):
        escape_chars = "_*[]()~`>#+-=|{}.!"
        return "".join("\\" + char if char in escape_chars else char for char in text)

    def info(self, log: str):
        print(f"[{self.trace_id}] {log}")

    async def sendMessage(self, text: str):
        await self.bot.send_message(
            chat_id=6538129881, text=text, parse_mode=ParseMode.HTML
        )


def select_json_block(text: str):
    regex = r',(?!\s*?[\{\["\'\w])'
    cleaned_input = re.sub(regex, "", text)
    match = re.search(r"```json\n([\s\S]*?)\n```", text)
    if match:
        json_data = match.group(1)
    else:
        raise ValueError("No valid JSON data found in the string.")

    return json.loads(json_data)


async def classify_client_response(
    ctx: Context, client: OpenAI, request: str, model="gpt-4"
):
    classify_prompt = f"""
Try to extract from text brand name, amount, detail name, part number from the text. Also recognize country by text.
<<<>>>
{request}
<<<>>>

If you cannot recognize specified parameters please put `null` value.

---
{detail_classification_schema}

{detail_classification_few_shot}

"""

    ctx.info(f"Classify prompt: {classify_prompt}")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": classify_prompt},
        ],
        stream=False,
    )

    ctx.info(f"Classification response: {resp.choices[0].message.content}")

    classified_json_data = select_json_block(resp.choices[0].message.content)

    classified_details = [DetailRequest(**item) for item in classified_json_data]

    await ctx.sendMessage(
        "\n\n".join(
            [
                f"<b>Amount:</b> {detail.amount}\n<b>Brand name:</b> {detail.brand_name}\n<b>Part number:</b> {detail.part_number}\n<b>Country:</b> {detail.country}"
                for detail in classified_details
            ]
        )
    )

    return classified_details


def google_search(query: str, country="us"):
    url = "https://google.serper.dev/search"

    payload = json.dumps({"q": query, "gl": country, "page": 1})

    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


def search_details_offers(ctx: Context, query: str):
    ctx.info(f"Google search query: {query}")

    search_response = json.loads(google_search(query))

    return search_response


def select_detail_by_part_number(db_cursor, part_number: str):
    query = f"select * from details_info where part_number='{part_number}'"

    try:
        db_cursor.execute(query)

        all_matches = db_cursor.fetchall()

        details = []
        for match in all_matches:
            details.append(
                Detail(
                    id=match[0],
                    part_number=match[1],
                    brand_name=match[4],
                    description=match[5],
                )
            )
        return details
    except:
        return []


def select_detail_by_ids(db_cursor, details_ids):
    details_ids_str = ", ".join([str(d) for d in details_ids])
    query = f"select * from details_info where id IN({details_ids_str})"

    db_cursor.execute(query)

    all_matches = db_cursor.fetchall()

    details = []
    for match in all_matches:
        details.append(
            Detail(
                id=match[0],
                part_number=match[1],
                brand_name=match[4],
                description=match[5],
            )
        )
    return details


def find_suitable_items(
    ctx,
    client: OpenAI,
    search_response,
    query: str,
    detail: DetailRequest,
    model="gpt-4",
):
    google_search_output = ""
    for idx, google_item in enumerate(search_response["organic"]):
        text = f"""
ID: {idx}
Title: {google_item['title']}
Snippet: {google_item['snippet']}
    """
        if "price" in google_item:
            text += f'Price: {google_item["currency"]}{google_item["price"]}'

        google_search_output += text + "\n\n"

    find_suitable_items_prompt = f"""
You are manufacturer sales specialist. You know many brands, models, articles of manufacturer details.

Metadata:
 amount: {detail.amount}
 brand_name: {detail.brand_name}
 part number: {detail.part_number}

Query: "{query}"

Select items based on query that would be most suitable by title, snippet for query. It good if item has price because it would be helpful for sales manager. It very good if brand name, part number equals to presented in Query and metadata, but it not strictly necessary.

Please list suitable IDs with Relevance field that describe why this item suitable for us, it could contains some checkpoints, like:

Relevance:
- equal part number
- equal brand_name
- contains price

{suitable_items_schema}

{suitable_items_few_shot}

{google_search_output}
"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": find_suitable_items_prompt},
        ],
        stream=False,
    )

    ctx.info(f"Suitable details: {resp.choices[0].message.content}")

    suitable_details_json_data = select_json_block(resp.choices[0].message.content)

    suitable_details = [SuitableDetail(**item) for item in suitable_details_json_data]

    return suitable_details


def get_top_relevant_messages(db_cursor, embeddings, k=3):
    try:
        query = f"""
            WITH vector_matches AS (
                SELECT brand_id, name, embedding <=> '{embeddings}' AS distance
                FROM {PGVECTOR_COLLECTION_NAME}
            )
            SELECT brand_id, name, distance
            FROM vector_matches
            ORDER BY distance
            LIMIT '{k}';
        """

        db_cursor.execute(query)
        all_matches = db_cursor.fetchall()

        relevant_matches = []
        print("All matches:")
        for doc in all_matches:
            print(f"-- {round(doc[2], 2)}: {doc[1]}")

            if round(doc[2], 2) <= float(SIMILARITY_SEARCH_LIMIT):
                relevant_matches.append({"document": doc, "score": doc[2]})

        if len(relevant_matches) == 0:
            print("No relevant matches found")
        else:
            print("Relevant matches: ")
            [
                print(f'-- {round(doc["score"], 2)}: {doc["document"][2]}')
                for doc in relevant_matches
            ]
        return relevant_matches
    except Exception as e:
        print(f"[get_top_relevant_messages] {type(e).__name__} exception: {e}")
        return []


def get_embeddings_vector(text: str, client: OpenAI):
    res = client.embeddings.create(input=[text], model=EMBEDDINGS_MODEL)
    return res.data[0].embedding


def select_brands_details(db_cursor, brand_ids):
    ids_str = ", ".join([str(b) for b in brand_ids])

    query = f"select * from details_info where brand_id IN({ids_str})"

    db_cursor.execute(query)

    return db_cursor.fetchall()


def select_brands(db_cursor, brand, client, k=3):
    brands_response = get_top_relevant_messages(
        db_cursor, get_embeddings_vector(brand, client)
    )
    return [brand["document"][0] for brand in brands_response]


def search_detail_at_db(db_cursor, client, detail: DetailRequest):
    details = []
    if detail.part_number:
        details = select_detail_by_part_number(db_cursor, detail.part_number)

    if len(details) == 0 and detail.brand_name:
        try:
            brand_ids = select_brands(db_cursor, detail.brand_name, client)
            brand_matches = select_brands_details(db_cursor, brand_ids)

            table_details = [f"{match[0]}, {match[1]}" for match in brand_matches]
            table_details_str = "\n".join(table_details)

            prompt = f"""
    Select detail ids, by part numbers that most suitable for this 'CD1-K-400/30"


    Your response should be a list of comma separated values, eg: `foo, bar, baz`

    The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

    ```json
    [12, 124, 12345]
    ```

    {table_details_str}
    """

            resp = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )

            json_data = select_json_block(resp.choices[0].message.content)

            details = select_detail_by_ids(db_cursor, json_data)
        except:
            return []

    return details


def remove_html(text):
    cleaned_text = re.sub(r"<[^>]+>", "", text)
    return cleaned_text


async def main():
    request = """
Buna ziua,

Va rog o oferta de pret si termen de livrare pentru urmatoarele produse:

INFRANOR CD1-K-400/30
INFRANOR CD1-pm-400/14
MAVILOR BS 073A.00.0105.D2 Type BLS-073
MAVILOR BS 1124.00.2105.00 Type BLS-112

Multumesc

Cu stima,
Claudiu Chesa
0747 420552
SC MOARA CIBIN SA
SIBIU

"""

    db_connection = psycopg2.connect(PGVECTOR_CONNECTION_STRING)
    db_cursor = db_connection.cursor()
    db_connection.autocommit = True

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    context = Context(bot)

    details = await classify_client_response(context, client, request)

    for detail in details:
        try:
            presneted_db_details = search_detail_at_db(db_cursor, client, detail)

            if len(presneted_db_details):
                await context.sendMessage(
                    "<b>Details at company table</b>\n\n"
                    + "\n\n".join(
                        [
                            f"<b>ID</b>: {detail.id}\n"
                            + f"<b>Brand name:</b> {detail.brand_name}\n<b>Part number:</b> {detail.part_number}\n<b>Description:</b> {detail.description}"
                            for detail in presneted_db_details
                        ]
                    )
                )

            query = f"{detail.brand_name} {detail.part_number}"

            search_response = search_details_offers(context, query)
            suitable_items = find_suitable_items(
                context, client, search_response, query, detail
            )

            suitable_items_str = "<b>Google search:</b>\n\n"
            for suitable_item in suitable_items:
                full_item_info = search_response["organic"][suitable_item.id]

                text = f"""
<b>Title:</b> {remove_html(full_item_info['title'])}
<b>Snippet:</b> {remove_html(full_item_info['snippet'])}
<b>Link:</b> {remove_html(full_item_info['link'])}
"""
                if "price" in full_item_info:
                    text += f'<b>Price:</b> {full_item_info["currency"]}{full_item_info["price"]}'

                suitable_items_str += text + "\n\n"

            context.info(suitable_items_str)
            await context.sendMessage(suitable_items_str)
        except Exception as exc:
            print(f"Error: {exc}")


asyncio.run(main())
