from typing import List
from agents.intent_classifier.base import BaseInstruction
from agents.intent_classifier.classify_intents import ClassifyIntentsInstruction
from agents.openai_client import create_completion
import re
import ast

from agents.statics import Colors

INTENT_CLASSIFIER_NAVIGATION = """
Please do the task from higher Sales Manager.
The task: {task}

The available instructions:
{instructions}

Allowed keys from storage: email, intents

Use the following format:

Thought: you should always think about what to do
Instruction: the instruction to take, should be one of available instructions
Instruction Input: take allowed key from storage that would needed to instruction completion or none, 
for instance it could look like ['intents', 'email']
Observation: the result of the action
... (this Thought/Instruction/Instruction Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""


# 1. Instruction: Intent Classification
# Instruction Input: ['email', 'intents']

class IntentClassifierAgent:

    def agent_prompt(self):
        return INTENT_CLASSIFIER_NAVIGATION

    def instructions(self) -> List[BaseInstruction]:
        return [ClassifyIntentsInstruction()]

    def prepare_input(self, task, agent_scratchpad, **kwargs):
        instructions_str = ''
        for idx, instruction in enumerate(self.instructions()):
            instructions_str += f'{idx+1}. Instruction: {instruction.name()}\nInstruction Input: {instruction.input_values()}\n'

        agent_scratchpad_str = '\n'.join(agent_scratchpad)

        return self.agent_prompt().format(task=task, instructions=instructions_str, **kwargs) + '\n\n' + agent_scratchpad_str

    def run(self, task, **kwargs):
        print('Intent classifier\n')
        agent_scratchpad = []
        do_iter = True
        iters = 0

        while do_iter or iters < 5:
            input = self.prepare_input(task, agent_scratchpad, **kwargs)
            print(f'{Colors.RED}Prompt:{Colors.RESET} {input}')
            response = create_completion([
                {"role": "user", "content": input}
            ],
                stop=['\nObservation:', '\n\tObservation:'],
                temperature=0.5)

            match = re.search(r"Final Answer:\s*(.*(?:\n(?!\n).*)*)", response)

            if match:
                do_iter = False
                return match.group(1)

            else:

                regex = (r"Thought\s*\d*\s*:[\s]*(.*?)[\s]*Instruction\s*\d*\s*:[\s]*(.*?)[\s]*Instruction\s*\d*\s*Input:[\s]*(.*)")

                instruction_match = re.search(regex, response, re.DOTALL)
                thought = instruction_match.group(1)
                instruction_name = instruction_match.group(2)
                instruction_input = ast.literal_eval(instruction_match.group(3))

                instruction = next(instr for instr in self.instructions() if instr.name() == instruction_name)

                instruction_output = instruction.run(**kwargs)

                agent_scratchpad.append(
                    f'Thought: {thought}\nInstruction: {instruction_name}\n' +
                    f'Instruction Input: {instruction_input}\nObservation: {instruction_output}')
                print('\n\n')

            iters += 1

        return response
