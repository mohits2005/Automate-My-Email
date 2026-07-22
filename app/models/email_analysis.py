from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class EmailAnalysis(Base):
    __tablename__ = "email_analysis"

    id = Column(Integer, primary_key=True, index=True)

    email_id = Column(
        Integer,
        ForeignKey("emails.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    summary = Column(String(1000), nullable=False)

    priority = Column(String(20), nullable=False)

    category = Column(String(100), nullable=False)

    action_required = Column(String(10), nullable=False)

    suggested_reply = Column(String(2000), nullable=False)

    created_at = Column(
        TIMESTAMP, 
        server_default=func.now(), 
        nullable=False
    )

    email = relationship(
        "Email",
        back_populates="analysis"
    )