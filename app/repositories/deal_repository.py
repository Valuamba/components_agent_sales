from typing import List

from sqlalchemy import select

from models.deal import Deal, Message
from repositories.base import BaseRepository
from sqlalchemy.orm import make_transient_to_detached, selectinload, joinedload

from schemas.v1.messages import MessageModel, IntentModel


class DealRepository(BaseRepository):
    def create_deal(self, deal: Deal):
        # with self.session_scope() as session:
        self.session.add(deal)
        return deal

    def get_deal(self, deal_id):
        # with self.session_scope() as session:
        deal = self.session.query(Deal).filter_by(deal_id=deal_id).first()
        return deal

    def get_deal_with_messages(self, deal_id: str):
        return self.session.query(Deal).where(Deal.deal_id == deal_id).options(
            joinedload(Deal.messages).joinedload(Message.intents)
        ).first()

    def get_deal_with_messages_v2(self, deal_id: str) -> List[MessageModel]:
        deal = self.session.query(Deal).where(Deal.deal_id == deal_id).options(
            joinedload(Deal.messages).joinedload(Message.intents)
        ).first()

        if not deal:
            raise Exception("Deal not found")

        messages = [
            MessageModel(
                uuid=msg.uuid,
                id=msg.id,
                body=msg.body,
                from_type=msg.from_type,
                intents=[
                    IntentModel(
                        uuid=intent.uuid,
                        intent=intent.intent,
                        sub_intent=intent.sub_intent,
                        branch=intent.branch
                    ) for intent in msg.intents
                ]
            ) for msg in deal.messages
        ]

        return messages

    def get_or_create_deal(self, deal_id, new_deal: Deal = None):
        # with self.session_scope() as session:
        deal = self.session.query(Deal).filter_by(deal_id=deal_id).first()
        if deal is None:
            if new_deal is not None:
                self.session.add(new_deal)
                self.session.commit()
                return new_deal
            else:
                deal = Deal(deal_id=deal_id)
                self.session.add(deal)
                self.session.commit()
                return deal
        return deal

