"""The examples in specs/policy.md, section 7, run through claims.process()."""
import pytest

from kavericlaims import claims

#  (example, grade, city, category, amount, currency, qty, receipt, status, expected reimbursable, expected flags)
EXAMPLES = [
    (1, "G2", "Bengaluru", "MEAL", 650.00, "INR", 1, True, "approved", 650.00, []),
    (2, "G2", "Mysuru", "MEAL", 650.00, "INR", 1, True, "approved", 600.00, ["OVER_LIMIT"]),
    (3, "G3", "Mysuru", "MEAL", 750.00, "INR", 1, True, "approved", 750.00, []),
    (4, "G1", "Pune", "MEAL", 499.99, "INR", 1, False, "approved", 499.99, []),
    (5, "G1", "Pune", "MEAL", 500.00, "INR", 1, False, "approved", 0.00, ["NO_RECEIPT"]),
    (7, "G2", "Dubai", "MEAL", 100.00, "AED", 1, True, "approved", 800.00, ["OVER_LIMIT"]),
    (8, "G3", "Hyderabad", "HOTEL", 13000.00, "INR", 2, True, "approved", 12000.00, ["OVER_LIMIT"]),
    (10, "G2", "Mumbai", "TRAVEL", 4800.00, "INR", 1, True, "approved", 4800.00, []),
    (11, "G1", "Mangaluru", "TRAVEL", 820.00, "INR", 1, False, "approved", 0.00, ["NO_RECEIPT"]),
    (12, "G3", "Chennai", "OTHER", 2450.00, "INR", 1, True, "approved", 2000.00, ["OVER_LIMIT"]),
]


@pytest.mark.parametrize("n, grade, city, cat, amount, cur, qty, receipt, status, reimb, flags", EXAMPLES,
                         ids=[f"example-{e[0]}" for e in EXAMPLES])
def test_single_claim_examples(rates, employees, make_claim, n, grade, city, cat, amount, cur, qty, receipt, status, reimb, flags):
    claim = make_claim("C-1", grade, cat, amount, city=city, currency=cur, qty=qty,
                       receipt="R.jpg" if receipt else "", status=status)
    [result] = claims.process([claim], employees, "2026-11")
    assert result["reimb"] == pytest.approx(reimb)
    assert result["flags"] == flags


def test_example_6_two_meals_share_the_daily_limit(rates, employees, make_claim):
    first = make_claim("C-1", "G2", "MEAL", 450.00)
    second = make_claim("C-2", "G2", "MEAL", 500.00)
    results = claims.process([second, first], employees, "2026-11")   # order in the file doesn't matter
    assert [r["reimb"] for r in results] == [450.00, 350.00]
    assert results[1]["flags"] == ["OVER_LIMIT"]


def test_example_9_internet_limit_is_per_month(rates, employees, make_claim):
    first = make_claim("C-1", "G1", "INTERNET", 700.00, city="Mysuru", date="2026-11-03")
    second = make_claim("C-2", "G1", "INTERNET", 600.00, city="Mysuru", date="2026-11-25")
    results = claims.process([first, second], employees, "2026-11")
    assert [r["reimb"] for r in results] == [700.00, 300.00]


def test_example_13_rejected_claim_is_ignored(rates, employees, make_claim):
    rejected = make_claim("C-1", "G2", "MEAL", 300.00, status="rejected")
    assert claims.process([rejected], employees, "2026-11") == []


def test_rejected_claim_does_not_use_up_the_daily_limit(rates, employees, make_claim):
    rejected = make_claim("C-1", "G2", "MEAL", 700.00, status="rejected")
    later = make_claim("C-2", "G2", "MEAL", 700.00)
    [result] = claims.process([rejected, later], employees, "2026-11")
    assert result["reimb"] == 700.00


def test_claim_without_receipt_does_not_use_up_the_daily_limit(rates, employees, make_claim):
    no_receipt = make_claim("C-1", "G2", "MEAL", 600.00, receipt="")
    later = make_claim("C-2", "G2", "MEAL", 800.00)
    results = claims.process([no_receipt, later], employees, "2026-11")
    assert [r["reimb"] for r in results] == [0.00, 800.00]
