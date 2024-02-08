from abc import ABC, abstractmethod


class BaseInstruction(ABC):
    instruction = "Abstract instruction prompt"

    @abstractmethod
    def input_values(self):
        pass

    @abstractmethod
    def response_format(self):
        pass

    @abstractmethod
    def name(self):
        pass

    def prepare_input(self, **kwargs):
        input = self.instruction.format(**kwargs)
        return input + '\n\n' + self.response_format

    @abstractmethod
    def prepare_output(self, output):
        pass

    @abstractmethod
    def run(self, **kwargs):
        pass
