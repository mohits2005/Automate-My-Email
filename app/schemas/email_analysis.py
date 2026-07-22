from pydantic import BaseModel
from datetime import datetime


class EmailAnalysisResponse(BaseModel):
    id: int
    email_id: int
    summary: str
    priority: str
    category: str
    action_required: str
    suggested_reply: str
    created_at: datetime

    class Config:
        from_attributes = True