# KA-103: Asset requests

| | |
|---|---|
| **From** | Farhan Sheikh, IT Service Desk lead |
| **Size** | Large |

## Why

> "Requests for laptops arrive by e-mail and get lost. I want to record a request in KaveriAssets, see what's still open, and fulfil it with one
> command that picks the right asset."

## Rules

1. `request EMP TYPE --reason TEXT` records an **open** request for an employee and an asset type (`laptop`, `monitor`, `phone`, `headset`).
   Request ids are `R-001`, `R-002`, ... in the order they're created.
2. It's refused if the employee is unknown, or **already holds** an asset of that type: `Ananya Iyer (E01) already has a laptop (KA-L001)`.
3. `requests` lists open requests, oldest first (then by id). With none, it prints `No open requests`.
4. `fulfil REQ` picks an **in-stock** asset of the requested type **in the employee's city**: the newest purchase date first, then the lowest asset id.
   It assigns the asset (the normal assign rules and history apply) and marks the request **fulfilled**, with the asset id and the date.
5. If nothing suitable is in stock, `fulfil` fails and says what's free elsewhere, if anything:
   `No free phone in Mysuru for R-002 (free elsewhere: KA-P002 in Bengaluru)`.
6. Fulfilling a request twice fails: `R-001 is already fulfilled (KA-L006 on 2026-12-02)`. An unknown id: `No request R-404`.
7. Errors print `Error: <message>` to stderr and exit with code 1, like the other commands.
8. Requests are kept in `data/requests.csv` (created on first use) with the columns
   `request_id,emp_id,type,reason,created,status,asset_id,closed`.

## Commands

```text
python -m kaveriassets request EMP TYPE --reason TEXT [--today YYYY-MM-DD]
python -m kaveriassets requests
python -m kaveriassets fulfil REQ [--today YYYY-MM-DD]
```

## Example (starting from the original data)

```text
> python -m kaveriassets request E07 laptop --reason "New joiner" --today 2026-12-01
Created R-001: laptop for Divya Hegde (E07, Mysuru)
> python -m kaveriassets request E01 phone --reason "On-call rota" --today 2026-12-01
Created R-002: phone for Ananya Iyer (E01, Mysuru)
> python -m kaveriassets request E01 laptop --reason "Faster laptop" --today 2026-12-01
Error: Ananya Iyer (E01) already has a laptop (KA-L001)
> python -m kaveriassets requests
R-001  2026-12-01  laptop   Divya Hegde (E07, Mysuru)  New joiner
R-002  2026-12-01  phone    Ananya Iyer (E01, Mysuru)  On-call rota
> python -m kaveriassets fulfil R-001 --today 2026-12-02
Fulfilled R-001: KA-L006 Lenovo ThinkPad T14 Gen 5 assigned to Divya Hegde (E07)
> python -m kaveriassets fulfil R-002 --today 2026-12-02
Error: No free phone in Mysuru for R-002 (free elsewhere: KA-P002 in Bengaluru)
> python -m kaveriassets fulfil R-001 --today 2026-12-03
Error: R-001 is already fulfilled (KA-L006 on 2026-12-02)
> python -m kaveriassets requests
R-002  2026-12-01  phone    Ananya Iyer (E01, Mysuru)  On-call rota
```

KA-L006 wins over KA-L005 (newer) and over KA-L007 (same date, lower id).
In the `requests` list, the type is padded to 8 characters, followed by one space.

## Done when

* The example prints exactly that, with the same exit codes. Tests use a temporary copy of the data, never `data/`.
* The request logic lives in its own module, not in `cli.py`.
