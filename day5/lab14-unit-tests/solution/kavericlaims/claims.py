"""Work out how much of each claim is reimbursed."""
from . import currency
from . import policy


def process(claims, emps, month):
    """Apply the policy to a month of claims; return one result dict per claim that isn't rejected."""
    res = []
    meal_used = {}
    net_used = {}
    claims = sorted(claims, key=lambda x: x.claim_id)
    for c in claims:
        if c.status == "rejected":
            continue
        if not c.emp_id in emps:
            print("WARNING: unknown employee " + c.emp_id + " on claim " + c.claim_id)
            continue
        e = emps[c.emp_id]
        amt = currency.to_inr(c.amount, c.currency, month)
        t = policy.get_tier(c.city, c.currency)
        r = {"id": c.claim_id, "emp": c.emp_id, "name": e.name, "cat": c.category, "date": c.date, "status": c.status,
             "claimed": amt, "reimb": 0.0, "flags": [], "notes": []}
        if c.currency != "INR":
            r["notes"].append("%.2f %s converted at %.2f = %.2f INR" % (c.amount, c.currency, currency.RATES[month][c.currency], amt))
        if policy.needs_receipt(amt) and c.receipt == "":
            r["flags"].append("NO_RECEIPT")
            r["notes"].append("No receipt for a claim of 500.00 or more: nothing reimbursed")
            res.append(r)
            continue
        lim = policy.get_limit(c.category, e.grade, t)
        if c.category == "MEAL":
            k = c.emp_id + "|" + c.date
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
            r["notes"].append("MEAL limit for %s in tier %d: %.2f per day, %.2f already used that day" % (e.grade, t, lim, u))
        elif c.category == "HOTEL":
            lim2 = lim * c.qty
            if amt > lim2:
                r["reimb"] = lim2
                r["flags"].append("OVER_LIMIT")
            else:
                r["reimb"] = amt
            r["notes"].append("HOTEL limit for %s in tier %d: %.2f per night x %d night(s)" % (e.grade, t, lim, c.qty))
        elif c.category == "INTERNET":
            k = c.emp_id
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
        elif c.category == "OTHER":
            if amt > lim:
                r["reimb"] = lim
                r["flags"].append("OVER_LIMIT")
            else:
                r["reimb"] = amt
            r["notes"].append("OTHER limit: %.2f per claim" % lim)
        elif c.category == "TRAVEL":
            r["reimb"] = amt
            r["notes"].append("TRAVEL has no limit")
        else:
            r["flags"].append("UNKNOWN_CATEGORY")
            r["notes"].append("Unknown category " + c.category + ": nothing reimbursed")
        r["reimb"] = round(r["reimb"], 2)
        res.append(r)
    return res
