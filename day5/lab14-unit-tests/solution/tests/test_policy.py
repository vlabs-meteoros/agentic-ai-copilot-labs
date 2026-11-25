"""Unit tests for kavericlaims.policy (first generated with Generate Tests, then corrected against specs/policy.md)."""
import pytest

from kavericlaims import policy


@pytest.mark.parametrize("city, currency, expected", [
    ("Bengaluru", "INR", 1),
    ("bengaluru", "INR", 1),
    ("Mysuru", "INR", 2),
    ("Mangaluru", "INR", 2),
    ("Dubai", "AED", 1),
    ("Mysuru", "USD", 1),
])
def test_get_tier(city, currency, expected):
    assert policy.get_tier(city, currency) == expected


@pytest.mark.parametrize("grade, tier1, tier2", [
    ("G1", 600, 450), ("G2", 800, 600), ("G3", 1000, 800), ("G4", 1500, 1200),
])
def test_meal_limits_match_table_a(grade, tier1, tier2):
    assert policy.get_limit("MEAL", grade, 1) == tier1
    assert policy.get_limit("MEAL", grade, 2) == tier2


@pytest.mark.parametrize("grade, tier1, tier2", [
    ("G1", 3000, 2000), ("G2", 4000, 3000), ("G3", 6000, 4500), ("G4", 9000, 7000),
])
def test_hotel_limits_match_table_b(grade, tier1, tier2):
    assert policy.get_limit("HOTEL", grade, 1) == tier1
    assert policy.get_limit("HOTEL", grade, 2) == tier2


def test_flat_limits():
    assert policy.get_limit("INTERNET", "G1", 2) == 1000
    assert policy.get_limit("OTHER", "G4", 1) == 2000
    assert policy.get_limit("TRAVEL", "G2", 1) == policy.NO_LIMIT


def test_unknown_category_or_grade_has_zero_limit():
    assert policy.get_limit("PARKING", "G2", 1) == 0
    assert policy.get_limit("MEAL", "G9", 1) == 0


@pytest.mark.parametrize("amount, expected", [
    (499.99, False),
    (500.00, True),   # "500 or more" needs a receipt
    (500.01, True),
    (0.0, False),
])
def test_needs_receipt_boundary(amount, expected):
    assert policy.needs_receipt(amount) is expected
