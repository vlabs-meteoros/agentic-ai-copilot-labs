# Lab 18: Resolve Issues, Fix Security Vulnerabilities, and Review Code with GitHub Copilot

| | |
|---|---|
| **Duration** | 55 minutes (plus an optional task on github.com) |
| **Topic** | Code Review with Copilot: Copilot in the code review process, human-in-the-loop (HITL) review. Debugging: resolving issues, identifying and fixing security vulnerabilities, static analysis for security |
| **You need** | Your `Desktop\kavericlaims-day6` window from Lab 17 (or a fresh one: `start-kavericlaims-day6.ps1 -Reset -FromLab17`) |
| **Files** | `kavericlaims\archive.py` and `issues\` in your copy; `pr-57\`, `REVIEW.md` and `solution\` in this folder |

> Based on the Microsoft Learn exercise *Resolve GitHub issues using GitHub Copilot*
> ([MicrosoftLearning/mslearn-github-copilot-dev](https://github.com/MicrosoftLearning/mslearn-github-copilot-dev), MIT licence), rewritten for the KaveriClaims app.

> [!IMPORTANT]
> This lab is optional. Feel free to explore it whenever you have some free time. You can skip it if your schedule is tight.

## Objectives

* Scan code with a **security** static analysis tool (bandit) and triage its findings: real, false positive, or accepted with a reason
* Resolve **issues** from their description: reproduce, find the root cause with Copilot, fix it test first, and close the issue
* Fix an **SQL injection** and a **path traversal**, including one that the tool doesn't find
* Use **Copilot code review** on a colleague's change, and decide as the human in the loop what to accept, reject or question

## The scenario

The auditors' archive (`archive.py`) was written by an intern in 2018 and never reviewed. Two issues are open against it, one from Finance Ops and one from IT Security.
Then a colleague asks you to review a pull request that the Finance controller "needs for Friday".

Issues normally live on GitHub. To keep the lab independent of your GitHub organisation's settings, they're in the `issues\` folder of your copy, written exactly as they'd be on GitHub.
The optional Task 6 does the same on github.com.

---

## Task 1: Scan for security problems with bandit (6 min)

1. Run bandit on the app (the settings in `pyproject.toml` leave out the tests):

   ```powershell
   bandit -c pyproject.toml -r .
   ```

2. **New Chat**, **Ask** mode:

   ```text
   #terminalLastCommand Triage these bandit findings for this app. For each one: is it a real risk here, what could an attacker or a mistake do,
   and how should it be fixed? Which ones are false positives? Put the most serious first.
   ```

**Checkpoint:** bandit reports **5** issues (High: 2, Medium: 1, Low: 2):

| Bandit | Where | What it is | Real? |
|---|---|---|---|
| **B602** | `archive.open_export` | `subprocess.call("notepad " + path, shell=True)`: a file name with `&` in it runs a command | Yes |
| **B324** | `archive.export_csv` | MD5 checksum | Weak hash; matters only if the checksum is used to prove a file wasn't changed |
| **B608** | `archive.search` | SQL built with `%` string formatting | Yes: issue #51 |
| B404 | `archive.py` | `import subprocess` | Information only |
| B311 | `bench.py` | `random` for fake timing data | False positive |

> Bandit doesn't report issue #52 at all. **No tool finds everything**, so you still review code yourself.

## Task 2: Resolve issue #51 (SQL injection) (14 min)

1. Open `issues\51-archive-search-crashes-on-apostrophe.md` and read it, including Arvind's comment.
2. Reproduce both problems:

   ```powershell
   python -m kavericlaims archive save --month 2026-09
   python -m kavericlaims archive save --month 2026-11
   python -m kavericlaims archive search "Driver's" --month 2026-09
   python -m kavericlaims archive search "%' OR 1=1 --" --month 2026-09
   ```

3. **New Chat**, **Ask** mode:

   ```text
   #file:issues/51-archive-search-crashes-on-apostrophe.md #file:kavericlaims/archive.py What is the root cause of both problems in this issue?
   Show me the SQL that actually runs for each of the two searches.
   ```

4. Fix it **test first**. **New Chat**, **Agent** mode:

   ```text
   Resolve #file:issues/51-archive-search-crashes-on-apostrophe.md.
   1. First write tests in tests/test_archive.py that reproduce both problems, using a temporary database (tmp_path), and run them to show they fail.
   2. Then fix archive.search with SQL parameters. Make sure % and _ in the search text are matched literally, not as wildcards.
   3. Run all the tests and bandit -c pyproject.toml -r .
   ```

5. Review the diff. Run the two searches from step 2 again, then commit with a message that says `Fix #51: ...`.

**Checkpoint:** before the fix, `Driver's` crashes with `sqlite3.OperationalError: near "s": syntax error`, and the injection returns `36 claim(s) found`
(every claim in the archive, from both months). After the fix, `Driver's` finds C-0904 and C-0907 (`2 claim(s) found`), the injection finds `0 claim(s)`,
and bandit no longer reports **B608**. Tests pass.

> The apostrophe crash and the injection are the **same bug**: user text pasted into SQL. Escaping quotes by hand would fix the crash and leave
> other tricks open. **Parameters** (`?`) keep data and SQL apart, so no text can change the query.

## Task 3: Resolve issue #52 (path traversal) (10 min)

1. Read `issues\52-export-writes-outside-the-export-folder.md`. Reproduce it, see where the file went, then delete it:

   ```powershell
   python -m kavericlaims archive export --month 2026-09 --name "..\..\escaped"
   Get-ChildItem escaped.csv
   Remove-Item escaped.csv
   ```

2. **New Chat**, **Agent** mode:

   ```text
   Resolve #file:issues/52-export-writes-outside-the-export-folder.md. Write failing tests first (relative paths with .. using both \ and /,
   an absolute Windows path, an empty name, a very long name), then fix export_csv so an export name can only be a plain file name
   (letters, digits, - and _). The CLI must print a clear message and exit with code 1, without a stack trace. Run all the tests.
   ```

3. Review the diff. Check that a normal export still works, then commit (`Fix #52: ...`):

   ```powershell
   python -m kavericlaims archive export --month 2026-09 --name "..\..\escaped"
   python -m kavericlaims archive export --month 2026-09 --name audit_2026-09
   ```

**Checkpoint:** before the fix, `escaped.csv` appears in `Desktop\kavericlaims-day6`, next to the `archive` folder. After the fix, the first command prints
`Export name '..\\..\\escaped' is not allowed: ...` and `$LASTEXITCODE` is `1`. The second writes `archive\exports\audit_2026-09.csv`. Tests pass.

> **Allow-list, don't block-list.** Blocking `..` misses `C:\...`, `\\server\share` and tricks nobody has thought of yet.
> Allowing only the characters a plain file name needs leaves nothing to forget.

## Task 4: Fix or accept the remaining findings (6 min)

1. **New Chat**, **Agent** mode:

   ```text
   #file:kavericlaims/archive.py Fix the remaining bandit findings and ruff findings in this file without changing what the commands do:
   open the export without a shell (os.startfile on Windows), and use SHA-256 instead of MD5 for the checksum.
   For findings that are not real risks (B404 if subprocess is still imported, B311 in bench.py), don't change the code:
   add "# nosec <id>" on that line and a comment line above it saying why. Then run bandit -c pyproject.toml -r ., ruff check . and python -m pytest.
   ```

2. Review the diff, especially every `nosec`: would you sign your name under each reason?

**Checkpoint:** `bandit -c pyproject.toml -r .` prints **No issues identified.** `ruff check .` prints **All checks passed!** Tests pass. Commit.

> A `nosec` without a reason is a finding swept under the carpet. With a reason, it's a **decision** a reviewer can check.

## Task 5: Review a colleague's pull request, with you in the loop (15 min)

Rohan's PR #57 adds a cost-centre summary. Read the description in the labs repository: `day6\lab18-issues-security-review\pr-57\PR.md`.

1. Bring his changes into your copy as uncommitted changes, plus the review form:

   ```powershell
   $pr = "$HOME\Desktop\agentic-ai-copilot-labs\day6\lab18-issues-security-review"
   Copy-Item "$pr\pr-57\kavericlaims\costcentre.py" kavericlaims\
   Copy-Item "$pr\pr-57\tests\test_costcentre.py" tests\
   Copy-Item "$pr\REVIEW.md" review-pr-57.md
   git add -N kavericlaims/costcentre.py tests/test_costcentre.py
   ```

2. Ask Copilot for a review. In **Source Control** (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>G</kbd>), hover over **Changes** and select the
   **Copilot Code Review - Uncommitted Changes** button. Comments appear in the editor and in the **Comments** panel.
   * If you don't have the button (it's a premium feature that your organisation may not enable): open `costcentre.py`, select all,
     right-click, and choose **Generate Code > Review**. Or in **Ask** mode:
     `#changes Review this change as a senior developer: correctness against the report, security, duplication, tests.`
3. **You** are the reviewer: Copilot only gives suggestions. For **each** comment, check it before you decide, and fill in a row of `review-pr-57.md`:

   ```powershell
   python -m kavericlaims.costcentre --month 2026-11
   python -m kavericlaims report --month 2026-11
   python -m kavericlaims.costcentre --month 2026-11 --min "__import__('os').system('whoami') or 0"
   bandit kavericlaims\costcentre.py
   python -m pytest tests\test_costcentre.py -v
   ```

4. Add anything you found that Copilot didn't. Then write the verdict and a short message to Rohan. Commit `review-pr-57.md` **only**, and remove his
   files from your copy (the PR isn't merged):

   ```powershell
   git reset -q kavericlaims/costcentre.py tests/test_costcentre.py
   Remove-Item kavericlaims\costcentre.py, tests\test_costcentre.py
   ```

**Checkpoint:** your review has **Request changes**, with at least these problems and evidence for each:

| Problem | Evidence |
|---|---|
| **Wrong total**: it adds up `claimed`, not `reimb` | `Total reimbursable: 66,299.55`, but the report says `Reimbursable: 59,788.50` (66,299.55 is the report's **Claimed**) |
| **Code injection**: `eval(a.min)` runs any Python | the third command prints your user name before the summary. bandit: **B307** |
| **Duplication**: `fmt_inr` re-implements `report.commas` | `report.commas(1234567.5)` gives the same string |
| **Weak tests**: `test_summarise_returns_a_dict` never checks a number | both tests still pass with the wrong total |
| No docstrings or type hints, against the project's instructions | `.github\copilot-instructions.md` |

> **Human in the loop** means a person is accountable for what gets merged. Copilot may miss the wrong total (it needs to know what "reimbursable"
> means in this app) and may suggest changes that don't matter. Check each comment with evidence; accept, reject or ask. Never "Approve" because
> the AI found nothing.

## Task 6 (optional): The same flow on github.com

Only if your organisation lets you create repositories, and your trainer says so. Copilot code review on github.com and assigning issues to Copilot
depend on your organisation's Copilot policies.

1. Create an **empty private** repository on github.com, for example `kavericlaims-day6`, and push your copy to it (GitHub shows the commands).
2. Create an issue from the text of `issues\52-export-writes-outside-the-export-folder.md`.
3. Create a branch, change something small (for example, split `cli.main` into one function per command), push it, and open a pull request with
   `Fixes #<issue number>` in the description.
4. On the pull request, under **Reviewers**, request **Copilot**. Read its comments, reply to one, and resolve or dismiss each. Merging closes the issue.
5. If your organisation has the **Copilot coding agent**, assign another issue to **Copilot** and review the pull request it opens, exactly like Task 5.

> Stuck? Compare with `day6\lab18-issues-security-review\solution\` in the labs repository.

---

## Summary

* **Security scanners** find known risky patterns fast (SQL built from strings, `shell=True`, `eval`, weak hashes), but not everything: #52 needed a person.
* **Resolve an issue** in four steps: reproduce it, find the root cause, write a failing test, fix. Mention the issue number in the commit.
* **Parameters** stop SQL injection. **Allow-lists** stop path traversal. **No shell, no eval** stops command and code injection.
* **Copilot code review** is a fast first reviewer. **You** decide, with evidence, and you're accountable for what's merged.

This is the end of Day 6. Day 7 uses GitHub Copilot with **JavaScript** and Python, and builds agents into existing apps.
