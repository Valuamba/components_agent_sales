from typing import List
from agents.intent_classifier.base import BaseInstruction
from agents.intent_classifier.classify_intents import ClassifyIntentsInstruction
from agents.openai_client import create_completion
import re
import ast

from agents.intent_classifier.agent import IntentClassifierAgent

SYSTEM_PROMPT = """
You are Senior Sales manager of first line of communication with customer. When customer send message you are the first person that define intents from email
and decide what to do next 

You have in under the authority following sales managers:
- Discount Sales manager: takes tasks related with negotiations about discounts, can accept only messages from customers with discount intent 
- Intent Classification Manager: helps to manage work with intents
- Customer Service Manager: this sales manager could answer on any customer questions, that other sales cannot to do.
"""

MAIN_PROMPT = """
As a Senior Sales Manager of first line of service, please read the following email from customer, extract all intents 
and then decide what sales manager you would delegate the task to write message. Do it step by step.

Messages processing instruction:
1. First of all you need to get message intent to better understand which manager could handle the email at next.
2. When you got the intent you needed to pass email to manager that has competence to work with message with intents.

[EMAIL FROM CUSTOMER]
{email}
[/EMAIL FROM CUSTOMER]

Allowed keys from storage: email, intents

Thought: you should always think about what to do
Assignee: the assignee manager from list
Task: the task for assignee manager
Task Input: take allowed key from storage that would needed to task completion or none, 
for instance it could look like ['intents', 'email']
Observation: the result of the task from manager
... (this Thought/Assignee/Task/Task Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""


# 1. Instruction: Intent Classification
# Instruction Input: ['email', 'intents']

class SeniorSalesAgent:

    def agent_prompt(self):
        return MAIN_PROMPT

    def instructions(self) -> List[BaseInstruction]:
        return [ClassifyIntentsInstruction()]

    def prepare_input(self, email, agent_scratchpad, **kwargs):
        agent_scratchpad_str = '\n'.join(agent_scratchpad)

        return self.agent_prompt().format(email=email, **kwargs) + '\n\n' + agent_scratchpad_str

    def run(self, email, **kwargs):
        print('Senior Sales\n')
        agent_scratchpad = []
        do_iter = True
        iters = 0

        while do_iter and iters < 5:

            response = create_completion([
                {"role": "assistant", "content": SYSTEM_PROMPT},
                {"role": "user", "content": self.prepare_input(email, agent_scratchpad, **kwargs)}
            ],
                stop=['\nObservation:', '\n\tObservation:'],
                temperature=0.5)

            match = re.search(r"Final Answer:\s*(.*(?:\n(?!\n).*)*)", response)

            if match:
                do_iter = False
                return match.group(1)

            else:

                regex = (r"Thought\s*\d*\s*:[\s]*(.*?)[\s]*" +
                         r"Assignee\s*\d*\s*:[\s]*(.*?)[\s]*" +
                         r"Task\s*\d*\s*:[\s]*(.*?)[\s]*" +
                         r"Task\s*\d*\s*Input:[\s]*(.*)")

                instruction_match = re.search(regex, response, re.DOTALL)
                thought = instruction_match.group(1)
                assignee = instruction_match.group(2)
                task = instruction_match.group(3)
                task_input = ast.literal_eval(instruction_match.group(4))

                print('\n\n')

                if assignee == 'Intent Classification Manager':
                    intent_classifier_agent = IntentClassifierAgent()

                    intents = intent_classifier_agent.run(task, **{
                        "email": email,
                        **kwargs
                    })

                    agent_scratchpad.append(
                        f'Thought: {thought}\nAssignee: {assignee}\n' +
                        f'Task: {task}\nTask Input: {task_input}\n' +
                        f'Observation: {intents}')
                else:
                    do_iter = False
                    print(f'Stop because there is no {assignee} agent.')
            iters += 1

        return response
