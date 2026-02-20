import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Uuid, func

from app.database import Base


class TravelProject(Base):
    __tablename__ = "travel_projects"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4, index=True)

    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)

    is_completed = Column(Boolean, nullable=False, default=False, server_default="0")
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def mark_completed(self) -> None:
        self.is_completed = True
        self.completed_at = datetime.datetime.now(datetime.UTC)

    def mark_incomplete(self) -> None:
        self.is_completed = False
        self.completed_at = None
