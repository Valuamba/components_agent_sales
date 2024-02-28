from sqlalchemy import select

from models.deal import Deal, Message, PurchaseHistory
from repositories.base import BaseRepository
from sqlalchemy.orm import make_transient_to_detached, selectinload, joinedload


class PurchaseHistoryRepository(BaseRepository):

    def get_client_id_by_deal(self, deal_id):
        deal = self.session.query(PurchaseHistory).filter(PurchaseHistory.deal_id == deal_id).first()

        if deal:
            return deal.client_id
        else:
            return None

    def get_client_history(self, client_id):
        results = self.session.query(PurchaseHistory).filter(PurchaseHistory.client_id == str(client_id)).order_by(
            PurchaseHistory.requisition_created).all()

        purchase_history = {}
        for result in results:
            date = result.requisition_created.date()
            if date not in purchase_history:
                purchase_history[date] = []

            margin = (result.price_sell - result.price_buy) / result.price_buy * 100 if result.price_buy else None

            history_item = {
                'id': result.deal_id,
                'brand_id': int(float(result.brand_id)) if result.brand_id else None,
                'articul': result.part_number,
                'client_title': result.client_title,
                'client_id': result.client_id,
                'price_buy': result.price_buy,
                'requisition_created': result.requisition_created,
                'brand_title': result.brand_title,
                'margin': round(margin, 2) if margin is not None else None,
                'price_sell': result.price_sell,
                'amount': result.amount
            }

            purchase_history[date].append(history_item)

        return purchase_history