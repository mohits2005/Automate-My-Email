from pydantic import BaseModel


class EmailReplyResponse(BaseModel):
    email_id: int
    reply: str