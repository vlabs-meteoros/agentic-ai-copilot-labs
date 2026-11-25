# Lab 14: Develop Unit Tests with GitHub Copilot

| | |
|---|---|
| **Duration** | 60 minutes |
| **Topic** | Using GitHub Copilot: unit and integration tests, finding edge cases, explaining errors and stack traces, suggesting fixes |
| **You need** | Your `Desktop\kavericlaims` window from Lab 13 (or a fresh copy from the original Lab 13 baseline using the reset instructions below). Day 5 setup completed (installs `pytest` and `pytest-cov`). |
| **Files** | `specs\policy.md`, `kavericlaims\*.py` and `tests\` in your copy; `solution\` in this folder |

> Based on the Microsoft Learn exercise *Develop unit tests using GitHub Copilot*
> ([MicrosoftLearning/mslearn-github-copilot-dev](https://github.com/MicrosoftLearning/mslearn-github-copilot-dev), MIT licence), rewritten for the KaveriClaims app.

## Objectives

* Run and debug **pytest** tests from VS Code's **Testing** view
* Let Copilot list the **edge cases** before you write a single test
* **Generate tests** for existing code, and check whether their expected values came from the code or from the requirements
* Write **tests from requirements** first, watch them fail, and fix the code (not the tests) with Copilot
* **Explain a stack trace** with Copilot, then fix the bug **test first**
* Use **fixtures**, `monkeypatch` and an **integration test**, then find the gaps with **coverage**

**Lab 14 broke, or you want a fresh start?** Start from the original Lab 13 baseline. Close the **kavericlaims** window first (**File > Close Window**), then run this in the labs repository window (your old copy is kept as `kavericlaims-old-...`):

```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\Desktop\agentic-ai-copilot-labs\day5\start-kavericlaims.ps1" -Reset
```

---

## Task 1: Run the tests from the Testing view (5 min)

1. In the **kavericlaims** window, select the **Testing** view in the Activity Bar (the flask icon).
   The start script turned on pytest for this folder, so your tests are listed under `tests`.
   * If you see **Configure Python Tests** instead, select it, then **pytest**, then the root folder **`.`**.
   * If tests don't load, check the Python interpreter (bottom right of the Status Bar) is the labs' `.venv`.
2. Select **Run Tests** (the double play icon at the top of the view). Then run a single test with the play icon next to it.
3. Open `tests\test_currency.py`. Each test has a green tick in the gutter: you can run or **debug** a test from there too.

**Checkpoint:** All existing tests pass. You should have **3** initial tests when starting from the original Lab 13 baseline.

## Task 2: Find the edge cases first (6 min)

The cheapest test to write is the one you thought of before writing code. **New Chat**, **Ask** mode:

```text
#file:specs/policy.md #file:kavericlaims/policy.py #file:kavericlaims/claims.py
List the edge cases a good test suite must cover for these rules: boundaries, shared limits, currencies,
rejected claims and bad input. Make it a checklist, most important first, and say which ones the current tests cover.
```

**Checkpoint:** the list includes at least: a claim of **exactly ₹500** without a receipt, two meals on the **same day** sharing one limit, a **rejected** claim
(it must not use up a limit), a claim **without a receipt** (it must not use up a limit either), a **foreign-currency** claim (tier 1), a hotel for **2 nights**,
an **unknown category or employee**, and a **month with no exchange rates**. Almost none are covered today.

> Keep this chat open: it's your checklist for the rest of the lab.

## Task 3: Generate tests for existing code (8 min)

1. Open `kavericlaims\policy.py` and select everything (<kbd>Ctrl</kbd>+<kbd>A</kbd>).
2. Right-click the selection and choose **Generate Code > Generate Tests** (on some versions: **Copilot > Generate Tests**).
   Or press <kbd>Ctrl</kbd>+<kbd>I</kbd> and type `/tests`.
3. Copilot proposes a test file, usually `tests\test_policy.py`. Review it and select **Keep** (or **Accept**), then save it.
4. Run the new tests from the **Testing** view.
5. **Read the expected values.** Find the test for the **G3 meal limit in a tier 2 city**. Does it expect **600** (the code) or **800** (the policy)?

**Checkpoint:** a new `tests\test_policy.py` with tests for `get_tier`, `get_limit` and `needs_receipt`. Either:
* it expects **600** and passes: Copilot copied the code's numbers, so the test **can't find the bug**. Correct the test to 800 now, and expect it to fail, or
* it expects **800** and fails: Copilot followed `tests.instructions.md` ("take expected values from the policy") and found the bug for you.

> **A test generated from the code tests what the code does, not what it should do.** It's a quick way to cover code, and a poor way to find bugs.
> Leave any failing test failing for now: Task 4 fixes the code.

## Task 4: Tests from requirements, then fix the code (12 min)

Section 7 of `specs\policy.md` is a table of examples with the correct answers. That's a test suite waiting to be written.

1. **New Chat**, **Agent** mode:

   ```text
   Create tests/test_policy_examples.py that checks every example in section 7 of #file:specs/policy.md by running
   claims through claims.process(). Use @pytest.mark.parametrize for the single-claim examples, and separate tests
   for examples 6, 9 and 13. Build the employees and claims inside the test file.
   Don't change any app code. Run python -m pytest and tell me which examples fail and why.
   ```

2. Read the commands before you select **Allow**, and keep the new file. The agent reports the failures.
3. Decide who's right. The instructions say it: **the policy is right**. So the fix goes in the app code, not in the tests.
4. In the **Testing** view, hover over a failed example test and select **Fix Test Failure** (the sparkle icon). Or, in a **New Chat** in **Agent** mode:

   ```text
   #testFailure The policy examples are correct. Fix the app code, not the tests, so they pass. Then run all the tests.
   ```

   (Newer VS Code versions list `#testFailure` as `#execute/testFailure`: pick it from the `#` list.)

5. Review the diff. **Did it change the code, or did it change the expected values in the tests?** Undo any change to the tests.
6. Run all tests. One more test now fails: the **golden test**. That's expected. You changed the behaviour on purpose,
   so the golden file is out of date. Read the failure, then update the golden file and look at what changed:

   ```powershell
   python -m kavericlaims report --month 2026-11 --out tests/golden/report_2026-11.txt
   python -m pytest
   ```

   Open **Source Control** and select `report_2026-11.txt` to see the diff. Then commit.

**Checkpoint:**
* Before the fix, **example 3** (G3 Mysuru meal: 600.00 instead of 750.00) and **example 5** (₹500.00 with no receipt: paid instead of `NO_RECEIPT`) fail
* The fix is two small changes in `policy.py`: G3 tier 2 meals become **800**, and `needs_receipt` uses **`>=`** instead of `>`
* The golden diff shows only **C-1105** (now 750.00), **C-1112** (now 0.00 `NO_RECEIPT`), their two employee totals and the grand total (**Reimbursable: 59,788.50**)
* All tests pass

> **Changing a golden file is a decision, not a fix.** Do it only when you know why the output changed, and check the diff shows nothing else.
> And notice: the old 3 tests covered these lines and still missed both bugs.

## Task 5: Explain a stack trace, then fix it test first (10 min)

1. Finance Ops says the October report crashes. Run it:

   ```powershell
   python -m kavericlaims report --month 2026-10
   ```

2. **New Chat**, **Ask** mode. Type `#terminalLastCommand` (newer VS Code versions list it as `#read/terminalLastCommand`: pick it from the `#` list), then:

   ```text
   #terminalLastCommand Explain this error: which file, line and data row cause it, and why?
   ```

   (Or select the error in the terminal, copy it and paste it into the chat.)

3. Write the test **before** the fix. **New Chat**, **Agent** mode:

   ```text
   Write a failing test first: in tests/test_storage.py, check that storage.load_claims reads an amount written as
   "1,250.00" (in quotes, as Excel exports it) as 1250.0. Create the CSV file in tmp_path. Run only that test and show
   me that it fails. Don't change the app code yet.
   ```

4. When you've seen it fail (**red**), send:

   ```text
   Now make that test pass with the smallest change to storage.py, then run all the tests.
   ```

5. Run the October report again.

**Checkpoint:**
* The explanation points to `float(...)` in `storage.load_claims`, and to claim **C-1005** in `data\claims_2026-10.csv`, whose amount is `"1,250.00"`.
  The error says `could not convert string to float: '1,250.00'` (or `'"1'` if your `storage.py` still splits lines on commas by hand)
* Your new test failed first, then passed (**green**). The fix removes the thousands separator before converting
* The October report runs: `Claims: 7   Flagged: 0`, `Reimbursable: 14,928.85`

> **Red, then green.** A test that you've seen fail is a test you know can fail. You'll do more of this on Day 6 (TDD and BDD).

## Task 6: Fixtures, monkeypatch and integration tests (10 min)

Your test files now repeat the same set-up (employees, claims, exchange rates), and `currency.RATES` is a global that one test can leave behind for the next.

1. **New Chat**, **Agent** mode:

   ```text
   Create tests/conftest.py with pytest fixtures:
   - rates: sets currency.RATES to the November 2026 rates with monkeypatch, for one test only
   - employees: one employee per grade (G1 in Pune, G2 in Bengaluru, G3 in Mysuru, G4 in Mumbai)
   - make_claim: a factory that builds a Claim with sensible defaults (receipt present, status approved)
   Update tests/test_currency.py and tests/test_policy_examples.py to use them.
   Then create tests/test_cli.py with integration tests that run cli.main() and check the printed output with capsys:
   the report for 2026-10 shows "Claims: 7"; show C-1110 shows the AED conversion; show C-9999 returns 1.
   Run all the tests.
   ```

2. Review the diffs and keep them. Open `tests\conftest.py`: fixtures are found by **name**. A test that takes a parameter called `rates` gets the fixture.

**Checkpoint:** `tests\conftest.py` has the three fixtures; `test_currency.py` no longer sets `currency.RATES =` directly; `tests\test_cli.py` passes.
All tests pass: about **40 to 60**, depending on how many Copilot generated.

> **Unit test**: one function, inputs built in the test, no files. **Integration test**: the whole app through `cli.main()`, with real files.
> You need both: the unit tests say *which* rule broke, the integration tests say the pieces still fit together.

## Task 7: Find the gaps with coverage (7 min)

1. Run the tests with coverage:

   ```powershell
   python -m pytest --cov --cov-report=term-missing
   ```

2. Look at the **Missing** column: line numbers no test runs. Pick a file with missing lines, for example `currency.py`. **New Chat**, **Agent** mode:

   ```text
   #file:kavericlaims/currency.py Lines <the missing lines> aren't covered by any test. Add tests to tests/test_currency.py
   that cover them, using pytest.raises and the rates fixture. Run the tests with coverage again.
   ```

**Checkpoint:** coverage goes up, typically to **95% or more** in total, and `currency.py` reaches 100%.

> **Covered is not tested.** On the first run of this lab, the 3 original tests already covered over **80%** of the code, and they missed both bugs from Task 4.
> Coverage shows you what **no** test runs. Whether the tests that do run check the right thing is up to you.

Stuck? Compare your work with `day5\lab14-unit-tests\solution\`. The reference solution starts from the original Lab 13 baseline and contains the completed exercises for this lab.

---

## Summary

| To... | Use |
|---|---|
| Run, debug and re-run tests | The **Testing** view (pytest) |
| Think of what to test | **Ask** with the spec and the code: "list the edge cases" |
| Cover existing code fast | **Generate Code > Generate Tests** or `/tests`, then **check where the expected values came from** |
| Find real bugs | **Tests from requirements**: the spec's examples, parametrized |
| Fix a failing test | **Fix Test Failure** or `#testFailure`, and make sure it fixed the **code**, not the test |
| Understand a crash | `#terminalLastCommand` + "explain which file, line and data cause it" |
| Fix a bug safely | A **failing test first**, then the smallest change that makes it pass |
| Share set-up between tests | Fixtures in `conftest.py`; `monkeypatch` for globals; `tmp_path` for files |
| Find untested code | `pytest --cov --cov-report=term-missing` |

That's Day 5. On Day 6 you'll debug, consolidate duplicated code and break up large functions, starting with `claims.process()`.
