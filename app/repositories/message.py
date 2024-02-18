from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound

from models import Deal
from models.deal import Message
from repositories.base import BaseRepository


class MessageRepository(BaseRepository):

    def append_message_to_chat_history_or_get(self, deal_id, hash, message: Message = None):

        max_message_id = self.session.query(func.max(Message.id)) \
                             .filter(Message.deal_id == deal_id, Message.hash != None) \
                             .scalar() or 0
        message.id = max_message_id + 1

        try:
            # Try to retrieve an existing message by hash
            query = select(Message).where(Message.hash == hash, Message.deal_id == deal_id)
            existing_message = self.session.execute(query).scalar_one()
            return existing_message
        except NoResultFound:
            # If no message exists with the given hash, and a new message is provided, append it
            if message:
                # Ensure the provided message has the correct deal_id and hash
                message.deal_id = deal_id
                message.hash = hash
                self.session.add(message)
                self.session.commit()
                return message
            else:
                # If no message is provided, return None or raise an exception based on your use case
                return None


    def append_message_to_deal(self, deal_id, message: Message):
        deal = self.session.query(Deal).filter_by(deal_id=deal_id).first()
        if not deal:
            raise ValueError("Deal not found")

            # Calculate next message_id_in_deal
        max_message_id = self.session.query(func.max(Message.id)) \
                             .filter(Message.deal_id == deal_id, Message.hash != None) \
                             .scalar() or 0
        message.id = max_message_id + 1
        self.session.add(message)
        self.session.commit()
        return message