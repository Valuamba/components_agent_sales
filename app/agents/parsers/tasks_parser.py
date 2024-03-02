import re
from typing import List, NamedTuple, Union


class Task(NamedTuple):
    summary: str
    assignee: str
    description: str
    input_keys: List[str] = []  # Now expecting a list of strings
    input: Union[str, None] = None


class Action(NamedTuple):
    action: str
    tasks: List[Task]


def parse_tasks(text: str) -> Action:
    action_match = re.search(r"Action: (.*)", text)
    action = action_match.group(1).strip() if action_match else ""

    tasks = []
    task_pattern = r"Task: (.*?)\nAssignee: (.*?)\nDescription: (.*?)((\nInput keys: (.*?))?(\nInput: (.*?))?)?\n\n?"
    task_matches = re.finditer(task_pattern, text, re.DOTALL)

    for match in task_matches:
        input_keys = match.group(6).strip().split(", ") if match.group(6) else []  # Splitting by comma and space
        tasks.append(Task(
            summary=match.group(1).strip(),
            assignee=match.group(2).strip(),
            description=match.group(3).strip(),
            input_keys=input_keys,
            input=match.group(8).strip() if match.group(8) else None
        ))

    return Action(action=action, tasks=tasks)