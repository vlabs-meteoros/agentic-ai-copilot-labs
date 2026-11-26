"""Tests for the asset register's rules (kaveriassets.service)."""
import pytest

from kaveriassets.models import AssetError


def test_list_filters_by_type_and_status(service):
    free_laptops = service.list_assets(type="laptop", status="in_stock")
    assert [a.asset_id for a in free_laptops] == ["KA-L005", "KA-L006", "KA-L007", "KA-L008"]


def test_list_rejects_an_unknown_type(service):
    with pytest.raises(AssetError, match="Unknown type"):
        service.list_assets(type="tablet")


def test_ids_are_not_case_sensitive(service):
    assert service.get_asset("ka-l001").asset_id == "KA-L001"
    assert service.get_employee("e01").name == "Ananya Iyer"


def test_find_employees_by_part_of_the_name(service):
    assert [e.emp_id for e in service.find_employees("hegde")] == ["E07", "E10"]
    assert [e.emp_id for e in service.find_employees("E12")] == ["E12"]
    assert service.find_employees("") == []


def test_assign_updates_the_asset_and_the_history(service, today):
    asset = service.assign("KA-L006", "E07", today)
    assert (asset.status, asset.assigned_to) == ("assigned", "E07")
    assert service.get_asset("KA-L006").assigned_to == "E07"
    assert service.history("KA-L006") == [{"date": "2026-12-01", "asset_id": "KA-L006", "action": "assigned", "emp_id": "E07"}]


@pytest.mark.parametrize("asset_id, emp_id, message", [
    ("KA-L001", "E07", "not in stock"),          # already assigned
    ("KA-L004", "E07", "not in stock"),          # in repair
    ("KA-L008", "E07", "Ship it first"),         # Bengaluru laptop, Mysuru employee
    ("KA-L005", "E01", "already has a laptop"),  # Ananya has KA-L001
    ("KA-L005", "E99", "No employee"),
    ("KA-X999", "E07", "No asset"),
])
def test_assign_refuses(service, today, asset_id, emp_id, message):
    with pytest.raises(AssetError, match=message):
        service.assign(asset_id, emp_id, today)


def test_return_puts_the_asset_back_in_stock(service, today):
    asset = service.return_asset("KA-L003", today)
    assert (asset.status, asset.assigned_to) == ("in_stock", "")
    assert service.history("KA-L003")[-1]["action"] == "returned"
    with pytest.raises(AssetError, match="not assigned"):
        service.return_asset("KA-L003", today)


def test_summary_counts_every_asset(service):
    counts = service.summary()
    assert counts["laptop"]["in_stock"] == 4
    assert sum(sum(c.values()) for c in counts.values()) == 22
