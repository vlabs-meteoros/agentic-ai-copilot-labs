# Feature: possible duplicate claims

**Requested by:** Finance Ops. **Status:** ready to build.

The auditors found the same taxi claimed twice last quarter. Finance Ops wants the app to point out claims that **might** be duplicates,
so a person can look at them before the month is paid. The app never rejects anything on its own: it only lists pairs to check.

## Command

```text
python -m kavericlaims duplicates --month 2026-09
```

## Rules

Two claims are a **possible duplicate pair** when all of these are true:

1. Same employee (`emp_id`).
2. Same category.
3. Same amount **and** same currency, exactly (to the paisa or cent). Amounts are compared as claimed, before any conversion.
4. Their dates are **at most 3 days apart**. Three days apart counts; four days apart doesn't. Count calendar days:
   2026-09-29 and 2026-10-01 are 2 days apart.
5. Neither claim is `rejected`.

The description doesn't matter: people describe the same taxi in different words.

## Output

* A pair is written as **(earlier claim ID, later claim ID)**, where "earlier" means the smaller claim ID.
* The list of pairs is sorted by the first ID, then the second ID.
* A claim can be in more than one pair. For three matching claims A, B and C you get (A, B), (A, C) and (B, C) if each two are close enough.
* No pairs: the command prints `No possible duplicates in 2026-09`.
* Otherwise it prints one line per pair, then a summary line. For September 2026:

```text
C-0901  C-0902  E01  MEAL        640.00 INR  2026-09-02 / 2026-09-04
C-0904  C-0907  E03  TRAVEL     1450.00 INR  2026-09-08 / 2026-09-11
C-0905  C-0908  E05  OTHER      1250.00 INR  2026-09-09 / 2026-09-12
C-0910  C-0911  E08  TRAVEL      380.00 INR  2026-09-18 / 2026-09-18
4 possible duplicate pair(s) in 2026-09
```

## Where the code goes

* A new module `kavericlaims/duplicates.py` with a function `find_duplicates(claims)` that takes a list of `Claim` objects (from `storage.load_claims`)
  and returns a list of `(Claim, Claim)` tuples, sorted as above.
* The CLI only prints the result.

## Examples

All claims are by employee E01 and approved, unless the table says otherwise.

| # | Claim A | Claim B | Pair? | Why |
|---|---|---|---|---|
| 1 | C-1, MEAL 640.00 INR, 2026-09-02 | C-2, MEAL 640.00 INR, 2026-09-04 | yes: (C-1, C-2) | 2 days apart |
| 2 | C-1, TRAVEL 1450.00 INR, 2026-09-08 | C-2, TRAVEL 1450.00 INR, 2026-09-11 | yes | exactly 3 days apart |
| 3 | C-1, TRAVEL 1450.00 INR, 2026-09-08 | C-2, TRAVEL 1450.00 INR, 2026-09-12 | no | 4 days apart |
| 4 | C-1, MEAL 640.00 INR | C-2, MEAL 640.00 INR, employee **E02** | no | different employees |
| 5 | C-1, MEAL 640.00 INR | C-2, **OTHER** 640.00 INR | no | different categories |
| 6 | C-1, MEAL 640.00 INR | C-2, MEAL **640.50** INR | no | different amounts |
| 7 | C-1, MEAL 40.00 **USD** | C-2, MEAL 40.00 **AED** | no | different currencies |
| 8 | C-1, MEAL 640.00 INR, status **rejected** | C-2, MEAL 640.00 INR | no | a rejected claim is never in a pair |
| 9 | C-1, TRAVEL 380.00 INR, 2026-09-29 | C-2, TRAVEL 380.00 INR, 2026-10-01 | yes | 2 days apart across a month end |
| 10 | **C-9**, MEAL 640.00 INR, 2026-09-04 | **C-3**, MEAL 640.00 INR, 2026-09-02 | yes: (C-3, C-9) | smaller ID first, whatever the order in the file |

Where the table gives no date, both claims are on 2026-09-02.
