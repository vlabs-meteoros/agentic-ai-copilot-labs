# cli.py - command line for KaveriClaims
import argparse

from . import bench
from . import claims
from . import currency
from . import report
from . import storage


def main(argv=None):
    p = argparse.ArgumentParser(prog="kavericlaims", description="Kaveri Systems expense claims")
    p.add_argument("--data", help="folder with the data files (default: the data folder next to the package)")
    sub = p.add_subparsers(dest="cmd")
    r = sub.add_parser("report", help="monthly report for Finance Ops")
    r.add_argument("--month", required=True, help="YYYY-MM, for example 2026-11")
    r.add_argument("--out", help="also write the report to this file")
    s = sub.add_parser("show", help="one claim, and the rules that were applied to it")
    s.add_argument("claim_id")
    s.add_argument("--month", required=True, help="YYYY-MM")
    b = sub.add_parser("bench", help="time the report on a big generated month")
    b.add_argument("--claims", type=int, default=8000)
    b.add_argument("--employees", type=int, default=500)
    a = p.parse_args(argv)

    if a.cmd == None:
        p.print_help()
        return 1
    if a.cmd == "bench":
        return bench.run(a.claims, a.employees)

    emps = storage.load_employees(a.data)
    currency.set_rates(storage.load_rates(a.data))
    rows = storage.load_claims(a.month, a.data)
    res = claims.process(rows, emps, a.month)

    if a.cmd == "report":
        text = report.build_report(res, emps, a.month)
        print(text, end="")
        if a.out:
            f = open(a.out, "w", encoding="utf-8", newline="\n")
            f.write(text)
            f.close()
            print("Report written to " + a.out)
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
            if c[0] == cid:
                print("%s is %s, so it is not processed." % (cid, c[9]))
                return 0
        print("No claim %s in %s" % (cid, a.month))
        return 1
    return 1
