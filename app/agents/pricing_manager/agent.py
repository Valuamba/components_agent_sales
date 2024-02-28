import json
from typing import List

from agents import AgentType
from agents.base import BaseAgent
from agents.classify_intents.prompts import INTENT_CLASSIFICATION_PROMPT, RESPONSE_FORMAT
from repositories import TaskRepository, DealRepository
from repositories.purchase_history import PurchaseHistoryRepository
from schemas.v1.intent import Message
from services import OpenAIClient, LoggingService
from services.client_statistics import ClientStatisticsService
from utility import select_json_block
from prompts import PROMPT, STOP, DISCOUNT_BLOCK_SCHEMA, RESPONSE_FORMAT


class ClassifyIntentsAgent(BaseAgent):
    def __init__(
            self,
            openai_client: OpenAIClient,
            logger: LoggingService,
            task_repository: TaskRepository,
            deal_repository: DealRepository,
            purchase_history_rep: PurchaseHistoryRepository
    ):
        super().__init__(openai_client, task_repository, logger)

        self.purchase_history_rep = purchase_history_rep
        self.client_statistics = ClientStatisticsService()
        self.deal_repository = deal_repository

    @staticmethod
    def get_str_from_messaging_history(deal_with_messages):
        messages_str = ''
        for msg in deal_with_messages.messages:
            intents_str = '\n'.join(
                [f'   - {intent.intent} -> {intent.sub_intent} -> {intent.branch}' for intent in msg.intents])
            msg_str = f'**from:** {msg.from_type.name}\n**Message {msg.id}:**\n```\n{msg.body}\n```\n**Intents:**\n{intents_str}'
            messages_str += msg_str + '\n\n'
        return messages_str

    def agent_type(self) -> AgentType:
        return AgentType.PricingManager

    def classify_messages_metadata_and_intents(self, deal_id, deal_info, model="gpt-4"):
        client_id = self.purchase_history_rep.get_client_id_by_deal(deal_id)
        purchase_history = self.purchase_history_rep.get_client_history(client_id)
        summarize_client_metrics = self.client_statistics.summarize_client_metrics(purchase_history)
        purchase_history_str = self.client_statistics.get_purchase_history_str(purchase_history)

        messaging_history = self.deal_repository.get_deal_with_messages_v2(deal_id)

        messaging_history_str = self.get_str_from_messaging_history(messaging_history)

        self.create_completion(deal_id,
        [{"role": "user", "content":
                PROMPT.format(response_format=RESPONSE_FORMAT, summarize_client_metrics=summarize_client_metrics,
                              purchase_history_str=purchase_history_str, messaging_history_str=messaging_history_str,
                              discount_block_schema=DISCOUNT_BLOCK_SCHEMA)},
            ],
            model=model,
            temperature=0.5
        )

        # messages_str = ''
        #
        # for idx, message in enumerate(messages):
        #     messages_str += f'Message {idx + 1}:\n```{message}```\n\n'
        #
        # completion = self.create_completion(deal_id,
        #     [{"role": "user", "content":
        #                 INTENT_CLASSIFICATION_PROMPT.format(chat_history_str=messages_str) + '\n\n' + RESPONSE_FORMAT},
        #     ],
        #     model=model,
        #     temperature=0.5
        # )
        # self.logger.debug(f'RESPONSE:\n{completion.content}')
        # response_raw_json = select_json_block(completion.content)
        # parsed_messages = [Message(**message) for message in response_raw_json]
        #
        # return parsed_messages