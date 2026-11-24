"""KaveriDesk HTTP API (KAV-215): read and create tickets over HTTP.

Run with:  python -m uvicorn kaveridesk.api:app --port 8000   then open http://127.0.0.1:8000/docs
"""
import os
from datetime import datetime
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .cli import DATA
from .service import SLA, TEAM, Desk
from .store import Store

ISO = "%Y-%m-%dT%H:%M"

app = FastAPI(title="KaveriDesk API", version="1.0")


class TicketIn(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    category: Literal["IT", "Security", "HR", "Finance", "Facilities"]
    priority: Literal["P1", "P2", "P3", "P4"] = "P3"
    requester: str = Field(min_length=1)


class TicketOut(BaseModel):
    id: str
    title: str
    category: str
    team: str
    priority: str
    status: str
    assignee: Optional[str]
    requester: str
    created: str
    due: str
    resolved_at: Optional[str]
    sla: str
    notes: list[str]


def get_desk() -> Desk:
    """A fresh Desk per request, so every request sees the latest data on disk."""
    folder = os.getenv("KAVERIDESK_DATA") or str(DATA)
    now_text = os.getenv("KAVERIDESK_NOW")
    now = datetime.strptime(now_text, "%Y-%m-%d %H:%M") if now_text else None
    return Desk(Store(folder), now)


def to_out(d: Desk, t) -> TicketOut:
    return TicketOut(
        id=t.id, title=t.title, category=t.category, team=TEAM[t.category], priority=t.priority,
        status=t.status, assignee=t.assignee, requester=t.requester,
        created=t.created.strftime(ISO), due=d.due(t).strftime(ISO),
        resolved_at=t.resolved_at.strftime(ISO) if t.resolved_at else None,
        sla=d.state(t), notes=list(t.notes),
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(team: Optional[str] = None, all: bool = False):
    d = get_desk()
    ts = [t for t in d.ts if all or t.status != "resolved"]
    if team:
        ts = [t for t in ts if TEAM[t.category].lower() == team.lower()]
    return [to_out(d, t) for t in sorted(ts, key=d.due)]


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: str):
    d = get_desk()
    try:
        return to_out(d, d.get(ticket_id))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"No ticket {ticket_id}")


@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(body: TicketIn):
    d = get_desk()
    t = d.new(body.title, body.category, body.priority, body.requester)
    return to_out(d, t)


@app.get("/breaches", response_model=list[TicketOut])
def breaches():
    d = get_desk()
    return [to_out(d, t) for t in d.breaches()]
