from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
import asyncio
from fastapi.encoders import jsonable_encoder
import uvicorn

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
    pkid = Column(Integer, primary_key=True, autoincrement=True)
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
    pkid: int
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
        from_attributes=True


class FeedbackUpdateRequest(BaseModel):
    feedback: str
    is_like: bool


class FeedbackResponse(BaseModel):
    pkid: int
    id: str
    feedback: str
    is_like: bool
    class Config:
        orm_mode = True


# @app.post("/prompts/", response_model=PromptVersion)
# def create_prompt_version(prompt_version: PromptVersionCreate, db: Session = Depends(get_db)):
#     db_prompt_version = PromptVersionDB(**prompt_version.dict())
#     db.add(db_prompt_version)
#     db.commit()
#     db.refresh(db_prompt_version)
#     return db_prompt_version
        
last_id_sent = 0  # Initialize with the last ID sent

def new_data_available(db: Session, last_id: int):
    return db.query(PromptVersion).filter(PromptVersion.pkid > last_id).first() is not None

def get_new_data(db: Session, last_id: int):
    global last_id_sent
    new_items = db.query(PromptVersion).filter(PromptVersion.pkid > last_id).all()
    if new_items:
        last_id_sent = new_items[-1].pkid  # Update with the latest ID sent
    return [PromptVersionSchema.from_orm(item) for item in new_items]


@app.post("/feedback/{item_id}", response_model=FeedbackResponse)
def update_feedback(item_id: str, feedback_data: FeedbackUpdateRequest, db: Session = Depends(get_db)):
    # Try to find the existing prompt version by id
    prompt_version = db.query(PromptVersion).filter(PromptVersion.id == item_id).first()

    # If it exists, update feedback and is_like
    if prompt_version:
        prompt_version.feedback = feedback_data.feedback
        prompt_version.is_like = feedback_data.is_like
    else:
        # If it doesn't exist, create a new PromptVersionDB entry
        prompt_version = PromptVersion(
            id=item_id,  # Assuming you want to manually set the UUID here, else remove this
            feedback=feedback_data.feedback,
            is_like=feedback_data.is_like,
            # Set other fields as necessary, or use default values
        )
        db.add(prompt_version)

    db.commit()
    db.refresh(prompt_version)
    return prompt_version


@app.get("/events")
async def get_events(request: Request, db: Session = Depends(get_db)):
    async def event_generator():
        global last_id_sent
        while True:
            if new_data_available(db, last_id_sent):
                print(last_id_sent)
                data = get_new_data(db, last_id_sent)
                json_compatible_data = jsonable_encoder(data)
                json_data = json.dumps(json_compatible_data)
                yield f"data: {json_data}\n\n"
            await asyncio.sleep(1)  # Polling frequency
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/prompts/", response_model=List[PromptVersionSchema])
def read_prompts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    global last_id_sent
    prompts = db.query(PromptVersion).offset(skip).limit(limit).all()
    if prompts:
        last_id_sent = prompts[-1].pkid
    return prompts


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8004, log_level="info")