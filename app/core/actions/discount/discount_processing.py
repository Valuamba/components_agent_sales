import redis
from pydantic import BaseModel, Field
from typing import List, Optional, Type, Any
from core.actions.base import BaseAction
from core.models.action import Action, ActionMetadata, Metadata
from core.bot import TelegramBotClient
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from models.deal import AgentTask, StatusType
from utility import select_json_block


class DiscountState(BaseModel):
    state: str
    justification: Optional[str] = None
    messages_ids: List[int]


class DiscountProcessingAction(BaseAction):
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger: LoggingService,
                 redis_client: redis.Redis):
        super().__init__(task_repository, telegram_bot, logger, openai_client, redis_client)

    @classmethod
    def get_action_name(cls):
        return "discount_processing"

    def prepare_ui(self, output):
        return f"""
Discount state: {output.state}
Justification: {output.justification}
"""

    def discount_processing(self, run_id: int, conversation: str) -> Action:
        prompt = f"""
Analyze the messages and try to figure out discount state at conversation.

By 'discount,' I also mean a request to lower the price, etc. The following or other terms may be used for this purpose: - discount, payment terms, lower price, 
your price is too high, provide us a cheaper price, better price, expensive.

The possible discount states: NotHandled, Rejected, RepeatedRequest, NotAsked.

Conversation:
{conversation}

Put the response into ```json``` format like this:
```json
{{
    "state": <discount state>,
    "justification": <justification why client ask for discount>, // fill this field only if it specified at customer messages
    "messages_ids": array[] // messages ids where customer or sales manager discuss or mention discount
}}
```
"""
        model = "gpt-4"
        action_version = 1
        return self.execute_action(run_id, prompt, model, DiscountState, self.get_action_name(), action_version)
