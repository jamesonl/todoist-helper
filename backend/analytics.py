"""Analytics utilities powering the contribution-style calendar."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import schema


@dataclass
class DailySummary:
    date: date
    open_tasks: int
    completed_tasks: int
    newly_added_tasks: int

    @property
    def intensity(self) -> int:
        """A composite score for coloring the heatmap."""

        return self.open_tasks + self.completed_tasks + self.newly_added_tasks


@dataclass
class CalendarCell:
    date: date
    summary: DailySummary | None

    @property
    def label(self) -> str:
        if self.summary is None:
            return "No activity"
        return (
            f"{self.summary.open_tasks} open, "
            f"{self.summary.completed_tasks} completed, "
            f"{self.summary.newly_added_tasks} added"
        )


def load_daily_summaries(session: Session, start: date, end: date) -> List[DailySummary]:
    """Load pre-computed summaries for the date range."""

    rows: Iterable[schema.DailyTaskSummary] = session.execute(
        select(schema.DailyTaskSummary).where(
            schema.DailyTaskSummary.date >= start,
            schema.DailyTaskSummary.date <= end,
        )
    ).scalars()

    return [
        DailySummary(
            date=row.date,
            open_tasks=row.open_tasks,
            completed_tasks=row.completed_tasks,
            newly_added_tasks=row.newly_added_tasks,
        )
        for row in rows
    ]


def build_calendar_matrix(start: date, end: date, summaries: Iterable[DailySummary]) -> List[List[CalendarCell]]:
    """Construct a matrix of weeks and days between the start and end."""

    summaries_by_date = {summary.date: summary for summary in summaries}
    num_days = (end - start).days + 1
    cells = [CalendarCell(date=start + timedelta(days=i), summary=summaries_by_date.get(start + timedelta(days=i))) for i in range(num_days)]

    weeks: List[List[CalendarCell]] = []
    for i in range(0, len(cells), 7):
        weeks.append(cells[i : i + 7])
    return weeks


__all__ = [
    "DailySummary",
    "CalendarCell",
    "load_daily_summaries",
    "build_calendar_matrix",
]
