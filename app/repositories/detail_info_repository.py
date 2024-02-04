from typing import List
from sqlalchemy.orm import Session
from models import DetailInfo


class DetailInfoRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_details_by_ids(self, detail_ids: List[int]) -> List[DetailInfo]:
        return self.session.query(DetailInfo).filter(DetailInfo.id.in_(detail_ids)).all()

    def get_detail_by_part_number(self, part_number: str) -> List[DetailInfo]:
        return self.session.query(DetailInfo).filter_by(part_number=part_number).all()

    def get_details_by_brand_ids(self, brand_ids: List[int]) -> List[DetailInfo]:
        return self.session.query(DetailInfo).filter(DetailInfo.brand_id.in_(brand_ids)).all()

