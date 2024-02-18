from typing import List

from models.deal import Intent
from repositories.base import BaseRepository
from schemas.v1.intent import Intent as IntentModel


class IntentRepository(BaseRepository):

    def batch_insert_intents_from_models(self, intent_models: List[IntentModel], message_id):
        """
        Batch insert intents from an array of Pydantic IntentModel objects,
        associated with a specified message_id.

        Parameters:
        - intent_models: List of IntentModel instances.
        - message_id: The message_id to associate these intents with.
        """
        intents_to_insert = [
            Intent(
                intent=model.intent,
                sub_intent=model.sub_intent,
                branch=model.branch,
                message_id=message_id
            )
            for model in intent_models
        ]

        # Assuming 'session' is your SQLAlchemy session
        self.session.add_all(intents_to_insert)
        self.session.commit()