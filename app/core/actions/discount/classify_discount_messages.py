import redis
from pydantic import BaseModel, Field
from typing import List, Optional, Type, Any
from core.actions.base import BaseAction
from core.models.action import Action, ActionMetadata, Metadata
from core.bot import TelegramBotClient
from models.deal import LLMRun
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from utils.cache import stored


class DiscountMessage(BaseModel):
    pass


class ClassifyDiscountMessages(BaseAction):
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger: LoggingService,
                 redis_client: redis.Redis):
        super().__init__(task_repository, telegram_bot, logger, openai_client, redis_client)

    @classmethod
    def get_action_name(cls):
        return "classify_discount_messages"

    def prepare_ui(self, output):
        return f"""
Messages amount: {len(output)}
"""


    # @stored
    def classify_discount_messages(self, run: LLMRun, conversation: str) -> Action:
        prompt = """
        You are Sales manager. Read a conversation between customer and manager and classify discount chronology discussion.

        Respond with array of messages where was mentioned or discussed discount.
        Respond with an empty string, if none is found

        ```txt
        $TXT
        ```
        
        Put the response into ```json``` format like this:
        ```json
        [
            {
                "message": <message>,
                "sender": <sender who sent the message> // customer or manager
            }
        ]
        ```
        """.strip() + "\n"

        filled = prompt.replace("$TXT", conversation)

        model = "gpt-4"
        action_version = 1
        return self.execute_action(run, filled, model, None, self.get_action_name(), action_version)