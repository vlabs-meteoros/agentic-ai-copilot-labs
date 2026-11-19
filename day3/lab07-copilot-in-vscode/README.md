# Lab 7: Enable and Explore GitHub Copilot in VS Code

| | |
|---|---|
| **Duration** | 35 minutes |
| **Topic** | Prompting Fundamentals: how GitHub Copilot responds to your instructions |
| **You need** | Your company GitHub account with a **GitHub Copilot Business** seat (your trainer confirms this) |
| **Files** | You create them in `day3\lab07-copilot-in-vscode\outputs\` (Git ignores this folder) |

> Adapted from the Microsoft Learn exercises *Enable GitHub Copilot in Visual Studio Code* and *Examine GitHub Copilot settings and user interface features*
> ([MicrosoftLearning/mslearn-github-copilot-dev](https://github.com/MicrosoftLearning/mslearn-github-copilot-dev), MIT licence), shortened for the lab VM and Python.

## Objectives

* Sign in to GitHub Copilot in VS Code and check that your Business seat is active
* Find the Copilot settings that matter (turn suggestions on and off, per language)
* Use the four ways to talk to Copilot: **Chat view**, **Quick Chat**, **Inline Chat** and **Smart Actions**
* See the difference between **Ask** mode (Copilot answers) and **Agent** mode (Copilot edits your files)
* Accept code completions (ghost text) and **next edit suggestions**

> **Copilot changes every month.** Buttons move and get renamed between VS Code versions. If a step doesn't match your screen exactly,
> look for the closest option, or hover over the icons for their names. The ideas stay the same.

---

## Task 1: Sign in to GitHub Copilot (5 min)

1. In VS Code, open **Help > About** and note the version. If it's older than about six months, run **Help > Check for Updates** (or ask your trainer).
2. At the bottom right of the window (the **Status Bar**), find the **Copilot icon** (a small face with goggles). Hover over it and select **Set up Copilot** or **Sign in**.

   * No Copilot icon at all? Open the Extensions view (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>X</kbd>), search for **GitHub Copilot Chat** and install it.

3. A browser window opens. Sign in with the **GitHub account that has your Copilot Business seat**, then select **Authorize Visual Studio Code**. Allow the browser to open VS Code again.

   * If VS Code shows a page that offers *Copilot Free*, still choose **Sign in**: once you sign in with your company account, Copilot picks up the Business seat.

4. Back in VS Code, select the Copilot icon in the Status Bar again. The menu now shows your account and Copilot status.

**Checkpoint:** the Copilot status menu opens without asking you to sign in. In the browser, `https://github.com/settings/copilot` says Copilot Business is active and **managed by your organization**.

> **Business vs Free:** with Copilot Business, your organization's admins decide the policies (for example, which models you can pick, whether suggestions matching public code are blocked, and whether MCP servers are allowed). That's why some options on the GitHub settings page are greyed out for you.

## Task 2: Copilot settings (5 min)

1. Select the **Copilot icon** in the Status Bar. Expand **Inline Suggestions** and look at the options:
   * turn suggestions off everywhere, or only for the current file's language
   * **Snooze** them for 5 minutes (useful when you're presenting or typing something Copilot keeps guessing wrong)
2. Open the Chat view: select the **Toggle Chat** icon next to the search bar at the top, or press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>I</kbd>.
3. In the Chat view, select **...** (top right) > **Settings**. The Settings editor opens, filtered to the chat settings. Scroll through them; settings marked **Preview** or **Experimental** may change. **Keep the defaults during this training.**
4. In the Settings search box, type `GitHub Copilot Enable`. You see a list of languages with `true`/`false`.
5. **markdown** is `false` by default, so Copilot doesn't suggest text while you write Markdown. Select the pencil icon, change it to `true` and select **OK**.
6. Close the Settings editor.

**Checkpoint:** `markdown` is now `true` in the **GitHub Copilot: Enable** list.

## Task 3: The Chat view and Ask mode (6 min)

1. Look at the bottom of the Chat view, from left to right:

   | Element | What it does |
   |---|---|
   | **Add Context** (paperclip or `#`) | Attach files, folders, selections, or tools so Copilot knows what you're talking about |
   | **Agent picker** (Ask / Plan / Agent) | **Ask** answers questions. **Plan** breaks a big task into steps. **Agent** edits files and runs commands for you |
   | **Model picker** | Chooses the model. **Leave it on Auto** in this training |
   | **Configure Tools** (in Agent mode) | The tools the agent may use: built-in ones and **MCP servers** (Lab 10) |
   | **Send** | Submits the prompt (or press <kbd>Enter</kbd>) |

2. Select **Ask** and the model **Auto**. Send this prompt:

   ```text
   Create a Python console app that prints Hello World to the console.
   ```

   In Ask mode, Copilot **explains** what to do, but it doesn't create anything.

3. Do it yourself in the VS Code terminal (<kbd>Ctrl</kbd>+<kbd>`</kbd>), at the repository root:

   ```powershell
   New-Item -ItemType Directory -Force day3\lab07-copilot-in-vscode\outputs | Out-Null
   Set-Content day3\lab07-copilot-in-vscode\outputs\hello.py "print('Hello World')"
   .\.venv\Scripts\python.exe day3\lab07-copilot-in-vscode\outputs\hello.py
   ```

**Checkpoint:** the terminal prints `Hello World`.

## Task 4: Quick Chat and context (4 min)

1. Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Alt</kbd>+<kbd>L</kbd> to open **Quick Chat** (a small chat box at the top of the window). Ask:

   ```text
   Tell me about the hello.py file
   ```

   Copilot can't see `hello.py` yet, so it gives a general answer or asks for the file.

2. In the Explorer, open `day3\lab07-copilot-in-vscode\outputs`, then **drag `hello.py` into the Quick Chat box**. The file appears as context under the prompt. Ask the same question again.

3. Select **Open in Chat View** (top right of Quick Chat) to continue the conversation in the main Chat view.

**Checkpoint:** the second answer describes *your* file (one `print` statement) and how to run it.

> **Lesson for prompting:** Copilot only knows what's in its **context**. The same question gives a vague answer without context and a precise one with it. You'll use this all through Day 3.

## Task 5: Ask mode vs Agent mode (5 min)

1. Open `hello.py` in the editor and **select** the `print` line.
2. In the Chat view, with **Ask** selected, send:

   ```text
   Change the selected code to print "Generate equations for addition and subtraction:"
   ```

   The answer contains a code block. Hover over it: **Apply**, **Insert at Cursor** and **Copy** appear. Don't use them yet.

3. Switch the agent picker to **Agent** and send the **same prompt** again.

   This time Copilot **edits the file itself**. The editor shows the change as a diff (green = added, red = removed), with **Keep** and **Undo** buttons.

4. Select **Keep**.

**Checkpoint:** `hello.py` now prints `Generate equations for addition and subtraction:`.

> In Agent mode Copilot can also run terminal commands and call tools. It **asks for your approval** before running commands.
> Read what it wants to run before you select **Allow**. You are the human in the loop.

## Task 6: Completions and next edit suggestions (6 min)

**Ghost text (code completion)**

1. In `hello.py`, put the cursor at the end of the `print` line and press <kbd>Enter</kbd>. Wait a second: grey **ghost text** appears.
2. Press <kbd>Tab</kbd> to accept it, or <kbd>Esc</kbd> to reject it. Copilot may suggest more lines after you accept.

**Next edit suggestions (NES)**

3. Replace everything in `hello.py` with:

   ```python
   import random

   print("Generate equations for addition and subtraction:")
   for i in range(5):
       num1 = random.randint(1, 99)
       num2 = random.randint(1, 99)
       print(f"{num1} + {num2} = {num1 + num2}")
       print(f"{num1} - {num2} = {num1 - num2}")
   ```

4. On the `num1 = ...` line, rename `num1` to `first`.
5. Look at the **left gutter**: an arrow appears where Copilot predicts your *next* edit (the other `num1`s). Press <kbd>Tab</kbd> to jump to it, and <kbd>Tab</kbd> again to accept. Repeat until all `num1`s are renamed. It may also offer to rename `num2` to `second`.
6. Run the file: `.\.venv\Scripts\python.exe day3\lab07-copilot-in-vscode\outputs\hello.py`

**Checkpoint:** no `num1` is left in the file, and it prints five additions and five subtractions.

## Task 7: Smart Actions (4 min)

Smart Actions are ready-made prompts on the right-click menu, so you don't have to type one.

1. Select all the code in `hello.py`, right-click it, and choose **Copilot > Explain** (on some versions it's directly **Explain**). The explanation appears in the Chat view.
2. Right-click the selection again and choose **Copilot > Review** (or **Review**). Copilot leaves review comments in the editor.

**Checkpoint:** the review suggests at least one improvement, for example a clearer variable name, a `main()` function, or a constant for the number of equations.
Accept or dismiss each comment.

---

## Summary

| You want to... | Use |
|---|---|
| Ask a question, get an explanation | **Chat view, Ask** |
| Have Copilot change files or run commands for you | **Chat view, Agent** (review every diff and command) |
| A quick question without leaving the editor | **Quick Chat** (<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Alt</kbd>+<kbd>L</kbd>) or **Inline Chat** (<kbd>Ctrl</kbd>+<kbd>I</kbd>) |
| Copilot to finish the line you're typing | Ghost text (<kbd>Tab</kbd> to accept) |
| Repeat an edit you started | Next edit suggestions (<kbd>Tab</kbd> to jump and accept) |
| Explain or review code without typing a prompt | **Smart Actions** (right-click) |

Next: **[Lab 8](../lab08-prompting-patterns/README.md)**, where you write better prompts for Copilot.