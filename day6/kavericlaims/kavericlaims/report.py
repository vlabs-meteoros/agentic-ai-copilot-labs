"""The monthly claims report for Finance Ops."""

WIDTH = 78
LINE_FORMAT = "%-7s %-4s %-16s %-9s %12s %12s  %s"
TOTAL_FORMAT = "%-4s %-16s %3d claim(s)  claimed %12s  reimbursable %12s"


def commas(amount: float) -> str:
    """Format an amount with thousands separators and 2 decimals: 1234567.5 -> '1,234,567.50'."""
    return f"{amount:,.2f}"


def build_report(res: list[dict], emps: dict, month: str) -> str:
    """Return the report text for the results of claims.process()."""
    lines = [
        f"KAVERI SYSTEMS - EXPENSE CLAIMS REPORT - {month}",
        "=" * WIDTH,
        LINE_FORMAT % ("CLAIM", "EMP", "NAME", "CATEGORY", "CLAIMED", "REIMBURSE", "FLAGS"),
    ]
    totals: dict[str, list] = {}  # emp_id -> [claims, claimed, reimbursable]
    for r in res:
        emp = emps.get(r["emp"])
        name = emp.name if emp else ""
        line = LINE_FORMAT % (r["id"], r["emp"], name, r["cat"], commas(r["claimed"]), commas(r["reimb"]), " ".join(r["flags"]))
        lines.append(line.rstrip())
        t = totals.setdefault(r["emp"], [0, 0.0, 0.0])
        t[0] += 1
        t[1] += r["claimed"]
        t[2] += r["reimb"]

    lines.append("-" * WIDTH)
    lines.append("TOTALS BY EMPLOYEE (highest reimbursement first)")
    rows = [(emp_id, emps[emp_id].name, *t) for emp_id, t in totals.items() if emp_id in emps]
    for emp_id, name, n, claimed, reimb in sorted(rows, key=lambda row: (-row[4], row[0])):
        lines.append(TOTAL_FORMAT % (emp_id, name, n, commas(claimed), commas(reimb)))

    lines.append("-" * WIDTH)
    total_claimed = sum(r["claimed"] for r in res)
    total_reimb = sum(r["reimb"] for r in res)
    flagged = sum(1 for r in res if r["flags"])
    lines.append(f"Claims: {len(res)}   Flagged: {flagged}")
    lines.append(f"Claimed: {commas(total_claimed)}   Reimbursable: {commas(total_reimb)}"
                 f"   Not reimbursed: {commas(total_claimed - total_reimb)}")
    return "\n".join(lines) + "\n"
