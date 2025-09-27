"""FastAPI application wiring together the backend services."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import analytics, schema, sync
from agents.workflows import copilot_orchestrator

DATABASE_URL = "sqlite:///./todoist_helper.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

schema.create_all(engine)

app = FastAPI(title="Todoist Helper")


def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class HeatmapResponse(BaseModel):
    weeks: list[list[dict[str, Any]]]


@app.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(days: int = 70, session: Session = Depends(get_session)) -> HeatmapResponse:
    end = date.today()
    start = end - timedelta(days=days)
    summaries = analytics.load_daily_summaries(session, start, end)
    matrix = analytics.build_calendar_matrix(start, end, summaries)
    weeks = [
        [
            {
                "date": cell.date.isoformat(),
                "summary": (
                    {
                        "date": cell.summary.date.isoformat(),
                        "openTasks": cell.summary.open_tasks,
                        "completedTasks": cell.summary.completed_tasks,
                        "newlyAddedTasks": cell.summary.newly_added_tasks,
                    }
                    if cell.summary
                    else None
                ),
            }
            for cell in week
        ]
        for week in matrix
    ]
    return HeatmapResponse(weeks=weeks)


class SyncRequest(BaseModel):
    payload: dict[str, Any]


@app.post("/sync")
def run_sync(request: SyncRequest, session: Session = Depends(get_session)) -> dict[str, str]:
    class _InlineClient(sync.TodoistClientProtocol):
        def sync(self, cursor: str | None = None) -> dict[str, Any]:
            return request.payload

    sync.synchronize(session, _InlineClient())
    return {"status": "ok"}


class ChatRequest(BaseModel):
    user_request: str
    context: dict[str, str] = {}


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    steps = copilot_orchestrator.plan(request.user_request, request.context)
    return {"steps": steps}
