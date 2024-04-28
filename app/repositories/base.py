from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from services import LoggingService

Base = declarative_base()


class BaseRepository:
    def __init__(self, session: Session, logger: LoggingService = None):
        self.session = session
        self.logger = logger

    # def __init__(self, db_url):
    #     self.engine = create_engine(db_url)
    #     Base.metadata.create_all(self.engine)
    #     self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
