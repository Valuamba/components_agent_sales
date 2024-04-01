from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
import enum


class StatusType(enum.Enum):
    Failed = 0
    Passed = 1
    Stopped = 2


class AgentTaskPydantic(BaseModel):
    task_id: int
    completion_cost: Optional[float] = None
    output_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    prompt: str
    response: Optional[str] = None
    agent_type: int
    status: int
    created_at: datetime
    updated_at: datetime
    deal_id: str

    class Config:
        from_attributes = True
        orm_mode = True
        use_enum_values = True  # Configure Pydantic to use enum values instead of enum names

    @validator('status', pre=True, allow_reuse=True)
    def convert_status_to_value(cls, value):
        if isinstance(value, StatusType):
            return value.value
        return value