from abc import ABC
from typing import List, Optional

from pydantic.v1 import BaseModel

from core.models.action import Action, ActionMetadata, Metadata, Data
from models.deal import AgentTask, StatusType
from repositories import TaskRepository
from services import OpenAIClient
from utility import select_json_block


class Serializable(BaseModel, ABC):

    @classmethod
    def get_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @classmethod
    def get_version(cls) -> "str":
        return "1.0"


class Part(BaseModel):
    amount: int
    brand_name: str
    part_number: str


class Client(BaseModel):
    country: str
    domain: str
    email: str
    office_country: str


class Intent(BaseModel):
    intent: str
    sub_intent: str
    branch: str


class ClassifyIntentsResponseSchema(Serializable):
    intents: List[Intent]


class ClassifyIntentsAction:
    def __init__(self, openai_client: OpenAIClient, task_repository: TaskRepository):
        self.openai_client = openai_client
        self.task_repository = task_repository

    @classmethod
    def get_action_name(cls):
        return "classify_intents"

    def create_completion(self) -> any:
        return {}

    def classify_intents(self, run_id: int, message: str):
        model = 'gpt-4'
        action_version = 1

        actual_status = StatusType.InProgress
        task = AgentTask(run_id=run_id, status=actual_status.name, action=self.get_action_name())
        self.task_repository.create_task_for_deal(task)

        prompt = f"""
Please attach to each message in chat history tags, annotations, indexes, intents to better classification and search.
The message could have one or more intents.

Message:
```
{message}
```

For example, this message would have intents:
- customer: Hello So as not to waste precious time. We order devices from offer no. 440822 of friday, 29 september 2023 . 
If possible, please provide an additional discount on your purchase. Please confirm acceptance of our order. 
In the meantime, once you know what the transport cost will be, we will discuss how to deliver the parcel to us 
or whether we will collect it ourselves.

Example of intents/sub-intents/branches namings:
   - Order Processing -> Order Placement Confirmation -> Confirmation of Specific Offer
   - Order Processing -> Order Acceptance Confirmation -> Confirmation of Order Receipt and Acceptance
   - Pricing and Quotes -> Discount Inquiry -> Request for Additional Discount on Purchase
   - Pricing and Quotes -> Transport Cost Inquiry -> Inquiry About Delivery Costs
   - Delivery and Shipping -> Delivery Method Discussion -> Discussing Whether to Ship or Self-Collect
   - Delivery and Shipping -> Discussing Logistics -> Coordination of Transport and Delivery Options
   - Product Inquiry -> Availability Check -> Inquiry about Availability of Specific Parts (Stators and Rotors)
   - Product Inquiry -> Product Comparison
   
Your response should be a list of comma separated values, eg: `foo, bar, baz`

The output should be a markdown code snippet formatted in the following adr, including the leading and trailing "\`\`\`json" and "\`\`\`":

```json
[
    {{
        "intent": <intent>,
        "sub_intent": <sub_intent>,
        "branch": <branch>,
    }}
]
```     
"""

        completion = self.openai_client.create_completion(
            model,
            [
                {"role": "user", "content": prompt}
            ],
        )

        response_raw_json = select_json_block(completion.content)
        parsed_intents = [Intent(**intent) for intent in response_raw_json]

        return Action(
            action=ActionMetadata(
                action_version=action_version,
                action_name=self.get_action_name(),
                action_id=task.task_id,
                action_time=round(completion.completion_time_ms, 0),
                action_status=actual_status.value,
            ),
            data=parsed_intents,
            metadata=Metadata(
                completion_cost_usd=round(completion.usage_cost_usd, 3),
                completion_time_sec=round(completion.completion_time_ms, 0),
                llm_model=completion.model,
                raw_output=completion.content
            )
        )
