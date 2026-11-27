"""The asset register's rules: find assets and employees, assign and return assets.

Every method reads the CSV files again, so the CLI, the tests and (later) an AI assistant always see the latest data.
Methods that change something take `today` as a parameter: the service never reads the clock itself.
"""
from collections import Counter
from dataclasses import replace
from datetime import date
from pathlib import Path

from kaveriassets import store
from kaveriassets.models import ASSET_TYPES, STATUSES, Asset, AssetError, Employee


class AssetService:
    """The IT asset register, on one data folder."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    # ------------------------------------------------------------------ reading
    def employees(self) -> dict[str, Employee]:
        """All employees, by employee id."""
        return store.load_employees(self.data_dir)

    def assets(self) -> list[Asset]:
        """All assets, sorted by asset id."""
        return sorted(store.load_assets(self.data_dir), key=lambda a: a.asset_id)

    def get_employee(self, emp_id: str) -> Employee:
        """One employee. Raises AssetError if the id is unknown."""
        employee = self.employees().get(emp_id.upper())
        if employee is None:
            raise AssetError(f"No employee {emp_id}")
        return employee

    def find_employees(self, text: str) -> list[Employee]:
        """Employees whose id or name contains `text` (any case), sorted by id."""
        needle = text.strip().lower()
        return [e for e in sorted(self.employees().values(), key=lambda e: e.emp_id)
                if needle and (needle in e.name.lower() or needle == e.emp_id.lower())]

    def get_asset(self, asset_id: str) -> Asset:
        """One asset. Raises AssetError if the id is unknown."""
        for asset in self.assets():
            if asset.asset_id == asset_id.upper():
                return asset
        raise AssetError(f"No asset {asset_id}")

    def list_assets(self, type: str | None = None, status: str | None = None, city: str | None = None) -> list[Asset]:
        """Assets, optionally only one type, one status and/or one city (any case), sorted by asset id."""
        if type is not None and type not in ASSET_TYPES:
            raise AssetError(f"Unknown type {type!r}: use one of {', '.join(ASSET_TYPES)}")
        if status is not None and status not in STATUSES:
            raise AssetError(f"Unknown status {status!r}: use one of {', '.join(STATUSES)}")
        return [a for a in self.assets()
                if (type is None or a.type == type) and (status is None or a.status == status)
                and (city is None or a.city.lower() == city.strip().lower())]

    def assets_of(self, emp_id: str) -> list[Asset]:
        """The assets an employee holds now."""
        return [a for a in self.assets() if a.assigned_to == emp_id and a.status == "assigned"]

    def history(self, asset_id: str) -> list[dict[str, str]]:
        """The events for one asset, oldest first."""
        return sorted((h for h in store.load_history(self.data_dir) if h["asset_id"] == asset_id), key=lambda h: h["date"])

    def summary(self) -> dict[str, Counter]:
        """For each asset type, how many assets have each status."""
        counts: dict[str, Counter] = {t: Counter() for t in ASSET_TYPES}
        for asset in self.assets():
            counts[asset.type][asset.status] += 1
        return counts

    # ------------------------------------------------------------------ changing
    def assign(self, asset_id: str, emp_id: str, today: date) -> Asset:
        """Give an in-stock asset to an employee in the same city. Returns the updated asset."""
        asset = self.get_asset(asset_id)
        employee = self.get_employee(emp_id)
        if asset.status != "in_stock":
            holder = f" (held by {asset.assigned_to})" if asset.assigned_to else ""
            raise AssetError(f"{asset.asset_id} is not in stock: it is {asset.status}{holder}")
        if asset.city != employee.city:
            raise AssetError(f"{asset.asset_id} is in {asset.city}, but {employee.label()} works in {employee.city}. Ship it first.")
        for held in self.assets_of(employee.emp_id):
            if held.type == asset.type:
                raise AssetError(f"{employee.label()} already has a {asset.type} ({held.asset_id})")
        updated = replace(asset, status="assigned", assigned_to=employee.emp_id)
        self._save(updated)
        store.append_history(self.data_dir, today, asset.asset_id, "assigned", employee.emp_id)
        return updated

    def return_asset(self, asset_id: str, today: date) -> Asset:
        """Take an assigned asset back into stock. Returns the updated asset."""
        asset = self.get_asset(asset_id)
        if asset.status != "assigned":
            raise AssetError(f"{asset.asset_id} is not assigned to anyone: it is {asset.status}")
        updated = replace(asset, status="in_stock", assigned_to="")
        self._save(updated)
        store.append_history(self.data_dir, today, asset.asset_id, "returned", asset.assigned_to)
        return updated

    def _save(self, changed: Asset) -> None:
        """Replace one asset in assets.csv, keeping the file's order."""
        assets = [changed if a.asset_id == changed.asset_id else a for a in store.load_assets(self.data_dir)]
        store.save_assets(self.data_dir, assets)
