# Lab 12: Build New Features with GitHub Copilot Agent Mode

| | |
|---|---|
| **Duration** | 50 minutes |
| **Topic** | Agent Mode: ask, explain, transform and summarize code; Copilot (chat and inline) vs Agent; when to use Agent, Chat or Inline; generating an API from requirements |
| **You need** | Your `Desktop\kaveridesk` window from Lab 11 (if you skipped Lab 11, run Lab 11 Task 1 first). Day 4 setup done (it installs FastAPI) |
| **Files** | `specs\escalation.md` and `specs\api.md` in your `kaveridesk` copy; `copilot-instructions.md` and `solution\` in this folder |

> Based on the Microsoft Learn exercise *Develop code features using GitHub Copilot tools*
> ([MicrosoftLearning/mslearn-github-copilot-dev](https://github.com/MicrosoftLearning/mslearn-github-copilot-dev), MIT licence), rewritten for the KaveriDesk app.

## Objectives

* Pick the right tool for the size of the change: **inline chat**, **Ask**, **Plan** or **Agent**
* Give the agent standing **instructions** (how to run and test this project) so you don't repeat them in every prompt
* Turn a written **spec** into a multi-file feature with tests, and review it like a pull request (**you are the human in the loop**)
* Generate a small **REST API from requirements** with FastAPI and try it in the browser

## Copilot vs Agent in one table

| | **Inline chat** (<kbd>Ctrl</kbd>+<kbd>I</kbd>) | **Ask** | **Plan** | **Agent** |
|---|---|---|---|---|
| What it does | Changes the code you selected, in place | Answers, explains, summarises; suggests code you apply yourself | Researches the code and writes a step-by-step plan; changes nothing | Edits many files, runs commands and tests, fixes its own errors, until the task is done |
| Best for | Small, local edits in one file | Understanding and deciding | Big or unclear tasks, before Agent starts | A feature or fix across several files |
| Your job | Accept or discard the diff | Decide what to do with the answer | Correct the plan, answer its questions | Approve commands, **review every diff**, run the tests yourself |

---

## Task 1: Give the agent its instructions (5 min)

1. Switch to the **kaveridesk** VS Code window. Open a terminal and activate the labs' Python (as done in earlier Lab):

   ```powershell
   & "$HOME\Desktop\agentic-ai-copilot-labs\.venv\Scripts\Activate.ps1"
   ```

2. Copy the prepared instructions file into your project:

   ```powershell
   New-Item -ItemType Directory -Force .github | Out-Null
   Copy-Item "$HOME\Desktop\agentic-ai-copilot-labs\day4\lab12-agent-mode\copilot-instructions.md" .github\
   ```

3. Open `.github\copilot-instructions.md` and read it. Copilot adds this file to **every** chat request in this workspace automatically:
   how to activate Python, how to run the tests, and the project's rules.

4. Check that Copilot uses it. **New Chat**, **Ask** mode:

   ```text
   How do I run the tests in this project, and which test framework should new tests use?
   ```

**Checkpoint:** the answer says `python -m unittest` and **unittest, not pytest**. Expand the **References** (or **Used n references**) line under
the answer: `copilot-instructions.md` is listed.

> You can also let Copilot write this file: in **Agent** mode, type `/init`. It studies the project and drafts the instructions for you to edit.

## Task 2: Small changes: inline chat and Ask (7 min)

**Inline chat for a small, local change**

1. Open `kaveridesk\cli.py`. Select the `cmd_list` function **and** the lines in `build()` that create the `list` parser
   (or simply select the whole file). Press <kbd>Ctrl</kbd>+<kbd>I</kbd> and send:

   ```text
   Add a --priority option (P1 to P4, not case-sensitive) to the list command that shows only tickets with that priority.
   ```

2. Review the diff and accept it. Test it:

   ```powershell
   python -m kaveridesk --now "2026-11-20 11:00" list --priority p2
   ```

**Ask mode to summarise and explain**

3. **New Chat**, **Ask** mode:

   ```text
   #file:cli.py Summarise every command of this CLI in a table: command, options, what it prints.
   ```

**Checkpoint:** `list --priority p2` shows **4 tickets** (INC-1009, INC-1013, INC-1007, INC-1011). The Ask answer is a table that already includes your new option.

> Inline chat was enough here: one file, a few lines, and you could check the result at a glance. Starting an agent for this costs more time than it saves.

## Task 3: Plan a bigger feature (8 min)

The Service Desk managers want a feature: open `specs\escalation.md` and read it. It touches the data model, the service, the CLI and the tests.
That's a job for an agent, but **plan it first**.

1. **New Chat**, select **Plan** in the agent picker (if your VS Code has no **Plan**, use **Ask**). Send:

   ```text
   #file:specs/escalation.md Plan how to implement this feature in this codebase.
   List the files you would change and why, the tests you would add, and any questions about the spec.
   ```

2. Read the plan. Check it against the spec:
   * Does it add an `escalated` field **with a default of false**, so old `tickets.json` files still load (requirement 4)?
   * Does it reuse `Desk.state()` instead of a new SLA calculation (requirement 8)?
   * Did it ask a sensible question? Answer it in the chat, or tell it to follow the spec as written.

**Checkpoint:** the plan names `models.py`, `service.py`, `cli.py` and a new `tests/test_escalation.py`, and keeps the SLA rules unchanged.

## Task 4: Let the agent build it, then review it (12 min)

1. In the **same chat** (so the plan is in context), switch to **Agent** and send:

   ```text
   Implement the plan for #file:specs/escalation.md. Add the tests the spec asks for, then run all the tests.
   ```

2. Watch the agent work. It reads files, edits several of them, and asks to run commands such as `python -m unittest`.
   **Read each command before you select Allow.** If a test fails, the agent reads the error and fixes the code by itself. That loop is what makes it an agent.
3. When it's done, **review like a pull request**. For each changed file, read the diff and select **Keep** or **Undo**. Ask yourself:
   * Did it change anything the spec didn't ask for? (for example the SLA calculation, or the data files)
   * Do the tests check the spec's examples, or only that "something happened"?
4. Test it yourself:

   ```powershell
   python -m kaveridesk --now "2026-11-20 11:00" escalate --dry-run
   python -m kaveridesk --now "2026-11-20 11:00" escalate
   python -m kaveridesk --now "2026-11-20 11:00" escalate
   python -m kaveridesk --now "2026-11-20 11:00" show INC-1009
   python -m unittest
   ```

5. Undo the data changes from your manual test, then commit the feature (Source Control, sparkle for the message, **Commit**):

   ```powershell
   git restore data
   ```

**Checkpoint:**
* The dry run lists **4 tickets**: INC-1003 (A05 -> A05), INC-1009 (A02 -> A01), INC-1013 (A04 -> A04) and INC-1005, which is **AT RISK** (A08 -> A07)
* The second real run prints `Nothing to escalate.`
* `show INC-1009` shows `Escalated: yes` and a note `...was assigned to A02`
* All tests pass (about 16 or more, depending on how many you added in Lab 11)

> Stuck, or the agent went in circles? Compare with `day4\lab12-agent-mode\solution\` in the labs repository. It's **one** good answer, not the only one.

## Task 5: Generate an API from requirements (13 min)

The intranet team wants a JSON API. Open `specs\api.md` and read it: endpoints, status codes, validation rules and tests are all written down.
A precise spec is the best prompt.

1. **New Chat**, **Agent** mode:

   ```text
   Implement #file:specs/api.md. Follow the project instructions. Add the tests the spec asks for and run all the tests.
   ```

2. Approve the commands you're happy with, review the diffs and keep them.
3. Start the API in the terminal:

   ```powershell
   $env:KAVERIDESK_NOW = "2026-11-20 11:00"
   python -m uvicorn kaveridesk.api:app --port 8000
   ```

   If Windows asks whether Python may use the network, choose **Allow** (private networks).

4. In the browser, open <http://127.0.0.1:8000/docs>. This page is **generated** from your FastAPI code and its Pydantic models. Try:
   * `GET /tickets` with `team` = `security ops`
   * `GET /tickets/{ticket_id}` with `INC-9999`
   * `POST /tickets` (**Try it out**) with `{"title": "Hi", "category": "IT", "requester": "you"}`, then with a proper title
5. Stop the server with <kbd>Ctrl</kbd>+<kbd>C</kbd>, run `git restore data` and commit.

**Checkpoint:**
* `team=security ops` returns **INC-1013** and **INC-1004**
* `INC-9999` returns **404** `{"detail": "No ticket INC-9999"}`
* The short title returns **422**; the proper one returns **201** with `"assignee": "A03"`
* `python -m unittest` passes, including the new `tests/test_api.py`

> **Generating APIs from requirements** works when the requirements say what a tester would check: paths, status codes, validation rules, examples.
> Vague requirements ("make an API for tickets") give you an API that *looks* right, with every edge case guessed.

## Task 6: Choose the right mode (5 min)

For each request, decide: **Inline**, **Ask**, **Plan** or **Agent**? Discuss with your neighbour, then check with the trainer.

| # | Request |
|---|---|
| 1 | "Rename the variable `u` in `Desk.state` to `fraction_used`" |
| 2 | "Why does `bh_between` return 0 when the end is before the start?" |
| 3 | "Add CSV export of the list command, with tests" |
| 4 | "Move the app from JSON files to SQLite" |
| 5 | "Make this error message friendlier" (one line selected) |
| 6 | "Which of our 5 teams has the worst SLA record, and why might that be?" |

---

## Summary

* **Inline** for small, local edits. **Ask** to understand, summarise and decide. **Plan** before big or unclear work. **Agent** for multi-file tasks that need running and testing.
* **Instructions files** give the agent the project's commands and rules once, for every prompt.
* A **written spec** is the best prompt for a feature or an API: the agent can implement it, and you can review against it.
* The agent makes the changes, but **you** own them: read every command before you allow it, review every diff, and run the tests yourself.

That's Day 4. On Day 5 you'll refactor existing code and write unit tests with Copilot.
