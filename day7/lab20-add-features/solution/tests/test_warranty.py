"""KA-102: warranty end dates and the warranty report."""
from datetime import date

import pytest

from kaveriassets.cli import days_text, main
from kaveriassets.warranty import add_months, warranty_report

EXPECTED = """\
Warranty report on 2026-12-01

Expired (4)
- KA-L004 Apple MacBook Air M2: ended 2025-03-05 (636 days ago), in repair
- KA-M004 Dell P2423D: ended 2026-06-30 (154 days ago), in stock (Bengaluru)
- KA-L003 Lenovo ThinkPad T14 Gen 3: ended 2026-11-10 (21 days ago), with Arjun Menon (E04)
- KA-P001 Samsung Galaxy A55: ended 2026-11-20 (11 days ago), with Farhan Sheikh (E06)

Expiring in the next 60 days (8)
- KA-H001 Jabra Evolve2 65: ends 2026-12-01 (today), with Rahul Verma (E02)
- KA-H002 Jabra Evolve2 65: ends 2026-12-01 (today), in stock (Mysuru)
- KA-L010 Apple MacBook Pro 14 M3: ends 2026-12-10 (in 9 days), with Kavya Shetty (E05)
- KA-L001 Lenovo ThinkPad T14 Gen 3: ends 2026-12-15 (in 14 days), with Ananya Iyer (E01)
- KA-M001 Dell P2423D: ends 2026-12-31 (in 30 days), with Ananya Iyer (E01)
- KA-P003 Samsung Galaxy A55: ends 2027-01-05 (in 35 days), with Ravi Kumar (E09)
- KA-P002 Apple iPhone 15: ends 2027-01-10 (in 40 days), in stock (Bengaluru)
- KA-L002 Dell Latitude 5440: ends 2027-01-20 (in 50 days), with Rahul Verma (E02)
"""


@pytest.mark.parametrize("start, months, end", [
    (date(2023, 12, 15), 36, date(2026, 12, 15)),
    (date(2024, 2, 29), 36, date(2027, 2, 28)),   # no 29 February in 2027
    (date(2024, 1, 31), 1, date(2024, 2, 29)),    # leap year
    (date(2025, 11, 30), 2, date(2026, 1, 30)),   # across a year end
])
def test_add_months(start, months, end):
    assert add_months(start, months) == end


def test_the_report_matches_the_ticket(capsys, data_dir):
    assert main(["--data", str(data_dir), "warranty", "--today", "2026-12-01"]) == 0
    assert capsys.readouterr().out == EXPECTED


def test_retired_assets_are_left_out(service, today):
    expired, expiring = warranty_report(service.assets(), today, 60)
    assert "KA-L009" not in [line.asset.asset_id for line in expired + expiring]


def test_ending_today_counts_as_expiring_not_expired(service, today):
    expired, expiring = warranty_report(service.assets(), today, 0)
    assert [line.asset.asset_id for line in expiring] == ["KA-H001", "KA-H002"]
    assert len(expired) == 4


def test_empty_sections_say_none(capsys, data_dir):
    main(["--data", str(data_dir), "warranty", "--today", "2020-01-01", "--within", "30"])
    out = capsys.readouterr().out
    assert "Expired (0)\n- none" in out
    assert "Expiring in the next 30 days (0)\n- none" in out


@pytest.mark.parametrize("days, text", [(0, "today"), (1, "in 1 day"), (9, "in 9 days"), (-1, "1 day ago"), (-21, "21 days ago")])
def test_days_text(days, text):
    assert days_text(days) == text


def test_negative_within_is_refused(capsys, data_dir):
    assert main(["--data", str(data_dir), "warranty", "--within", "-5"]) == 1
