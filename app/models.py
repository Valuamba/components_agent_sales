from pydantic import BaseModel
from typing import List, Optional
import datetime


class CompletionResponse(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    content: str
    model: str
    usage_cost_usd: float


class EmailRequest(BaseModel):
    body: str
    subject: str | None
    from_client: str | None
    sign: str | None
    date: datetime.datetime | None


class DetailRequest(BaseModel):
    amount: int | None
    brand_name: str
    part_number: str
    country: Optional[str] = None


class GoogleSearchItems(BaseModel):
    title: str
    snippet: str
    link: str
    currency: str | None
    price: float | None
    relevance: List[str]


class Detail(BaseModel):
    id: int
    brand_name: str
    part_number: str
    description: str


class SuitableDetail(BaseModel):
    id: int
    relevance: List[str]
