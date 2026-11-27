# cli.py - command line for KaveriClaims
import argparse

from . import archive
from . import bench
from . import claims
from . import currency
from . import duplicates
from . import payroll
from . import report
from . import storage
from . import team


def main(argv=None):  # noqa: C901 - one branch per command; splitting it is optional in Lab 17 Task 6
    p = argparse.ArgumentParser(prog="kavericlaims", description="Kaveri Systems expense claims")
    p.add_argument("--data", help="folder with the data files (default: the data folder next to the package)")
    sub = p.add_subparsers(dest="cmd")
    r = sub.add_parser("report", help="monthly report for Finance Ops")
    r.add_argument("--month", required=True, help="YYYY-MM, for example 2026-11")
    r.add_argument("--out", help="also write the report to this file")
    s = sub.add_parser("show", help="one claim, and the rules that were applied to it")
    s.add_argument("claim_id")
    s.add_argument("--month", required=True, help="YYYY-MM")
    pr = sub.add_parser("payroll", help="CSV of approved reimbursements for payroll")
    pr.add_argument("--month", required=True, help="YYYY-MM")
    pr.add_argument("--out", help="also write the CSV to this file")
    t = sub.add_parser("team", help="what a manager's team (direct and indirect reports) claimed")
    t.add_argument("--manager", required=True, action="append", help="manager's emp_id; repeat for more managers")
    t.add_argument("--month", required=True, help="YYYY-MM")
    d = sub.add_parser("duplicates", help="pairs of claims that might be the same expense twice")
    d.add_argument("--month", required=True, help="YYYY-MM")
    ar = sub.add_parser("archive", help="the auditors' archive of processed months (archive/claims.db)")
    asub = ar.add_subparsers(dest="action", required=True)
    a1 = asub.add_parser("save", help="process a month and store it in the archive")
    a1.add_argument("--month", required=True, help="YYYY-MM")
    a2 = asub.add_parser("search", help="archived claims whose description contains TEXT")
    a2.add_argument("text")
    a2.add_argument("--month", required=True, help="YYYY-MM")
    a3 = asub.add_parser("export", help="write an archived month to archive/exports/NAME.csv")
    a3.add_argument("--month", required=True, help="YYYY-MM")
    a3.add_argument("--name", required=True, help="file name for the export, without .csv")
    a3.add_argument("--open", action="store_true", help="open the export in Notepad")
    b = sub.add_parser("bench", help="time the report on a big generated month")
    b.add_argument("--claims", type=int, default=8000)
    b.add_argument("--employees", type=int, default=500)
    a = p.parse_args(argv)

    if a.cmd is None:
        p.print_help()
        return 1
    if a.cmd == "bench":
        return bench.run(a.claims, a.employees)

    if a.cmd == "duplicates":
        rows = storage.load_claims(a.month, a.data)
        print(duplicates.format_pairs(duplicates.find_duplicates(rows), a.month), end="")
        return 0

    emps = storage.load_employees(a.data)
    currency.set_rates(storage.load_rates(a.data))
    rows = storage.load_claims(a.month, a.data)
    res = claims.process(rows, emps, a.month)

    if a.cmd == "team":
        try:
            print(team.team_summary(res, emps, a.manager, a.month))
        except ValueError as err:
            print(err)
            return 1
        return 0
    if a.cmd == "archive":
        if a.action == "save":
            n = archive.save_month(res, rows, a.month)
            print("Archived %d claims for %s" % (n, a.month))
        elif a.action == "search":
            found = archive.search(a.text, a.month)
            for row in found:
                print("%-7s %-4s %-16s %s  %-34s %12s" % (row[0], row[1], row[2], row[3], row[4], report.commas(row[5])))
            print("%d claim(s) found" % len(found))
        elif a.action == "export":
            path, checksum = archive.export_csv(a.month, a.name)
            print("Exported %s to %s (md5 %s)" % (a.month, path, checksum))
            if a.open:
                archive.open_export(path)
        return 0
    if a.cmd == "report":
        text = report.build_report(res, emps, a.month)
        print(text, end="")
        if a.out:
            with open(a.out, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print("Report written to " + a.out)
        return 0
    elif a.cmd == "payroll":
        rows_out = payroll.build_payroll(res, emps)
        text = payroll.to_csv(rows_out)
        print(text, end="")
        total = sum(float(row[4]) for row in rows_out)
        print("Payroll %s: %d employees, %s INR" % (a.month, len(rows_out), report.commas(total)))
        if a.out:
            with open(a.out, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            print("Payroll written to " + a.out)
        return 0
    elif a.cmd == "show":
        cid = a.claim_id.upper()
        for x in res:
            if x["id"] == cid:
                print("%s  %s %s  %s  %s  (%s)" % (x["id"], x["emp"], x["name"], x["cat"], x["date"], x["status"]))
                print("Claimed:      %12s INR" % report.commas(x["claimed"]))
                print("Reimbursable: %12s INR" % report.commas(x["reimb"]))
                if len(x["flags"]) > 0:
                    print("Flags:        " + " ".join(x["flags"]))
                else:
                    print("Flags:        -")
                print("Rules applied:")
                for n in x["notes"]:
                    print("  - " + n)
                return 0
        for c in rows:
            if c.claim_id == cid:
                print("%s is %s, so it is not processed." % (cid, c.status))
                return 0
        print("No claim %s in %s" % (cid, a.month))
        return 1
    return 1
