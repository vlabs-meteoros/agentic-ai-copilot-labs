# Lab 13: Context, Legacy Code and Images in Copilot Chat

| | |
|---|---|
| **Duration** | 45 minutes |
| **Topic** | Copilot Chat & Agent Mode: working with context (files, folders, the codebase, instructions), explaining legacy code, multi-modal AI (an image and text together) |
| **You need** | Copilot signed in. Day 5 setup done. Task 6 also needs the Azure values in `.env` (same as Day 4) |
| **Files** | Your own copy of the **KaveriClaims** app in `Desktop\kavericlaims` (Task 1 creates it). You'll use the same copy in Labs 14 and 15. `copilot-instructions.md`, `tests.instructions.md` and `receipt_to_claim.py` in this folder |

## Objectives

* See how the **context** you give Copilot changes its answer: one file, another file, or the whole codebase
* Give Copilot standing rules with a repository-wide **instructions file** and a **path-specific** one (`applyTo`)
* **Explain legacy code** you didn't write, and check the explanation against the written policy and by running the code
* Send an **image and text together**: a receipt in Copilot Chat, then the same idea from Python with gpt-4.1-mini and Pydantic

## The scenario

Finance Ops at **Kaveri Systems** uses **KaveriClaims** to work out how much of each employee expense claim is paid back.
It was written in 2015 for Python 2, ported to Python 3 in 2019, and nobody has touched it since. The rules it should follow are written down
in `specs/policy.md`. Today the app is yours: in this lab you understand it, in Lab 14 you refactor it, and in Lab 15 you test it.

---

## Task 1: Get your copy of KaveriClaims (5 min)

1. In VS Code (the window with the labs repository), open a terminal at the repository root. If you haven't done *Before you start* yet, do it now.
2. Create your own copy of the app and open it:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\day5\start-kavericlaims.ps1
   ```

   The script copies `day5\kavericlaims` to `Desktop\kavericlaims`, makes it a Git repository with one commit, turns on pytest for it,
   and opens it in a **new VS Code window**. Keep the old window open: you need it in Task 6.

   * If VS Code asks **Do you trust the authors of the files in this folder?**, select **Yes, I trust the authors**.
   * If the new window shows a blue **Restricted Mode** bar at the top instead, select **Manage** in that bar, then **Trust**.
     In Restricted Mode, Agent mode and the Testing view don't work.
   * If no window opens, use **File > Open Folder... > Desktop\kavericlaims** yourself.

3. **In the new window**, open a terminal (<kbd>Ctrl</kbd>+<kbd>`</kbd>). Activate the labs' Python, then run the report and the tests:

   ```powershell
   & "$HOME\Desktop\agentic-ai-copilot-labs\.venv\Scripts\Activate.ps1"
   python -m kavericlaims report --month 2026-11
   python -m pytest
   ```

   * If activation says *running scripts is disabled*, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal first.
   * If your labs repository isn't on the Desktop, use the activation command the script printed.

**Checkpoint:** the report ends with `Claims: 22   Flagged: 10` and `Reimbursable: 60,138.50`. pytest prints `3 passed`.

> From here until Task 6, **work in the `kavericlaims` window**. Copilot only looks at the folder that is open.

## Task 2: The context decides the answer (7 min)

Copilot answers from the context you give it. Ask the **same question** with three different contexts.

1. Open the Chat view (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>I</kbd>), select **New Chat**, choose **Ask** and keep the model on **Auto**. Send:

   ```text
   #file:kavericlaims/policy.py What is the daily meal limit for a G3 employee in Mysuru? Answer from this file only.
   ```

2. Select **New Chat** and send the same question with a different file:

   ```text
   #file:specs/policy.md What is the daily meal limit for a G3 employee in Mysuru? Answer from this file only.
   ```

3. Select **New Chat** once more and let Copilot search the whole workspace:

   ```text
   #codebase What is the daily meal limit for a G3 employee in Mysuru? Say which files you used.
   ```

4. There are three ways to add context. Try one you haven't used yet:
   * type `#` and pick a file, a folder or a symbol from the list
   * **drag** a file or a whole folder (for example `specs`) from the Explorer onto the chat input
   * select **Add Context** (the paperclip or **+** next to the chat input) > **Files & Folders**

**Checkpoint:** with `policy.py` the answer is **₹600**. With `policy.md` it is **₹800**. With `#codebase`, the answer names the files it read, and it may
spot that the two disagree.

> **The same question gets a different answer from a different context.** Copilot didn't make a mistake: it reported what each file says.
> Choosing the context is part of writing the prompt. Keep the difference in mind: you come back to it in Task 4.

## Task 3: Standing instructions: one for the repository, one for the tests (6 min)

1. Copy the two prepared instructions files into your project:

   ```powershell
   New-Item -ItemType Directory -Force .github\instructions | Out-Null
   Copy-Item "$HOME\Desktop\agentic-ai-copilot-labs\day5\lab13-context-multimodal\copilot-instructions.md" .github\
   Copy-Item "$HOME\Desktop\agentic-ai-copilot-labs\day5\lab13-context-multimodal\tests.instructions.md" .github\instructions\
   ```

2. Open both files and read them.
   * `.github\copilot-instructions.md` is added to **every** chat request in this workspace: how to run things, and the project's rules.
   * `.github\instructions\tests.instructions.md` starts with `applyTo: "tests/**/*.py"`. Copilot adds it only when the work involves
     **test files**. Path-specific instructions keep the general file short.

3. Check the repository-wide file. **New Chat**, **Ask**:

   ```text
   How do I run the tests in this project, and which test framework should new tests use?
   ```

4. Check the test file rules. **New Chat**, **Ask**:

   ```text
   #file:tests/test_currency.py Review this test file against our rules for tests. List what doesn't follow them.
   ```

**Checkpoint:**
* The first answer says `python -m pytest` and **pytest**. Expand **References** (or **Used n references**) under the answer: `copilot-instructions.md` is listed.
* The review points out that `test_currency.py` sets the global `currency.RATES` **directly** instead of with `monkeypatch`, so one test can
  affect another. `tests.instructions.md` is usually in the References too. If it isn't, it still applies when Agent mode reads or edits files in `tests\`.

> You don't have to write these files by hand. In **Agent** mode, `/init` drafts a repository-wide file from the code, and `/create-instructions`
> drafts a path-specific one. Either way, read and edit what it writes: wrong instructions are followed as faithfully as right ones.

## Task 4: Explain legacy code, then check the explanation (10 min)

1. Open `kavericlaims\claims.py`. Select the whole `process` function, right-click it and choose **Copilot > Explain** (on some versions: **Explain**).
2. In the same chat, ask for the explanation in a form you can check:

   ```text
   Make a table with one row per category: which limit applies, whether the limit is shared between claims
   (and over which period), and which flags the category can set.
   ```

3. Legacy code often hides its data structure. Ask:

   ```text
   What do c[5], c[6], c[8] and e[1] hold? Where in the code are those positions defined?
   ```

4. **Check one row of the table by running the code.** Ananya Rao has two meal claims on 2 November:

   ```powershell
   python -m kavericlaims show C-1102 --month 2026-11
   ```

5. Now compare the code with the written policy. **New Chat**, **Ask**:

   ```text
   #file:kavericlaims/policy.py #file:specs/policy.md Do the limits in get_limit match tables A and B in the policy?
   List every difference with its line number.
   ```

6. Confirm the difference with a real claim. Priya Nair is a **G3** in **Mysuru**:

   ```powershell
   python -m kavericlaims show C-1105 --month 2026-11
   ```

**Checkpoint:**
* The table says MEAL limits are shared **per employee per day**, INTERNET **per employee per month**, HOTEL is per night times `qty`, OTHER is per claim
  and TRAVEL has no limit
* `c[5]` is the amount, `c[6]` the currency, `c[8]` the receipt and `e[1]` the grade. The positions are only written down in a **comment** in `storage.py`
* `show C-1102` gives **350.00** with `OVER_LIMIT`: the first claim that day already used 450.00 of the 800.00 limit
* Copilot finds one difference: G3, tier 2 meals are **600** in the code but **800** in the policy. `show C-1105` confirms that the app pays **600.00** instead of 750.00

> **Don't fix it yet.** In Lab 14 you refactor without changing behaviour, so the bug stays. In Lab 15 you write tests from the policy first, see them fail,
> and then fix it. Note that `e[1]` and `c[5]` made the explanation harder than it needed to be: that is the first thing Lab 14 fixes.

## Task 5: Multi-modal: a receipt image in Copilot Chat (7 min)

Kavya Shetty (E06, grade G2) had a breakfast meeting with a client in Mysuru and wants to claim the bill.

1. In the Explorer, open `receipts\CCW-2026-11873.png` to see the receipt.
2. **New Chat**, **Ask**. **Drag** the image from the Explorer onto the chat input (or select **Add Context** > **Files & Folders** and pick the image).
   It appears as an attachment above the input.
3. Send:

   ```text
   #file:specs/policy.md The attached receipt is from a breakfast meeting with a client in Mysuru, claimed by Kavya Shetty
   (E06, grade G2). Which lines are claimable as a MEAL? Work out the claimable amount, including those lines' share of the tax.
   Then write the claim as one row in the format of #file:data/claims_2026-11.csv, with claim ID C-1125 and status submitted.
   ```

   If Copilot says it can't see images, open the model picker and choose another model (most current models accept images), then send again.

4. Copilot read the receipt. Now **run the code** to see what the app would pay. Try the new row on a temporary copy of the data (the real `data` folder stays untouched):

   ```powershell
   $tmp = "$env:TEMP\kc-data-$(Get-Random)"
   Copy-Item data $tmp -Recurse
   Add-Content "$tmp\claims_2026-11.csv" "C-1125,E06,2026-11-15,MEAL,Mysuru,225.75,INR,1,CCW-2026-11873.png,submitted,Client breakfast"
   python -m kavericlaims --data $tmp show C-1125 --month 2026-11
   ```

   If Copilot's row has a different amount, use its amount in the `Add-Content` line.

**Checkpoint:**
* Claimable: **Filter Coffee x2** (120.00) and **Masala Dosa** (95.00). **Coffee Beans 500g** isn't (groceries). The **Mysore Pak (250g)** box is take-home sweets,
  so most answers leave it out
* Amount: **₹225.75** (215.00 plus 10.75 tax), or **225.76** if Copilot rounds each tax line separately. Date `2026-11-15`, category `MEAL`, city `Mysuru`
* The app pays **0.00** with `OVER_LIMIT`: *600.00 already used that day*. Kavya's lunch claim C-1115 on the same day had already used up her G2 tier 2 limit

> **Vision reads the picture; the code applies the rules.** Copilot read every line correctly, but it didn't look for her other claims that day.
> Whether the Mysore Pak counts is a policy question, not an AI one: ask Finance Ops, then make the policy say so.

## Task 6: Multi-modal from Python: image + text to a checked claim (8 min)

Copilot Chat is for you, the developer. To build the same thing **into an app**, you call a vision model yourself.

1. Switch to the **labs repository** window. In its terminal (with the `.venv` active), run:

   ```powershell
   python day5\lab13-context-multimodal\receipt_to_claim.py
   ```

2. Read the output from top to bottom: the lines the model read and marked `CLAIM`, then the numbers **checked in Python**, then the draft CSV row.
3. Open `day5\lab13-context-multimodal\receipt_to_claim.py` and find `build_messages`. One user message carries a **list of parts**: a text part,
   then an `image_url` part holding the PNG as a base64 `data:` URL. That is all "multi-modal input" means at the API level.
   The `DraftClaim` Pydantic model is sent as the response schema (Day 4, Lab 11), so the answer always has this shape.
4. Run the same request **without** the image:

   ```powershell
   python day5\lab13-context-multimodal\receipt_to_claim.py --no-image
   ```

5. Add a field with Copilot. In `receipt_to_claim.py`, put the cursor on the `TODO (Lab 13, Task 6)` line in `DraftClaim`, press <kbd>Ctrl</kbd>+<kbd>I</kbd> and send:

   ```text
   Replace this TODO with a field payment_method: how the bill was paid, as printed on the receipt.
   ```

   Accept it and run the script again (without `--no-image`).

**Checkpoint:**
* With the image: four lines, two marked `CLAIM`, and the Python check shows a claimable amount of **225.75**. The token count is a few thousand: the image costs tokens too
* Without the image: the answer still has **exactly the same shape**, but the merchant is empty or made up and the numbers are zeros or invented
* After your edit, the output ends with `your new field(s): {'payment_method': 'UPI'}` (or *Paid via UPI*)

> **A schema guarantees the shape of the answer, not the truth of it.** Without the image, the model still had to fill in every field.
> That's why the script checks the arithmetic in Python, and why a person checks the draft before it becomes a claim.

---

## Summary

| To... | Use |
|---|---|
| Point Copilot at exactly the right code | `#file:`, a dragged file or folder, or **Add Context** |
| Let Copilot find the code itself | `#codebase`, and ask it to name the files it used |
| Give rules for every request | `.github/copilot-instructions.md` (or `/init`) |
| Give rules for some files only | `.github/instructions/*.instructions.md` with `applyTo` |
| Understand legacy code | **Explain**, then ask for a **table** and **run the code** to check one row |
| Check code against requirements | Attach the code **and** the spec, and ask for differences with line numbers |
| Use an image | Drag it into Chat; from Python, send a `text` part and an `image_url` part in one message |

Keep the `kavericlaims` window open. Next: **[Lab 14: Refactor and Improve Existing Code](../lab14-refactor/README.md)**.
