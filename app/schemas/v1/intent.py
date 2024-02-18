from typing import List, Literal
from pydantic import BaseModel, Field
import json


class Intent(BaseModel):
    intent: str
    sub_intent: str
    branch: str


class Message(BaseModel):
    id: str  # Adjust the type as needed (e.g., int for integer IDs)
    body: str
    from_: Literal['customer', 'manager'] = Field(..., alias='from')
    intents: List[Intent]

    class Config:
        allow_population_by_field_name = True