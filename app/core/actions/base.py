from abc import ABC
from typing import Any, Optional, Type

from pydantic import BaseModel

from core.bot import TelegramBotClient
from core.models.action import ActionMetadata, Action, Metadata
from models.deal import StatusType, AgentTask
from repositories import TaskRepository
from services import LoggingService
from utility import select_json_block


class BaseAction(ABC):

    def __init__(self,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger_service: LoggingService,
                 openai_client):
        self.logger = logger_service
        self.telegram_bot = telegram_bot
        self.task_repository = task_repository
        self.db_session = task_repository.session
        self.openai_client = openai_client


    def create_task(self, run_id: int, prompt: str, action_name: str) -> AgentTask:
        task = AgentTask(
            run_id=run_id,
            status=StatusType.InProgress.name,
            action=action_name,
            prompt=prompt
        )
        self.task_repository.create_task_for_deal(task)
        return task

    def update_task_status(self, task: AgentTask, status: StatusType):
        task.status = status.name
        self.task_repository.session.commit()

    def execute_action(self, run_id: int, prompt: str, model: str, schema: Optional[Type[BaseModel]], action_name: str, action_version: int) -> Action:
        task = self.create_task(run_id, prompt, action_name)
        try:
            completion = self.openai_client.create_completion(
                model,
                [
                    {"role": "user", "content": prompt}
                ],
            )

            task.response = completion.content  # Store raw output
            self.task_repository.session.commit()

            response_raw_json = select_json_block(completion.content)

            if schema:
                parsed_data = schema(**response_raw_json)
            else:
                parsed_data = response_raw_json

            actual_status = StatusType.Passed
            self.update_task_status(task, actual_status)

            return self.build_action(parsed_data, self.prepare_ui(parsed_data), completion, action_name, action_version, task.task_id)

        except Exception as e:
            return self.handle_error(e, task, task.run_id)

    def build_action(self, data: Any, ui_message, completion: Any, action_name: str, action_version: int, task_id: int) -> Action:
        return Action(
            action=ActionMetadata(
                action_version=action_version,
                action_name=action_name,
                action_id=task_id,
                action_time=round(completion.completion_time_ms, 0),
                action_status=StatusType.Passed.value,
            ),
            ui_message=ui_message,
            data=data,
            metadata=Metadata(
                completion_cost_usd=round(completion.usage_cost_usd, 3),
                completion_time_sec=round(completion.completion_time_ms, 0),
                llm_model=completion.model,
                raw_output=completion.content
            )
        )

    @classmethod
    def get_action_name(cls):
        return __class__.__name__

    def prepare_ui(self, output):
        return None

    def handle_error(self, exc, task, run_id):
        error_message = f"Failed to process action [{self.get_action_name()}]: {str(exc)}"
        self.logger.error(error_message)
        self.telegram_bot.notify_admins(error_message, **{
            'action': self.get_action_name(),
            'task_id': task.task_id,
            'run_id': run_id
        })

        actual_status = StatusType.Failed
        task.status = actual_status.name
        task.error = str(exc)
        self.db_session.commit()

        return Action(
            action=ActionMetadata(
                action_version=1,
                action_name=self.get_action_name(),
                action_id=task.task_id,
                action_time=None,
                action_status=actual_status.value,
            ),
            error={'code': type(exc).__name__, 'message': str(exc)}
        )