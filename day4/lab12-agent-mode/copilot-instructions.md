# KaveriDesk: instructions for GitHub Copilot

## About the project
- KaveriDesk is a Python command-line app (the `kaveridesk` package) that tracks helpdesk tickets and their SLAs.
- Data lives in JSON files in `data/`. Feature specs live in `specs/`.

## Running things (Windows, PowerShell)
- Python is in the labs' virtual environment. In a new terminal, activate it first:
  `& "$HOME\Desktop\agentic-ai-copilot-labs\.venv\Scripts\Activate.ps1"`
- Run the app: `python -m kaveridesk --now "2026-11-20 11:00" <command>`
- Run the tests: `python -m unittest`. Run them after every change, and fix failures before you finish.

## Rules for code
- The `kaveridesk` package uses only the Python standard library. FastAPI is allowed only in `kaveridesk/api.py`.
- Tests use `unittest` (not pytest), in the style of `tests/test_service.py`: a temporary copy of `data/` and a fixed `NOW`.
- Never edit the files in `data/` to make a feature or a test work. Existing data files must keep loading.
- Don't change how due dates and SLA states are calculated unless the task says so.
- Give every new function a one-line docstring and type hints.
