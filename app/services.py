from models import Detail, DetailRequest, SuitableDetail
from utility import select_json_block

from openai import OpenAI
from psycopg2.extensions import cursor as CursorType


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

class LoggerService:
    def __init__(self, context):
        self.context = context

    def info(self, msg: str):
        print(f'[{self.context.trace_id}] {msg}')


class DetailInfoRepository:

    def __init__(self, cursor, vector_collection_name, similarity_search_limit):
        self.cursor: CursorType = cursor
        self.vector_collection_name = vector_collection_name
        self.similarity_search_limit = similarity_search_limit

    def get_top_relevant_messages(self, embeddings, k=3):
        try:
            query = f"""
                WITH vector_matches AS (
                    SELECT brand_id, name, embedding <=> '{embeddings}' AS distance
                    FROM {self.vector_collection_name}
                )
                SELECT brand_id, name, distance
                FROM vector_matches
                ORDER BY distance
                LIMIT '{k}';
            """
            
            self.cursor.execute(query)
            all_matches = self.cursor.fetchall()
            
            relevant_matches = []
            print('All matches:')
            for doc in all_matches:
                print(f'-- {round(doc[2], 2)}: {doc[1]}')
                
                if round(doc[2], 2) <= float(self.similarity_search_limit):
                    relevant_matches.append({
                        "document": doc,
                        "score": doc[2]
                        })

            if len(relevant_matches) == 0:
                print("No relevant matches found")
            else:
                print("Relevant matches: ")
                [print(f'-- {round(doc["score"], 2)}: {doc["document"][2]}') for doc in relevant_matches]
            return relevant_matches
        except Exception as e:
            print(f"[get_top_relevant_messages] {type(e).__name__} exception: {e}")
            return []

    def select_detail_by_ids(self, details_ids):
        details_ids_str = ', '.join([str(d) for d in details_ids])
        query = f"select * from details_info where id IN({details_ids_str})"

        self.cursor.execute(query)

        all_matches = self.cursor.fetchall()

        details = []
        for match in all_matches:
            details.append(Detail(
                id=match[0],
                part_number=match[1],
                brand_name=match[4],
                description=match[5]
            ))
        return details

    def select_detail_by_part_number(self, part_number: str):
        query = f"select * from details_info where part_number='{part_number}'"

        try:
            self.cursor.execute(query)

            all_matches = self.cursor.fetchall()

        
            details = []
            for match in all_matches:
                details.append(Detail(
                    id=match[0],
                    part_number=match[1],
                    brand_name=match[4],
                    description=match[5]
                ))
            return details
        except:
            return []
        
    def select_brands_details(self, brand_ids):
        ids_str = ', '.join([str(b) for b in brand_ids])

        query = f"select * from details_info where brand_id IN({ids_str})"

        self.cursor.execute(query)

        return self.cursor.fetchall()
        

class ClassifyEmailAgent:

    def __init__(self, 
                 openai_client: OpenAI, 
                 logger: LoggerService, 
                 famaga_repo: DetailInfoRepository):
        self.openai_client = openai_client
        self.logger = logger
        self.famaga_repo = famaga_repo

    async def classify_client_response(self, request: str, model = 'gpt-4'):
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

        self.logger.info(f'Classify prompt: {classify_prompt}')

        resp = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": classify_prompt}
                ],
                stream=False,
            )

        self.logger.info(f'Classification response: {resp.choices[0].message.content}')
            

        classified_json_data = select_json_block(resp.choices[0].message.content)

        classified_details = [DetailRequest(**item) for item in classified_json_data]

        # await ctx.sendMessage('\n\n'.join([ f'<b>Amount:</b> {detail.amount}\n<b>Brand name:</b> {detail.brand_name}\n<b>Part number:</b> {detail.part_number}\n<b>Country:</b> {detail.country}'  
        #                             for detail in classified_details]))

        return classified_details
    
    def find_suitable_items(self, search_response, query: str, detail: DetailRequest, model = 'gpt-4'):
        google_search_output = ''
        for idx, google_item in enumerate(search_response['organic']):
            text = f"""
    ID: {idx}
    Title: {google_item['title']}
    Snippet: {google_item['snippet']}
        """
            if 'price' in google_item:
                text += f'Price: {google_item["currency"]}{google_item["price"]}'
                
            google_search_output += text + '\n\n'


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

                
        resp = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": find_suitable_items_prompt}
                ],
                stream=False,
            )
        
        self.logger.info(f'Suitable details: {resp.choices[0].message.content}')

        suitable_details_json_data = select_json_block(resp.choices[0].message.content)

        suitable_details = [SuitableDetail(**item) for item in suitable_details_json_data]

        return suitable_details
    
    def get_embeddings_vector(self, text: str, openai_embeddings_model: str = 'text-embedding-ada-002'):
        res = self.openai_client.embeddings.create(input = [text], model=openai_embeddings_model)
        return res.data[0].embedding
    

    def select_brands(self, brand, k=3):
        brands_response = self.famaga_repo.get_top_relevant_messages(self.get_embeddings_vector(brand))
        return [brand['document'][0] for brand in brands_response]

    def search_detail_at_db(self, detail: DetailRequest):
        details = []
        if detail.part_number:
            details = self.famaga_repo.select_detail_by_part_number(detail.part_number)
            
        if len(details) == 0 and detail.brand_name:
            try:
                brand_ids = self.select_brands(detail.brand_name)
                brand_matches = self.famaga_repo.select_brands_details(brand_ids)

                table_details = [ f'{match[0]}, {match[1]}' for match in brand_matches]
                table_details_str = '\n'.join(table_details)

                prompt = f"""
        Select detail ids, by part numbers that most suitable for this 'CD1-K-400/30"


        Your response should be a list of comma separated values, eg: `foo, bar, baz`

        The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

        ```json
        [12, 124, 12345]
        ```

        {table_details_str}
        """

                resp = self.openai_client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0
                )

                json_data = select_json_block(resp.choices[0].message.content)

                details = self.famaga_repo.select_detail_by_ids(json_data)
            except:
                return []

        return details