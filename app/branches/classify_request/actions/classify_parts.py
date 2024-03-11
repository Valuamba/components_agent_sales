from typing import Optional, List
from pydantic import BaseModel

from branches.branch import AgentFinish
from branches.completion import GPTCompletionResolver
from branches.utils import select_json_block


class DetailRequest(BaseModel):
    amount: int | None
    brand_name: str | None
    part_number: str


class ClientInfo(BaseModel):
    country: Optional[str] = None
    domain: Optional[str] = None
    email: Optional[str] = None
    office_country: Optional[str] = None


class ClassifyAgentResponse(BaseModel):
    parts: List[DetailRequest]
    client: ClientInfo
    deal_id: Optional[int] = None
    message_id: Optional[int] = None
    agent_task_id: Optional[int] = None


class ClassifyPartsAction:
    def __init__(self, gpt_completion_resolver):
        self.gpt_completion_resolver: GPTCompletionResolver = gpt_completion_resolver

    def name(self) -> str:
        return "classify_parts"

    def classify_client_response(self, deal_id, message):
        response = self.gpt_completion_resolver.create_completion(name=self.name(), deal_id=deal_id, messages=[
            {"role": "user", "content": f"""
Try to extract from text brand name, amount, detail name, part number from the text. Also recognize country by text.
<<<>>>
{message}
<<<>>>

If you cannot recognize specified parameters please put `null` value.

---
Your response should be a list of comma separated values, eg: `foo, bar, baz`

The output should be a markdown code snippet formatted in the following adr, including the leading and trailing "\`\`\`json" and "\`\`\`":

```json
{{
    "parts": [
        {{
           "amount": int // This is the amount of details
           "brand_name": string // This is thr brand  name of detail
           "part_number": string // This is the part number of detail
        }}
    ],
    "client": {{
        "country": string // This is the country of detail,
        "domain": string // customer company domain
        "email": string // customer email,
        "office_country": string // country of customer office
    }}
}}
```        

"""}], temperature=0.3)
        classified_json_data = select_json_block(response)
        order = ClassifyAgentResponse.model_validate(classified_json_data)

        return AgentFinish(output=order, action=self.name())