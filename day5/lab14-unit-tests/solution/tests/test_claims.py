"""Edge cases of claims.process() that the policy examples don't cover."""
from kavericlaims import claims


def test_claim_from_unknown_employee_is_skipped_with_a_warning(rates, employees, make_claim, capsys):
    assert claims.process([make_claim("C-1", "E99", "MEAL", 100.0)], employees, "2026-11") == []
    assert "unknown employee E99" in capsys.readouterr().out


def test_unknown_category_reimburses_nothing(rates, employees, make_claim):
    [result] = claims.process([make_claim("C-1", "G2", "PARKING", 100.0)], employees, "2026-11")
    assert result["reimb"] == 0
    assert result["flags"] == ["UNKNOWN_CATEGORY"]


def test_hotel_within_limit_is_paid_in_full(rates, employees, make_claim):
    [result] = claims.process([make_claim("C-1", "G4", "HOTEL", 8200.0, city="Mumbai")], employees, "2026-11")
    assert result["reimb"] == 8200.0
    assert result["flags"] == []


def test_meal_limit_already_used_up_gives_zero(rates, employees, make_claim):
    results = claims.process([make_claim("C-1", "G2", "MEAL", 800.0), make_claim("C-2", "G2", "MEAL", 100.0)],
                             employees, "2026-11")
    assert [r["reimb"] for r in results] == [800.0, 0.0]
    assert results[1]["flags"] == ["OVER_LIMIT"]
