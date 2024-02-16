from models.deal import Deal
from repositories.base import BaseRepository


class DealRepository(BaseRepository):
    def create_deal(self, deal: Deal):
        with self.session_scope() as session:
            session.add(deal)
            return deal

    def get_deal(self, deal_id):
        with self.session_scope() as session:
            deal = session.query(Deal).filter_by(deal_id=deal_id).first()
            return deal

    def get_or_create_deal(self, deal_id, new_deal: Deal = None):
        with self.session_scope() as session:
            deal = session.query(Deal).filter_by(deal_id=deal_id).first()
            if deal is None:
                session.add(new_deal)
                session.commit()
            return deal

