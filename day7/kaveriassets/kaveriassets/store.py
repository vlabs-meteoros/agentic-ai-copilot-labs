"""Reads and writes the CSV files in a data folder: employees.csv, assets.csv and history.csv."""
import csv
from datetime import date
from pathlib import Path

from kaveriassets.models import Asset, Employee

ASSET_FIELDS = ["asset_id", "type", "model", "serial", "city", "purchase_date", "warranty_months", "status", "assigned_to", "notes"]
HISTORY_FIELDS = ["date", "asset_id", "action", "emp_id"]


def load_employees(data_dir: Path) -> dict[str, Employee]:
    """All employees, by employee id."""
    with open(data_dir / "employees.csv", newline="", encoding="utf-8") as f:
        return {row["emp_id"]: Employee(row["emp_id"], row["name"], row["team"], row["city"]) for row in csv.DictReader(f)}


def load_assets(data_dir: Path) -> list[Asset]:
    """All assets, in the order of the file."""
    with open(data_dir / "assets.csv", newline="", encoding="utf-8") as f:
        return [
            Asset(
                asset_id=row["asset_id"],
                type=row["type"],
                model=row["model"],
                serial=row["serial"],
                city=row["city"],
                purchase_date=date.fromisoformat(row["purchase_date"]),
                warranty_months=int(row["warranty_months"]),
                status=row["status"],
                assigned_to=row["assigned_to"],
                notes=row["notes"],
            )
            for row in csv.DictReader(f)
        ]


def save_assets(data_dir: Path, assets: list[Asset]) -> None:
    """Write every asset back to assets.csv."""
    with open(data_dir / "assets.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ASSET_FIELDS)
        writer.writeheader()
        for a in assets:
            writer.writerow({**a.__dict__, "purchase_date": a.purchase_date.isoformat()})


def load_history(data_dir: Path) -> list[dict[str, str]]:
    """Every event in history.csv (date, asset_id, action, emp_id), oldest first as written."""
    path = data_dir / "history.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def append_history(data_dir: Path, when: date, asset_id: str, action: str, emp_id: str = "") -> None:
    """Add one event to history.csv (creating the file if needed)."""
    path = data_dir / "history.csv"
    new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow({"date": when.isoformat(), "asset_id": asset_id, "action": action, "emp_id": emp_id})
