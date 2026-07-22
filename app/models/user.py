from sqlalchemy import Integer, String, Boolean, DateTime, Column, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 

from app.database.database import Base


class User(Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(String(255), nullable=False, unique=True, index=True)

    hashed_password = Column(String(255), nullable=True)

    google_id = Column(String(255), unique=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)

    emails = relationship(
        "Email",
        back_populates="user",
        cascade="all, delete-orphan"
    )

