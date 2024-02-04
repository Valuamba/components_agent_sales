from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB  # Assuming JSONB for vector; adjust as needed
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Embedding(Base):
    __tablename__ = 'embeddings'

    id = Column(Integer, primary_key=True)
    embedding = Column(JSONB)  # Adjust based on actual type
    text = Column(Text)
    created_at = Column(DateTime, default=func.now())
