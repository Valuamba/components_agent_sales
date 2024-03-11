import json
import re
from typing import List, Union
import yaml
from branches.branch import Branch, Node, NodeType, Action


def load_yaml(file):
    with open(file, 'r') as stream:
        data = yaml.safe_load(stream)
    return data


def get_block_schema_branch_instruction(branch: Branch, branches: List[Branch]):
    block_schema = []

    for decision in branch.decision_points:
        block_schema.append(f'**[DP: {decision.point}]**')
        for condition in decision.conditions:
            condition_description = next(c.condition for c in branch.conditions if c.name == condition.name)
            block_schema.append(f' *    **Condition:** "{condition_description}"')

            def outcomes_to_string(outcomes: List[Node], branch: Branch, branches: List[Branch]):
                for outcome in outcomes:
                    if outcome.type == NodeType.Condition:
                        outcome_description = condition_description
                    elif outcome.type == NodeType.Action:
                        outcome_description = next(
                            action.action for action in branch.actions if outcome.name == action.name)
                    elif outcome.type == NodeType.Branch:
                        outcome_description = next(branch.branch for branch in branches if outcome.name == branch.name)
                    else:
                        raise Exception(f'There is no handling of {outcome.type} outcome node type.')
                    outcome_str = f'[{outcome.type.value.capitalize()}: "{outcome_description}"]'
                    block_schema.append(f' 	        *   **→ {outcome_str}')

            if len(condition.true_outcomes) > 0:
                block_schema.append(f' 	*    **Yes:**')
                outcomes_to_string(condition.true_outcomes, branch, branches)
            if len(condition.false_outcomes) > 0:
                block_schema.append(f' 	*    **No:**')
                outcomes_to_string(condition.false_outcomes, branch, branches)
        block_schema.append('\n')

    for action in branch.actions:
        block_schema.append(f'[Action: {action.action}]')

    block_schema_str = '\n'.join(block_schema)
    return block_schema_str


def parse_output(output: str, branch, branches) ->  Union[Action, Branch]:
    if action_match := re.search(r'Action\s*\d*\s*:[\s]*(.*)', output, re.DOTALL):
        matched_action = next(action for action in branch.actions if action.action == action_match.group(1).strip())
        return matched_action
    elif branch_match := re.search(r'Branch\s*\d*\s*:[\s]*(.*)', output, re.DOTALL):
        matched_branch = next(branch for branch in branches if branch.branch == branch_match.group(1).strip())
        return matched_branch

    return None


def select_json_block(text: str):
    match = re.search(r"```json\n([\s\S]*?)\n```", text)
    if match:
        json_data = match.group(1)
    else:
        raise ValueError("No valid JSON data found in the string.")

    return json.loads(json_data)


def messaging_history_to_str(messaging_history):
    return '\n\n'.join(f'**Message {idx + 1}:**\n```{msg}\n```'
                       for idx, msg in enumerate(messaging_history))