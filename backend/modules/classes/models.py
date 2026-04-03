from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.base import Base


class ClassSession(Base):
    __tablename__ = "classes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    course_id: Mapped[str] = mapped_column(String, ForeignKey("courses.id"))
    course_name: Mapped[str] = mapped_column(String)
    topic_name: Mapped[str] = mapped_column(String)
    assignment_name: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[str] = mapped_column(String)
    start_time: Mapped[str] = mapped_column(String)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=90)
    timezone: Mapped[str] = mapped_column(String)
    zoom_meeting_id: Mapped[str] = mapped_column(String)
    zoom_join_url: Mapped[str] = mapped_column(String)
    calendar_event_id: Mapped[str | None] = mapped_column(String, nullable=True)
    mentor_email: Mapped[str | None] = mapped_column(String, nullable=True)
    sheet_row_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course: Mapped["Course"] = relationship("Course", back_populates="classes")
