import logging
import traceback
from configs.logger import name as logger_name


class LoggingService:
    def __init__(self, context):
        self.context = context
        self.logger = logging.getLogger(logger_name)

    def log(self, level, message: str, extra_info=None):
        if extra_info is None:
            extra_info = {}
        extra = {'request_id': self.context.trace_id, 'extra_info': extra_info}
        self.logger.log(level, message, extra=extra)

    def info(self, message: str, extra_info=None):
        self.log(logging.INFO, message, extra_info)

    def error(self, message: str, extra_info=None):
        error_message = f"{message}\n\nStack trace: {traceback.format_exc()}"
        self.log(logging.ERROR, error_message, extra_info)

    def debug(self, message: str, extra_info=None):
        self.log(logging.DEBUG, message, extra_info)

    def warning(self, message: str, extra_info=None):
        self.log(logging.WARNING, message, extra_info)