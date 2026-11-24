# fx_rates_py2.py - add a month of exchange rates to ../data/fx_rates.json
# from the bank's weekly rate sheet (buy and sell rates).
#
# Finance Ops, 2014. PYTHON 2.7 ONLY. Nobody has run it since the 2019 laptop refresh.
#
# usage: python fx_rates_py2.py bank_rates_2026-12.csv 2026-12

import sys
import json


def main():
    if len(sys.argv) < 3:
        print "usage: python fx_rates_py2.py <bank csv> <YYYY-MM>"
        sys.exit(1)
    fn = sys.argv[1]
    month = sys.argv[2]

    try:
        f = open(fn)
    except IOError, e:
        print "cannot open", fn, e
        sys.exit(1)

    totals = {}
    counts = {}
    for line in f.readlines()[1:]:
        date, cur, buy, sell = line.strip().split(",")
        mid = (float(buy) + float(sell)) / 2
        if totals.has_key(cur):
            totals[cur] = totals[cur] + mid
            counts[cur] = counts[cur] + 1
        else:
            totals[cur] = mid
            counts[cur] = 1
    f.close()

    rates = {}
    for cur, tot in totals.iteritems():
        rates[cur] = round(tot / counts[cur], 2)

    print "Average mid rates for", month
    print json.dumps({month: rates}, sort_keys=True)

    answer = raw_input("Add them to ../data/fx_rates.json? [y/N] ")
    if answer.lower() == "y":
        all_rates = json.load(open("../data/fx_rates.json"))
        all_rates[month] = rates
        json.dump(all_rates, open("../data/fx_rates.json", "w"), indent=2, sort_keys=True)
        print "Saved."


main()
