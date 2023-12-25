from pydantic import BaseModel
from typing import List

    
class Detail(BaseModel):
    id: int
    brand_name: str
    part_number: str
    description: str