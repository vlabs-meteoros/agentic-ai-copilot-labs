"""Tests for kavericlaims.storage."""
from kavericlaims import storage

HEADER = "claim_id,emp_id,date,category,city,amount,currency,qty,receipt,status,description\n"


def test_amount_with_thousands_separator_is_read(tmp_path):
    (tmp_path / "claims_2026-10.csv").write_text(
        HEADER + 'C-1005,E05,2026-10-16,OTHER,Mysuru,"1,250.00",INR,1,R-1005.pdf,approved,Printed brochures\n',
        encoding="utf-8")
    [claim] = storage.load_claims("2026-10", tmp_path)
    assert claim.amount == 1250.00
    assert claim.description == "Printed brochures"


def test_missing_month_returns_no_claims(tmp_path, capsys):
    assert storage.load_claims("2026-12", tmp_path) == []
    assert "No claims file for 2026-12" in capsys.readouterr().out


def test_missing_rates_file_gives_a_warning_and_no_rates(tmp_path, capsys):
    assert storage.load_rates(tmp_path) == {}
    assert "WARNING" in capsys.readouterr().out


def test_employees_are_loaded():
    emps = storage.load_employees()
    assert len(emps) == 12
    assert emps["E03"].grade == "G3"
    assert emps["E12"].manager == ""
