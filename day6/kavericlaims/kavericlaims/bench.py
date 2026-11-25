"""Generate a big, fake month of claims and time how long processing and the report take.

Used by `python -m kavericlaims bench`. This file is a lab tool: you don't need to refactor it.
"""
import random
import time

from . import claims, currency, report
from .models import Claim, Employee

CITIES = ["Bengaluru", "Mysuru", "Pune", "Mangaluru", "Chennai", "Hubballi"]
CATEGORIES = ["MEAL", "MEAL", "MEAL", "TRAVEL", "TRAVEL", "HOTEL", "INTERNET", "OTHER"]


def fake_data(n_emps, n_claims, seed=42):
    """Return (employees, claims) in the same shapes as storage.load_employees and storage.load_claims."""
    rnd = random.Random(seed)
    emps = {}
    for i in range(n_emps):
        eid = "E%05d" % (i + 1)
        emps[eid] = Employee(eid, "Employee %d" % (i + 1), rnd.choice(["G1", "G2", "G3", "G4"]), rnd.choice(CITIES), "", "CC-ENG")
    ids = list(emps)
    rows = []
    for j in range(n_claims):
        day = rnd.randint(1, 30)
        rows.append(Claim("C-%06d" % (j + 1), rnd.choice(ids), "2026-11-%02d" % day, rnd.choice(CATEGORIES),
                     rnd.choice(CITIES), round(rnd.uniform(50, 6000), 2), "INR", rnd.randint(1, 3),
                     rnd.choice(["", "R.jpg", "R.jpg", "R.jpg"]), "approved", "generated"))
    return emps, rows


def run(n_claims=8000, n_emps=500):
    """Print how long claims.process() and report.build_report() take on generated data."""
    currency.set_rates({"2026-11": {"USD": 84.20, "AED": 22.93, "SGD": 64.90}})
    emps, rows = fake_data(n_emps, n_claims)
    print("Generated %d employees and %d claims" % (n_emps, n_claims))
    t0 = time.perf_counter()
    res = claims.process(rows, emps, "2026-11")
    t1 = time.perf_counter()
    text = report.build_report(res, emps, "2026-11")
    t2 = time.perf_counter()
    print("process():      %6.2f s" % (t1 - t0))
    print("build_report(): %6.2f s   (%d lines)" % (t2 - t1, text.count("\n")))
    return 0
