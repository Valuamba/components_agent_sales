from pydantic import BaseModel, Field
from typing import Type, Any
from core.actions.base import BaseAction
from core.clients.google_sheet import GoogleSheet
from core.models.action import Action, ActionMetadata, Metadata
from core.bot import TelegramBotClient
from repositories import TaskRepository
from services import OpenAIClient, LoggingService
from models.deal import AgentTask, StatusType, LLMRun
from utility import select_json_block


class TaskExecutionOutput(BaseModel):
    output: str


class TaskExecutionAction(BaseAction):
    def __init__(self,
                 openai_client: OpenAIClient,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger: LoggingService,
                 ghconv: GoogleSheet,
                 redis):
        super().__init__(task_repository, telegram_bot, logger, openai_client, redis)
        self.ghconv = ghconv

    @classmethod
    def get_action_name(cls):
        return "task_execution"

    def execute_task(self, run: LLMRun, instruction: str, discount_messages: str, purchase_history: str, current_offer: str) -> Action:
        prompt = f"""
You are sales manager. Please do task by instruction:
{instruction}

The conversation with customer context:

Messages about discount at conversation:
```
{discount_messages}
```

{purchase_history}

Deal offer:
{current_offer}

Please use new lines symbols \n or tabs \t to format text if needed. Put result into single string line, if paragraphs 
are needed use \\n symbol.

Put result of task into ```json``` format, like this:
```json
{{
    "output": "the output of task" // Please use new lines symbols \\n or tabs \\t to format text if needed
}}
```
"""
        model = "gpt-4"
        action_version = 1
        return self.execute_action(run, prompt, model, TaskExecutionOutput, self.get_action_name(), action_version)