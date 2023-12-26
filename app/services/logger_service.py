

class LoggerService:
    def __init__(self, context):
        self.context = context

    def info(self, msg: str):
        print(f'[{self.context.trace_id}] {msg}')

