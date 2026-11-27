"""Work out how much of each claim is reimbursed."""
from . import currency
from . import policy
from .models import Claim, Employee


def process(claims: list[Claim], emps: dict[str, Employee], month: str) -> list[dict]:
    """Apply the policy to a month of claims; return one result dict per claim that isn't rejected."""
    used: dict[str, float] = {}  # shared limits already used: "MEAL|emp|date" or "INTERNET|emp" -> INR
    results = []
    for claim in sorted(claims, key=lambda c: c.claim_id):
        if claim.status == "rejected":
            continue
        if claim.emp_id not in emps:
            print(f"WARNING: unknown employee {claim.emp_id} on claim {claim.claim_id}")
            continue
        results.append(_process_claim(claim, emps[claim.emp_id], month, used))
    return results


def _process_claim(claim: Claim, emp: Employee, month: str, used: dict[str, float]) -> dict:
    """Return the result dict for one claim, updating the shared limits in used."""
    amount = currency.to_inr(claim.amount, claim.currency, month)
    result = _new_result(claim, emp, amount)
    if claim.currency != "INR":
        rate = currency.RATES[month][claim.currency]
        result["notes"].append(f"{claim.amount:.2f} {claim.currency} converted at {rate:.2f} = {amount:.2f} INR")
    if policy.needs_receipt(amount) and claim.receipt == "":
        result["flags"].append("NO_RECEIPT")
        result["notes"].append("No receipt for a claim of 500.00 or more: nothing reimbursed")
        return result
    _apply_limit(result, claim, emp, amount, used)
    result["reimb"] = round(result["reimb"], 2)
    return result


def _new_result(claim: Claim, emp: Employee, amount: float) -> dict:
    """Return a result dict for a claim with nothing reimbursed yet."""
    return {"id": claim.claim_id, "emp": claim.emp_id, "name": emp.name, "cat": claim.category, "date": claim.date,
            "status": claim.status, "claimed": amount, "reimb": 0.0, "flags": [], "notes": []}


def _apply_limit(result: dict, claim: Claim, emp: Employee, amount: float, used: dict[str, float]) -> None:
    """Set result["reimb"], flags and notes for the claim's category limit."""
    tier = policy.get_tier(claim.city, claim.currency)
    limit = policy.get_limit(claim.category, emp.grade, tier)
    if claim.category == "MEAL":
        already = _cap_shared(result, amount, limit, used, f"MEAL|{claim.emp_id}|{claim.date}")
        result["notes"].append(f"MEAL limit for {emp.grade} in tier {tier}: {limit:.2f} per day, "
                               f"{already:.2f} already used that day")
    elif claim.category == "INTERNET":
        already = _cap_shared(result, amount, limit, used, f"INTERNET|{claim.emp_id}")
        result["notes"].append(f"INTERNET limit: {limit:.2f} per month, {already:.2f} already used that month")
    elif claim.category == "HOTEL":
        _cap(result, amount, limit * claim.qty)
        result["notes"].append(f"HOTEL limit for {emp.grade} in tier {tier}: {limit:.2f} per night x {claim.qty} night(s)")
    elif claim.category == "OTHER":
        _cap(result, amount, limit)
        result["notes"].append(f"OTHER limit: {limit:.2f} per claim")
    elif claim.category == "TRAVEL":
        result["reimb"] = amount
        result["notes"].append("TRAVEL has no limit")
    else:
        result["flags"].append("UNKNOWN_CATEGORY")
        result["notes"].append(f"Unknown category {claim.category}: nothing reimbursed")


def _cap(result: dict, amount: float, limit: float) -> None:
    """Reimburse amount up to limit; flag OVER_LIMIT if anything is cut."""
    if amount > limit:
        result["reimb"] = limit
        result["flags"].append("OVER_LIMIT")
    else:
        result["reimb"] = amount


def _cap_shared(result: dict, amount: float, limit: float, used: dict[str, float], key: str) -> float:
    """Cap amount by what is left of a shared limit, record what this claim uses, and return what was used before."""
    already = used.get(key, 0.0)
    _cap(result, amount, max(limit - already, 0))
    used[key] = already + result["reimb"]
    return already
