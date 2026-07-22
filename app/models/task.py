from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    email_id = Column(Integer, ForeignKey("emails.id"))

    task = Column(String(500))

    deadline = Column(String(255))

    status = Column(String(20), default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)

    email = relationship("Email")