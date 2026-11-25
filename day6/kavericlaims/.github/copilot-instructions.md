# KaveriClaims: instructions for GitHub Copilot

## About the project
- KaveriClaims is a Python command-line app (the `kavericlaims` package) that works out how much of each expense claim Kaveri Systems reimburses.
- It started as 2015 legacy code. `policy.py`, `storage.py`, `report.py` and `payroll.py` have been cleaned up; `claims.py`, `cli.py`,
  `team.py` (added 2024) and `archive.py` (added 2018) have not.
- `specs/policy.md` is the source of truth for the rules. If the code and the policy disagree, the policy is right and the code has a bug.
  Feature specs are in `specs/`. Bug reports and security reports are in `issues/`.
- Data: `data/employees.csv`, `data/claims_YYYY-MM.csv` (one file per month), `data/fx_rates.json`.
  `archive/` (created when you run `archive save`) holds the auditors' SQLite database and CSV exports.
- `js/` holds a JavaScript port of the policy rules and its tests (Node.js, no packages).

## Running things (Windows, PowerShell)
- Python is in the labs' virtual environment. In a new terminal, activate it first:
  `& "$HOME\Desktop\agentic-ai-copilot-labs\.venv\Scripts\Activate.ps1"`
- Run the app: `python -m kavericlaims report --month 2026-11`, `python -m kavericlaims show C-1105 --month 2026-11`,
  `python -m kavericlaims team --manager E10 --month 2026-11`, `python -m kavericlaims archive search Taxi --month 2026-09`
- Run the tests: `python -m pytest`. Run them after every change, and fix failures before you finish.
- Static analysis: `ruff check .` (style and likely bugs) and `bandit -c pyproject.toml -r .` (security).
- JavaScript tests: `node --test js/policy.test.js`

## Rules for code
- The `kavericlaims` package uses only the Python standard library and must run on Python 3.10 or later.
- Keep these public functions, with the same names and parameters, because other code and the tests use them:
  `storage.load_employees`, `storage.load_claims`, `storage.load_rates`, `currency.set_rates`, `currency.to_inr`,
  `policy.get_tier`, `policy.get_limit`, `policy.needs_receipt`, `claims.process`, `report.build_report`, `report.commas`,
  `team.reports_of`, `team.team_summary`, `archive.save_month`, `archive.search`, `archive.export_csv`, `cli.main`.
- A refactoring must not change behaviour: the golden tests in `tests/` must still pass. Never edit `tests/golden/` to make a test pass.
- Never edit the files in `data/`.
- SQL: always pass values as parameters (`?`), never with string formatting. Never use `eval`, `exec` or `shell=True`.
- Give every new or changed function a one-line docstring and type hints.
