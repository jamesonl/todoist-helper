"""Synchronization pipeline between Todoist and the SQL mirror."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import schema

logger = logging.getLogger(__name__)


@dataclass
class TodoistTask:
    """Minimal representation of a Todoist task for synchronization."""

    id: int
    content: str
    description: str | None
    project_id: int
    section_id: int | None
    parent_id: int | None
    order: int
    priority: int
    due_date: datetime | None
    completed: bool
    completed_at: datetime | None
    url: str | None
    labels: List[int]
    created_at: datetime
    updated_at: datetime


@dataclass
class TodoistProject:
    id: int
    name: str
    color: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class TodoistSection:
    id: int
    project_id: int
    name: str
    order: int
    created_at: datetime
    updated_at: datetime


@dataclass
class TodoistLabel:
    id: int
    name: str
    color: str | None


class TodoistClientProtocol:
    """Protocol describing methods used by the sync pipeline."""

    def sync(self, cursor: str | None = None) -> Dict[str, Any]:  # pragma: no cover - protocol
        raise NotImplementedError


def upsert_project(session: Session, project: TodoistProject) -> schema.Project:
    db_project = session.get(schema.Project, project.id)
    if db_project is None:
        db_project = schema.Project(id=project.id)
        session.add(db_project)

    db_project.name = project.name
    db_project.color = project.color
    db_project.is_archived = project.is_archived
    db_project.created_at = project.created_at
    db_project.updated_at = project.updated_at
    return db_project


def upsert_section(session: Session, section: TodoistSection) -> schema.Section:
    db_section = session.get(schema.Section, section.id)
    if db_section is None:
        db_section = schema.Section(id=section.id)
        session.add(db_section)

    db_section.name = section.name
    db_section.project_id = section.project_id
    db_section.order = section.order
    db_section.created_at = section.created_at
    db_section.updated_at = section.updated_at
    return db_section


def upsert_label(session: Session, label: TodoistLabel) -> schema.Label:
    db_label = session.get(schema.Label, label.id)
    if db_label is None:
        db_label = schema.Label(id=label.id)
        session.add(db_label)

    db_label.name = label.name
    db_label.color = label.color
    return db_label


def upsert_task(session: Session, task: TodoistTask) -> schema.Task:
    db_task = session.get(schema.Task, task.id)
    if db_task is None:
        db_task = schema.Task(id=task.id)
        session.add(db_task)

    db_task.content = task.content
    db_task.description = task.description
    db_task.project_id = task.project_id
    db_task.section_id = task.section_id
    db_task.parent_id = task.parent_id
    db_task.order = task.order
    db_task.priority = task.priority
    db_task.due_date = task.due_date.date() if isinstance(task.due_date, datetime) else task.due_date
    db_task.completed = task.completed
    db_task.completed_at = task.completed_at
    db_task.created_at = task.created_at
    db_task.updated_at = task.updated_at
    db_task.url = task.url

    # Sync labels
    existing_label_ids = {tl.label_id for tl in db_task.labels}
    incoming_label_ids = set(task.labels)

    for label_id in incoming_label_ids - existing_label_ids:
        db_task.labels.append(schema.TaskLabel(task=db_task, label_id=label_id))

    for label_id in existing_label_ids - incoming_label_ids:
        to_remove = next(tl for tl in db_task.labels if tl.label_id == label_id)
        session.delete(to_remove)

    return db_task


def update_daily_summary(session: Session, task: schema.Task) -> None:
    """Update daily summary metrics for the task's dates."""

    relevant_dates: Iterable[datetime] = filter(None, [task.created_at, task.completed_at])
    for event_date in relevant_dates:
        summary = session.execute(
            select(schema.DailyTaskSummary).where(schema.DailyTaskSummary.date == event_date.date())
        ).scalar_one_or_none()
        if summary is None:
            summary = schema.DailyTaskSummary(date=event_date.date())
            session.add(summary)

        if event_date == task.created_at:
            summary.newly_added_tasks += 1
            summary.open_tasks += 1
        if event_date == task.completed_at:
            summary.completed_tasks += 1
            summary.open_tasks = max(summary.open_tasks - 1, 0)
        summary.updated_at = datetime.utcnow()


def synchronize(session: Session, client: TodoistClientProtocol) -> None:
    """Run a full sync with Todoist."""

    cursor = None
    sync_cursor = session.get(schema.SyncCursor, "full")
    if sync_cursor:
        cursor = sync_cursor.cursor

    payload = client.sync(cursor)

    projects = [TodoistProject(**p) for p in payload.get("projects", [])]
    sections = [TodoistSection(**s) for s in payload.get("sections", [])]
    labels = [TodoistLabel(**l) for l in payload.get("labels", [])]
    tasks = [TodoistTask(**t) for t in payload.get("tasks", [])]

    for project in projects:
        upsert_project(session, project)
    for section in sections:
        upsert_section(session, section)
    for label in labels:
        upsert_label(session, label)
    for task in tasks:
        db_task = upsert_task(session, task)
        update_daily_summary(session, db_task)

    if sync_cursor is None:
        sync_cursor = schema.SyncCursor(resource="full")
        session.add(sync_cursor)
    sync_cursor.cursor = payload.get("sync_token")
    sync_cursor.updated_at = datetime.utcnow()

    session.commit()


__all__ = [
    "TodoistTask",
    "TodoistProject",
    "TodoistSection",
    "TodoistLabel",
    "TodoistClientProtocol",
    "synchronize",
]
