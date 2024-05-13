from typing import Optional, List
from pydantic import BaseModel


class DetailRequest(BaseModel):
    amount: Optional[int] = None
    brand_name: Optional[str] = None
    part_number: Optional[str] = None


class ClientInfo(BaseModel):
    country: Optional[str] = None
    domain: Optional[str] = None
    email: Optional[str] = None
    office_country: Optional[str] = None
    mobile_phone: Optional[str] = None
    office_phone: Optional[str] = None
    fax: Optional[str] = None


class ClassifyAgentResponse(BaseModel):
    parts: List[DetailRequest]
    client: ClientInfo
    deal_id: Optional[int] = None
    message_id: Optional[int] = None
    agent_task_id: Optional[int] = None