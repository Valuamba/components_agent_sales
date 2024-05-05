from abc import ABC
from typing import List, Optional, Any, Union

from pydantic import BaseModel


class Metadata(BaseModel):
    completion_cost_usd: float
    completion_time_sec: float
    llm_model: str
    raw_output: Optional[str] = None


class Data(BaseModel):
    class Config:
        exclude_none = True


class ActionError(BaseModel):
    code: int
    message: str


class ActionMetadata(BaseModel):
    action_version: int
    action_name: str
    action_id: int
    action_time: float | None = None
    action_status: Optional[int] = None  # Optional for events without error


class Action(BaseModel):
    action: ActionMetadata
    ui_message: str | None = None
    data: Any = None
    metadata: Metadata | None = None
    error: Any = None


class Actions(BaseModel):
    actions: List[Action]