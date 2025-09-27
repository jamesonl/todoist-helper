"""Database schema definitions for the Todoist helper backend.

This module defines the SQLAlchemy ORM models that mirror the Todoist data we
care about as well as helper utilities for working with the schema. The goal of
this file is to make the first next step from the README concrete by providing a
clear schema that can be created in any SQL database supported by SQLAlchemy.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Project(Base):
    """Represents a Todoist project."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)
    color = Column(String(32), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Section(Base):
    """Represents a logical grouping of tasks inside a project."""

    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    project = relationship("Project", back_populates="sections")
    tasks = relationship("Task", back_populates="section", cascade="all, delete-orphan")


Project.sections = relationship("Section", order_by=Section.order, back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    """Represents a Todoist task."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=False)
    content = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="SET NULL"), nullable=True)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    priority = Column(Integer, nullable=False, default=1)
    due_date = Column(Date, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    url = Column(String(512), nullable=True)

    project = relationship("Project", back_populates="tasks")
    section = relationship("Section", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], back_populates="children")
    children = relationship("Task", back_populates="parent", cascade="all, delete-orphan")
    labels = relationship("TaskLabel", back_populates="task", cascade="all, delete-orphan")


class Label(Base):
    """Represents a Todoist label."""

    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False, unique=True)
    color = Column(String(32), nullable=True)

    tasks = relationship("TaskLabel", back_populates="label", cascade="all, delete-orphan")


class TaskLabel(Base):
    """Associative table between tasks and labels."""

    __tablename__ = "task_labels"
    __table_args__ = (UniqueConstraint("task_id", "label_id", name="uq_task_label"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    label_id = Column(Integer, ForeignKey("labels.id", ondelete="CASCADE"), nullable=False)

    task = relationship("Task", back_populates="labels")
    label = relationship("Label", back_populates="tasks")


class SyncCursor(Base):
    """Tracks the last sync positions for Todoist resources."""

    __tablename__ = "sync_cursors"

    resource = Column(String(64), primary_key=True)
    cursor = Column(String(256), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DailyTaskSummary(Base):
    """Stores aggregated task metrics used by the contribution-style calendar."""

    __tablename__ = "daily_task_summaries"
    __table_args__ = (UniqueConstraint("date", name="uq_daily_task_date"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    open_tasks = Column(Integer, nullable=False, default=0)
    completed_tasks = Column(Integer, nullable=False, default=0)
    newly_added_tasks = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def create_all(engine) -> None:
    """Create all database tables for the configured engine."""

    Base.metadata.create_all(engine)


def drop_all(engine) -> None:
    """Drop all database tables for the configured engine."""

    Base.metadata.drop_all(engine)
