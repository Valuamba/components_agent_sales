from itertools import chain

from pydantic import BaseModel
from typing import List, Union, Optional, Any
from enum import Enum
import yaml


class NodeType(Enum):
    Branch = "branch"
    Condition = "condition"
    DecisionPoint = "point"
    Action = "action"


class Node(BaseModel):
    name: str
    type: NodeType


class Condition(BaseModel):
    condition: str
    name: str
    true_outcomes: List[Node] = []
    false_outcomes: List[Node] = []


class Action(BaseModel):
    name: str
    action: str
    stop: bool = False


class DecisionPoint(BaseModel):
    name: str
    point: str
    conditions: List[Condition]


class Branch(BaseModel):
    name: str
    branch: str
    decision_points: List[DecisionPoint]
    conditions: List[Condition]
    main: bool = False
    actions: List[Action] = []


class AgentIteration(BaseModel):
    iter_obj: Union[Branch, Action]
    state: bool = False


class AgentFinish(BaseModel):
    output: Any
    action: str
    log: str = None


def parse_condition(condition_content):
    def map_outcomes(key: bool):
        outcomes = []
        if key in condition_content.keys():
            for true_node in condition_content[key]:
                assert len(true_node.keys()) <= 1, "The length of the array is more than 1."
                node_name = list(true_node.keys())[0]
                outcomes.append(Node(name=true_node[node_name], type=NodeType(node_name)))
        return outcomes

    condition = Condition(name=condition_content['condition'], condition=condition_content['name'],
                          true_outcomes=map_outcomes(True), false_outcomes=map_outcomes(False))
    return condition


def parse_point(point_content):
    point = DecisionPoint(name=point_content['point'],
                          point=point_content['name'],
                          conditions=[parse_condition(condition) for condition in point_content['conditions']])
    return point


def parse_action(action):
    return Action(name=action['action'], action=action['name'], stop=action.get('break', False))


def parse_branch(data, name):
    decision_points = [parse_point(decision) for decision in data['decisions']]

    branch = Branch(branch=name,
                    name=data['branch'],
                    decision_points=decision_points,
                    actions=[parse_action(action) for action in data['actions']],
                    conditions=list(chain.from_iterable([point.conditions for point in decision_points]))
                   )
    return branch
