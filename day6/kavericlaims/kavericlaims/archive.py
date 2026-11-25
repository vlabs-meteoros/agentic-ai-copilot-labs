# archive.py - keep processed months in a small SQLite database for the auditors
# written in 2018 by an intern as a "temporary" tool; Finance Ops has used it every month since
import hashlib
import os
import sqlite3
import subprocess

ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archive")
DB = os.path.join(ARCHIVE_DIR, "claims.db")
EXPORT_DIR = os.path.join(ARCHIVE_DIR, "exports")


def connect(db=None):
    if db == None:
        db = DB
    os.makedirs(os.path.dirname(os.path.abspath(db)), exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE IF NOT EXISTS claims (month TEXT, id TEXT, emp TEXT, name TEXT, cat TEXT, "
                "date TEXT, description TEXT, claimed REAL, reimb REAL, flags TEXT)")
    return con


def save_month(res, rows, month, db=None):
    # replace the month in the archive with these results
    con = connect(db)
    con.execute("DELETE FROM claims WHERE month = ?", (month,))
    desc = {}
    for c in rows:
        desc[c.claim_id] = c.description
    for r in res:
        con.execute("INSERT INTO claims VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (month, r["id"], r["emp"], r["name"], r["cat"], r["date"], desc.get(r["id"], ""),
                     r["claimed"], r["reimb"], " ".join(r["flags"])))
    con.commit()
    con.close()
    return len(res)


def search(text, month, db=None):
    # claims of one month whose description contains text
    con = connect(db)
    sql = "SELECT id, emp, name, date, description, reimb FROM claims WHERE month = '%s' AND description LIKE '%%%s%%' ORDER BY id" % (month, text)
    rows = con.execute(sql).fetchall()
    con.close()
    return rows


def export_csv(month, name, db=None, export_dir=None):
    # write the month to <export folder>/<name>.csv; name is what Finance Ops wants the file to be called
    if export_dir == None:
        export_dir = EXPORT_DIR
    os.makedirs(export_dir, exist_ok=True)
    path = os.path.join(export_dir, name + ".csv")
    con = connect(db)
    rows = con.execute("SELECT id, emp, name, cat, date, claimed, reimb, flags FROM claims WHERE month = ? ORDER BY id",
                       (month,)).fetchall()
    con.close()
    f = open(path, "w", encoding="utf-8")
    f.write("claim_id,emp_id,name,category,date,claimed,reimbursable,flags\n")
    for r in rows:
        f.write(",".join([str(x) for x in r]) + "\n")
    f.close()
    checksum = hashlib.md5(open(path, "rb").read()).hexdigest()
    return path, checksum


def open_export(path):
    # open the file in Notepad so Finance Ops can check it before they send it
    subprocess.call("notepad " + path, shell=True)
