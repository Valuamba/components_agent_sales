from agents import AgentType
from agents.base import BaseAgent
from agents.parsers.action_parser import parse_action
from agents.parsers.email_parser import parse_email_input
from agents.parsers.tasks_parser import Task
from agents.purchasing_manager.prompts import SYSTEM_MESSAGE, STOP
from repositories import TaskRepository
from services import OpenAIClient, LoggingService


class PurchasingManagerAgent(BaseAgent):
    def __init__(
            self,
            openai_client: OpenAIClient,
            logger: LoggingService,
            task_repository: TaskRepository,
    ):
        super().__init__(openai_client, task_repository, logger)

    def agent_type(self) -> AgentType:
        return AgentType.PurchasingManager

    @staticmethod
    def agent_name() -> str:
        return "Purchasing Manager"

    def system_message(self) -> str:
        return SYSTEM_MESSAGE

    def complete_task(self, deal_id, task: Task, task_input_str):
        response = self.create_completion(deal_id, [
            {"role": "user", "content": f"""
{self.system_message()}

        The available tools:
        *   `SendEmail`
        *   *   Tool input: {{ "body": <email_body> }}

        You need to complete the task from higher manager, if it needed you can ask managers under from your authority to complete your task, to do this you need
        meet input format to set task.

        The task author: Pricing Manager
        Task: {task.summary}
        Description: {task.description}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [SendEmail]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        DO NOT USE MARKDOWN FORMAT FOR RESPONSE.

        {task_input_str}
        """}
        ],
        model='gpt-4', temperature=0.5, stop=STOP)

        parsed_data = parse_action(response.content)
        if parsed_data.get('type') == 'action' and parsed_data.get('action') == 'SendEmail':
            return parse_email_input(parsed_data.get('input'))
