"""Golden-file test: the November report must not change by even one character.

If you change the report ON PURPOSE (for example, after fixing a bug), update the golden file:
    python -m kavericlaims report --month 2026-11 --out tests/golden/report_2026-11.txt
"""
from pathlib import Path

from kavericlaims import cli

GOLDEN = Path(__file__).parent / "golden" / "report_2026-11.txt"


def test_november_report_matches_golden_file(capsys):
    cli.main(["report", "--month", "2026-11"])
    assert capsys.readouterr().out == GOLDEN.read_text(encoding="utf-8")
