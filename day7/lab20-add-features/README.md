# Lab 20: Add New Features to an Existing Python App

| | |
|---|---|
| **Duration** | 50 minutes |
| **Topic** | Using GitHub Copilot with Python: the Copilot extension, crafting prompts, improving a Python project. Adding features to an existing application |
| **You need** | Day 7 setup done, Copilot signed in |
| **Files** | Your own copy of **KaveriAssets** in `Desktop\kaveriassets` (Task 1 creates it). `backlog\KA-101...`, `KA-102...` and `KA-103...` in your copy; `solution\` in this folder |

> [!IMPORTANT]
> This lab is optional. Feel free to explore it whenever you have some free time. You can skip it if your schedule is tight.

## Objectives

* Ask Copilot Chat **Python questions** about a codebase you didn't write, and check the answers in the code
* Add features of three sizes, each with the Copilot tool that fits: **inline chat** (small), **Ask then Agent** (medium), **plan then Agent** (large)
* Give Copilot a **ticket with exact examples**, and hold the result to it with tests
* Keep the existing app working: house rules in `.github\copilot-instructions.md`, tests after every change, one commit per feature

## The scenario

**KaveriAssets** is the IT asset register of Kaveri Systems: 22 laptops, monitors, phones and headsets in Mysuru and Bengaluru, and who has them.
It works, it has tests, and the service desk has three tickets waiting in `backlog\`. You'll ship all three today, and in Lab 21 you'll add an AI assistant to it.

| Ticket | Feature | Size | Copilot tool |
|---|---|---|---|
| KA-101 | `list --free` and `--city` | Small | Inline chat |
| KA-102 | Warranty report | Medium | Ask (design), then Agent |
| KA-103 | Asset requests: `request`, `requests`, `fulfil` | Large | Plan, then Agent |

---

## Task 1: Get your copy of KaveriAssets (5 min)

1. In the labs repository window, in a terminal at the repository root:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\day7\start-kaveriassets.ps1
   ```

   A **new VS Code window** opens on `Desktop\kaveriassets`. If it shows a **Restricted Mode** bar, select **Manage** > **Trust**.
2. In the new window, open a terminal. It already uses the labs' Python (no activation needed). Run:

   ```powershell
   python -m kaveriassets list
   python -m kaveriassets show KA-L001
   python -m kaveriassets summary
   python -m pytest
   ```

3. Open `.github\copilot-instructions.md` and read it (2 minutes). Copilot reads it with every request in this window.

**Checkpoint:** `list` ends with `22 asset(s)`. `summary` shows 4 laptops in stock. `17 passed`.

> **Your data changes when you try commands.** `assign`, `return` (and the new commands) write to `data\`. After trying one, put the data back with
> `git restore data` (and `git clean -f data` once `data\requests.csv` exists). The tests never use `data\`: they use a temporary copy of `tests\fixtures\`.

## Task 2: Ask Copilot about the Python (8 min)

**New Chat**, **Ask** mode. Check each answer in the code before you move on.

1. ```text
   #codebase Where does the app decide whether an asset can be assigned? List every rule, with the file and function.
   ```

2. Open `kaveriassets\service.py`, select the line `updated = replace(asset, status="assigned", assigned_to=employee.emp_id)` and ask:

   ```text
   #selection Why does this use dataclasses.replace instead of asset.status = "assigned"? What would happen if I wrote that instead?
   ```

   Then try it: in the terminal run `python -c "from kaveriassets.service import AssetService; a = AssetService('data').get_asset('KA-L005'); a.status = 'x'"`.
3. ```text
   #file:kaveriassets/cli.py --today has default=date.today(). When exactly is date.today() called? Is there a catch if this code
   ran in a long-lived process, like a web server?
   ```

4. Open `kaveriassets\store.py`, select `save_assets`, and type `/explain`. Then ask a plain Python question in the same chat:
   `What's the difference between csv.reader and csv.DictReader, and why does newline="" matter when opening a CSV file?`

**Checkpoint:** the rules are all in `AssetService.assign`: the asset and the employee exist, the asset is **in stock**, it's in the **same city**,
and the employee doesn't already hold one of that **type**. `Asset` is a **frozen** dataclass, so `a.status = 'x'` raises
`dataclasses.FrozenInstanceError: cannot assign to field 'status'`. `date.today()` runs **once**, when the parser is built: fine for a command-line run,
stale in a process that runs past midnight.

> **Copilot Chat knows Python, and with `#codebase`, `#file` and `#selection` it knows *your* Python.** The general answer (frozen dataclasses)
> and the specific answer (this function relies on it) are both useful; only the second is about your code.

## Task 3: KA-101, small: inline chat (8 min)

1. Open `backlog\KA-101-list-filters.md` and read it.
2. Open `kaveriassets\service.py`, put the cursor inside `list_assets`, press <kbd>Ctrl</kbd>+<kbd>I</kbd> (inline chat) and type:

   ```text
   Add an optional city parameter: keep only assets in that city, ignoring case and spaces around it. Update the docstring.
   ```

   Review the diff in the editor, then **Accept**.
3. Open `kaveriassets\cli.py`, put the cursor in the `list` section of `build_parser`, <kbd>Ctrl</kbd>+<kbd>I</kbd>:

   ```text
   Add --city CITY and --free to the list command as #file:backlog/KA-101-list-filters.md says. --free and --status can't be
   used together (mutually exclusive group). Pass them on to service.list_assets in main().
   ```

   Inline chat may change `main()` too, or only the parser. If `main()` wasn't changed, put the cursor there and ask again.
4. Try the ticket's examples (they only read data). Then **New Chat**, **Agent** mode:

   ```text
   Add tests/test_list_filters.py with tests for the examples in #file:backlog/KA-101-list-filters.md, using the data_dir fixture. Run python -m pytest.
   ```

**Checkpoint:** the three examples print exactly what the ticket shows (5 assets, 1 asset, `No assets match.`).
`python -m kaveriassets list --free --status assigned` prints a usage error ending `argument --status: not allowed with argument --free`. Tests pass. Commit.

> **Inline chat is for one place at a time.** It sees the file you're in (and what you `#` mention), and shows a diff right there.
> A change across two files took two small prompts, and that's normal.

## Task 4: KA-102, medium: design in Ask, build in Agent (12 min)

1. Open `backlog\KA-102-warranty-report.md` and read it.
2. **New Chat**, **Ask** mode. Design before code:

   ```text
   #file:backlog/KA-102-warranty-report.md #codebase We're adding this report. Don't write the full code yet. Answer:
   1. Which module should the end-date rule and the report logic go in, and why not cli.py?
   2. How do you add months to a date in the standard library, and what goes wrong with 2024-02-29 + 36 months?
   3. Which lines in the ticket's example are the edge cases a test must cover?
   ```

   Read the answers. Push back on anything that breaks `.github\copilot-instructions.md` (for example, logic in `cli.py`, or a new package like `dateutil`).
3. Same chat, switch to **Agent** mode (the chat history stays):

   ```text
   Implement KA-102 as we discussed. The output must match the ticket's example exactly; add a test that compares the whole text
   for --today 2026-12-01, and tests for the end-date rule (29 February, a year end). Run python -m pytest until everything passes.
   ```

4. Run it yourself:

   ```powershell
   python -m kaveriassets warranty --today 2026-12-01
   python -m kaveriassets warranty --today 2026-12-01 --within 10
   ```

**Checkpoint:** the first command prints exactly the ticket's example: `Expired (4)` and `Expiring in the next 60 days (8)`, starting with KA-H001
(`today`) and ending with KA-L002 (`in 50 days`). KA-L011 (bought 2024-02-29) ends on **2027-02-28**, so it's not in the 60-day list.
With `--within 10`: `Expiring in the next 10 days (3)`. Tests pass. Commit.

> The usual slips: KA-H001 and KA-H002 (ending **today**) counted as expired, `1 days`, or a crash on 29 February.
> The ticket's example plus a whole-text test catches all three. If Copilot "fixes" the test instead of the code, undo and say so.

## Task 5: KA-103, large: plan first, then Agent (15 min)

1. Open `backlog\KA-103-asset-requests.md` and read it.
2. **New Chat**. Choose **Plan** in the agents drop-down if your VS Code has it; otherwise use **Ask** mode. Send:

   ```text
   #file:backlog/KA-103-asset-requests.md #codebase Plan this feature for KaveriAssets. Don't write code. Give me:
   the new module and its functions, how requests are stored, which existing functions you'll reuse (don't duplicate the assign rules),
   the CLI changes, and the list of tests (one per rule, plus the ticket's example end to end).
   ```

   Review the plan. Check one thing in particular: `fulfil` must assign through `AssetService.assign`, so the city, stock and one-per-type rules and the history all still apply.
3. Same chat, switch to **Agent** mode:

   ```text
   Implement the plan. The ticket's example must print exactly what it shows, with the same exit codes. Tests use the data_dir fixture,
   never data/. Run python -m pytest until everything passes.
   ```

4. Try the ticket's example yourself, command by command, then put the data back:

   ```powershell
   python -m kaveriassets request E07 laptop --reason "New joiner" --today 2026-12-01
   python -m kaveriassets request E01 phone --reason "On-call rota" --today 2026-12-01
   python -m kaveriassets requests
   python -m kaveriassets fulfil R-001 --today 2026-12-02
   python -m kaveriassets fulfil R-002 --today 2026-12-02
   git restore data; git clean -f data
   ```

**Checkpoint:** `fulfil R-001` picks **KA-L006** (newer than KA-L005, and a lower id than KA-L007, bought the same day).
`fulfil R-002` prints `Error: No free phone in Mysuru for R-002 (free elsewhere: KA-P002 in Bengaluru)` and `$LASTEXITCODE` is `1`.
After `git restore data; git clean -f data`, `git status` shows no changes in `data\`. Tests pass. Commit.

> **Plan, then build.** For a feature that touches several files, a plan you can read in one minute saves a ten-minute review of code that went the wrong way.
> The plan is also the moment to say *"reuse `assign`, don't copy its rules"*.

> Stuck, or the agent went in circles? Compare with `day7\lab20-add-features\solution\` in the labs repository. It's **one** good answer, not the only one.
> To start Lab 21 from it: close the KaveriAssets window, then run `.\day7\start-kaveriassets.ps1 -Reset -FromLab20` from the labs window.

---

## Summary

* Copilot Chat answers Python questions in general, and about *your* code with `#codebase`, `#file` and `#selection`. Check the specific answers in the code.
* Match the tool to the size: **inline chat** for one place, **Ask** to design, **Plan** for a multi-file feature, **Agent** to build and run the tests.
* A ticket with **exact examples** turns "looks right" into a test that passes or fails.
* House rules in `copilot-instructions.md` (where logic goes, no clock in the service, tests on fixtures) keep three features consistent with the code that was already there.

Next: **[Lab 21: Integrate an AI Agent into the App](../lab21-ai-agent/README.md)**.
