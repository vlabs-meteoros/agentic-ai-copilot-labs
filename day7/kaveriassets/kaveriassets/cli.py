"""Command-line interface: python -m kaveriassets <command> ...

    python -m kaveriassets list [--type laptop] [--status in_stock]
    python -m kaveriassets show KA-L001
    python -m kaveriassets assign KA-L006 E07 [--today 2026-12-01]
    python -m kaveriassets return KA-L006 [--today 2026-12-01]
    python -m kaveriassets summary
"""
import argparse
import sys
from datetime import date
from pathlib import Path

from kaveriassets.models import ASSET_TYPES, STATUSES, Asset, AssetError, Employee
from kaveriassets.service import AssetService

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


def build_parser() -> argparse.ArgumentParser:
    """The argparse parser for every command."""
    parser = argparse.ArgumentParser(prog="python -m kaveriassets", description="KaveriAssets: the Kaveri Systems IT asset register")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="data folder (default: data/ next to the package)")
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("list", help="list assets")
    p.add_argument("--type", choices=ASSET_TYPES)
    p.add_argument("--status", choices=STATUSES)

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
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one command. Returns the exit code: 0 for success, 1 if the register refused the request."""
    args = build_parser().parse_args(argv)
    service = AssetService(args.data)
    try:
        if args.command == "list":
            print(format_list(service.list_assets(type=args.type, status=args.status), service.employees()))
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
    except AssetError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0
