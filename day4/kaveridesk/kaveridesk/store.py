import json
from datetime import date, datetime
from pathlib import Path

from .models import Agent, Ticket

F = "%Y-%m-%d %H:%M"


def _d(s):
    return datetime.strptime(s, F) if s else None


def _s(d):
    return d.strftime(F) if d else None


class Store:
    def __init__(self, folder):
        self.p = Path(folder)

    def _r(self, name):
        with open(self.p / name, encoding="utf-8") as f:
            return json.load(f)

    def tickets(self):
        out = []
        for x in self._r("tickets.json"):
            x["created"] = _d(x["created"])
            x["resolved_at"] = _d(x.get("resolved_at"))
            out.append(Ticket(**x))
        return out

    def save(self, ts):
        rows = []
        for t in ts:
            x = dict(t.__dict__)
            x["created"] = _s(t.created)
            x["resolved_at"] = _s(t.resolved_at)
            rows.append(x)
        tmp = self.p / "tickets.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        tmp.replace(self.p / "tickets.json")

    def agents(self):
        return [Agent(**a) for a in self._r("agents.json")]

    def hols(self):
        return {date.fromisoformat(x["date"]) for x in self._r("holidays.json")}
