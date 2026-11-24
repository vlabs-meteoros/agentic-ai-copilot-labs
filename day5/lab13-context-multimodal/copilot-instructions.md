# KaveriClaims: instructions for GitHub Copilot

## About the project
- KaveriClaims is a Python command-line app (the `kavericlaims` package) that works out how much of each expense claim Kaveri Systems reimburses.
- It is legacy code: written in 2015 for Python 2, ported to Python 3 in 2019, never refactored.
- `specs/policy.md` is the source of truth for the rules. If the code and the policy disagree, the policy is right and the code has a bug.
- Data: `data/employees.csv`, `data/claims_YYYY-MM.csv` (one file per month), `data/fx_rates.json`. Receipt images: `receipts/`.

## Running things (Windows, PowerShell)
- Python is in the labs' virtual environment. In a new terminal, activate it first:
  `& "$HOME\Desktop\agentic-ai-copilot-labs\.venv\Scripts\Activate.ps1"`
- Run the app: `python -m kavericlaims report --month 2026-11`, `python -m kavericlaims show C-1105 --month 2026-11`, `python -m kavericlaims bench`
- Run the tests: `python -m pytest`. Run them after every change, and fix failures before you finish.

## Rules for code
- The `kavericlaims` package uses only the Python standard library and must run on Python 3.10 or later.
- Keep these public functions, with the same names and parameters, because other code and the tests use them:
  `storage.load_employees`, `storage.load_claims`, `storage.load_rates`, `currency.set_rates`, `currency.to_inr`,
  `policy.get_tier`, `policy.get_limit`, `policy.needs_receipt`, `claims.process`, `report.build_report`, `report.commas`, `cli.main`.
- A refactoring must not change behaviour: `tests/test_golden.py` must still pass. Never edit `tests/golden/` to make a test pass.
- Never edit the files in `data/`.
- Give every new or changed function a one-line docstring and type hints.
