import re
from typing import List, Dict, Union


class DecisionPoint:
    def __init__(self, decision: str, observation: str):
        self.decision = decision
        self.observation = observation


class Action:
    def __init__(self, action: str, task: str, assignee: str, description: str, input_keys: List[str],
                 input: Dict[str, str]):
        self.action = action
        self.task = task
        self.assignee = assignee
        self.description = description
        self.input_keys = input_keys
        self.input = input


class FinalAnswer:
    def __init__(self, thought: str, conclusion: str):
        self.thought = thought
        self.conclusion = conclusion


def parse_section(section: str) -> Union[DecisionPoint, Action, FinalAnswer]:
    if section.startswith('Decision Point'):
        decision, observation = re.findall(r'Decision Point: (.*?)\nObservation: (.*?)\n', section, re.DOTALL)[0]
        return DecisionPoint(decision.strip(), observation.strip())
    elif section.startswith('Action'):
        # Use regex to capture the base action details
        action_regex = r'Action: (.*?)\nTask: (.*?)\nAssignee: (.*?)\nDescription: (.*?)\n'
        action_match = re.search(action_regex, section, re.DOTALL)
        if action_match:
            action, task, assignee, description = action_match.groups()
            # Initialize optional fields
            input_keys = []
            input_dict = {}
            # Check for optional fields
            input_keys_match = re.search(r'Input keys: (.*?)\n', section, re.DOTALL)
            if input_keys_match:
                input_keys = input_keys_match.group(1).split(', ')
            input_match = re.search(r'Input: ({.*?})', section, re.DOTALL)
            if input_match:
                input_str = input_match.group(1).strip()
                input_dict = eval(input_str)  # Convert string to dict safely
            return Action(action.strip(), task.strip(), assignee.strip(), description.strip(), input_keys, input_dict)
    elif section.startswith('Thought'):
        thought, conclusion = re.findall(r'Thought: (.*?)\nConclusion: (.*?)\n', section, re.DOTALL)[0]
        return FinalAnswer(thought.strip(), conclusion.strip())
    else:
        return None


def parse_input(text: str):
    sections = re.split(r'\n(?=Decision Point|Action|Thought)', text.strip())
    parsed_elements = [parse_section(section) for section in sections if section.strip() != '']
    return parsed_elements


# Your raw text goes here
raw_text = """
Decision Point: User Request Processing  
Observation: This is not the first message from the user.  

Decision Point: Request Classification  
Observation: The user left a request indicating specific parts.  

Action: Classify parts in the customer's request  

Task: Classify Parts  
Assignee: Classify Parts Manager  
Description: The user has mentioned a specific part in their request. This part needs to be classified.  
Input keys: message_id  
Input: { "message_id": "1"}  

Action: Send an offer to the customer  

Task: Send Offer to client  
Assignee: Sales Manager  
Description: After the part has been classified, an offer needs to be sent to the client for the specified part.  

Thought: The client's request has been processed and an offer has been sent.  
Conclusion: The client's request for a specific part has been addressed. The next step would be awaiting the client's response to the offer.
"""

parsed_elements = parse_input(raw_text)
for element in parsed_elements:
    print(element)
