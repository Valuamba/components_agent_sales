from abc import ABC

from core.bot import TelegramBotClient
from core.models.action import ActionMetadata, Action
from models.deal import StatusType
from repositories import TaskRepository
from services import LoggingService


class BaseAction(ABC):

    def __init__(self,
                 task_repository: TaskRepository,
                 telegram_bot: TelegramBotClient,
                 logger_service: LoggingService):
        self.logger = logger_service
        self.telegram_bot = telegram_bot
        self.task_repository = task_repository
        self.db_session = task_repository.session

    @classmethod
    def get_action_name(cls):
        return __class__.__name__

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