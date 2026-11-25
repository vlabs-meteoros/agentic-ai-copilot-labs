"""Integration tests: run the whole app through cli.main(), with real files."""
from kavericlaims import cli


def test_october_report_runs(capsys):
    assert cli.main(["report", "--month", "2026-10"]) == 0
    out = capsys.readouterr().out
    assert "C-1005" in out
    assert "Claims: 7" in out


def test_show_explains_a_foreign_currency_claim(capsys):
    assert cli.main(["show", "C-1110", "--month", "2026-11"]) == 0
    out = capsys.readouterr().out
    assert "85.00 AED converted at 22.93 = 1949.05 INR" in out
    assert "1,500.00" in out
    assert "OVER_LIMIT" in out


def test_show_a_rejected_claim(capsys):
    assert cli.main(["show", "C-1106", "--month", "2026-11"]) == 0
    assert "rejected" in capsys.readouterr().out


def test_show_an_unknown_claim_fails(capsys):
    assert cli.main(["show", "C-9999", "--month", "2026-11"]) == 1
    assert "No claim C-9999" in capsys.readouterr().out


def test_report_out_writes_the_same_text(capsys, tmp_path):
    out_file = tmp_path / "report.txt"
    cli.main(["report", "--month", "2026-11", "--out", str(out_file)])
    printed = capsys.readouterr().out
    assert out_file.read_text(encoding="utf-8") in printed


def test_report_with_a_data_folder_copy(capsys, data_dir):
    (data_dir / "claims_2026-11.csv").unlink()
    assert cli.main(["--data", str(data_dir), "report", "--month", "2026-11"]) == 0
    assert "Claims: 0" in capsys.readouterr().out
