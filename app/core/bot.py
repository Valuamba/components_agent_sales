import uuid

from configs.config import app_settings
import requests

from services import LoggingService


class TelegramBotClient:
    def __init__(self, logger: LoggingService):
        self.logger = logger
        self.token = app_settings.bot_token

    def notify_admins(self, message, **kwargs):
        for user_id in app_settings.notify_users_ids:
            try:
                self.notify_admin(user_id, message, **kwargs)
            except Exception as e:
                error_message = f"Unhandled exception occurred when send message to bot [{user_id}]: {str(e)}"
                self.logger.error(error_message)

    def notify_admin(self, user_id, message, **kwargs):
        send_message_url = f'https://api.telegram.org/bot{self.token}/sendMessage'

        kwargs['trace_id'] = self.logger.context.trace_id
        params_str = '\n'.join([f'{key}: {value}'for key, value in kwargs.items()])

        params = {
            'chat_id': user_id,
            'text': message + '\n\n' + params_str,
            'parse_mode': 'HTML',
        }

        response = requests.post(send_message_url, data=params)
        if response.status_code == 200:
            self.logger.info(f'Message was sent successfully to user: {user_id}')
        else:
            self.logger.info(f'Failed to send message to user: {user_id}')
