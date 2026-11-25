# team.py - team summary for managers
# added in 2024 by the Ops team ("managers keep asking Finance what their team spent")


def fmt(x):
    # 12380 -> "12,380.00"
    return "{:,.2f}".format(x)


def reports_of(emps, manager, found=[]):
    # everyone who reports to manager, directly or through someone else
    for e in emps.values():
        if e.manager == manager:
            found.append(e.emp_id)
            reports_of(emps, e.emp_id, found)
    return found


def team_summary(res, emps, managers, month):
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
        lines.append("  Team total: " + total)
        lines.append("")
    return "\n".join(lines)
