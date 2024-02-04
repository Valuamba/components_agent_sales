from models.deal import Deal
from repositories.base import BaseRepository


class DealRepository(BaseRepository):
    def create_deal(self, **kwargs):
        with self.session_scope() as session:
            deal = Deal(**kwargs)
            session.add(deal)
            return deal

    def get_deal(self, deal_id):
        with self.session_scope() as session:
            deal = session.query(Deal).filter_by(deal_id=deal_id).first()
            return deal