from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from configs.config import app_settings

DATABASE_URL = app_settings.famaga_db_url

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

metadata = MetaData(schema="stage")
Base = declarative_base(metadata=metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit the transaction after the request handling
    except Exception as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise e
    finally:
        db.close()
