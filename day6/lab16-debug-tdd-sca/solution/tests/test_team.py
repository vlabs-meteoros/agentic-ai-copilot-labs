"""Tests for the team summary (Lab 17, Tasks 1-3: each bug gets a test that fails before the fix)."""
import pytest

from kavericlaims import cli, team
from kavericlaims.models import Employee

EMPS = {
    "B1": Employee("B1", "Big Boss", "G4", "Bengaluru", "", "CC-X"),
    "M1": Employee("M1", "Manager One", "G3", "Bengaluru", "B1", "CC-X"),
    "M2": Employee("M2", "Manager Two", "G3", "Mysuru", "B1", "CC-X"),
    "A1": Employee("A1", "Ann", "G1", "Bengaluru", "M1", "CC-X"),
    "A2": Employee("A2", "Bob", "G1", "Mysuru", "M2", "CC-X"),
}


def test_team_total_is_printed_with_thousands_separator():
    res = [{"emp": "A1", "reimb": 1200.0}, {"emp": "A1", "reimb": 50.5}]
    text = team.team_summary(res, EMPS, ["M1"], "2026-11")
    assert "Team total: 1,250.50" in text


def test_unknown_manager_gives_a_clear_error_not_a_key_error():
    with pytest.raises(ValueError, match="E99"):
        team.team_summary([], EMPS, ["E99"], "2026-11")


def test_unknown_manager_on_the_command_line_exits_with_1(capsys):
    assert cli.main(["team", "--manager", "E99", "--month", "2026-11"]) == 1
    assert "E99" in capsys.readouterr().out


def test_indirect_reports_are_included():
    assert sorted(team.reports_of(EMPS, "B1")) == ["A1", "A2", "M1", "M2"]


def test_second_call_does_not_include_the_first_managers_team():
    assert team.reports_of(EMPS, "M1") == ["A1"]
    assert team.reports_of(EMPS, "M2") == ["A2"]


def test_two_managers_in_one_command(capsys):
    assert cli.main(["team", "--manager", "E10", "--manager", "E11", "--month", "2026-11"]) == 0
    out = capsys.readouterr().out
    assert "TEAM OF E10 Sneha Patil - 2026-11 (3 people)" in out
    assert "TEAM OF E11 Farhan Sheikh - 2026-11 (2 people)" in out
