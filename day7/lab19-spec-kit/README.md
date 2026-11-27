# Lab 19: Implement a Product Feature with GitHub Spec Kit (JavaScript)

| | |
|---|---|
| **Duration** | 70 minutes |
| **Topic** | Using GitHub Copilot with JavaScript: the Copilot extension, crafting prompts, improving a JavaScript project. Spec-driven development with GitHub Spec Kit |
| **You need** | Day 7 setup done (*Before you start* in the [Day 7 README](../README.md)), Copilot signed in, Node.js (`node --version` shows v18 or later) |
| **Files** | Your own copy of **KaveriRooms** in `Desktop\kaverirooms` (Task 1 creates it). `docs\FR-12-recurring-bookings.md` in your copy; `acceptance\` and `solution\` in this folder |

> [!IMPORTANT]
> This lab is optional. Feel free to explore it whenever you have some free time. You can skip it if your schedule is tight.

## Objectives

* Ask Copilot Chat **coding questions about JavaScript** in a real project, and check the answers against the code
* Set up **GitHub Spec Kit** in an existing project and see what it adds for Copilot
* Go from a feature request to working code in Spec Kit's steps: **constitution, specify, clarify, plan, tasks, implement**
* **Review** each step's document before moving on, and check the result against an **acceptance test** you didn't write

## The scenario

**KaveriRooms** is the meeting-room booking app for the Kaveri Systems office in Mysuru: a small Node.js API and a browser page, no npm packages.
Facilities has asked for **recurring weekly bookings** (feature request FR-12). Instead of typing "add recurring bookings" into Agent mode and hoping,
you'll use **Spec Kit**: Copilot writes a spec, a plan and a task list first, you review each one, and only then does it write code.

> **Spec Kit in one sentence:** the specification is the source of truth; the plan, the tasks and the code are generated from it, and each step is a document you can read and fix.
> Spec Kit adds *skills* to Copilot: `/speckit-constitution`, `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`.

---

## Task 1: Get your copy of KaveriRooms (6 min)

1. In VS Code (the window with the labs repository), open a terminal at the repository root and run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\day7\start-kaverirooms.ps1
   ```

   It copies the app to `Desktop\kaverirooms`, makes it a Git repository with one commit, and opens it in a **new VS Code window**.
   If the new window shows a **Restricted Mode** bar, select **Manage** > **Trust**.
2. In the **new** window, open a terminal (<kbd>Ctrl</kbd>+<kbd>`</kbd>) and run the tests:

   ```powershell
   node --test
   ```

3. Start the app and look at it:

   ```powershell
   node src/server.js
   ```

   Open **http://localhost:3000/?date=2026-12-08** in the browser. Try to book **Kabini** on 8 December, 09:00-10:00. Then book it 10:00-11:00.
   Go to **25 December** with the arrows. Stop the server with <kbd>Ctrl</kbd>+<kbd>C</kbd> when you're done.

**Checkpoint:** `node --test` ends with `# pass 21` and `# fail 0`. The first booking fails with *kabini is already booked 09:00-09:30 on 2026-12-08 (B-1006)*;
the second one works. 25 December shows *Office closed: Christmas*.

## Task 2: Ask Copilot about the JavaScript (10 min)

You're new to this codebase. Use Copilot Chat in **Ask** mode to learn it, and check every answer against the code.

1. **New Chat**, **Ask** mode:

   ```text
   #codebase Give me a tour of this project: what each file in src/ does, and what happens, file by file, when the browser books a room.
   ```

2. Open `src\rules.js`, select the `overlaps` function, and ask:

   ```text
   #selection Explain this check. Why are 09:00-10:00 and 10:00-11:00 not overlapping? Give me three test cases at the edges.
   ```

3. Open `src\server.js`. Select the `readJsonBody` function and ask:

   ```text
   #selection Explain the Promise in this function: what resolve and reject are, and how the caller in handle() waits for it.
   What happens if the body isn't JSON?
   ```

4. Ask about the language itself:

   ```text
   #file:src/server.js What does `require.main === module` do at the bottom of this file, and why do the tests need it?
   ```

5. Use **inline chat** to improve one thing: open `src\store.js`, put the cursor inside `nextBookingId`, press <kbd>Ctrl</kbd>+<kbd>I</kbd> and type
   `Explain this line by line in a short comment above it`. Read the comment before you **Accept** it; **Discard** it if it's wrong.

**Checkpoint:** the tour names the four files in `src\` and the path *browser `app.js` → `POST /api/bookings` → `createBooking` → `validateBooking`, `findConflict` → `saveBookings`*.
End times are **exclusive**: one meeting can start the moment the last one ends. `readJsonBody` turns Node's `data`/`end` events into a Promise;
`handle()` waits with `await`, and a bad body becomes a **400** because the server turns a rejected `BookingError` into a response.
`require.main === module` is true only when you run `node src/server.js`, so the tests can `require` the file without starting a server on port 3000.

> **Ask, then check.** Copilot's tour is a fast first read, not the truth. If an answer names a function, select it and look.

## Task 3: Add Spec Kit to the project (5 min)

Setup put Spec Kit's command-line tool, `specify`, in the labs' Python environment (or in `.speckit-venv` if your `.venv` is Python 3.10).
The KaveriRooms window's terminals can already run it.

1. In the KaveriRooms terminal:

   ```powershell
   specify version
   specify init --here --integration copilot --script ps --force
   ```

   `--here` uses this folder, `--integration copilot` sets it up for GitHub Copilot, `--script ps` uses PowerShell scripts, and `--force` merges into a folder that isn't empty.
2. Look at what it added in the **Explorer**: `.github\skills\` (one folder per Spec Kit command) and `.specify\` (templates, scripts and `memory\constitution.md`).
   Open `.github\skills\speckit-specify\SKILL.md` and skim it: this is the prompt Copilot follows when you type `/speckit-specify`.
3. In the Chat view, switch to **Agent** mode and type `/speckit` in the chat box. The Spec Kit commands appear in the list. Don't send anything yet.
4. Commit (Source Control, sparkle for the message).

**Checkpoint:** `specify init` ends with **Project ready.** and lists the next steps `/speckit-constitution` ... `/speckit-implement`.
Your existing files (including `.github\copilot-instructions.md`) are unchanged: `git status` shows only new `.github/skills/` and `.specify/` folders.

> **`specify` is not recognized?** Your copy was probably made before setup could install Spec Kit (a `.venv` on Python 3.10 needs the newer setup).
> In the **labs** window, run `git pull` and setup again (*Before you start* in the [Day 7 README](../README.md)), then try `specify version` again in the KaveriRooms terminal.
> If it's still not recognized, setup put Spec Kit in `.speckit-venv` (your `.venv` is Python 3.10). Run it from there:
>
> ```powershell
> $specify = Join-Path (Split-Path (Split-Path (Split-Path $env:SPECKIT_PYTHON_EXECUTABLE))) ".speckit-venv\Scripts\specify.exe"
> & $specify version
> & $specify init --here --integration copilot --script ps --force
> ```
>
> The first line finds Spec Kit in the labs folder. You only need `specify` in this task; the later steps run in Copilot Chat.

> If the `/speckit-...` commands don't appear, reload the window (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> > **Developer: Reload Window**).

## Task 4: The constitution (5 min)

The **constitution** holds the rules every feature must follow. Spec Kit checks the plan against it later.

1. **New Chat**, **Agent** mode, and send (one message):

   ```text
   /speckit-constitution Create the KaveriRooms constitution from these principles:
   1. Simple and dependency-free: Node.js 18+, CommonJS, built-in modules only. No npm packages, no build step, no browser framework.
   2. Rules in one place: office rules live in src/rules.js and booking logic in src/ modules, never in server.js or the browser code.
   3. Every rule has a test: each rule in a spec gets a node:test test; tests never touch data/; node --test passes before work is done.
   4. Don't break the API: existing endpoints and responses stay compatible; errors are {"error": "..."} with 400, 404 or 409.
   5. Explain every refusal: when the app refuses or skips something, it says why in plain words.
   Governance: the constitution wins over any plan; changing it needs a version bump and a reason.
   ```

2. Open `.specify\memory\constitution.md`. Check that all five principles are there, with your wording, and a version and date at the bottom.
   If anything is missing or invented, tell Copilot in the same chat.

**Checkpoint:** the constitution has five principles and a **Version** line (usually `1.0.0`). Commit.

## Task 5: Specify: what and why, not how (10 min)

1. Open `docs\FR-12-recurring-bookings.md` and read it (3 minutes). Note the 9 rules and the API in *Technical notes*.
2. **New Chat**, **Agent** mode:

   ```text
   /speckit-specify Recurring weekly bookings for KaveriRooms, as described in docs/FR-12-recurring-bookings.md.
   Read that file first: it is the source of truth, including its rules, technical notes and what is out of scope.
   ```

   Copilot runs a Spec Kit script (select **Allow** after you've read the command) and writes `specs\001-...\spec.md`.
3. Review `spec.md` like a product owner. Look for:
   * **User stories** with priorities (P1, P2, ...) and *Given / When / Then* acceptance scenarios
   * **Functional requirements** (`FR-001`, ...): can you find each of the 9 rules from the request?
   * **Edge cases**: a series across the year end, `weeks` of 1 or 13, a Saturday start, no free week at all
   * Any `[NEEDS CLARIFICATION: ...]` markers
4. If a rule is missing or wrong, say so in the same chat, for example: `Rule 7 is missing: if no week can be booked, nothing is saved and the request fails.`

**Checkpoint:** a folder like `specs\001-recurring-bookings\` with `spec.md` (and often `checklists\requirements.md`). Every one of the 9 rules maps to at least one requirement.
Commit.

> **Why no code yet?** A spec is cheap to change and easy to review with Facilities. A wrong assumption found here costs one sentence; found in Task 9, it costs a re-implementation.

## Task 6 (optional): Clarify (5 min)

1. Same chat, or **New Chat**, **Agent** mode: `/speckit-clarify`
2. Copilot asks up to five questions, one at a time, usually with a recommended answer. Answer from the feature request where you can.
   Where the request doesn't say, decide as the product owner would, for example:
   * *A series number for each new series?* → `S-1001`, `S-1002`, ... (it's in the technical notes)
   * *If the first week is a holiday?* → skip it like any other week
3. Check that each answer was written into `spec.md` (a **Clarifications** section, and the requirement it changed).

**Checkpoint:** `spec.md` has a `## Clarifications` section with today's date and your answers. Commit.

## Task 7: Plan: how, in this codebase (8 min)

1. **New Chat**, **Agent** mode:

   ```text
   /speckit-plan Use the existing stack: Node.js 18+, CommonJS, node:http and node:test, no packages.
   Follow the API in the Technical notes of docs/FR-12-recurring-bookings.md exactly.
   Put the series logic in a new src/series.js that reuses validateBooking and findConflict from src/bookings.js.
   Store seriesId on each booking in data/bookings.json. Update public/app.js and index.html for the form and the day view.
   ```

2. Open the new files in `specs\001-...\`: `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts\`. In `plan.md`, find the **Constitution Check**:
   did each of your five principles pass?
3. Check the plan against the technical notes: `POST /api/series` returns **201** / **400** / **409**, `DELETE /api/series/:seriesId` returns **200** `{ "cancelled": n }` / **404**.

**Checkpoint:** `plan.md` lists `src/series.js` as new, and `src/server.js`, `src/store.js`, `public/app.js` and `public/index.html` as changed, and no npm packages.
The Constitution Check passes. Commit.

## Task 8: Tasks (4 min)

1. **New Chat**, **Agent** mode: `/speckit-tasks`
2. Open `tasks.md`. Tasks are numbered (`T001`, ...), grouped by user story, and marked `[P]` when they can run in parallel. Check that:
   * there are **test tasks** (principle 3), and they come **before** the code they test
   * the order makes sense: shared helpers, then booking a series, then skipping, then cancelling, then the browser page
3. (Optional) `/speckit-analyze` checks that the spec, plan and tasks agree. Read its report; fix anything marked **CRITICAL** or **HIGH**.

**Checkpoint:** `tasks.md` with roughly 15-30 tasks in phases. Commit.

## Task 9: Implement (15 min)

1. **New Chat**, **Agent** mode:

   ```text
   /speckit-implement Work through tasks.md in order. Run node --test after each phase and fix failures before going on.
   Tick each task in tasks.md when it's done.
   ```

2. While it works: read each command before you select **Allow**, and watch `tasks.md` fill with `[X]`. If it asks to install an npm package, say no:
   the constitution says no packages.
3. When it's done, run the tests yourself, then try the feature in the browser:

   ```powershell
   node --test
   node src/server.js
   ```

   Open http://localhost:3000/?date=2026-12-04 and book **Kabini**, Friday **4 December**, 10:00-11:00, `Design review`, 4 people, **6 weeks**.
   Use the arrows to find the next Fridays. Then stop the server.

**Checkpoint:** all tests pass. The browser says 4 of 6 weeks were booked, and 25 December and 1 January were skipped as holidays.
The series bookings are marked in the day view. Commit.

> If the agent stops halfway (for example after the API, before the browser page), run `/speckit-implement` again: it continues from the unticked tasks.

## Task 10: The acceptance test (7 min)

Facilities' tester wrote an **acceptance test** from FR-12 alone. It doesn't know how your code works inside: it only calls the API.

1. Copy it from the labs repository into your app (in the KaveriRooms terminal):

   ```powershell
   Copy-Item "$HOME\Desktop\agentic-ai-copilot-labs\day7\lab19-spec-kit\acceptance\series.acceptance.test.js" test\
   node --test
   ```

2. If a test fails, **don't change the acceptance test**. **New Chat**, **Agent** mode:

   ```text
   test/series.acceptance.test.js fails (see #terminalLastCommand). The acceptance test follows docs/FR-12-recurring-bookings.md.
   Find which requirement in our spec or plan is different from FR-12, fix the spec first, then the code. Don't change the acceptance test.
   ```

3. When everything passes, commit.

**Checkpoint:** `node --test` passes, including the 14 acceptance tests (`# fail 0`).
The common misses are the exact skip reasons (`holiday: Christmas`, `conflict with B-1003`), the **409** when no week is free, and `{ "cancelled": n }`.

> Stuck, or the agent went in circles? Compare with `day7\lab19-spec-kit\solution\` in the labs repository: `src\series.js`, the changed files,
> tests, and an example `spec.md`. It's **one** good answer, not the only one.

---

## Summary

* Copilot Chat is a fast way into unfamiliar JavaScript: ask with `#codebase`, `#file` or `#selection`, then **check** the answer in the code.
* Spec Kit turns one big prompt into small, reviewable steps: **constitution → spec → (clarify) → plan → tasks → implement**.
* The **spec** is about what and why; the **plan** is about how, in your codebase; the **constitution** keeps every plan honest.
* You review a document at every step. The cheapest bug to fix is a wrong sentence in the spec.
* An acceptance test written from the request, not from the code, tells you whether you built what was asked.

Next: **[Lab 20: Add New Features to an Existing Python App](../lab20-add-features/README.md)**.
