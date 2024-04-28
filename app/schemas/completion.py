from pydantic import BaseModel
from typing import List, Optional
import datetime


class CompletionResponse(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    content: str
    model: str
    usage_cost_usd: float
    completion_time_ms: float


class EmailRequest(BaseModel):
    body: str
    subject: str | None
    from_client: str | None
    sign: str | None
    date: datetime.datetime | None


class DetailRequest(BaseModel):
    amount: int | None
    brand_name: str | None
    part_number: str


class ClientInfo(BaseModel):
    country: Optional[str] = None
    domain: Optional[str] = None
    email: Optional[str] = None
    office_country: Optional[str] = None


class ClassifiedMessageData(BaseModel):
    parts: List[DetailRequest]
    client: ClientInfo


class GoogleSearchItems(BaseModel):
    title: str
    snippet: str
    link: str
    currency: str | None
    price: float | None
    relevance: List[str]


class Metadata(BaseModel):
    full_brand: str


class GoogleSearchResponse(BaseModel):
    google_items: List[GoogleSearchItems]
    metadata: Metadata


class Detail(BaseModel):
    id: int
    brand_name: str
    part_number: str
    description: str


class SuitableDetail(BaseModel):
    id: int
    relevance: List[str]
