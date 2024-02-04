from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from configs.config import app_settings

# Database URL, replace it with your actual database connection string
DATABASE_URL = app_settings.famaga_db_url

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Use scoped_session to ensure thread safety
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base class for the models
Base = declarative_base()

# Dependency to get DB session
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
