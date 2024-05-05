from pydantic import BaseModel, Field
from typing import Type, Any
from core.actions.base import BaseAction
from core.models.action import Action, ActionMetadata, Metadata
from core.bot import TelegramBotClient
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from models.deal import AgentTask, StatusType
from utility import select_json_block


class DocumentSelection(BaseModel):
    document_name: str


class DocumentSelectionAction(BaseAction):
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger: LoggingService):
        super().__init__(task_repository, telegram_bot, logger, openai_client)

    @classmethod
    def get_action_name(cls):
        return "document_selection"

    def document_selection(self, run_id: int, discount_messages: str, purchase_history: str, current_offer: str) -> Action:
        prompt = f"""
Select one of documents with instructions:

- Discount -> Default: default instruction how to do negotiations with customer about decision and pricing.
- Discount -> Purchased same product: guide how to deal with loyal customer that already bought product that requires at current deal.

Messages about discount at conversation:
```
{discount_messages}
```

{purchase_history}

Deal offer:
{current_offer}

Put the response into ```json``` format like this:
```json
{{
    "document_name": <the name of docuemnt>
}}
```
"""
        model = "gpt-4"
        action_version = 1
        return self.execute_action(run_id, prompt, model, DocumentSelection, self.get_action_name(), action_version)
