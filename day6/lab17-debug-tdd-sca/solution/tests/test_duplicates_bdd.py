"""Step definitions for tests/features/duplicates.feature (Lab 17, Task 5), with pytest-bdd."""
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from kavericlaims.duplicates import find_duplicates
from kavericlaims.models import Claim

scenarios("features/duplicates.feature")


@pytest.fixture
def claims():
    """The claims a scenario builds up."""
    return []


@given(parsers.parse("these claims by employee {emp}"))
def these_claims(claims, emp, datatable):
    header, *rows = datatable
    for row in rows:
        r = dict(zip(header, row, strict=True))
        claims.append(Claim(r["claim"], emp, r["date"], r["category"], "Bengaluru", float(r["amount"]),
                            r["currency"], 1, "R.jpg", r["status"], "bdd"))


@given(parsers.parse('claim "{claim_id}" was rejected'))
def claim_was_rejected(claims, claim_id):
    for c in claims:
        if c.claim_id == claim_id:
            c.status = "rejected"


@when(parsers.parse('{emp} also claims "{claim_id}" for {category} {amount:f} {currency} on {day}'))
def also_claims(claims, emp, claim_id, category, amount, currency, day):
    claims.append(Claim(claim_id, emp, day, category, "Bengaluru", amount, currency, 1, "R.jpg", "approved", "bdd"))


@then(parsers.parse('Finance Ops sees the pair "{first}" and "{second}"'))
def sees_the_pair(claims, first, second):
    assert [(a.claim_id, b.claim_id) for a, b in find_duplicates(claims)] == [(first, second)]


@then("Finance Ops sees no pairs")
def sees_no_pairs(claims):
    assert find_duplicates(claims) == []
