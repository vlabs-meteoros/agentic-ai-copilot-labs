# Feature: KaveriDesk HTTP API (KAV-215)

**Requested by:** Intranet portal team  **Status:** ready for development

## Why

The intranet portal wants to show tickets and let employees raise new ones. It needs a small JSON API
over the same data and rules as the command-line tool.

## Requirements

* Use **FastAPI** in a new file `kaveridesk/api.py`, with Pydantic models for every request and response body.
* Reuse `Desk` and `Store`. Don't copy any SLA or assignment logic into the API.
* The data folder is `data/` by default. If the environment variable `KAVERIDESK_DATA` is set, use that folder instead (the tests need this).
* "Now" is the real time, unless the environment variable `KAVERIDESK_NOW` is set (format `YYYY-MM-DD HH:MM`), like `--now` in the CLI.
* Dates and times in responses use the format `YYYY-MM-DDTHH:MM`.

### Endpoints

| Method and path | What it does | Success | Errors |
|---|---|---|---|
| `GET /health` | Health check | `200` `{"status": "ok"}` | |
| `GET /tickets` | Open tickets, sorted by due date. Optional query parameters: `team` (not case-sensitive) and `all=true` (include resolved tickets) | `200` list of tickets | |
| `GET /tickets/{ticket_id}` | One ticket, including its notes | `200` ticket | `404` `{"detail": "No ticket INC-9999"}` |
| `POST /tickets` | Create a ticket. Body: `title` (3-120 characters), `category`, `priority` (`P1`-`P4`, default `P3`), `requester` | `201` the new ticket, with its assignee and due time | `422` for a missing field, a title that is too short, an unknown category or priority |
| `GET /breaches` | Open tickets that have breached their SLA | `200` list of tickets | |

Every ticket in a response has: `id`, `title`, `category`, `team`, `priority`, `status`, `assignee`, `requester`, `created`, `due`,
`resolved_at`, `sla` (`OK`, `AT RISK`, `BREACHED` or `MET`) and `notes`.

## Tests

Add `tests/test_api.py` using `fastapi.testclient.TestClient`, against a **temporary copy** of the data folder and `KAVERIDESK_NOW=2026-11-20 11:00`.
Cover each endpoint, the 404, and at least two different 422 cases.

## How to run it

```powershell
python -m uvicorn kaveridesk.api:app --port 8000
```

Then open <http://127.0.0.1:8000/docs>.
