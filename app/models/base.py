import uuid
from sqlalchemy import Column, Integer, TIMESTAMP, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import current_timestamp

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, default=current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, default=current_timestamp(), onupdate=current_timestamp(), nullable=False)