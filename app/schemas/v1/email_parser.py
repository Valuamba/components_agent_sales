from pydantic import BaseModel


class EmailContent(BaseModel):
    deal_id: int
    html_content: str
    subject: str