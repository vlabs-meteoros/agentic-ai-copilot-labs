"""Tests for the auditors' archive (Lab 18: issues #51 and #52, and the bandit findings)."""
import pytest

from kavericlaims import archive


def result(claim_id, emp="E01", reimb=100.0):
    return {"id": claim_id, "emp": emp, "name": "Test", "cat": "TRAVEL", "date": "2026-09-08",
            "claimed": reimb, "reimb": reimb, "flags": []}


class Row:
    def __init__(self, claim_id, description):
        self.claim_id = claim_id
        self.description = description


@pytest.fixture
def db(tmp_path):
    """An archive in a temporary folder with two September claims and one November claim."""
    path = str(tmp_path / "claims.db")
    archive.save_month([result("C-1"), result("C-2")],
                       [Row("C-1", "Driver's allowance for Mandya visit"), Row("C-2", "Taxi to airport")], "2026-09", path)
    archive.save_month([result("C-9")], [Row("C-9", "Hotel 100% refundable")], "2026-11", path)
    return path


def test_search_finds_text_with_an_apostrophe(db):
    """Issue #51: this crashed with sqlite3.OperationalError."""
    assert [r[0] for r in archive.search("Driver's", "2026-09", db)] == ["C-1"]


def test_search_cannot_be_used_to_read_other_months(db):
    """Issue #51: "%' OR 1=1 --" returned every claim in the archive."""
    assert archive.search("%' OR 1=1 --", "2026-09", db) == []


def test_percent_sign_is_searched_literally(db):
    assert archive.search("%", "2026-09", db) == []
    assert [r[0] for r in archive.search("100%", "2026-11", db)] == ["C-9"]


def test_search_is_still_case_insensitive(db):
    assert [r[0] for r in archive.search("taxi", "2026-09", db)] == ["C-2"]


@pytest.mark.parametrize("name", ["..\\..\\Desktop\\payroll", "../../escaped", "C:\\Users\\Public\\x", "a/b", "", "x" * 65])
def test_export_name_that_is_a_path_is_refused(db, tmp_path, name):
    """Issue #52: the name was joined to the folder as it was, so it could point anywhere."""
    with pytest.raises(ValueError, match="not allowed"):
        archive.export_csv("2026-09", name, db, str(tmp_path / "exports"))


def test_export_writes_inside_the_export_folder(db, tmp_path):
    path, checksum = archive.export_csv("2026-09", "audit_2026-09", db, str(tmp_path / "exports"))
    assert path == str(tmp_path / "exports" / "audit_2026-09.csv")
    lines = (tmp_path / "exports" / "audit_2026-09.csv").read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("claim_id,")
    assert [line.split(",")[0] for line in lines[1:]] == ["C-1", "C-2"]
    assert len(checksum) == 64  # SHA-256, not MD5


def test_export_command_refuses_a_path_with_a_message(capsys, monkeypatch, tmp_path):
    from kavericlaims import cli
    monkeypatch.setattr(archive, "DB", str(tmp_path / "claims.db"))
    monkeypatch.setattr(archive, "EXPORT_DIR", str(tmp_path / "exports"))
    assert cli.main(["archive", "export", "--month", "2026-09", "--name", "..\\..\\escaped"]) == 1
    assert "not allowed" in capsys.readouterr().out
    assert not (tmp_path / "exports").exists() or not any((tmp_path / "exports").iterdir())
