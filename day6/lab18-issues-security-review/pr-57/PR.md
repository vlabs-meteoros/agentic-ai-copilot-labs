# Pull request #57: Add a cost-centre summary for the Finance controller

**Author:** Rohan (Finance IT) · **Base:** `main` · **Files:** `kavericlaims/costcentre.py` (new), `tests/test_costcentre.py` (new)

The Finance controller asked for one line per cost centre with the number of claims and the reimbursable amount,
plus each cost centre's share of the month. Some cost centres are tiny, so `--min` hides the ones below an amount.

```text
python -m kavericlaims.costcentre --month 2026-11
python -m kavericlaims.costcentre --month 2026-11 --min 10*1000
```

Tests pass locally. I'd like to merge this today, the controller needs it for Friday.
