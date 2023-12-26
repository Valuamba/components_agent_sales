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


        

