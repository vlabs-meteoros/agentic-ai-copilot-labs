"""The records KaveriAssets keeps: employees and assets."""
from dataclasses import dataclass
from datetime import date

ASSET_TYPES = ("laptop", "monitor", "phone", "headset")
STATUSES = ("in_stock", "assigned", "repair", "retired")


class AssetError(Exception):
    """A request the asset register refuses, with a message for the user (unknown id, asset not free, ...)."""


@dataclass(frozen=True)
class Employee:
    """A Kaveri Systems employee who can hold assets."""
    emp_id: str
    name: str
    team: str
    city: str

    def label(self) -> str:
        """'Ananya Iyer (E01)'."""
        return f"{self.name} ({self.emp_id})"


@dataclass(frozen=True)
class Asset:
    """One piece of IT equipment. `assigned_to` is an employee id, or "" when nobody holds it."""
    asset_id: str
    type: str
    model: str
    serial: str
    city: str
    purchase_date: date
    warranty_months: int
    status: str
    assigned_to: str = ""
    notes: str = ""
