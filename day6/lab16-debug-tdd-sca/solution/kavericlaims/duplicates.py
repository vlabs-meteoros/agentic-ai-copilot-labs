"""Possible duplicate claims (specs/duplicates.md)."""
from datetime import date
from itertools import combinations

from .models import Claim

MAX_DAYS_APART = 3


def is_possible_duplicate(a: Claim, b: Claim) -> bool:
    """Return True if two claims match on employee, category, amount and currency and are at most 3 days apart."""
    if "rejected" in (a.status, b.status):
        return False
    same = (a.emp_id, a.category, a.amount, a.currency) == (b.emp_id, b.category, b.amount, b.currency)
    days_apart = abs((date.fromisoformat(a.date) - date.fromisoformat(b.date)).days)
    return same and days_apart <= MAX_DAYS_APART


def find_duplicates(claims: list[Claim]) -> list[tuple[Claim, Claim]]:
    """Return every possible duplicate pair as (smaller claim ID, larger claim ID), sorted by the two IDs."""
    ordered = sorted(claims, key=lambda c: c.claim_id)
    return [(a, b) for a, b in combinations(ordered, 2) if is_possible_duplicate(a, b)]


def format_pairs(pairs: list[tuple[Claim, Claim]], month: str) -> str:
    """Return the text the duplicates command prints."""
    if not pairs:
        return f"No possible duplicates in {month}\n"
    lines = [f"{a.claim_id}  {b.claim_id}  {a.emp_id}  {a.category:<8} {a.amount:>9.2f} {a.currency}  {a.date} / {b.date}"
             for a, b in pairs]
    lines.append(f"{len(pairs)} possible duplicate pair(s) in {month}")
    return "\n".join(lines) + "\n"
