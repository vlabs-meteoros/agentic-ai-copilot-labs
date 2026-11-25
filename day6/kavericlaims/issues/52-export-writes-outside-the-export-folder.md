# #52 Archive export can write files outside the export folder

**Opened by:** Arvind (IT Security) · **Labels:** `security` `archive` · **Assignee:** you

## Summary

`archive export --name` is used to name the file, and the name goes straight into the path. A name with `..` in it, or a full path,
writes the CSV anywhere the user can write. On a shared Finance PC that's a way to overwrite someone else's files.

## Steps to reproduce

```text
python -m kavericlaims archive save --month 2026-09
python -m kavericlaims archive export --month 2026-09 --name "..\..\escaped"
```

The message says `Exported 2026-09 to ...\archive\exports\..\..\escaped.csv`, and the file is created **next to** the `archive` folder,
not inside `archive\exports`. With `--name "C:\Users\Public\anything"` it goes to that folder.

## Expected

Export names are plain file names. Anything that could be a path is refused with a clear message, and nothing is written.
Finance Ops only ever uses names like `audit_2026-09`.

## Notes

Our static analysis tool (bandit) does **not** report this one. Please add a test for it.
