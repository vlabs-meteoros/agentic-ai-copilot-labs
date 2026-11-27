# Lab 17: Debugging, TDD and BDD, and Static Analysis with GitHub Copilot

| | |
|---|---|
| **Duration** | 60 minutes |
| **Topic** | Debugging: using Copilot to identify and resolve common errors, TDD and BDD with Copilot (tests from requirements), resolving static code analysis (SCA) violations with Copilot |
| **You need** | Your `Desktop\kavericlaims-day6` window from Lab 16 (or a fresh one: `start-kavericlaims-day6.ps1 -Reset -FromLab16`) |
| **Files** | `kavericlaims\team.py`, `specs\duplicates.md` and `ruff.toml` in your copy; `duplicates.feature` and `solution\` in this folder |

## Objectives

* Resolve **common Python errors** with Copilot: read the stack trace, fix the cause, and add a test so it stays fixed
* Find a **silent logic bug** with the VS Code debugger, then let Copilot explain what you saw
* Build a feature **test first** (TDD) from a written spec: red, green, refactor
* Describe behaviour in **Gherkin** (BDD) and let Copilot write the step definitions
* Run a **static analysis** tool (ruff), fix its findings with Copilot, and decide which ones to suppress

## The scenario

The Ops team added a `team` command in 2024 so managers can see what their team spent. It has never worked properly, and today a manager is waiting.
After that, Finance Ops wants a **duplicate claims** check, and they've written the spec. Finally, IT wants static analysis in the build,
and you get to see what it would have caught.

---

## Task 1: A crash with a stack trace (6 min)

1. Run the new command for Sneha Patil (E10):

   ```powershell
   python -m kavericlaims team --manager E10 --month 2026-11
   ```

   It crashes. Read the **last three lines** of the stack trace yourself first: the error type, the message, and the line in **your** code.

2. Fix it with Copilot. Either:
   * hover over the failed command in the terminal and select the **sparkle** (*Fix using Copilot* / *Explain using Copilot*), or
   * **New Chat**, **Ask** mode: `/fix #terminalLastCommand`
3. Apply the fix, run the command again, then ask for a test that would have caught it:

   ```text
   Add a test to tests/test_team.py that fails with the old bug: team_summary must print the team total with a thousands separator.
   Build the employees and results inside the test.
   ```

**Checkpoint:** the error was `TypeError: can only concatenate str (not "float") to str` at `lines.append("  Team total: " + total)`.
After the fix, the output ends with `Team total: 5,700.00` for 3 people (E03, E05, E06). `python -m pytest` passes. Commit.

> A good fix uses what the code already has: `team.py` has an `fmt()` function for money. `str(total)` would also stop the crash, but would print `5700.0`.

## Task 2: A KeyError, and a friendly message (5 min)

1. A manager typed the wrong ID:

   ```powershell
   python -m kavericlaims team --manager E99 --month 2026-11
   ```

2. **New Chat**, **Ask** mode: `#terminalLastCommand #file:kavericlaims/team.py #file:kavericlaims/cli.py Why does this crash, and what's the best place to handle it?`
3. Ask Copilot to make the change you agree with: an unknown manager prints a clear message and the command exits with code 1 (not a stack trace).
   Ask for a test too.

**Checkpoint:** the crash was `KeyError: 'E99'` at `boss = emps[m]`. Now the command prints a message that names `E99`, and
`$LASTEXITCODE` is `1`. Tests pass. Commit.

> **Where to handle an error is a design choice.** Here `team_summary` checks its input and raises a `ValueError`, and the CLI turns that into a message and exit code 1.
> Ask Copilot for the trade-offs before you accept the first suggestion.

## Task 3: A silent bug, found with the debugger (12 min)

No crash this time, just wrong numbers. Ask for two teams at once:

```powershell
python -m kavericlaims team --manager E10 --manager E11 --month 2026-11
```

Farhan Sheikh (E11) has **two** people (E07, E08), but the output says **5 people** and includes Sneha's team. Run E11 on its own and it's right.

1. Open `kavericlaims\team.py`. Click in the margin left of the first line inside `reports_of` (`for e in emps.values():`) to set a **breakpoint** (red dot).
2. Open **Run and Debug** (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>D</kbd>), choose **Lab 17: team for E10 and E11**, and press <kbd>F5</kbd>.
3. Each time it stops, look at `manager` and `found` in **VARIABLES**, then press <kbd>F5</kbd> (Continue). Count the stops.
   Watch for the first stop where `manager` is `'E11'`: what's already in `found`?
4. Stop debugging (<kbd>Shift</kbd>+<kbd>F5</kbd>). Select the `def reports_of(...)` line, and in **Ask** mode:

   ```text
   #selection When reports_of is called for the second manager, found already contains the first manager's team,
   even though the call doesn't pass found. Why? How do I fix it without changing the function's signature for callers?
   ```

5. Apply the fix, and add a test that calls `reports_of` twice in a row. Remove the breakpoint.

**Checkpoint:** at the first stop for `'E11'`, `found` was already `['E03', 'E05', 'E06']`. The cause is a **mutable default argument**
(`found=[]` is created **once**, when Python defines the function, and shared by every call). After the fix (`found=None`, then `if found is None: found = []`):
E11 has `(2 people)` and `Team total: 12,830.00`. Try `--manager E12`: 11 people, `Team total: 50,888.50`
(the report's total minus Deepa's own flight). Tests pass. Commit.

> The debugger showed **what** happened; Copilot explained **why**. Together they're faster than either alone, and you never had to guess.

## Task 4: Test-driven development from a spec (15 min)

Open `specs\duplicates.md` and read it. Finance Ops wrote the rules **and 10 examples**. In TDD you turn the examples into tests **before** any code exists.

1. **Red.** **New Chat**, **Agent** mode:

   ```text
   We're doing TDD. Read #file:specs/duplicates.md and write tests/test_duplicates.py with one test per example in the
   Examples table (use pytest.mark.parametrize), plus a test for three matching claims. Import find_duplicates from
   kavericlaims.duplicates. Do NOT create kavericlaims/duplicates.py yet. Run the tests and show me that they fail.
   ```

   Review the tests against the spec's table **before** you keep them: the tests are now the definition of "done".

2. Run them yourself:

   ```powershell
   python -m pytest tests/test_duplicates.py
   ```

3. **Green.** Same chat:

   ```text
   Now implement kavericlaims/duplicates.py with the smallest code that makes the tests pass. Don't change the tests.
   Then add the duplicates command to the CLI exactly as the spec's Command and Output sections say, with a test for the
   September output. Run all the tests.
   ```

4. Check the real data against the spec's expected output:

   ```powershell
   python -m kavericlaims duplicates --month 2026-09
   python -m kavericlaims duplicates --month 2026-11
   ```

5. **Refactor.** In **Ask** mode: `#file:kavericlaims/duplicates.py Can this be simpler or clearer without changing behaviour? Keep the tests green.`
   Apply what you agree with, run the tests, commit.

**Checkpoint:** in step 2 pytest can't even load the file: `ERROR tests/test_duplicates.py` with `ModuleNotFoundError: No module named 'kavericlaims.duplicates'`,
and `1 error during collection`. That's the red step.
After step 3 all tests pass. September prints the 4 pairs from the spec, ending `4 possible duplicate pair(s) in 2026-09`;
November prints `No possible duplicates in 2026-11`.

> Examples 2, 3 and 9 are the ones a quick implementation gets wrong: "at most 3 days" is **inclusive**, and comparing only the day of the month
> breaks across a month end. Because the tests came from the spec, Copilot couldn't skip them.

## Task 5: The same behaviour in Gherkin (BDD) (10 min)

**BDD** writes behaviour in plain language that Finance Ops can read and check (Given / When / Then), and the scenarios run as tests.

1. Copy the feature file that Finance Ops' analyst wrote into your tests, and read it:

   ```powershell
   New-Item -ItemType Directory -Force tests\features | Out-Null
   Copy-Item "$HOME\Desktop\agentic-ai-copilot-labs\day6\lab17-debug-tdd-sca\duplicates.feature" tests\features\
   ```

2. **New Chat**, **Agent** mode:

   ```text
   Write tests/test_duplicates_bdd.py with pytest-bdd step definitions for #file:tests/features/duplicates.feature.
   Use scenarios("features/duplicates.feature"), a fixture that holds the list of claims, parsers.parse for the step parameters,
   and the datatable argument for the table in the Background. Call kavericlaims.duplicates.find_duplicates. Run the tests.
   ```

3. Add a scenario **yourself**, at the end of the feature file, without writing any Python:

   ```gherkin
     Scenario: The same amount in a different currency is not a duplicate
       When E01 also claims "C-2" for TRAVEL 380.00 AED on 2026-09-08
       Then Finance Ops sees no pairs
   ```

4. Run the tests again.

**Checkpoint:** `python -m pytest -v -k bdd` shows **4** passing scenarios, including yours. Your scenario needed no new Python: it reused the existing steps.

> That's the point of BDD: once the steps exist, people who don't write Python can add cases. The step definitions are the only "glue" code.

## Task 6: Static analysis with ruff (12 min)

**Static code analysis** (SCA) reads code without running it, and finds bugs, risky patterns and style problems. The rules for this project are in `ruff.toml`.

1. Run it on the whole project:

   ```powershell
   ruff check .
   ```

2. Let ruff fix what it can fix safely, and see what's left:

   ```powershell
   ruff check . --fix
   ruff check .
   ```

3. Fix the rest **outside `archive.py`** with Copilot (Lab 18 fixes `archive.py`). **New Chat**, **Agent** mode:

   ```text
   #terminalLastCommand Fix these ruff findings, except the ones in kavericlaims/archive.py. Don't change behaviour.
   For C901 on cli.main, don't refactor it: explain the options, then add "# noqa: C901" with a short reason.
   Run ruff check . --exclude kavericlaims/archive.py and python -m pytest when you're done.
   ```

4. Now see what static analysis would have told you about Task 3, in seconds and without a debugger. Run ruff on the **original** `team.py` from the `start` tag:

   ```powershell
   git show start:kavericlaims/team.py | ruff check --select B006 --stdin-filename team.py -
   ```

**Checkpoint:** step 1 finds about 12 problems, 5 of them in `archive.py` (your Lab 16 and 17 code may add a few). `--fix` fixes 3 of them (`not in`, an unused import).
After step 3, `ruff check . --exclude kavericlaims/archive.py` prints **All checks passed!** and tests pass. Step 4 prints
**B006 Do not use mutable data structures for argument defaults** at `found=[]`. That's your Task 3 bug. Commit.

> **Fix, or suppress with a reason?** A suppression (`# noqa: C901 - ...`) is a decision that a person made and wrote down. Splitting `cli.main` into
> one function per command would be the better fix. If you have time left, ask Agent mode to do it (Lab 16, Task 5 shows how), and remove the `noqa`.

> Stuck? Compare with `day6\lab17-debug-tdd-sca\solution\` in the labs repository. To start Lab 18 from it: close the KaveriClaims window, then run
> `.\day6\start-kavericlaims-day6.ps1 -Reset -FromLab17` from the labs window.

---

## Summary

* For a **crash**, the stack trace's last lines say what and where; Copilot (`/fix`, terminal sparkle) says why. Always add the test that would have caught it.
* For a **silent bug**, reproduce it with the smallest input, stop at a breakpoint, and look. Then ask Copilot to explain what you saw.
* **TDD**: tests from the spec first (red), the smallest code that passes (green), then clean up (refactor). The tests stop Copilot from "improving" the rules.
* **BDD**: Gherkin scenarios are requirements that run. Copilot writes the step definitions; anyone can add scenarios.
* **Static analysis** finds whole classes of bugs before anyone runs the code. Fix most findings; suppress only with a written reason.

Next: **[Lab 18: Resolve Issues, Fix Security Vulnerabilities, and Review Code](../lab18-issues-security-review/README.md)**.
