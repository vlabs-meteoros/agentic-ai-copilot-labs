# claims.py - work out how much of each claim is reimbursed
from . import currency
from . import policy


def process(claims, emps, month):
    res = []
    meal_used = {}
    net_used = {}
    claims = sorted(claims, key=lambda x: x[0])
    for c in claims:
        if c[9] == "rejected":
            continue
        if not c[1] in emps:
            print("WARNING: unknown employee " + c[1] + " on claim " + c[0])
            continue
        e = emps[c[1]]
        amt = currency.to_inr(c[5], c[6], month)
        t = policy.get_tier(c[4], c[6])
        r = {"id": c[0], "emp": c[1], "name": e[0], "cat": c[3], "date": c[2], "status": c[9],
             "claimed": amt, "reimb": 0.0, "flags": [], "notes": []}
        if c[6] != "INR":
            r["notes"].append("%.2f %s converted at %.2f = %.2f INR" % (c[5], c[6], currency.RATES[month][c[6]], amt))
        if policy.needs_receipt(amt) and c[8] == "":
            r["flags"].append("NO_RECEIPT")
            r["notes"].append("No receipt for a claim over 500.00: nothing reimbursed")
            res.append(r)
            continue
        lim = policy.get_limit(c[3], e[1], t)
        if c[3] == "MEAL":
            k = c[1] + "|" + c[2]
            if k in meal_used:
                u = meal_used[k]
            else:
                u = 0.0
            left = lim - u
            if left < 0:
                left = 0
            if amt > left:
                r["reimb"] = left
                r["flags"].append("OVER_LIMIT")
            else:
                r["reimb"] = amt
            meal_used[k] = u + r["reimb"]
            r["notes"].append("MEAL limit for %s in tier %d: %.2f per day, %.2f already used that day" % (e[1], t, lim, u))
        elif c[3] == "HOTEL":
            lim2 = lim * c[7]
            if amt > lim2:
                r["reimb"] = lim2
                r["flags"].append("OVER_LIMIT")
            else:
                r["reimb"] = amt
            r["notes"].append("HOTEL limit for %s in tier %d: %.2f per night x %d night(s)" % (e[1], t, lim, c[7]))
        elif c[3] == "INTERNET":
            k = c[1]
            if k in net_used:
                u = net_used[k]
            else:
                u = 0.0
            left = lim - u
            if left < 0:
                left = 0
            if amt > left:
                r["reimb"] = left
                r["flags"].append("OVER_LIMIT")
            else:
                r["reimb"] = amt
            net_used[k] = u + r["reimb"]
            r["notes"].append("INTERNET limit: %.2f per month, %.2f already used that month" % (lim, u))
        elif c[3] == "OTHER":
            if amt > lim:
                r["reimb"] = lim
                r["flags"].append("OVER_LIMIT")
            else:
                r["reimb"] = amt
            r["notes"].append("OTHER limit: %.2f per claim" % lim)
        elif c[3] == "TRAVEL":
            r["reimb"] = amt
            r["notes"].append("TRAVEL has no limit")
        else:
            r["flags"].append("UNKNOWN_CATEGORY")
            r["notes"].append("Unknown category " + c[3] + ": nothing reimbursed")
        r["reimb"] = round(r["reimb"], 2)
        res.append(r)
    return res
