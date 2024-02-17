from models.deal import Deal
from repositories.base import BaseRepository
from sqlalchemy.orm import make_transient_to_detached


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
                if new_deal is not None:
                    session.add(new_deal)
                    session.commit()
                    return new_deal
                else:
                    deal = Deal(deal_id=deal_id)
                    session.add(deal)
                    session.commit()
                    return deal
            return deal

