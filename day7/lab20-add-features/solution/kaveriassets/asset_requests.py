"""KA-103: asset requests. An employee asks for a type of asset; IT fulfils the request from stock in their city."""
import csv
from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path

from kaveriassets.models import ASSET_TYPES, AssetError
from kaveriassets.service import AssetService

REQUEST_FIELDS = ["request_id", "emp_id", "type", "reason", "created", "status", "asset_id", "closed"]


@dataclass(frozen=True)
class AssetRequest:
    """One request. status is 'open' or 'fulfilled'; asset_id and closed are set when it's fulfilled."""
    request_id: str
    emp_id: str
    type: str
    reason: str
    created: str
    status: str = "open"
    asset_id: str = ""
    closed: str = ""


def load_requests(data_dir: Path) -> list[AssetRequest]:
    """Every request in data/requests.csv (none if the file doesn't exist yet)."""
    path = Path(data_dir) / "requests.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [AssetRequest(**row) for row in csv.DictReader(f)]


def save_requests(data_dir: Path, requests: list[AssetRequest]) -> None:
    """Write every request to data/requests.csv."""
    with open(Path(data_dir) / "requests.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUEST_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(r) for r in requests)


def create_request(service: AssetService, emp_id: str, asset_type: str, reason: str, today: date) -> AssetRequest:
    """Record a new open request. Refuses unknown employees and types, and employees who already hold that type."""
    employee = service.get_employee(emp_id)
    if asset_type not in ASSET_TYPES:
        raise AssetError(f"Unknown type {asset_type!r}: use one of {', '.join(ASSET_TYPES)}")
    for held in service.assets_of(employee.emp_id):
        if held.type == asset_type:
            raise AssetError(f"{employee.label()} already has a {asset_type} ({held.asset_id})")
    requests = load_requests(service.data_dir)
    request = AssetRequest(f"R-{len(requests) + 1:03d}", employee.emp_id, asset_type, reason.strip(), today.isoformat())
    save_requests(service.data_dir, [*requests, request])
    return request


def open_requests(service: AssetService) -> list[AssetRequest]:
    """Open requests, oldest first (then by request id)."""
    return sorted((r for r in load_requests(service.data_dir) if r.status == "open"), key=lambda r: (r.created, r.request_id))


def pick_asset(service: AssetService, asset_type: str, city: str):
    """The in-stock asset to hand out: right type and city, newest purchase date first, then the lowest asset id. None if none."""
    candidates = [a for a in service.list_assets(type=asset_type, status="in_stock") if a.city == city]
    candidates.sort(key=lambda a: (-a.purchase_date.toordinal(), a.asset_id))
    return candidates[0] if candidates else None


def fulfil_request(service: AssetService, request_id: str, today: date):
    """Assign the best in-stock asset to an open request and close it. Returns (request, asset)."""
    requests = load_requests(service.data_dir)
    request = next((r for r in requests if r.request_id == request_id.upper()), None)
    if request is None:
        raise AssetError(f"No request {request_id}")
    if request.status != "open":
        raise AssetError(f"{request.request_id} is already {request.status} ({request.asset_id} on {request.closed})")
    employee = service.get_employee(request.emp_id)
    asset = pick_asset(service, request.type, employee.city)
    if asset is None:
        elsewhere = [a.asset_id + " in " + a.city for a in service.list_assets(type=request.type, status="in_stock")]
        hint = f" (free elsewhere: {', '.join(elsewhere)})" if elsewhere else ""
        raise AssetError(f"No free {request.type} in {employee.city} for {request.request_id}{hint}")
    assigned = service.assign(asset.asset_id, employee.emp_id, today)
    closed = replace(request, status="fulfilled", asset_id=assigned.asset_id, closed=today.isoformat())
    save_requests(service.data_dir, [closed if r.request_id == closed.request_id else r for r in requests])
    return closed, assigned
