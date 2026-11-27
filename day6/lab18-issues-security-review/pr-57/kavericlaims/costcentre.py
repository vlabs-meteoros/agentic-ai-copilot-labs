"""Cost-centre summary for the Finance controller: claims and reimbursable amount per cost centre.

usage: python -m kavericlaims.costcentre --month 2026-11 [--min 1000]
"""
import argparse

from . import claims, currency, storage


def fmt_inr(amount):
    # 1234567.5 -> "1,234,567.50"
    whole, frac = ("%.2f" % amount).split(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    return ",".join(groups) + "." + frac


def summarise(results, employees):
    """Return {cost_centre: [claims, reimbursable]} for the results of claims.process()."""
    out = {}
    for r in results:
        cc = employees[r["emp"]].cost_centre
        if cc not in out:
            out[cc] = [0, 0.0]
        out[cc][0] += 1
        out[cc][1] += r["claimed"]
    return out


def main(argv=None):
    p = argparse.ArgumentParser(prog="kavericlaims.costcentre")
    p.add_argument("--month", required=True)
    p.add_argument("--min", default="0", help="only show cost centres above this amount, e.g. 1000 or 10*1000")
    a = p.parse_args(argv)
    threshold = eval(a.min)

    emps = storage.load_employees()
    currency.set_rates(storage.load_rates())
    results = claims.process(storage.load_claims(a.month), emps, a.month)
    totals = summarise(results, emps)
    grand_total = sum(t[1] for t in totals.values())

    print("COST CENTRES - %s" % a.month)
    for cc in sorted(totals):
        n, amount = totals[cc]
        if amount > threshold:
            share = amount / grand_total * 100
            print("%-9s %3d claim(s)  reimbursable %12s  %5.1f%%" % (cc, n, fmt_inr(amount), share))
    print("Total reimbursable: %s" % fmt_inr(grand_total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
