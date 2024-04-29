from typing import Optional, List
from pydantic import BaseModel


class DetailRequest(BaseModel):
    amount: int | None
    brand_name: str | None
    part_number: str | None


class ClientInfo(BaseModel):
    country: Optional[str] = None
    domain: Optional[str] = None
    email: Optional[str] = None
    office_country: Optional[str] = None


class ClassifyAgentResponse(BaseModel):
    parts: List[DetailRequest]
    client: ClientInfo
    deal_id: Optional[int] = None
    message_id: Optional[int] = None
    agent_task_id: Optional[int] = None