"""Shared pytest fixtures for the KaveriClaims tests."""
import shutil
from pathlib import Path

import pytest

from kavericlaims import currency
from kavericlaims.models import Claim, Employee

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def rates(monkeypatch):
    """November 2026 exchange rates, set for one test only (currency.RATES is global)."""
    r = {"2026-11": {"USD": 84.20, "AED": 22.93, "SGD": 64.90}}
    monkeypatch.setattr(currency, "RATES", r)
    return r


@pytest.fixture
def employees():
    """One employee per grade, in a tier 1 and a tier 2 city."""
    return {
        "G1": Employee("G1", "Grade One", "G1", "Pune", "", "CC-T"),
        "G2": Employee("G2", "Grade Two", "G2", "Bengaluru", "", "CC-T"),
        "G3": Employee("G3", "Grade Three", "G3", "Mysuru", "", "CC-T"),
        "G4": Employee("G4", "Grade Four", "G4", "Mumbai", "", "CC-T"),
    }


@pytest.fixture
def make_claim():
    """Factory for claims: make_claim("C-1", "G2", "MEAL", 650.0, city="Mysuru")."""
    def _make(claim_id, emp_id, category, amount, city="Bengaluru", currency="INR", qty=1,
              receipt="R.jpg", status="approved", date="2026-11-10"):
        return Claim(claim_id, emp_id, date, category, city, amount, currency, qty, receipt, status, "test")
    return _make


@pytest.fixture
def data_dir(tmp_path):
    """A temporary copy of data/, so a test can add or break files safely."""
    target = tmp_path / "data"
    shutil.copytree(DATA, target)
    return target
