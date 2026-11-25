"""js/policy_cases.json must match the Python policy, so the JavaScript port (Lab 16) is tested against the real rules."""
import json
from pathlib import Path

from kavericlaims import policy

CASES = json.loads((Path(__file__).resolve().parent.parent / "js" / "policy_cases.json").read_text(encoding="utf-8"))


def test_tier_cases_match_python():
    for c in CASES["get_tier"]:
        assert policy.get_tier(c["city"], c["currency"]) == c["expected"], c


def test_limit_cases_match_python():
    for c in CASES["get_limit"]:
        assert policy.get_limit(c["category"], c["grade"], c["tier"]) == c["expected"], c


def test_receipt_cases_match_python():
    for c in CASES["needs_receipt"]:
        assert policy.needs_receipt(c["amount"]) == c["expected"], c
