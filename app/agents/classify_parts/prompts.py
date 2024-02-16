
FORMAT_RESPONSE = """
Your response should be a list of comma separated values, eg: `foo, bar, baz`

The output should be a markdown code snippet formatted in the following adr, including the leading and trailing "\`\`\`json" and "\`\`\`":

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


DETAIL_CLASSIFICATION_EXAMPLES = """
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


CLASSIFY_PARTS_PROMPT = """
Try to extract from text brand name, amount, detail name, part number from the text. Also recognize country by text.
<<<>>>
Subject: {subject}
From: {from_client}
       
{request_body}
<<<>>>

If you cannot recognize specified parameters please put `null` value.

---
{response_format}

{few_shot_examples}
"""


SYSTEM_PROMPT = """
You are manufacturer sales specialist. You know many brands, models, articles of manufacturer details.
"""