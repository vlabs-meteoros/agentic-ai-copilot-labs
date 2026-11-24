from datetime import datetime

from .clock import add_bh, bh_between
from .models import Ticket

TEAM = {
    "IT": "Service Desk",
    "Security": "Security Ops",
    "HR": "People Ops",
    "Finance": "Finance Ops",
    "Facilities": "Facilities",
}
SLA = {"P1": 4, "P2": 8, "P3": 18, "P4": 45}
WARN = 0.75


class Desk:
    def __init__(self, store, now=None):
        self.s = store
        self.ts = store.tickets()
        self.ag = store.agents()
        self.h = store.hols()
        self.now = now or datetime.now().replace(second=0, microsecond=0)

    def get(self, tid):
        for t in self.ts:
            if t.id == tid.upper():
                return t
        raise KeyError(f"No ticket {tid}")

    def due(self, t):
        return add_bh(t.created, SLA[t.priority], self.h)

    def used(self, t):
        end = t.resolved_at or self.now
        return bh_between(t.created, end, self.h) / SLA[t.priority]

    def state(self, t):
        if t.status == "resolved":
            return "MET" if t.resolved_at <= self.due(t) else "BREACHED"
        u = self.used(t)
        if u >= 1:
            return "BREACHED"
        if u >= WARN:
            return "AT RISK"
        return "OK"

    def load(self, aid):
        return sum(1 for t in self.ts if t.assignee == aid and t.status != "resolved")

    def _pick(self, cat):
        c = [a for a in self.ag if a.team == TEAM[cat] and self.load(a.id) < a.max_open]
        if not c:
            return None
        return min(c, key=lambda a: (self.load(a.id), a.name)).id

    def new(self, title, cat, pri, req):
        if cat not in TEAM:
            raise ValueError(f"Unknown category {cat}. Use one of: {', '.join(TEAM)}")
        if pri not in SLA:
            raise ValueError(f"Unknown priority {pri}. Use one of: {', '.join(SLA)}")
        n = max([int(t.id.split("-")[1]) for t in self.ts] + [1000]) + 1
        t = Ticket(id=f"INC-{n}", title=title, category=cat, priority=pri, requester=req, created=self.now)
        t.assignee = self._pick(cat)
        if t.assignee:
            t.status = "in_progress"
        self.ts.append(t)
        self.s.save(self.ts)
        return t

    def assign(self, tid, aid):
        t = self.get(tid)
        if aid not in [a.id for a in self.ag]:
            raise ValueError(f"No agent {aid}")
        t.assignee = aid
        if t.status == "open":
            t.status = "in_progress"
        self.s.save(self.ts)
        return t

    def resolve(self, tid, note=""):
        t = self.get(tid)
        if t.status == "resolved":
            raise ValueError(f"{t.id} is already resolved")
        t.status = "resolved"
        t.resolved_at = self.now
        if note:
            t.notes.append(note)
        self.s.save(self.ts)
        return t

    def lead(self, team):
        for a in self.ag:
            if a.team == team and a.lead:
                return a.id
        return None

    def to_escalate(self):
        r = [t for t in self.ts
             if t.status != "resolved" and not t.escalated and self.state(t) in ("AT RISK", "BREACHED")]
        return sorted(r, key=self.due)

    def escalate(self, dry_run=False):
        done = []
        for t in self.to_escalate():
            old = t.assignee
            new = self.lead(TEAM[t.category]) or old
            done.append((t, self.state(t), old, new))
            if dry_run:
                continue
            note = (f"Escalated on {self.now:%Y-%m-%d %H:%M} (SLA {self.state(t)}, "
                    f"{self.used(t):.0%} used); was assigned to {old or 'nobody'}")
            t.assignee = new
            t.status = "in_progress"
            t.notes.append(note)
            t.escalated = True
        if done and not dry_run:
            self.s.save(self.ts)
        return done

    def breaches(self):
        r = [t for t in self.ts if t.status != "resolved" and self.state(t) == "BREACHED"]
        return sorted(r, key=self.due)

    def stats(self):
        out = {}
        for team in TEAM.values():
            mine = [t for t in self.ts if TEAM[t.category] == team]
            done = [t for t in mine if t.status == "resolved"]
            met = [t for t in done if self.state(t) == "MET"]
            out[team] = {
                "open": len(mine) - len(done),
                "breached": sum(1 for t in mine if t.status != "resolved" and self.state(t) == "BREACHED"),
                "resolved": len(done),
                "met_pct": round(100 * len(met) / len(done)) if done else None,
            }
        return out
