# Lab 15: Consolidate Duplicate Code, Refactor a Large Function, and Migrate to JavaScript

| | |
|---|---|
| **Duration** | 50 minutes |
| **Topic** | Debugging (consolidate duplicate code). Code Understanding and Migration: explaining code, refactoring large functions, translating code to another language |
| **You need** | Day 6 setup done (*Before you start* in the [Day 6 README](../README.md)), Copilot signed in, Node.js 18+ for Task 6 (Day 6 setup installs it) |
| **Files** | Your own copy of **KaveriClaims 2.0** in `Desktop\kavericlaims-day6` (Task 1 creates it). `kavericlaims\claims.py`, `kavericlaims\policy.py` and `js\` in your copy; `test_golden_notes.py` and `solution\` in this folder |

> Based on the Microsoft Learn exercises *Consolidate duplicate code using GitHub Copilot* and *Refactor large functions using GitHub Copilot*
> ([MicrosoftLearning/mslearn-github-copilot-dev](https://github.com/MicrosoftLearning/mslearn-github-copilot-dev), MIT licence), rewritten for the KaveriClaims app.

## Objectives

* Check that your **safety net** covers what you're about to change, and close the gap if it doesn't
* Ask Copilot to **find duplicated logic** across a codebase, then **consolidate** it into one helper
* Split a **large function** into small, focused functions, and measure the result with a complexity check
* **Explain** a module and **translate** it to JavaScript, with tests that prove both versions agree

## The scenario

Day 5 cleaned up half of KaveriClaims. Version 2.0 still has `claims.process()`: 81 lines, one loop, six `if`/`elif` branches,
and two pairs of branches that do the same thing with different names. Every policy change starts there, so it's the next thing to fix.
Then the web team wants the policy rules in JavaScript for the new claim form. They must give exactly the same answers as the Python.

---

## Task 1: Get your copy of KaveriClaims 2.0 (5 min)

1. In VS Code (the window with the labs repository), open a terminal at the repository root. If you haven't done *Before you start* yet, do it now.
2. Create your Day 6 copy and open it:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1
   ```

   The script copies `day6\kavericlaims` to `Desktop\kavericlaims-day6`, makes it a Git repository with one commit (tagged `start`),
   turns on pytest, adds a debug configuration for Lab 16, and opens it in a **new VS Code window**. Your Day 5 copy isn't touched.

   * If VS Code asks **Do you trust the authors of the files in this folder?**, select **Yes, I trust the authors**.
   * If no window opens, use **File > Open Folder... > Desktop\kavericlaims-day6** yourself.

3. **In the new window**, open a terminal (<kbd>Ctrl</kbd>+<kbd>`</kbd>). Activate the labs' Python, then run the report, the tests and a complexity check:

   ```powershell
   & "$HOME\Desktop\agentic-ai-copilot-labs\.venv\Scripts\Activate.ps1"
   python -m kavericlaims report --month 2026-11
   python -m pytest
   ruff check kavericlaims\claims.py --select C901
   ```

   * If activation says *running scripts is disabled*, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal first.

**Checkpoint:** the report ends with `Claims: 22   Flagged: 10` and `Reimbursable: 59,788.50` (Day 5's fixes are in). pytest prints `62 passed`.
ruff prints **C901 `process` is too complex (19 > 10)**.

> **Complexity 19** means 19 independent paths through one function. The usual limit is 10. Each path is a case to test and to keep in your head.

From here until the end of Lab 18, **work in the `kavericlaims-day6` window**.

## Task 2: Check the safety net before you refactor (5 min)

1. **New Chat**, **Ask** mode:

   ```text
   #file:kavericlaims/claims.py #file:tests/test_golden.py I'm about to refactor process(). Which of its outputs does the test suite
   NOT check character by character? Look at what the golden test compares.
   ```

2. Read the answer. The golden test compares the **report**, and the report doesn't print the **notes** (`show`'s "Rules applied" lines).
   A refactoring could change every note and the tests would still pass.
3. Close the gap with a second golden test. Copy it from the labs repository and run pytest **twice**:

   ```powershell
   Copy-Item "$HOME\Desktop\agentic-ai-copilot-labs\day6\lab15-consolidate-refactor\test_golden_notes.py" tests\
   python -m pytest
   python -m pytest
   ```

   The first run **records** `tests\golden\notes.txt` from today's code and skips. The second run compares with it.
4. Open `tests\golden\notes.txt` and skim it. Then commit both files (Source Control, sparkle for the message, **Commit**).

**Checkpoint:** first run `62 passed, 1 skipped`; second run `63 passed`. `notes.txt` has 91 lines, starting with `C-0901 640.00 -`.

> A golden file records what the code does **now**, bugs included. Record it before you change anything, never after.

## Task 3: Find the duplicated logic (7 min)

1. **New Chat**, **Ask** mode:

   ```text
   #codebase Find duplicated or near-duplicated logic in the kavericlaims package. For each one, list the files and functions,
   what is the same, what is different, and how risky it would be to merge. Start with claims.py.
   ```

2. Read the answer, then open `kavericlaims\claims.py` and compare the **MEAL** and **INTERNET** branches side by side.

**Checkpoint:** the answer includes at least:
* **MEAL and INTERNET** in `process()`: the same "shared limit" logic (look up what's used, cap at what's left, record the new total).
  Only the key (`emp|date` or `emp`) and the note differ.
* **HOTEL and OTHER**: the same "cap at a limit, flag OVER_LIMIT" logic, with a different limit.
* `if k in meal_used: u = meal_used[k] else: u = 0.0`, which is `dict.get(k, 0.0)`.
* Outside `claims.py`: `team.fmt()` re-implements `report.commas()`, and `team.team_summary()` adds up per-employee totals the way `report.py` used to.

> Leave `team.py` and `archive.py` alone today: Labs 17 and 18 fix them. Note that Copilot found duplication **across files**, which is hard to spot by reading one file at a time.

## Task 4: Consolidate the duplicated branches (10 min)

1. In `claims.py`, select the whole `process` function. Press <kbd>Ctrl</kbd>+<kbd>I</kbd> and send:

   ```text
   Remove the duplication without changing behaviour or any note text:
   - a helper _cap(result, amount, limit) that reimburses up to the limit and adds OVER_LIMIT if anything is cut
   - a helper _cap_shared(result, amount, limit, used, key) for limits shared between claims (MEAL per day, INTERNET per month):
     it caps at what is left, records the new total in used[key], and returns what was used before
   - use one dict for both shared limits, with keys like "MEAL|E01|2026-11-02" and "INTERNET|E01"
   Use _cap for HOTEL and OTHER, and _cap_shared for MEAL and INTERNET.
   ```

2. Read the diff before you select **Accept**. Check the HOTEL branch still multiplies the limit by the number of nights.
3. Run the tests:

   ```powershell
   python -m pytest
   ```

4. If both golden tests pass, commit. If one fails, read which lines differ (pytest shows them), then **Undo** or ask Copilot to fix that difference.

**Checkpoint:** `63 passed`. `process()` contains no `if k in ...` blocks, and the cap logic exists **once**.

> **Why one dict with prefixed keys?** A meal key and an internet key can never collide (`MEAL|...` vs `INTERNET|...`), and adding a third shared limit later needs no new variable.

## Task 5: Split the large function (12 min)

`process()` is shorter now, but it still does five jobs: skip claims, convert currency, check the receipt, pick the limit, and build the result.

1. **New Chat**, **Agent** mode:

   ```text
   Refactor #file:kavericlaims/claims.py so that process() only loops over the claims and skips rejected claims and unknown employees.
   Move the work for one claim into small functions, each doing one job, for example:
   _process_claim (one claim: convert, check the receipt, apply the limit), _new_result (the empty result dict), and
   _apply_limit (the category branches). Keep _cap and _cap_shared. Use f-strings and descriptive names (claim, emp, amount,
   result, not c, e, amt, r). Keep every note's text exactly the same. Then run python -m pytest and
   ruff check kavericlaims/claims.py --select C901, and fix anything that fails.
   ```

2. Read each command before you select **Allow**. Then review the diff like a pull request:
   * Is every function short enough to read at once? Does each name say what it does?
   * Did anything outside `claims.py` change? (It shouldn't.) Did `tests\golden\` change? (It mustn't.)
3. Run the checks yourself, and the benchmark to be sure nothing got slow:

   ```powershell
   python -m pytest
   ruff check kavericlaims\claims.py --select C901
   python -m kavericlaims bench
   ```

4. Commit.

**Checkpoint:** `63 passed`. ruff prints **All checks passed!** `process()` is about 10 lines, and no function in `claims.py` is longer than about 25 lines.
`bench` prints about the same `process()` time as before.

> **Small functions are easier to test.** `_cap_shared` can now be tested with three numbers and a dict, without building claims and employees.
> Ask Copilot for those tests if you have time left at the end.

## Task 6: Explain the policy, then translate it to JavaScript (11 min)

The web team's claim form needs the policy rules in the browser. Translating by hand is slow and error-prone; translating with Copilot is fast,
and **the tests decide** whether it's right.

1. In the **kavericlaims-day6** window's terminal, check that Node.js is there:

   ```powershell
   node --version
   ```

   You need **v18 or later** (setup installs v26). If `node` isn't found:

   * Open a **new** terminal in this window (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>`</kbd>) and try again. The start script put Node.js on the PATH
     for new terminals, but not for one that was already open.
   * Still not found? Add the Node.js that setup installed to this terminal, then try again:

     ```powershell
     $env:Path += ";" + [Environment]::GetEnvironmentVariable("Path", "User")
     node --version
     ```

   * Still not found? Setup couldn't install it. In the **labs** window, run `powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1` again
     and read the **Node.js** step. If it says *could not be installed*, the VM can't reach nodejs.org: tell your trainer, and pair with a neighbour for this task.

2. **New Chat**, **Ask** mode. Make sure you understand the code before you translate it:

   ```text
   #file:kavericlaims/policy.py Explain this module to a JavaScript developer who has never used Python:
   what each function does, which Python features it uses (sets, dicts of tuples, tuple unpacking, dict.get, x if c else y), and what would need care
   in JavaScript.
   ```

3. Open `js\policy.test.js` and `js\policy_cases.json`. The test is already written: it calls `getTier`, `getLimit` and `needsReceipt` with every case
   in the JSON file. `tests\test_policy_cases.py` checks the same JSON against the Python, so the cases are known to be right. Run it:

   ```powershell
   node --test js/policy.test.js
   ```

   It fails with `Cannot find module './policy.js'`. That's the "red" step.

4. **New Chat**, **Agent** mode:

   ```text
   Translate #file:kavericlaims/policy.py to JavaScript in js/policy.js: CommonJS (module.exports), no packages, camelCase names
   getTier, getLimit, needsReceipt, and export NO_LIMIT and RECEIPT_THRESHOLD. Keep the same rules, tables and comments.
   Don't change js/policy.test.js or js/policy_cases.json. Run node --test js/policy.test.js until it passes.
   ```

5. Prove the tests can catch a mistake: in `js\policy.js`, change `>=` in `needsReceipt` to `>`, run `node --test js/policy.test.js`, read the failure,
   then change it back.

**Checkpoint:** `node --test js/policy.test.js` ends with `# pass 4` and `# fail 0`. With `>`, it fails on `needsReceipt(500)`. `python -m pytest` still passes. Commit.

> **Shared test cases keep two languages honest.** When the policy changes, regenerate `policy_cases.json` from the Python and both versions are checked again.
> Things that often go wrong in a translation: rounding (Python's `round(2.5)` is `2`, JavaScript's `Math.round(2.5)` is `3`), integer division (`//`),
> and `dict.get` defaults. That's why the next step would be shared cases for `claims.process()` too.

> Stuck, or the agent went in circles? Compare with `day6\lab15-consolidate-refactor\solution\` in the labs repository. It's **one** good answer, not the only one.
> To start Lab 16 from it: close the KaveriClaims window, then run `.\day6\start-kavericlaims-day6.ps1 -Reset -FromLab15` from the labs window.

---

## Summary

* Before a refactoring, ask **what your tests don't check**, and close that gap first (here: a second golden file for the notes).
* `#codebase` finds duplication **across files**; you decide which duplicates are worth merging and in what order.
* Consolidate first (one helper for one idea), then split (one function per job). Each step ends with green tests and a commit.
* A **complexity check** (`ruff --select C901`) turns "this function is too big" into a number you can track.
* For a translation, give Copilot a **failing test** to make pass. Explain-then-translate beats translate-and-hope.

Next: **[Lab 16: Debugging, TDD and BDD, and Static Analysis](../lab16-debug-tdd-sca/README.md)**.
