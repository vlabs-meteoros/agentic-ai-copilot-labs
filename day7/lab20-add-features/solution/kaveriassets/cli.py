"""Command-line interface: python -m kaveriassets <command> ...

    python -m kaveriassets list [--type laptop] [--status in_stock | --free] [--city Mysuru]
    python -m kaveriassets show KA-L001
    python -m kaveriassets assign KA-L006 E07 [--today 2026-12-01]
    python -m kaveriassets return KA-L006 [--today 2026-12-01]
    python -m kaveriassets summary
    python -m kaveriassets warranty [--within 60] [--today 2026-12-01]
    python -m kaveriassets request E07 laptop --reason "New joiner" [--today 2026-12-01]
    python -m kaveriassets requests
    python -m kaveriassets fulfil R-001 [--today 2026-12-01]
"""
import argparse
import sys
from datetime import date
from pathlib import Path

from kaveriassets.models import ASSET_TYPES, STATUSES, Asset, AssetError, Employee
from kaveriassets.service import AssetService
from kaveriassets.warranty import WarrantyLine, warranty_report
from kaveriassets import asset_requests

DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data"


def parse_day(text: str) -> date:
    """argparse type for --today: a YYYY-MM-DD date."""
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a date (use YYYY-MM-DD): {text}") from None


def holder_text(asset: Asset, employees: dict[str, Employee]) -> str:
    """Who has the asset, for the list: 'E01 Ananya Iyer', or '' if nobody."""
    if not asset.assigned_to:
        return ""
    employee = employees.get(asset.assigned_to)
    return f"{asset.assigned_to} {employee.name}" if employee else asset.assigned_to


def format_list(assets: list[Asset], employees: dict[str, Employee]) -> str:
    """One line per asset, in columns."""
    if not assets:
        return "No assets match."
    lines = [f"{a.asset_id:<9}{a.type:<9}{a.model:<28}{a.city:<11}{a.status:<10}{holder_text(a, employees)}".rstrip()
             for a in assets]
    lines.append(f"{len(assets)} asset(s)")
    return "\n".join(lines)


def format_asset(service: AssetService, asset: Asset) -> str:
    """Everything about one asset."""
    if asset.status == "assigned":
        employee = service.get_employee(asset.assigned_to)
        status = f"assigned to {employee.name} ({employee.emp_id}, {employee.team})"
    else:
        status = asset.status.replace("_", " ")
    lines = [
        f"{asset.asset_id}  {asset.model} ({asset.type})",
        f"Serial:    {asset.serial}",
        f"City:      {asset.city}",
        f"Purchased: {asset.purchase_date.isoformat()}, warranty {asset.warranty_months} months",
        f"Status:    {status}",
        f"Notes:     {asset.notes or '-'}",
    ]
    history = service.history(asset.asset_id)
    if history:
        lines.append("History:")
        lines += [f"  {h['date']}  {h['action']:<9}{h['emp_id']}".rstrip() for h in history]
    return "\n".join(lines)


def format_summary(service: AssetService) -> str:
    """A table: asset types down, statuses across."""
    counts = service.summary()
    header = f"{'':<9}" + "".join(f"{s:>10}" for s in STATUSES) + f"{'total':>8}"
    rows = [f"{t:<9}" + "".join(f"{counts[t][s]:>10}" for s in STATUSES) + f"{sum(counts[t].values()):>8}" for t in ASSET_TYPES]
    return "\n".join([header, *rows])


def warranty_holder(asset: Asset, employees: dict[str, Employee]) -> str:
    """Where the asset is, for the warranty report: 'with Ananya Iyer (E01)', 'in stock (Mysuru)' or 'in repair'."""
    if asset.status == "assigned":
        employee = employees.get(asset.assigned_to)
        return f"with {employee.label()}" if employee else f"with {asset.assigned_to}"
    if asset.status == "in_stock":
        return f"in stock ({asset.city})"
    return f"in {asset.status}"


def days_text(days: int) -> str:
    """'today', 'in 1 day', 'in 9 days', '1 day ago', '21 days ago'."""
    if days == 0:
        return "today"
    count = f"{abs(days)} day{'s' if abs(days) != 1 else ''}"
    return f"in {count}" if days > 0 else f"{count} ago"


def format_warranty(expired: list[WarrantyLine], expiring: list[WarrantyLine], employees: dict[str, Employee],
                    today: date, within: int) -> str:
    """The KA-102 warranty report."""
    def line(item: WarrantyLine, verb: str) -> str:
        a = item.asset
        return f"- {a.asset_id} {a.model}: {verb} {item.end.isoformat()} ({days_text(item.days)}), {warranty_holder(a, employees)}"

    out = [f"Warranty report on {today.isoformat()}", "", f"Expired ({len(expired)})"]
    out += [line(item, "ended") for item in expired] or ["- none"]
    out += ["", f"Expiring in the next {within} days ({len(expiring)})"]
    out += [line(item, "ends") for item in expiring] or ["- none"]
    return "\n".join(out)


def build_parser() -> argparse.ArgumentParser:
    """The argparse parser for every command."""
    parser = argparse.ArgumentParser(prog="python -m kaveriassets", description="KaveriAssets: the Kaveri Systems IT asset register")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="data folder (default: data/ next to the package)")
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("list", help="list assets")
    p.add_argument("--type", choices=ASSET_TYPES)
    which = p.add_mutually_exclusive_group()
    which.add_argument("--status", choices=STATUSES)
    which.add_argument("--free", action="store_true", help="only assets in stock (same as --status in_stock)")
    p.add_argument("--city", help="only assets in this city (any case)")

    p = commands.add_parser("show", help="everything about one asset")
    p.add_argument("asset_id")

    p = commands.add_parser("assign", help="give an in-stock asset to an employee")
    p.add_argument("asset_id")
    p.add_argument("emp_id")
    p.add_argument("--today", type=parse_day, default=date.today())

    p = commands.add_parser("return", help="take an asset back into stock")
    p.add_argument("asset_id")
    p.add_argument("--today", type=parse_day, default=date.today())

    commands.add_parser("summary", help="how many assets of each type, by status")

    p = commands.add_parser("warranty", help="warranties that have ended or end soon")
    p.add_argument("--within", type=int, default=60, help="days ahead to look (default 60)")
    p.add_argument("--today", type=parse_day, default=date.today())

    p = commands.add_parser("request", help="record a request for an asset")
    p.add_argument("emp_id")
    p.add_argument("type", choices=ASSET_TYPES)
    p.add_argument("--reason", required=True)
    p.add_argument("--today", type=parse_day, default=date.today())

    commands.add_parser("requests", help="open requests, oldest first")

    p = commands.add_parser("fulfil", help="assign an in-stock asset to an open request")
    p.add_argument("request_id")
    p.add_argument("--today", type=parse_day, default=date.today())
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one command. Returns the exit code: 0 for success, 1 if the register refused the request."""
    args = build_parser().parse_args(argv)
    service = AssetService(args.data)
    try:
        if args.command == "list":
            status = "in_stock" if args.free else args.status
            print(format_list(service.list_assets(type=args.type, status=status, city=args.city), service.employees()))
        elif args.command == "show":
            print(format_asset(service, service.get_asset(args.asset_id)))
        elif args.command == "assign":
            asset = service.assign(args.asset_id, args.emp_id, args.today)
            print(f"Assigned {asset.asset_id} ({asset.model}) to {service.get_employee(asset.assigned_to).label()}")
        elif args.command == "return":
            asset = service.return_asset(args.asset_id, args.today)
            print(f"Returned {asset.asset_id} ({asset.model}) to stock in {asset.city}")
        elif args.command == "summary":
            print(format_summary(service))
        elif args.command == "warranty":
            if args.within < 0:
                raise AssetError("--within must be 0 or more")
            expired, expiring = warranty_report(service.assets(), args.today, args.within)
            print(format_warranty(expired, expiring, service.employees(), args.today, args.within))
        elif args.command == "request":
            request = asset_requests.create_request(service, args.emp_id, args.type, args.reason, args.today)
            employee = service.get_employee(request.emp_id)
            print(f"Created {request.request_id}: {request.type} for {employee.name} ({employee.emp_id}, {employee.city})")
        elif args.command == "requests":
            pending = asset_requests.open_requests(service)
            if not pending:
                print("No open requests")
            employees = service.employees()
            for r in pending:
                e = employees[r.emp_id]
                print(f"{r.request_id}  {r.created}  {r.type:<8} {e.name} ({e.emp_id}, {e.city})  {r.reason}")
        elif args.command == "fulfil":
            request, asset = asset_requests.fulfil_request(service, args.request_id, args.today)
            print(f"Fulfilled {request.request_id}: {asset.asset_id} {asset.model} assigned to {service.get_employee(asset.assigned_to).label()}")
    except AssetError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0
