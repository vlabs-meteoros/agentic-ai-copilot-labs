"""KA-102: warranty end dates and the warranty report."""
import calendar
from dataclasses import dataclass
from datetime import date

from kaveriassets.models import Asset


def add_months(start: date, months: int) -> date:
    """The same day `months` later; the last day of the month if that day doesn't exist (2024-02-29 + 36 months = 2027-02-28)."""
    month_index = start.month - 1 + months
    year, month = start.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(start.day, calendar.monthrange(year, month)[1]))


def warranty_end(asset: Asset) -> date:
    """The last day of the asset's warranty."""
    return add_months(asset.purchase_date, asset.warranty_months)


@dataclass(frozen=True)
class WarrantyLine:
    """One asset in the warranty report, with its end date and the days from today (negative = ended)."""
    asset: Asset
    end: date
    days: int


def warranty_report(assets: list[Asset], today: date, within_days: int) -> tuple[list[WarrantyLine], list[WarrantyLine]]:
    """(expired, expiring): warranties that ended before today, and those ending from today to today + within_days.
    Retired assets are left out. Both lists are sorted by end date, then asset id."""
    lines = sorted((WarrantyLine(a, warranty_end(a), (warranty_end(a) - today).days) for a in assets if a.status != "retired"),
                   key=lambda line: (line.end, line.asset.asset_id))
    expired = [line for line in lines if line.days < 0]
    expiring = [line for line in lines if 0 <= line.days <= within_days]
    return expired, expiring
