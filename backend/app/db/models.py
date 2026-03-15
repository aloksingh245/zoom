from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    classes: Mapped[list["ClassSession"]] = relationship("ClassSession", back_populates="course", cascade="all, delete-orphan")


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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course: Mapped["Course"] = relationship("Course", back_populates="classes")
