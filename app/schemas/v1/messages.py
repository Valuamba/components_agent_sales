from typing import List
from pydantic import BaseModel, UUID4


class IntentModel(BaseModel):
    uuid: UUID4
    intent: str
    sub_intent: str
    branch: str


class MessageModel(BaseModel):
    uuid: UUID4
    id: int
    body: str
    from_type: int
    intents: List[IntentModel]


class DealMessagesResponse(BaseModel):
    deal_uuid: UUID4
    messages: List[MessageModel]