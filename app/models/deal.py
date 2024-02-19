import uuid
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class FromType(enum.Enum):
    Manager = 0
    Customer = 1

class StatusType(enum.Enum):
    Failed = 0
    Passed = 1
    Stopped = 2


class Deal(Base):
    __tablename__ = 'deal'

    id = Column(Integer, primary_key=True, autoincrement=True)
    deal_id = Column(Integer, unique=True, nullable=False)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    subject = Column(String, nullable=False)
    customer = Column(String, nullable=True)

    country = Column(String(255))
    domain = Column(String(255))
    email = Column(String(255))
    office_country = Column(String(255))
    phone_number = Column(String(255))

    messages = relationship("Message", back_populates="deal")
    part_inquiries = relationship("PartInquiry", back_populates="deal")
    agent_tasks = relationship("AgentTask", back_populates="deal")


class AgentTask(Base):
    __tablename__ = 'agent_task'

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    completion_cost = Column(Float, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=True)
    agent_type = Column(Integer, nullable=False)
    status = Column(Enum(StatusType), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deal_id = Column(Integer, ForeignKey('deal.deal_id'))

    deal = relationship("Deal", back_populates="agent_tasks")
    task_feedbacks = relationship("TaskFeedback", back_populates="agent_task")


class TaskFeedback(Base):
    __tablename__ = 'task_feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    task_id = Column(Integer, ForeignKey('agent_task.task_id'))
    feedback = Column(String, nullable=True)
    is_like = Column(Integer, nullable=False)

    agent_task = relationship("AgentTask", back_populates="task_feedbacks")
    issues = relationship("Issue", secondary="taskfeedback_issue_link")


class IssueGroup(Base):
    __tablename__ = 'issue_group'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    issues = relationship("Issue", back_populates="issue_group")


class Issue(Base):
    __tablename__ = 'issue'

    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    description = Column(String, nullable=False)

    issue_group_id = Column(Integer, ForeignKey('issue_group.id'))

    issue_group = relationship("IssueGroup", back_populates="issues")

    task_feedbacks = relationship("TaskFeedback", secondary="taskfeedback_issue_link")


class PartInquiry(Base):
    __tablename__ = 'part_inquiry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    brand_id = Column(Integer, nullable=True)
    brand_name = Column(String, nullable=True)
    full_brand_name = Column(String, nullable=True)
    amount = Column(Integer, nullable=True)
    part_number = Column(String, nullable=True)
    deal_id = Column(Integer, ForeignKey('deal.deal_id'))

    deal = relationship("Deal", back_populates="part_inquiries")


class Message(Base):
    __tablename__ = 'message'

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(Integer)
    deal_id = Column(Integer, ForeignKey('deal.deal_id'))
    body = Column(String, nullable=False)
    hash = Column(String, nullable=True)
    sign = Column(String, nullable=True)
    from_type = Column(Integer, nullable=False)
    reply_to = Column(Integer, ForeignKey('message.message_id'))
    sent_at = Column(DateTime, nullable=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    deal = relationship("Deal", back_populates="messages")
    intents = relationship("Intent", back_populates="message")


class Intent(Base):
    __tablename__ = 'intent'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    intent = Column(String, nullable=False)
    sub_intent = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    message_id = Column(Integer, ForeignKey('message.message_id'))

    message = relationship("Message", back_populates="intents")


# Association Table for Many-to-Many relationship between TaskFeedback and Issue
taskfeedback_issue_link = Table(
    'taskfeedback_issue_link', Base.metadata,
    Column('task_feedback_id', Integer, ForeignKey('task_feedback.id'), primary_key=True),
    Column('issue_id', Integer, ForeignKey('issue.issue_id'), primary_key=True)
)
