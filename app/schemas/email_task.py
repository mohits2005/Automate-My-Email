from pydantic import BaseModel
from typing import List


class Task(BaseModel):
    task: str
    deadline: str


class EmailTaskResponse(BaseModel):
    email_id: int
    tasks: List[Task]