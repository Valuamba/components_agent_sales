import json
from typing import List

from agents import AgentType
from agents.base import BaseAgent
from agents.classify_intents.prompts import INTENT_CLASSIFICATION_PROMPT, RESPONSE_FORMAT
from repositories import TaskRepository
from schemas.v1.intent import Message
from services import OpenAIClient, LoggingService
from utility import select_json_block


class ClassifyIntentsAgent(BaseAgent):
    def __init__(
            self,
            openai_client: OpenAIClient,
            logger: LoggingService,
            task_repository: TaskRepository
    ):
        super().__init__(openai_client, task_repository, logger)

    def agent_type(self) -> AgentType:
        return AgentType.ClassifyIntents

    def classify_messages_metadata_and_intents(self, deal_id, messages: List[str], model="gpt-4"):
        messages_str = ''

        for idx, message in enumerate(messages):
            messages_str += f'Message {idx + 1}:\n```{message}```\n\n'

        completion = self.create_completion(deal_id,
            [{"role": "user", "content":
                        INTENT_CLASSIFICATION_PROMPT.format(chat_history_str=messages_str) + '\n\n' + RESPONSE_FORMAT},
            ],
            model=model,
            temperature=0.5
        )
        self.logger.debug(f'RESPONSE:\n{completion.content}')
        response_raw_json = select_json_block(completion.content)
        parsed_messages = [Message(**message) for message in response_raw_json]

        return parsed_messages

