import logging


class LoggingService:
    def __init__(self, context, name: str):
        self.context = context
        self.logger = logging.getLogger(name)

    def info(self, message: str):
        self.logger.info(f'[{self.context.trace_id}] {message}')

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)
