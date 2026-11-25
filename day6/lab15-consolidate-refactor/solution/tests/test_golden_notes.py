"""Golden-file test for the notes and flags that claims.process() writes (what `show` prints as "Rules applied").

test_golden.py only protects the report, and the report doesn't show the notes. This test closes that gap.

The first run records tests/golden/notes.txt from the current code and skips. Every run after that compares with it.
Record it BEFORE you refactor, and commit it. To record it again on purpose, delete the file and run pytest.
"""
from pathlib import Path

import pytest

from kavericlaims import claims, currency, storage

GOLDEN = Path(__file__).parent / "golden" / "notes.txt"
MONTHS = ["2026-09", "2026-10", "2026-11"]


def all_notes() -> str:
    """Return every processed claim of the sample months with its reimbursement, flags and notes."""
    emps = storage.load_employees()
    currency.set_rates(storage.load_rates())
    lines = []
    for month in MONTHS:
        for r in claims.process(storage.load_claims(month), emps, month):
            lines.append(f"{r['id']} {r['reimb']:.2f} {' '.join(r['flags']) or '-'}")
            lines.extend(f"    {note}" for note in r["notes"])
    return "\n".join(lines) + "\n"


def test_notes_match_golden_file():
    text = all_notes()
    if not GOLDEN.exists():
        GOLDEN.write_text(text, encoding="utf-8", newline="\n")
        pytest.skip(f"Recorded {GOLDEN.name} from the current code. Commit it, then run pytest again.")
    assert text == GOLDEN.read_text(encoding="utf-8")
