from pydantic import BaseModel
from datetime import datetime


class TaskResponse(BaseModel):
    id: int
    email_id: int
    task: str
    deadline: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskStatusUpdate(BaseModel):
    status: str