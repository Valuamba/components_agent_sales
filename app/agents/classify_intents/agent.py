import json
from typing import List

from agents.classify_intents.prompts import INTENT_CLASSIFICATION_PROMPT, RESPONSE_FORMAT
from schemas.v1.intent import Message
from services import OpenAIClient, LoggingService
from utility import select_json_block


class ClassifyIntentsAgent:
    def __init__(
            self,
            openai_client: OpenAIClient,
            logger: LoggingService,
    ):
        self.openai_client = openai_client
        self.logger = logger

    def classify_messages_metadata_and_intents(self, messages: List[str], model="gpt-4"):
        messages_str = '\n\n'.join(messages)
        completion = self.openai_client.create_completion(
            model,
            [
                    {"role": "user", "content":
                        INTENT_CLASSIFICATION_PROMPT.format(chat_history_str=messages_str) + '\n\n' + RESPONSE_FORMAT},
            ],
            temperature=0.5
        )
        self.logger.info(f'RESPONSE:\n{completion.content}')
        response_raw_json = select_json_block(completion.content)
        parsed_messages = [Message(**message) for message in response_raw_json]

        return parsed_messages

