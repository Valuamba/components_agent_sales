
from agents.intent_classifier.classify_intents_prompt import RESPONSE_FORMAT, INTENT_CLASSIFICATION_PROMPT, \
    REQUIRED_VALUES, INTENT_CLASSIFICATIONI_INSTRUCTION_NAME
from agents.openai_client import create_completion
from agents.intent_classifier.base import BaseInstruction
import json

from pydantic import BaseModel
from typing import List

from agents.utils import select_json_block


class Intent(BaseModel):
    intent: str
    sub_intent: str
    branch: str

class Root(BaseModel):
    intents: List[Intent]
    

class ClassifyIntentsInstruction(BaseInstruction):
    # response_format = RESPONSE_FORMAT
    instruction = INTENT_CLASSIFICATION_PROMPT

    def instruction_name(self):
        return INTENT_CLASSIFICATIONI_INSTRUCTION_NAME
    def response_format(self):
        return RESPONSE_FORMAT

    def input_values(self):
        return REQUIRED_VALUES

    def name(self):
        return INTENT_CLASSIFICATIONI_INSTRUCTION_NAME
    
    def prepare_input(self, **kwargs):
        input = self.instruction.format(**kwargs)
        return input + '\n\n' + self.response_format()

    def prepare_output(self, output: Root):
        return 'Intents:\n' + '\n'.join([ f'{intent.intent} -> {intent.sub_intent} -> {intent.branch}' for intent in output.intents])

    def run(self, **kwargs):
        input = self.prepare_input(**kwargs)
        print(f'Prompt: {input}')
        response = create_completion([
            {"role": "user", "content": input}
        ], temperature=0.5)

        json_block = select_json_block(response)

        # print(f'Json block: {json_block}')

        model_obj = Root.model_validate(json_block)
        # add to database

        return self.prepare_output(model_obj)