from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
import tiktoken
import os
from dotenv import load_dotenv

from ipywidgets import widgets, Layout, Button, Textarea, HBox
from IPython.display import display
import threading
import openai

completion_pricing_per_1k_tokens_usd = {
    "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
    "gpt-4-1106-vision-preview": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-32k": {"input": 0.06, "output": 0.12},
    "gpt-3.5-turbo-1106": {"input": 0.0010, "output": 0.002},
    "gpt-3.5-turbo-instruct": {"input": 0.0010, "output": 0.002},
}

assistants_api_price_usd = {
    "Code interpreter": {"input": 0.03},
    "Retrieval": {"input": 0.2},
}


# Define your Pydantic model for data validation
class PromptVersion(BaseModel):
    pkid: Optional[int] = None 
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    prompt: str
    response: str
    model: str
    input_tokens: int
    output_tokens: int
    tags: Optional[str] = None
    total_price: float
    is_like: Optional[bool] = None
    temperature: Optional[float] = None
    feedback: Optional[str] = None

Base = declarative_base()

# Define your SQLAlchemy model for the database schema
class PromptVersionDB(Base):
    __tablename__ = 'prompt_versions'
    pkid = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    prompt = Column(Text)
    response = Column(Text)
    model = Column(String)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    temperature = Column(Float)
    total_price = Column(Float)
    feedback = Column(Text)
    tags = Column(Text)
    is_like = Column(Boolean)


def num_tokens_from_string(string: str, encoding_name: str = "gpt-3.5-turbo") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
    

class GPTDatabaseLogger:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        if os.getenv('OPENAI_API_KEY') is None:
            load_dotenv()
        self.client = openai.OpenAI()

    def create_completion(self, messages, temperature, output = True, tags: str = None,
                          model: str = 'gpt-4', **kwargs): 
        tokens_pricing = completion_pricing_per_1k_tokens_usd[model]

        prompt = "\n\n".join([msg['role'] + ": " + msg['content'] for msg in messages])
        prompt_tokens = sum([ num_tokens_from_string(msg['content']) for msg in messages])
    
        response = self.client.chat.completions.create(model=model, 
                                                  messages=messages, 
                                                  temperature=temperature, 
                                                  stream=True, **kwargs
                                                 )
        collected_messages = []
        for chunk in response:
            if chunk.choices[0].delta.content:
                if output:
                    print(chunk.choices[0].delta.content, end='')
                collected_messages.append(chunk.choices[0].delta.content)

        content_str = ''.join(collected_messages)
        output_tokens = num_tokens_from_string(content_str)

        total_price = (tokens_pricing['input'] * prompt_tokens + tokens_pricing['output'] * output_tokens) / 1000

        prompt_version = PromptVersion(
            prompt=prompt, 
            response=content_str, 
            model=model,
            temperature=temperature,
            input_tokens=prompt_tokens, 
            output_tokens=output_tokens,
            total_price=total_price,
            tags=tags
        )
        
        session = self.Session()
        db_record = PromptVersionDB(**prompt_version.dict())
        session.add(db_record)
        session.commit()
        self.note_id = db_record.id  # Assuming the record has an ID field
        session.close()

        # Step 3: Return result from method
        print("\n\n--------------------\n\nNote saved without feedback. ID:", self.note_id)
        print(f'Input tokens: {prompt_tokens} Output tokens: {output_tokens} Total price: {round(total_price, 2)}$\n\n')

        # Step 4: Run the window for feedback form
        self.collect_feedback()

        return content_str

    
    def collect_feedback(self):
        feedback_input = Textarea(
            value='',
            placeholder='Type your feedback here...',
            description='Feedback:',
            disabled=False,
            layout=Layout(width='70%', height='80px')
        )

        like_button = Button(description='👍 Like', button_style='success', tooltip='Like this content')
        dislike_button = Button(description='👎 Dislike', button_style='danger', tooltip='Dislike this content')
        feedback_button = Button(description='Submit Feedback', button_style='success', tooltip='Click to submit feedback')

        def on_like_disliked(b):
            session = self.Session()
            note_to_update = session.query(PromptVersionDB).filter_by(id=self.note_id).first()
            if note_to_update:
                if b.description == '👍 Like':
                    note_to_update.is_like = True
                elif b.description == '👎 Dislike':
                    note_to_update.is_like = False
                session.commit()
            session.close()

        def on_feedback_submitted(b):
            feedback = feedback_input.value
            session = self.Session()
            note_to_update = session.query(PromptVersionDB).filter_by(id=self.note_id).first()
            if note_to_update:
                note_to_update.feedback = feedback
                session.commit()
                print("Feedback updated successfully.")
            else:
                print("Note not found.")
            session.close()
            feedback_input.value = ''  # Clear input after submission

        feedback_button.on_click(on_feedback_submitted)
        like_button.on_click(on_like_disliked)
        dislike_button.on_click(on_like_disliked)

        display(HBox([like_button, dislike_button]), feedback_input, feedback_button)