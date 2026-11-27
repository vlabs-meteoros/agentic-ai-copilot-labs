"""Tests for possible duplicate claims, written from the examples in specs/duplicates.md (Lab 17, Task 4)."""
import pytest

from kavericlaims import cli
from kavericlaims.duplicates import find_duplicates
from kavericlaims.models import Claim


def claim(claim_id, category="MEAL", amount=640.00, currency="INR", date="2026-09-02", emp="E01", status="approved"):
    return Claim(claim_id, emp, date, category, "Bengaluru", amount, currency, 1, "R.jpg", status, "test")


def ids(pairs):
    return [(a.claim_id, b.claim_id) for a, b in pairs]


@pytest.mark.parametrize("a, b, expected", [
    (claim("C-1", date="2026-09-02"), claim("C-2", date="2026-09-04"), [("C-1", "C-2")]),                        # 1
    (claim("C-1", "TRAVEL", 1450.0, date="2026-09-08"), claim("C-2", "TRAVEL", 1450.0, date="2026-09-11"),
     [("C-1", "C-2")]),                                                                                           # 2
    (claim("C-1", "TRAVEL", 1450.0, date="2026-09-08"), claim("C-2", "TRAVEL", 1450.0, date="2026-09-12"), []),  # 3
    (claim("C-1"), claim("C-2", emp="E02"), []),                                                                 # 4
    (claim("C-1"), claim("C-2", "OTHER"), []),                                                                   # 5
    (claim("C-1"), claim("C-2", amount=640.50), []),                                                             # 6
    (claim("C-1", amount=40.0, currency="USD"), claim("C-2", amount=40.0, currency="AED"), []),                  # 7
    (claim("C-1", status="rejected"), claim("C-2"), []),                                                         # 8
    (claim("C-1", "TRAVEL", 380.0, date="2026-09-29"), claim("C-2", "TRAVEL", 380.0, date="2026-10-01"),
     [("C-1", "C-2")]),                                                                                           # 9
    (claim("C-9", date="2026-09-04"), claim("C-3", date="2026-09-02"), [("C-3", "C-9")]),                        # 10
], ids=[f"example-{n}" for n in range(1, 11)])
def test_spec_examples(a, b, expected):
    assert ids(find_duplicates([a, b])) == expected


def test_three_matching_claims_give_three_pairs():
    claims = [claim("C-3"), claim("C-1"), claim("C-2")]
    assert ids(find_duplicates(claims)) == [("C-1", "C-2"), ("C-1", "C-3"), ("C-2", "C-3")]


def test_no_claims_no_pairs():
    assert find_duplicates([]) == []


def test_september_command_output(capsys):
    assert cli.main(["duplicates", "--month", "2026-09"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert [line.split()[:2] for line in out[:-1]] == [["C-0901", "C-0902"], ["C-0904", "C-0907"],
                                                       ["C-0905", "C-0908"], ["C-0910", "C-0911"]]
    assert out[-1] == "4 possible duplicate pair(s) in 2026-09"


def test_month_without_duplicates(capsys):
    cli.main(["duplicates", "--month", "2026-11"])
    assert capsys.readouterr().out == "No possible duplicates in 2026-11\n"
