"""KA-103: asset requests."""
from datetime import date

import pytest

from kaveriassets import asset_requests
from kaveriassets.cli import main
from kaveriassets.models import AssetError


def run(capsys, data_dir, *args):
    code = main(["--data", str(data_dir), *args])
    out, err = capsys.readouterr()
    return code, out.strip(), err.strip()


def test_the_ticket_walkthrough(capsys, data_dir):
    assert run(capsys, data_dir, "request", "E07", "laptop", "--reason", "New joiner", "--today", "2026-12-01") == \
        (0, "Created R-001: laptop for Divya Hegde (E07, Mysuru)", "")
    assert run(capsys, data_dir, "request", "E01", "phone", "--reason", "On-call rota", "--today", "2026-12-01") == \
        (0, "Created R-002: phone for Ananya Iyer (E01, Mysuru)", "")
    assert run(capsys, data_dir, "request", "E01", "laptop", "--reason", "Faster laptop", "--today", "2026-12-01") == \
        (1, "", "Error: Ananya Iyer (E01) already has a laptop (KA-L001)")
    assert run(capsys, data_dir, "requests")[1].splitlines() == [
        "R-001  2026-12-01  laptop   Divya Hegde (E07, Mysuru)  New joiner",
        "R-002  2026-12-01  phone    Ananya Iyer (E01, Mysuru)  On-call rota",
    ]
    assert run(capsys, data_dir, "fulfil", "R-001", "--today", "2026-12-02") == \
        (0, "Fulfilled R-001: KA-L006 Lenovo ThinkPad T14 Gen 5 assigned to Divya Hegde (E07)", "")
    assert run(capsys, data_dir, "fulfil", "R-002", "--today", "2026-12-02") == \
        (1, "", "Error: No free phone in Mysuru for R-002 (free elsewhere: KA-P002 in Bengaluru)")
    assert run(capsys, data_dir, "fulfil", "R-001", "--today", "2026-12-03") == \
        (1, "", "Error: R-001 is already fulfilled (KA-L006 on 2026-12-02)")
    assert run(capsys, data_dir, "requests")[1] == "R-002  2026-12-01  phone    Ananya Iyer (E01, Mysuru)  On-call rota"


def test_no_open_requests(capsys, data_dir):
    assert run(capsys, data_dir, "requests") == (0, "No open requests", "")


def test_pick_newest_then_lowest_id(service):
    assert asset_requests.pick_asset(service, "laptop", "Mysuru").asset_id == "KA-L006"   # L006 and L007 tie on date
    assert asset_requests.pick_asset(service, "phone", "Mysuru") is None


def test_fulfilling_writes_history_and_closes_the_request(service, today):
    request = asset_requests.create_request(service, "E12", "laptop", "New joiner", today)
    closed, asset = asset_requests.fulfil_request(service, request.request_id, date(2026, 12, 2))
    assert (closed.status, closed.asset_id, closed.closed) == ("fulfilled", "KA-L008", "2026-12-02")
    assert service.get_asset("KA-L008").assigned_to == "E12"
    assert service.history("KA-L008")[-1]["action"] == "assigned"
    assert asset_requests.open_requests(service) == []


@pytest.mark.parametrize("emp_id, asset_type, message", [("E99", "laptop", "No employee"), ("E07", "tablet", "Unknown type")])
def test_bad_requests(service, today, emp_id, asset_type, message):
    with pytest.raises(AssetError, match=message):
        asset_requests.create_request(service, emp_id, asset_type, "x", today)


def test_unknown_request(service, today):
    with pytest.raises(AssetError, match="No request R-404"):
        asset_requests.fulfil_request(service, "R-404", today)
