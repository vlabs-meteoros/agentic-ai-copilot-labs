# Lab 10: Analyze and Document Unfamiliar Code with GitHub Copilot

| | |
|---|---|
| **Duration** | 40 minutes |
| **Topic** | Prompt Engineering for code: explaining code, comments as prompts, existing code as examples, tests from existing functions, readability and documentation |
| **You need** | Copilot signed in (Day 3, Lab 7). No Azure keys |
| **Files** | Your own copy of the **KaveriDesk** app in `Desktop\kaveridesk` (Task 1 creates it). You'll use the same copy again in Lab 13 |

> Based on the Microsoft Learn exercise *Analyze and document code using GitHub Copilot*
> ([MicrosoftLearning/mslearn-github-copilot-dev](https://github.com/MicrosoftLearning/mslearn-github-copilot-dev), MIT licence), rewritten around a smaller Kaveri Systems app.

## Objectives

* Get a fast overview of a codebase you've never seen, with `#codebase`, `/explain` and a diagram
* Treat Copilot's explanation as a **hypothesis** and check it by running the code
* Write docstrings and better names with inline chat, and write code by typing a **comment as a prompt**
* Generate **unit tests from existing functions**, using the existing tests as an example
* Generate a README and a commit message

## The scenario

A colleague at **Kaveri Systems** wrote **KaveriDesk**, a small command-line tool that tracks IT helpdesk tickets and their **SLA** (the time the
team has to fix a ticket). Then they moved to another team. There's no documentation, the names are short and cryptic, and the tool is now yours.

---

## Task 1: Get your copy of KaveriDesk (5 min)

1. In VS Code (the window with the labs repository), open a terminal at the repository root and pull today's labs if you haven't yet:

   ```powershell
   git pull
   ```

2. Create your own copy of the app and open it:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\day4\start-kaveridesk.ps1
   ```

   The script copies `day4\kaveridesk` to `Desktop\kaveridesk`, makes it a Git repository with one commit, and opens it in a **new VS Code window**.
   Keep the old window open; you'll need it for Lab 12.

   * If VS Code asks **Do you trust the authors of the files in this folder?**, select **Yes, I trust the authors**.
   * If no window opens, use **File > Open Folder... > Desktop\kaveridesk** yourself.

3. **In the new window**, open a terminal (<kbd>Ctrl</kbd>+<kbd>`</kbd>). Activate the labs' Python and run the app and its tests:

   ```powershell
   & "$HOME\Desktop\agentic-ai-copilot-labs\.venv\Scripts\Activate.ps1"
   python -m kaveridesk --now "2026-11-20 11:00" list
   python -m unittest
   ```

   * If activation says *running scripts is disabled*, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal first.
   * If your labs repository isn't on the Desktop, use the activation command the script printed.

   `--now` makes the app pretend it's **Friday 20 November 2026, 11:00**, so everyone sees the same results.

**Checkpoint:** `list` shows **10 tickets**, three of them `BREACHED`. The tests print `Ran 7 tests` and `OK`.

> From here to the end of Lab 10, **work in the `kaveridesk` window**. Copilot only looks at the folder that is open, so `#codebase` now means just this app.

## Task 2: Get the big picture (8 min)

1. Open the Chat view (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>I</kbd>), select **New Chat**, choose **Ask** and keep the model on **Auto**. Send:

   ```text
   #codebase Describe this project for a new developer: what it does, what each file and folder is for,
   and how to run it.
   ```

   `#codebase` tells Copilot to search the whole workspace for the files it needs, instead of only the file you have open.

2. Ask for a picture. VS Code draws Mermaid diagrams right in the chat:

   ```text
   #codebase Draw a Mermaid diagram of how the Python modules in kaveridesk depend on each other.
   Show the data files too.
   ```

3. Now ask three questions a new owner would ask. Send them one at a time:

   ```text
   #codebase What do the priorities P1 to P4 mean, and what does the number 18 mean for P3?
   ```

   ```text
   #codebase When does the SLA clock run, and when is it stopped?
   ```

   ```text
   #codebase How does the app decide who a new ticket is assigned to?
   ```

4. **Check the last answer by running the code.** Create a ticket, look at who gets it, then undo the change to the data:

   ```powershell
   python -m kaveridesk --now "2026-11-20 11:00" new "Mouse not working" --category IT --priority P4 --requester you
   git restore data
   ```

**Checkpoint:** you can explain, in your own words, that:
* P1-P4 have SLAs of **4, 8, 18 and 45 business hours**, so 18 hours is **two working days**
* the clock runs **Monday to Friday, 09:00-18:00**, and skips the holidays in `data\holidays.json`
* a new ticket goes to the agent in the right team with the **fewest open tickets** who isn't full (`max_open`). Your new IT ticket went to **A03** (Imran Khan, who had none)

> **An explanation is a hypothesis.** Copilot reads the code well, but it can still be wrong, especially about edge cases.
> The quickest check is to **run the code** with an input whose answer you can predict.

## Task 3: Explain the hardest code and look for edge cases (8 min)

1. Open `kaveridesk\clock.py`. It has the trickiest logic and the worst names (`O`, `C`, `_wd`, `_nxt`, `h`, `t`).
2. Select the whole `_nxt` function. Right-click it and choose **Explain** (on some versions: **Copilot > Explain**). The explanation appears in the Chat view.
3. Ask a follow-up in the same chat. Examples make an explanation much easier to check:

   ```text
   Give me a table of 5 example inputs for _nxt (a datetime) and what it returns. Include a Saturday,
   an evening, an early morning and the holiday on 27 November 2026.
   ```

4. Now use Copilot to **look for edge cases**. Select **New Chat** and send:

   ```text
   #file:service.py #file:clock.py Is a ticket counted as breached at exactly its due time?
   Is the answer the same for open tickets and for resolved tickets? Point to the lines.
   ```

5. Check the answer against the app. Ticket INC-1013 is due **exactly** at 11:00:

   ```powershell
   python -m kaveridesk --now "2026-11-20 11:00" show INC-1013
   ```

**Checkpoint:** INC-1013 shows `BREACHED (100% of business hours used)`. Copilot points out that an **open** ticket counts as breached **at** its due time
(`used >= 1`), but a **resolved** ticket resolved at exactly its due time counts as **MET** (`resolved_at <= due`). The two rules don't agree.

> Don't fix it yet. Finding the question is the point: you'd now ask the business which rule is right. Note it for the README (Task 6).

## Task 4: Better names, docstrings, and comments as prompts (9 min)

**Docstrings**

1. In `clock.py`, select everything (<kbd>Ctrl</kbd>+<kbd>A</kbd>) and press <kbd>Ctrl</kbd>+<kbd>I</kbd> to open **inline chat**. Type `/doc` and press <kbd>Enter</kbd>.
2. Read the docstrings in the diff. Do they match what you learned in Task 3? Select **Keep** (or **Accept**) if they do.

**Better names**

3. Select everything again, press <kbd>Ctrl</kbd>+<kbd>I</kbd> and send:

   ```text
   Rename O, C, _wd, _nxt, h, t, left, tot and end to descriptive names. Keep the public function names
   add_bh and bh_between, because other files use them. Don't change any behaviour.
   ```

4. Review the diff and keep it. Then prove nothing broke:

   ```powershell
   python -m unittest
   ```

**Comments as prompts**

5. Go to the end of `clock.py` and type this comment, then press <kbd>Enter</kbd>:

   ```python
   # is_business_hours(moment, holidays=()): return True if moment is on a working day
   # (not a weekend or a holiday) and between opening and closing time
   ```

6. Type `def ` and wait for the ghost text. Press <kbd>Tab</kbd> to accept it (press <kbd>Enter</kbd> and <kbd>Tab</kbd> again if it suggests more lines).
   Copilot writes the function **from your comment**, and it reuses the constants and helpers already in the file:
   **your existing code is the example it follows**.
7. Try it with a Saturday and a Monday morning:

   ```powershell
   python -c "from datetime import datetime as d; from kaveridesk.clock import is_business_hours as f; print(f(d(2026,11,21,10,0)), f(d(2026,11,23,10,0)))"
   ```

**Checkpoint:** `clock.py` has docstrings and readable names, the 7 tests still pass, and your new function prints `False True`.

> **Comments as prompts work best when they say what, for which inputs, and with which rules**, like a tiny spec. A comment like `# check time` gets a guess.

## Task 5: Generate tests from existing functions (6 min)

The existing tests in `tests\test_service.py` show the team's style: `unittest`, a temporary copy of the data in `setUp`, and a fixed `NOW`.
Good tests for new code should look the same, so give Copilot that file **as an example**.

1. **New Chat**, switch to **Agent** mode, and send:

   ```text
   #file:tests/test_service.py is an example of how we write tests. Following the same style (unittest,
   the same setUp with a temporary copy of the data, the same NOW), create tests/test_rules.py with tests
   for Desk.state and Desk._pick in #file:kaveridesk/service.py. Cover:
   - a resolved ticket that met its SLA, and one that breached it
   - an open ticket that is AT RISK
   - an open ticket at exactly its due time (INC-1013)
   - a new Facilities ticket when Lakshmi Bhat (A08) is already full
   Use ticket IDs from data/tickets.json. Then run: python -m unittest
   ```

2. The agent creates the file and asks to run the command. Read it, select **Allow**, review the new file and select **Keep**.

**Checkpoint:** `python -m unittest` now runs **12 or more** tests and all pass.

> **Read the asserted values, not just the green result.** A generated test passes if it asserts what the code *does*, even when that's a bug.
> Does the INC-1013 test assert `BREACHED`? Then it documents today's behaviour, including the inconsistency from Task 3.

## Task 6: Write the README and commit (5 min)

1. **New Chat**, **Agent** mode:

   ```text
   #codebase Create README.md for this project with these sections: Description, How SLAs work
   (priorities, business hours, holidays, the AT RISK threshold), Project structure (a bullet list),
   Commands (one example per command, using --now "2026-11-20 11:00"), Running the tests, Known issues.
   Under Known issues, mention that open tickets are breached at exactly their due time but resolved
   tickets are not. Keep it under 120 lines.
   ```

2. Open `README.md` and **try two commands from it**. A README with a wrong command is worse than none.
3. Commit your work. Open **Source Control** (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>G</kbd>), select the **sparkle** icon in the message box to let Copilot write
   the commit message, edit it if needed, then select **Commit** (choose **Yes** if it asks to stage all changes).

**Checkpoint:** `README.md` exists, its example commands work, and Source Control shows **no** pending changes (your commit is in the history).

---

## Summary

| To... | Use |
|---|---|
| Understand a whole project | `#codebase` in **Ask** mode, plus a Mermaid diagram |
| Understand one function | Select it > **Explain** (or `/explain`), then ask for **examples** |
| Find edge cases | Ask a precise question with `#file:` context, then **run the code** to check |
| Add docstrings | Inline chat (<kbd>Ctrl</kbd>+<kbd>I</kbd>) > `/doc` |
| Write code from intent | A specific **comment as a prompt**, then <kbd>Tab</kbd> |
| Match the team's style | Attach existing code **as an example** |
| Tests for existing code | Agent mode with the existing tests as the example, then read every assert |

Keep the `kaveridesk` window: you'll add features to it in **[Lab 12](../lab12-agent-mode/README.md)**. Next: **[Lab 11](../lab11-voice-agent/README.md)**.
