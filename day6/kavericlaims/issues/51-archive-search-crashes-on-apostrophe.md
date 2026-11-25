# #51 Archive search crashes when the text has an apostrophe

**Opened by:** Lakshmi (Finance Ops) · **Labels:** `bug` `archive` · **Assignee:** you

## What happened

I was looking for the driver's allowance claims from September, for the auditors:

```text
python -m kavericlaims archive save --month 2026-09
python -m kavericlaims archive search "Driver's" --month 2026-09
```

It printed a long error that ends with:

```text
sqlite3.OperationalError: near "s": syntax error
```

Searching for `Driver` (without the `'s`) works and finds C-0904 and C-0907.

## What I expected

The two driver's allowance claims, C-0904 and C-0907.

---

**Comment from Arvind (IT Security):** I had a look because of the error message. That's not just a crash. Try

```text
python -m kavericlaims archive search "%' OR 1=1 --" --month 2026-09
```

after archiving November too. It returns the claims of **every month in the archive**, not just September.
Please fix the cause, not only the apostrophe, and add a test that would catch it coming back.
