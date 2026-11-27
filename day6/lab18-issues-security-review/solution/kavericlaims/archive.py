# archive.py - keep processed months in a small SQLite database for the auditors
# written in 2018 by an intern as a "temporary" tool; Finance Ops has used it every month since
import hashlib
import os
import re
import sqlite3
from pathlib import Path

ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archive")
DB = os.path.join(ARCHIVE_DIR, "claims.db")
EXPORT_DIR = os.path.join(ARCHIVE_DIR, "exports")

# Export names: letters, digits, "-" and "_" only, so a name can never be a path (issue #52)
EXPORT_NAME = re.compile(r"[A-Za-z0-9_-]{1,64}")


def connect(db: str | None = None) -> sqlite3.Connection:
    """Open the archive database, creating it and its table if needed."""
    if db is None:
        db = DB
    os.makedirs(os.path.dirname(os.path.abspath(db)), exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE IF NOT EXISTS claims (month TEXT, id TEXT, emp TEXT, name TEXT, cat TEXT, "
                "date TEXT, description TEXT, claimed REAL, reimb REAL, flags TEXT)")
    return con


def save_month(res: list[dict], rows: list, month: str, db: str | None = None) -> int:
    """Replace the month in the archive with these results; return how many claims were stored."""
    con = connect(db)
    con.execute("DELETE FROM claims WHERE month = ?", (month,))
    desc = {c.claim_id: c.description for c in rows}
    for r in res:
        con.execute("INSERT INTO claims VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (month, r["id"], r["emp"], r["name"], r["cat"], r["date"], desc.get(r["id"], ""),
                     r["claimed"], r["reimb"], " ".join(r["flags"])))
    con.commit()
    con.close()
    return len(res)


def search(text: str, month: str, db: str | None = None) -> list[tuple]:
    """Return the claims of one month whose description contains text (issue #51: parameters, not string formatting)."""
    con = connect(db)
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = con.execute("SELECT id, emp, name, date, description, reimb FROM claims "
                       "WHERE month = ? AND description LIKE ? ESCAPE '\\' ORDER BY id",
                       (month, f"%{escaped}%")).fetchall()
    con.close()
    return rows


def export_csv(month: str, name: str, db: str | None = None, export_dir: str | None = None) -> tuple[str, str]:
    """Write the month to <export folder>/<name>.csv; return the path and the file's SHA-256 checksum."""
    if not EXPORT_NAME.fullmatch(name):
        raise ValueError(f"Export name {name!r} is not allowed: use letters, digits, '-' and '_' only")
    if export_dir is None:
        export_dir = EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)
    path = os.path.join(export_dir, name + ".csv")
    con = connect(db)
    rows = con.execute("SELECT id, emp, name, cat, date, claimed, reimb, flags FROM claims WHERE month = ? ORDER BY id",
                       (month,)).fetchall()
    con.close()
    with open(path, "w", encoding="utf-8") as f:
        f.write("claim_id,emp_id,name,category,date,claimed,reimbursable,flags\n")
        for r in rows:
            f.write(",".join([str(x) for x in r]) + "\n")
    checksum = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return path, checksum


def open_export(path: str) -> None:
    """Open the export in the default app for .csv files (Windows only), without a shell."""
    # Bandit B606 reviewed: no shell is involved, so a file name can't run commands. Windows only.
    os.startfile(path)  # nosec B606
