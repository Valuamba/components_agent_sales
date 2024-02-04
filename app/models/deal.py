from sqlalchemy import  Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Deal(Base):
    __tablename__ = 'Deal'

    deal_id = Column(Integer, primary_key=True)
    subject = Column(String(255))
    country = Column(String(255))
    domain = Column(String(255))
    email = Column(String(255))
    office_country = Column(String(255))
    phone_number = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)