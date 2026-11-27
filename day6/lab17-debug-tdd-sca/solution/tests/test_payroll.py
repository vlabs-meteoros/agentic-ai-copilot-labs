"""Tests for the payroll export (specs/payroll.md)."""

from kavericlaims import cli, payroll
from kavericlaims.models import Employee

EMPS = {
    "E01": Employee("E01", "Ananya Rao", "G2", "Bengaluru", "E09", "CC-ENG"),
    "E02": Employee("E02", "Rahul Menon", "G1", "Bengaluru", "E09", "CC-ENG"),
}


def result(emp, reimb, status="approved"):
    return {"emp": emp, "reimb": reimb, "status": status}


def test_only_approved_claims_are_paid():
    rows = payroll.build_payroll([result("E01", 100.0), result("E01", 50.0, "submitted"), result("E02", 70.0, "rejected")], EMPS)
    assert rows == [["E01", "Ananya Rao", "CC-ENG", "1", "100.00"]]


def test_employee_with_nothing_reimbursed_gets_no_row():
    rows = payroll.build_payroll([result("E01", 0.0), result("E02", 12.5)], EMPS)
    assert [row[0] for row in rows] == ["E02"]


def test_amount_has_two_decimals_and_no_thousands_separator():
    rows = payroll.build_payroll([result("E01", 12000.0), result("E01", 380.0)], EMPS)
    assert rows[0][3:] == ["2", "12380.00"]


def test_november_payroll_matches_the_spec(capsys, tmp_path):
    out_file = tmp_path / "payroll.csv"
    assert cli.main(["payroll", "--month", "2026-11", "--out", str(out_file)]) == 0
    printed = capsys.readouterr().out
    assert "Payroll 2026-11: 8 employees, 40,060.00 INR" in printed
    lines = out_file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "emp_id,name,cost_centre,claims,amount"
    assert lines[1] == "E01,Ananya Rao,CC-ENG,2,800.00"
    assert lines[4] == "E07,Nikhil Joshi,CC-OPS,2,12380.00"
    assert len(lines) == 9
