from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ClassifyPartRequest(BaseModel):
    deal_id: int
    body: str
    subject: Optional[str] = None
    from_client: Optional[str] = None
    sign: Optional[str] = None
    date: Optional[datetime] = None


class IssueModel(BaseModel):
    issue_id: int
    description: str

    class Config:
        orm_mode = True


class TaskFeedbackCreate(BaseModel):
    task_id: Optional[int] = None
    feedback: Optional[str] = None
    is_like: int
    issues: List[int] = []

    class Config:
        orm_mode = True