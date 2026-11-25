"""Read the data files."""
import csv
import json
from pathlib import Path

from .models import Claim, Employee

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _folder(data_dir: str | Path | None) -> Path:
    """Return the data folder to use: data_dir, or the default data folder."""
    return Path(data_dir) if data_dir is not None else DATA_DIR


def _read_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV file with a header row into a list of dicts."""
    with path.open(newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if any(row.values())]


def load_employees(data_dir: str | Path | None = None) -> dict[str, Employee]:
    """Load data/employees.csv as {emp_id: Employee}."""
    rows = _read_rows(_folder(data_dir) / "employees.csv")
    return {row["emp_id"]: Employee(**row) for row in rows}


def load_claims(month: str, data_dir: str | Path | None = None) -> list[Claim]:
    """Load data/claims_<month>.csv; return [] (and say so) if there is no file for that month."""
    path = _folder(data_dir) / f"claims_{month}.csv"
    if not path.exists():
        print(f"No claims file for {month}")
        return []
    return [
        Claim(
            claim_id=row["claim_id"],
            emp_id=row["emp_id"],
            date=row["date"],
            category=row["category"].upper(),
            city=row["city"],
            amount=float(row["amount"].replace(",", "")),  # Excel exports write "1,250.00"
            currency=row["currency"].upper(),
            qty=int(row["qty"]),
            receipt=row["receipt"],
            status=row["status"].lower(),
            description=row["description"],
        )
        for row in _read_rows(path)
    ]


def load_rates(data_dir: str | Path | None = None) -> dict:
    """Load data/fx_rates.json as {month: {currency: rate}}; return {} if it can't be read."""
    path = _folder(data_dir) / "fx_rates.json"
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as err:
        print(f"WARNING: could not read {path.name}: {err}")
        return {}
