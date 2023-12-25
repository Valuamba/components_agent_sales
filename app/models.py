from pydantic import BaseModel
from typing import List, Optional
import datetime


class EmailRequest(BaseModel):
    body: str
    subject: str | None
    from_client: str | None
    sign: str | None
    date: datetime.datetime | None


class DetailRequest(BaseModel):
    amount: int
    brand_name: str
    part_number: str
    country: Optional[str] = None


class Detail(BaseModel):
    id: int
    brand_name: str
    part_number: str
    description: str


class SuitableDetail(BaseModel):
    id: int
    relevance: List[str]