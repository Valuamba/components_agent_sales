from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware

DATABASE_URL = "sqlite:///../notebooks/famaga/prompt_versions.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Assuming PromptVersionDB class is already defined as per your model

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PromptVersion(Base):
    __tablename__ = 'prompt_versions'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    prompt = Column(Text)
    response = Column(Text)
    model = Column(String)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_price = Column(Float)
    feedback = Column(Text)
    temperature = Column(Float)
    tags = Column(Text)
    is_like = Column(Integer)

class PromptVersionSchema(BaseModel):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    prompt: str
    response: str
    model: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_price: Optional[float] = None
    feedback: Optional[str] = None
    temperature: Optional[float] = None
    tags: Optional[str] = None
    is_like: Optional[bool] = None

    class Config:
        orm_mode = True

# @app.post("/prompts/", response_model=PromptVersion)
# def create_prompt_version(prompt_version: PromptVersionCreate, db: Session = Depends(get_db)):
#     db_prompt_version = PromptVersionDB(**prompt_version.dict())
#     db.add(db_prompt_version)
#     db.commit()
#     db.refresh(db_prompt_version)
#     return db_prompt_version

@app.get("/prompts/", response_model=List[PromptVersionSchema])
def read_prompts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prompts = db.query(PromptVersion).offset(skip).limit(limit).all()
    return prompts
