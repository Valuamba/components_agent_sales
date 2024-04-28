from typing import List

from sqlalchemy import select

from models.deal import Deal, Message, LLMRun
from repositories.base import BaseRepository
from sqlalchemy.orm import make_transient_to_detached, selectinload, joinedload

from schemas.v1.messages import MessageModel, IntentModel
from services import LoggingService


class RunRepository(BaseRepository):

    def create_run(self, run: LLMRun):
        self.session.add(run)
        self.session.commit()
        self.logger.info(f'Run created with ID: {run.run_id}')
        return run