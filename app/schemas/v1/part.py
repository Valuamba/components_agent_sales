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