from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Uuid, func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=True)
    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
