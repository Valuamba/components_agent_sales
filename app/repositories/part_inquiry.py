from models import Deal
from models.deal import PartInquiry
from repositories.base import BaseRepository


class PartInquiryRepository(BaseRepository):
    def create_part_inquiry_for_deal(self, part_inquiry: PartInquiry):
        with self.session_scope() as session:
            deal = session.query(Deal).filter_by(deal_id=part_inquiry.deal_id).first()
            if not deal:
                raise ValueError("Deal not found")

            session.add(part_inquiry)
            session.commit()
            return part_inquiry