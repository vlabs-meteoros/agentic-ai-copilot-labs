# KaveriAssets: instructions for GitHub Copilot

## About the project
- KaveriAssets is the IT asset register of Kaveri Systems: laptops, monitors, phones and headsets in the Mysuru and Bengaluru offices,
  who holds them, and their history. It's a Python command-line app (the `kaveriassets` package).
- `models.py` has the records (`Employee`, `Asset`, frozen dataclasses) and `AssetError`. `store.py` reads and writes the CSV files.
  `service.py` (`AssetService`) holds the rules. `cli.py` is the command line. `llm.py` connects to the shared Azure OpenAI deployment.
- New work is described in `backlog/` (one Markdown ticket per feature, with exact examples). The ticket is the source of truth.
- Data: `data/employees.csv`, `data/assets.csv`, `data/history.csv` (and `data/requests.csv` once requests exist).

## Running things (Windows, PowerShell)
- The terminals in this VS Code window already use the labs' Python environment.
- Run the app: `python -m kaveriassets list`, `python -m kaveriassets show KA-L001`, `python -m kaveriassets summary`.
- Commands that change data (`assign`, `return`, ...) write to `data/`. After trying one, put the data back with `git restore data`.
- Run the tests: `python -m pytest`. Run them after every change, and fix failures before you finish.

## Rules for code
- Python 3.10 or later, standard library only (plus `openai` and `python-dotenv` in `llm.py`).
- Business rules go in `service.py` (or a new module next to it), never in `cli.py`: the CLI only parses arguments and prints.
- The service never reads the clock: methods that need a date take `today: date`, and the CLI passes `--today` (default: today's date).
- Refusals raise `AssetError` with a message for the user. The CLI prints `Error: <message>` to stderr and returns exit code 1.
- Tests use pytest and the fixtures in `tests/conftest.py`: `data_dir` (a temporary copy of `tests/fixtures/`), `service` and `today` (2026-12-01).
  Tests never read or write `data/`. Never edit `tests/fixtures/` to make a test pass.
- Keep the existing commands, their options and their output unchanged unless a ticket says otherwise.
- Give every new function a one-line docstring and type hints.
