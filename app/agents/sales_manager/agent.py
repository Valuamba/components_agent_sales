from agents import AgentType
from agents.base import BaseAgent
from agents.parsers.action_parser import parse_action
from agents.parsers.email_parser import parse_email_input, parse_apply_discount_input
from agents.parsers.tasks_parser import Task
from agents.sales_manager.prompts import SYSTEM_MESSAGE, STOP
from repositories import TaskRepository
from services import OpenAIClient, LoggingService


class SalesManagerAgent(BaseAgent):
    def __init__(
            self,
            openai_client: OpenAIClient,
            logger: LoggingService,
            task_repository: TaskRepository
    ):
        super().__init__(openai_client, task_repository, logger)


    def agent_type(self) -> AgentType:
        return AgentType.SalesManager

    @staticmethod
    def agent_name() -> str:
        return "Sales Manager"

    def system_message(self) -> str:
        return SYSTEM_MESSAGE

    def complete_task(self, deal_id, task: Task, task_input_str):
        response = self.create_completion(deal_id, [
            {"role": "user", "content": f"""
{self.system_message()}

The available tools:
*   `SendEmail`
*   *   Tool input: {{ "body": <email_body> }}
*   `ApplyDiscount`
*   *   Tool input: {{ "discount": <discount_value_percents int|float>, "part_number": <part_number>}}

You need to complete the task from higher manager, if it needed you can ask managers under from your authority to complete your task, to do this you need meet input format to set task.

The task author: Pricing Manager
Task: {task.summary}
Description: {task.description}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [SendEmail]
Action Input: the input to the action, if action is json the keys and values should be in one line if it's needed place \\n to text values.
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

If there no Action to apply please do not mention Action, Action Input and Observation, just use the `Thougth`
and `Middle Observation`.

DO NOT USE MARKDOWN FORMAT FOR RESPONSE.

{task_input_str}
            """}
        ],
        model='gpt-4', temperature=0.5, stop=STOP)

        # agent_task = self.task_repository.get_task_by_id(165)
        # content = agent_task.response
        content = response.content
        parsed_data = parse_action(content)
        if parsed_data.get('type') == 'action':
            if parsed_data.get('action') == 'SendEmail':
                return parse_email_input(parsed_data.get('input'))
            elif parsed_data.get('action') == 'ApplyDiscount':
                return parse_apply_discount_input(parsed_data.get('input'), parsed_data.get('action'))
