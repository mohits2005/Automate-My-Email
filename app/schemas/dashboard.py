from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_emails: int
    analyzed_emails: int
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
    high_priority_emails: int