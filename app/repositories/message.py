from sqlalchemy import func

from models import Deal
from models.deal import Message
from repositories.base import BaseRepository


class MessageRepository(BaseRepository):
    def append_message_to_deal(self, deal_id, message: Message):
        with self.session_scope() as session:
            deal = session.query(Deal).filter_by(deal_id=deal_id).first()
            if not deal:
                raise ValueError("Deal not found")

            # Calculate next message_id_in_deal
            max_message_id = session.query(func.max(Message.id)).filter_by \
                (deal_id=deal_id).scalar() or 0
            message.id = max_message_id + 1
            session.add(message)
            session.commit()
            return message