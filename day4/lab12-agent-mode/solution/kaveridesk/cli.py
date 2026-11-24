import argparse
import sys
from datetime import datetime
from pathlib import Path

from .service import TEAM, Desk
from .store import Store

DATA = Path(__file__).resolve().parent.parent / "data"


def _row(d, t):
    due = d.due(t).strftime("%d %b %H:%M")
    who = t.assignee or "-"
    return f"{t.id:<9} {t.priority:<3} {t.status:<12} {d.state(t):<9} {due:<13} {who:<6} {t.title[:40]}"


def _head():
    print(f"{'ID':<9} {'Pri':<3} {'Status':<12} {'SLA':<9} {'Due':<13} {'Agent':<6} Title")
    print("-" * 95)


def cmd_list(d, a):
    ts = [t for t in d.ts if a.all or t.status != "resolved"]
    if a.team:
        ts = [t for t in ts if TEAM[t.category].lower() == a.team.lower()]
    if a.priority:
        ts = [t for t in ts if t.priority == a.priority.upper()]
    _head()
    for t in sorted(ts, key=d.due):
        print(_row(d, t))
    print(f"\n{len(ts)} ticket(s)")


def cmd_show(d, a):
    t = d.get(a.id)
    print(f"{t.id}: {t.title}")
    print(f"  Category : {t.category} ({TEAM[t.category]})")
    print(f"  Priority : {t.priority}")
    print(f"  Requester: {t.requester}")
    print(f"  Assignee : {t.assignee or '-'}")
    print(f"  Status   : {t.status}")
    print(f"  Created  : {t.created:%a %d %b %Y %H:%M}")
    print(f"  Due      : {d.due(t):%a %d %b %Y %H:%M}")
    if t.resolved_at:
        print(f"  Resolved : {t.resolved_at:%a %d %b %Y %H:%M}")
    print(f"  SLA      : {d.state(t)} ({d.used(t):.0%} of business hours used)")
    if t.escalated:
        print("  Escalated: yes")
    for n in t.notes:
        print(f"  Note     : {n}")


def cmd_new(d, a):
    t = d.new(a.title, a.category, a.priority, a.requester)
    print(f"Created {t.id}, assigned to {t.assignee or 'nobody (team is full)'}, due {d.due(t):%a %d %b %H:%M}")


def cmd_assign(d, a):
    t = d.assign(a.id, a.agent)
    print(f"{t.id} assigned to {t.assignee}")


def cmd_resolve(d, a):
    t = d.resolve(a.id, a.note)
    print(f"{t.id} resolved: SLA {d.state(t)}")


def cmd_breaches(d, a):
    b = d.breaches()
    if not b:
        print("No open tickets have breached their SLA.")
        return
    _head()
    for t in b:
        print(_row(d, t))
    print(f"\n{len(b)} breached ticket(s)")


def cmd_escalate(d, a):
    done = d.escalate(dry_run=a.dry_run)
    if not done:
        print("Nothing to escalate.")
        return
    for t, state, old, new in done:
        print(f"{t.id:<9} {state:<9} {old or '-'} -> {new or '-'}")
    print(f"{len(done)} ticket(s) {'would be escalated' if a.dry_run else 'escalated'}")


def cmd_stats(d, a):
    print(f"{'Team':<14} {'Open':>5} {'Breached':>9} {'Resolved':>9} {'SLA met':>8}")
    print("-" * 50)
    for team, s in d.stats().items():
        pct = "-" if s["met_pct"] is None else f"{s['met_pct']}%"
        print(f"{team:<14} {s['open']:>5} {s['breached']:>9} {s['resolved']:>9} {pct:>8}")


def build():
    p = argparse.ArgumentParser(prog="kaveridesk")
    p.add_argument("--data", default=str(DATA))
    p.add_argument("--now", help='pretend the time is "YYYY-MM-DD HH:MM"')
    sub = p.add_subparsers(dest="cmd", required=True)

    x = sub.add_parser("list")
    x.add_argument("--team")
    x.add_argument("--all", action="store_true")
    x.add_argument("--priority", choices=["P1", "P2", "P3", "P4"], type=str.upper)
    x.set_defaults(fn=cmd_list)

    x = sub.add_parser("show")
    x.add_argument("id")
    x.set_defaults(fn=cmd_show)

    x = sub.add_parser("new")
    x.add_argument("title")
    x.add_argument("--category", required=True)
    x.add_argument("--priority", default="P3")
    x.add_argument("--requester", required=True)
    x.set_defaults(fn=cmd_new)

    x = sub.add_parser("assign")
    x.add_argument("id")
    x.add_argument("agent")
    x.set_defaults(fn=cmd_assign)

    x = sub.add_parser("resolve")
    x.add_argument("id")
    x.add_argument("--note", default="")
    x.set_defaults(fn=cmd_resolve)

    sub.add_parser("breaches").set_defaults(fn=cmd_breaches)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)

    x = sub.add_parser("escalate")
    x.add_argument("--dry-run", action="store_true")
    x.set_defaults(fn=cmd_escalate)
    return p


def main(argv=None):
    a = build().parse_args(argv)
    now = datetime.strptime(a.now, "%Y-%m-%d %H:%M") if a.now else None
    try:
        a.fn(Desk(Store(a.data), now), a)
    except (KeyError, ValueError) as e:
        print(f"Error: {e.args[0]}", file=sys.stderr)
        return 1
    return 0
