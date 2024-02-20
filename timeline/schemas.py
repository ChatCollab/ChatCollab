from pydantic import BaseModel
from typing import List

# Import datetime for the EventSchema
from datetime import datetime

class AgentBaseSchema(BaseModel):
    name: str
    isSource: bool
    tags: List[str]

class AgentCreateSchema(AgentBaseSchema):
    pass

class AgentSchema(AgentBaseSchema):
    id: int
    public_key: str
    private_key: str
    isSource: bool

    class Config:
        orm_mode = True

class EventBaseSchema(BaseModel):
    title: str
    payload: str
    tags: List[str]

class EventCreateSchema(EventBaseSchema):
    pass

class EventSchema(EventBaseSchema):
    id: int
    created_at: datetime
    source_id: int

    class Config:
        orm_mode = True
