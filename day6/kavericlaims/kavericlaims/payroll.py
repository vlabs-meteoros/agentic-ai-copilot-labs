"""Payroll export: what each employee is paid for their approved claims (specs/payroll.md)."""
import csv
import io

HEADER = ["emp_id", "name", "cost_centre", "claims", "amount"]


def build_payroll(results: list[dict], employees: dict) -> list[list[str]]:
    """Return one row per employee with approved claims worth more than 0.00, sorted by emp_id."""
    totals: dict[str, list] = {}  # emp_id -> [approved claims, reimbursable]
    for r in results:
        if r["status"] != "approved":
            continue
        t = totals.setdefault(r["emp"], [0, 0.0])
        t[0] += 1
        t[1] += r["reimb"]
    rows = []
    for emp_id in sorted(totals):
        count, amount = totals[emp_id]
        if round(amount, 2) > 0 and emp_id in employees:
            emp = employees[emp_id]
            rows.append([emp_id, emp.name, emp.cost_centre, str(count), f"{amount:.2f}"])
    return rows


def to_csv(rows: list[list[str]]) -> str:
    """Return the rows as CSV text with the header row."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(HEADER)
    writer.writerows(rows)
    return out.getvalue()
