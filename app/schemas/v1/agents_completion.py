from typing import Optional, List

from pydantic import BaseModel


class DealInfo(BaseModel):
    price_buy: Optional[float] = None
    price_sell: Optional[float] = None
    margin: Optional[float] = None
    discount: Optional[float] = None

    def to_string(self) -> str:
        return f"""
Price sell: {self.price_sell if self.price_sell is not None else 'N/A'}
Price buy: {self.price_buy if self.price_buy is not None else 'N/A'}
Margin: {self.margin if self.margin is not None else 'N/A'}%
Discount: {self.discount if self.discount is not None else 'N/A'}%
"""


class AgentCompletionRequest(BaseModel):
    deal_id: str
    deal_info: DealInfo


class HandleMessagesHtmlRequest(BaseModel):
    deal_id: str
    messages_html: str

class HandleMessagesRequest(BaseModel):
    deal_id: str
    messages: List[str]