# team.py - team summary for managers
# added in 2024 by the Ops team ("managers keep asking Finance what their team spent")


def fmt(x: float) -> str:
    """Format an amount with thousands separators and 2 decimals: 12380 -> '12,380.00'."""
    return f"{x:,.2f}"


def reports_of(emps: dict, manager: str, found: list[str] | None = None) -> list[str]:
    """Return everyone who reports to manager, directly or through someone else."""
    if found is None:
        found = []
    for e in emps.values():
        if e.manager == manager:
            found.append(e.emp_id)
            reports_of(emps, e.emp_id, found)
    return found


def team_summary(res: list[dict], emps: dict, managers: list[str], month: str) -> str:
    """Return the team summary text for each manager in managers."""
    for m in managers:
        if m not in emps:
            raise ValueError(f"No employee {m}: check the --manager value")
    lines = []
    for m in managers:
        boss = emps[m]
        ids = reports_of(emps, m)
        lines.append("TEAM OF %s %s - %s (%d people)" % (m, boss.name, month, len(ids)))
        total = 0.0
        for i in sorted(ids):
            n = 0
            amount = 0.0
            for r in res:
                if r["emp"] == i:
                    n = n + 1
                    amount = amount + r["reimb"]
            lines.append("  %-4s %-16s %3d claim(s)  reimbursable %12s" % (i, emps[i].name, n, fmt(amount)))
            total = total + amount
        lines.append("  Team total: " + fmt(total))
        lines.append("")
    return "\n".join(lines)
