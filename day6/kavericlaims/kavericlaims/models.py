"""Data classes for the rows in the data files."""
from dataclasses import dataclass


@dataclass
class Employee:
    """One row of data/employees.csv."""

    emp_id: str
    name: str
    grade: str
    city: str
    manager: str
    cost_centre: str


@dataclass
class Claim:
    """One row of data/claims_YYYY-MM.csv."""

    claim_id: str
    emp_id: str
    date: str
    category: str
    city: str
    amount: float
    currency: str
    qty: int
    receipt: str
    status: str
    description: str
