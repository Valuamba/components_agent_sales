from schemas.completion import (
    DetailRequest,
    SuitableDetail,
    ClassifiedMessageData,
    EmailRequest,
)
from utility import select_json_block

# from services.detail_info_repository import DetailInfoRepository
from repositories import DetailInfoRepository, EmbeddingRepository
from services.logger_service import LoggingService
from services.openai_client import OpenAIClient


detail_classification_schema = """
Your response should be a list of comma separated values, eg: `foo, bar, baz`

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

```json
{
    "parts": [
        {
           "amount": int // This is the amount of details
           "brand_name": string // This is thr brand  name of detail
           "part_number": string // This is the part number of detail
        }
    ],
    "client": {
        "country": string // This is the country of detail,
        "domain": string // customer company domain
        "email": string // customer email,
        "office_country": string // country of customer office
    }
}
```
"""

detail_classification_few_shot = """
Answer could contain comma separated list of json objects, like in following example:

```json
{
    "parts": [
        {
           "amount": 1,
           "brand_name": "Airtac",
           "part_number": "A05-DMSE-020"
        },
        {
           "amount": 15,
           "brand_name": "Clayton",
           "part_number": "0039042"
        }
    ],
    "client": {
        "country": "Romania",
        "domain": "epno.com.mx",
        "email": "roberto.sosa@epno.com.mx",
        "office_country": "Mexico"
    }
}
```
"""

system_prompt = """
You are manufacturer sales specialist. You know many brands, models, articles of manufacturer details.
"""


suitable_items_few_shot = """
Answer could contain comma separated list of json objects, like in following example for query "E+E EE741":
```json
{
    "google_items": [
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
        }
    ],
    "metadata": {
        "full_brand": ""E+E Elektronik"
    }
]
```
"""

suitable_items_schema = """
Your response should be a list of comma separated values, eg: `foo, bar, baz`

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

```json
{
    "google_items": [
        {
           "id": int // This is the Id of item
           "relevance": string[] // This is relevant string array that shows relevant parameters
        }
    ],
    "metadata": {
        "full_brand": string
    }
}
```
"""


class ClassifyEmailAgent:
    def __init__(
        self,
        openai_client: OpenAIClient,
        logger: LoggingService,
        detail_info_repository: DetailInfoRepository,
        embeddings_repository: EmbeddingRepository,
    ):
        self.openai_client = openai_client
        self.logger = logger
        self.detail_info_repository = detail_info_repository
        self.embeddings_repository = embeddings_repository

    async def classify_client_response(self, request: EmailRequest, model="gpt-4"):
        classify_prompt = f"""
        Try to extract from text brand name, amount, detail name, part number from the text. Also recognize country by text.
        <<<>>>
        Subject: {request.body}
        From: {request.from_client}

        {request.body}
        <<<>>>

        If you cannot recognize specified parameters please put `null` value.

        ---
        {detail_classification_schema}

        {detail_classification_few_shot}

        """

        self.logger.info(f"Classify prompt: {classify_prompt}")

        completion = self.openai_client.create_completion(
            model,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": classify_prompt},
            ],
        )

        self.logger.info(
            f"Classification response: {completion.content}. Spent: {completion.usage_cost_usd}$"
        )

        classified_json_data = select_json_block(completion.content)
        order = ClassifiedMessageData.model_validate(classified_json_data)

        # classified_details = [DetailRequest(**item) for item in classified_json_data]

        # await ctx.sendMessage('\n\n'.join([ f'<b>Amount:</b> {detail.amount}\n<b>Brand name:</b> {detail.brand_name}\n<b>Part number:</b> {detail.part_number}\n<b>Country:</b> {detail.country}'
        #                             for detail in classified_details]))

        return order, completion.usage_cost_usd

    def find_suitable_items(
        self, search_itmes, query: str, detail: DetailRequest, model="gpt-4"
    ):
        google_search_output = ""
        for idx, google_item in enumerate(search_itmes):
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

    Fullbrand -  full manufacturer or supplier brand without details about parts finded in items.

    {suitable_items_schema}

    {suitable_items_few_shot}

    {google_search_output}
    """

        completion = self.openai_client.create_completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": find_suitable_items_prompt},
            ],
        )

        self.logger.info(f"Suitable details: {completion.content}")

        suitable_details_json_data = select_json_block(completion.content)

        suitable_details = [
            SuitableDetail(**item)
            for item in suitable_details_json_data["google_items"]
        ]

        return (
            suitable_details,
            completion.usage_cost_usd,
            suitable_details_json_data["metadata"],
        )

    def get_embeddings_vector(
        self, text: str, openai_embeddings_model: str = "text-embedding-ada-002"
    ):
        res = self.openai_client.client.embeddings.create(
            input=[text], model=openai_embeddings_model
        )
        return res.data[0].embedding

    def select_brands(self, brand, k=3):
        brands_response = self.embeddings_repository.get_top_relevant_messages(
            self.get_embeddings_vector(brand)
        )
        return [brand["document"][0] for brand in brands_response]

    def search_detail_at_db(self, detail: DetailRequest, model="gpt-4"):
        details = []
        if detail.part_number:
            details = self.detail_info_repository.get_detail_by_part_number(
                detail.part_number
            )

        if len(details) == 0 and detail.brand_name:
            try:
                brand_ids = self.select_brands(detail.brand_name)
                brand_matches = self.detail_info_repository.get_details_by_brand_ids(
                    brand_ids
                )

                table_details = [
                    f"{match.id}, {match.part_number}" for match in brand_matches
                ]
                table_details_str = "\n".join(table_details)

                prompt = f"""
        Select detail ids, by part numbers that most suitable for this '{detail.part_number}"


        Your response should be a list of comma separated values, eg: `foo, bar, baz`

        The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

        ```json
        [12, 124, 12345]
        ```

        {table_details_str}
        """
                completion = self.openai_client.create_completion(
                    model,
                    [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0,
                )

                json_data = select_json_block(completion.content)

                details = self.detail_info_repository.get_details_by_ids(json_data)

                return details, completion.usage_cost_usd
            except Exception as exc:
                self.logger.error(str(exc))
                return [], 0

        return details, 0
