import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, Uuid, func

from app.database import Base


class ProjectPlace(Base):
    __tablename__ = "project_places"
    __table_args__ = (UniqueConstraint("project_id", "external_id", name="uq_project_places_project_id_external_id"),)

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4, index=True)

    project_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("travel_projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    external_id = Column(Integer, index=True, nullable=False)
    title = Column(String, nullable=True)

    notes = Column(String, nullable=True)
    visited = Column(Boolean, nullable=False, default=False, server_default="0")
    visited_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def mark_visited(self) -> None:
        self.visited = True
        self.visited_at = datetime.datetime.now(datetime.UTC)

    def mark_unvisited(self) -> None:
        self.visited = False
        self.visited_at = None
