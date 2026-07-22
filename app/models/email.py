from sqlalchemy import Integer, String, Boolean, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Email(Base):

    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    gmail_message_id = Column(String(255), unique=True, nullable=False)

    sender = Column(String(255), nullable=False)

    recipent = Column(String(255), nullable=False)

    subject = Column(String(255), nullable=True)

    body = Column(Text, nullable=False)

    recieved_at = Column(DateTime(timezone=True))

    processed = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="emails")

    analysis = relationship(
        "EmailAnalysis",
        back_populates="email",
        uselist=False,
        cascade="all, delete"
    )
