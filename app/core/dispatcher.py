from typing import List

from pydantic import BaseModel

from core.actions.classify_contacts import Person
from core.actions.classify_intents import Intent


class Task(BaseModel):
    summary: str


def dispatch(contacts_details: Person, intents: List[Intent]) -> List[Task]:
    tasks: List[Task] = []
    for intent in intents:
        if intent.intent == 'Product Inquiry':
            if intent.sub_intent == 'Product Details Request':
                # Todo: add check weather customer ask about datasheet
                tasks.append(Task(summary="Find datasheet and share it with customer"))

    return tasks