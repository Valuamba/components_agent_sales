import json
from typing import List

from agents import AgentType
from agents.base import BaseAgent
from agents.classify_intents.prompts import INTENT_CLASSIFICATION_PROMPT, RESPONSE_FORMAT
from agents.parsers.tasks_parser import parse_tasks, Task
from agents.purchasing_manager.agent import PurchasingManagerAgent
from agents.sales_manager.agent import SalesManagerAgent
from repositories import TaskRepository, DealRepository
from repositories.purchase_history import PurchaseHistoryRepository
from schemas.v1.agents_completion import DealInfo
from schemas.v1.intent import Message
from schemas.v1.messages import MessageModel
from services import OpenAIClient, LoggingService
from services.client_statistics import ClientStatisticsService
from utility import select_json_block
from agents.pricing_manager.prompts import PROMPT, STOP, DISCOUNT_BLOCK_SCHEMA, RESPONSE_FORMAT


class PricingManagerAgent(BaseAgent):
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
    def get_str_from_messaging_history(messages: List[MessageModel]):
        messages_str = ''
        for msg in messages:
            intents_str = '\n'.join(
                [f'   - {intent.intent} -> {intent.sub_intent} -> {intent.branch}' for intent in msg.intents])
            msg_str = f'**from:** {msg.from_type.name}\n**Message {msg.id}:**\n```\n{msg.body}\n```\n**Intents:**\n{intents_str}'
            messages_str += msg_str + '\n\n'
        return messages_str

    @staticmethod
    def get_tasks_map(summarize_client_metrics, purchase_history_str, messaging_history_str):
        return {
            'deal_info': {
                "name": "Deal Details",
                "description": "Current information about the deal, including the offer, discount rates, profit margin, and other relevant metadata necessary for sales managers to make informed decisions.",
                "value": "Current margin: 23.5%"
            },
            'client_profile': {
                "name": "Client Metrics",
                "description": "A summary of metrics that provide insights into the client's profile.",
                "value": summarize_client_metrics
            },
            'client_purchase_history': {
                "name": "Purchase History",
                "description": "A record of all purchases made by the client, used for analyzing buying patterns.",
                "value": purchase_history_str
            },
            'chat_history': {
                "name": "Messaging History",
                "description": "A string representation of the conversation history with the client.",
                "value": messaging_history_str
            }
        }

    @staticmethod
    def prepare_task_input(task: Task, tasks_key_storage_map):
        block_descriptions_str = ''
        block_values_str = ''
        for key in task.input_keys:
            key_info = tasks_key_storage_map[key]

            block_descriptions_str += f"""
    *   **\[{key_info['name'].upper()}\]** Block

        *   **Description**: {key_info['description']}
    """

            block_values_str += f"""
    **[{key_info['name'].upper()}]**
    {key_info['value']}
    **[/{key_info['name'].upper()}]**
        """

        tool_input = json.loads(task.input)
        tool_input_str = '\n'.join([f'{key}: {value}' for key, value in tool_input.items()])

        return f"""
    The input data that could be used:
    {tool_input_str}

    {block_descriptions_str}

    {block_values_str}
    """

    def sub_agents(self):
        return {
            PurchasingManagerAgent.agent_name(): PurchasingManagerAgent,
            SalesManagerAgent.agent_name(): SalesManagerAgent
        }

    def agent_type(self) -> AgentType:
        return AgentType.PricingManager

    def classify_messages_metadata_and_intents(self, deal_id: int, deal_info: DealInfo, model="gpt-4"):
        client_id = self.purchase_history_rep.get_client_id_by_deal(deal_id)
        purchase_history = self.purchase_history_rep.get_client_history(client_id)
        summarize_client_metrics = self.client_statistics.summarize_client_metrics(purchase_history)
        purchase_history_str = self.client_statistics.get_purchase_history_str(purchase_history)

        messaging_history = self.deal_repository.get_deal_with_messages_v2(deal_id)
        messaging_history_str = self.get_str_from_messaging_history(messaging_history)

        # task = self.task_repository.get_task_by_id(161)
        pricing_manager_response = self.create_completion(deal_id,
        [{"role": "user", "content":
                PROMPT.format(response_format=RESPONSE_FORMAT, summarize_client_metrics=summarize_client_metrics,
                              purchase_history_str=purchase_history_str, messaging_history_str=messaging_history_str,
                              discount_block_schema=DISCOUNT_BLOCK_SCHEMA, deal_info=deal_info.to_string())},
            ],
            model=model,
            temperature=0.5,
            stop=STOP
        )
        #
        #
        # emails = []
        action = parse_tasks(pricing_manager_response.content)
        emails = []
        # action = parse_tasks(task.response)
        for task in action.tasks:
            task_key_storage_map = self.get_tasks_map(summarize_client_metrics,
                                                      purchase_history_str, messaging_history_str)
            task_input = self.prepare_task_input(task, task_key_storage_map)
            agent_class = self.sub_agents().get(task.assignee)
            if not agent_class:
                agent_class = self.sub_agents().get(PurchasingManagerAgent.agent_name())
            agent_obj = agent_class(self.openai_client, self.logger, self.task_repository)
            emails.append(agent_obj.complete_task(deal_id, task, task_input))

        return emails

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