from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DetailInfo(Base):
    __tablename__ = 'details_info'

    id = Column(Integer, primary_key=True)
    part_number = Column(String(500))
    model_number = Column(String(200))
    brand_id = Column(Integer)
    title = Column(String(500))
    description = Column(Text)