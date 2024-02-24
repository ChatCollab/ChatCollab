import os
import base64
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, ARRAY, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
import json


Base = declarative_base()

def generate_key():
    """Generate a random base64-encoded key."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')

class Agent(Base):
    """
    Represents the source of an event.

    Attributes:
    id : int
        Unique identifier for the agent.
    public_key : str
        Auto-generated public key for the agent.
    private_key : str
        Auto-generated private key for the agent.
    isSource : bool
        Whether the agent is a source rather than autonomous agent.
    name : str
        Name or descriptor of the agent.
    events : list[Event]
        List of events associated with this agent.
    tags : list[str]
        List of tags (strings) associated with this agent.
    """
    
    __tablename__ = 'agent'
    
    id = Column(Integer, primary_key=True)
    public_key = Column(String, default=generate_key, unique=True, nullable=False)
    private_key = Column(String, default=generate_key, unique=True, nullable=False)
    isSource = Column(Boolean, default=False)
    name = Column(String, unique=True, nullable=False)
    events = relationship("Event", back_populates="source")
    _tags = Column("tags", String)

    def __setattr__(self, key, value):
        if key in ["public_key", "private_key"] and getattr(self, key, None):
            raise AttributeError(f"{key} is immutable and cannot be modified after being set.")
        super().__setattr__(key, value)

    @property
    def tags(self):
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value)

class Event(Base):
    """
    Represents an event in a timeline.
    
    Attributes:
    id : int
        Unique identifier for the event.
    title : str
        Title or name of the event.
    payload : str
        Payload associated with the event.
    created_at : datetime
        Datetime when the event was created.
    source_id : int
        Foreign key pointing to the associated agent.
    source : Agent
        The agent/source associated with this event.
    tags : list[str]
        List of tags (strings) associated with this event.
    """
    
    __tablename__ = 'event'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    payload = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    source_id = Column(Integer, ForeignKey('agent.id'))
    source = relationship("Agent", back_populates="events")
    _tags = Column("tags", String)

    @property
    def tags(self):
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value)


# Create the database
DATABASE_URL = "sqlite:///./timeline.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)