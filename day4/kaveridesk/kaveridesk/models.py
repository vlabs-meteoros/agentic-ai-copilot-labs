from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Ticket:
    id: str
    title: str
    category: str
    priority: str
    requester: str
    created: datetime
    status: str = "open"
    assignee: Optional[str] = None
    resolved_at: Optional[datetime] = None
    notes: list = field(default_factory=list)


@dataclass
class Agent:
    id: str
    name: str
    team: str
    max_open: int = 5
    lead: bool = False
