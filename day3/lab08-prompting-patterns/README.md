# Lab 8: From a Weak Prompt to a Structured Prompt

| | |
|---|---|
| **Duration** | 45 minutes |
| **Topic** | Prompting Fundamentals (iterative prompting) and Prompting Patterns (zero-, one- and few-shot; naming, modularity, readability) |
| **You need** | Copilot signed in (Lab 8). Everything happens in the **Copilot Chat view**: no code to write, no keys |
| **Files** | `outage_facts.md`, `scorecard.md`, `customer_messages.md`, `leave_report.py`, `my_prompts.md` (your worksheet) |

## Objectives

* See what a weak prompt costs you: generic text and invented facts
* Rewrite a business prompt with six building blocks: **Role, Context, Task, Audience and tone, Output format, Constraints**
* Improve a prompt in a loop, with Copilot reviewing your prompt
* Use **zero-shot**, **one-shot** and **few-shot** prompting, and see when examples matter
* Apply the same ideas to code: ask for good **naming, modularity and readability**, and check the result

## The scenario

You work at **Kaveri Systems** (the same fictional company as Day 2). Its payroll product **KaveriPay** was down for two and a half hours on Friday 14 November.
Your manager wants a customer email, and the support team wants help sorting customer messages.

---

## Task 1: Start with a weak prompt (5 min)

1. Make your own copy of the worksheet. In the terminal, at the repository root:

   ```powershell
   New-Item -ItemType Directory -Force day3\lab08-prompting-patterns\outputs | Out-Null
   Copy-Item day3\lab08-prompting-patterns\my_prompts.md day3\lab08-prompting-patterns\outputs\
   ```

   Open `outputs\my_prompts.md`. You'll note your prompts and scores there.

2. Open the Chat view (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>I</kbd>). Select **New Chat** (the **+** icon), choose **Ask**, and keep the model on **Auto**.
3. Send this prompt, exactly as written:

   ```text
   Write an email to customers about the outage.
   ```

4. Read the email. Ask yourself:
   * Which outage? When? What caused it? Copilot doesn't know, so it **invented** details or left `[placeholders]`.
   * Who is it from? What should the customer do now?

5. Open `scorecard.md` and score the prompt (not the email). Write the score and what was invented in your worksheet.

**Checkpoint:** the weak prompt scores about **1-2 out of 12**, and the email contains made-up or placeholder details.

> **Why this happens:** an LLM always produces *something*. When the prompt leaves gaps, the model fills them with the most likely-sounding text.
> That is the same hallucination you saw on Day 2, Lab 6. Your job is to leave fewer gaps.

## Task 2: Rewrite it as a structured prompt (10 min)

A structured prompt answers six questions. Here they are for the outage email:

| Building block | Your answer for this email |
|---|---|
| **Role** | Who should Copilot be? *A customer communications writer for a B2B software company* |
| **Context** | The facts. They're in `outage_facts.md`: attach the file instead of retyping |
| **Task** | *Write an apology and update email about the outage* |
| **Audience and tone** | *Payroll managers at our customers. Not technical. Calm, honest, apologetic, no excuses* |
| **Output format** | *Subject line, then at most 150 words, with a short bullet list for what happened and what we're doing* |
| **Constraints** | *Use only the facts in the file. Don't mention team or employee names. No technical jargon. Say clearly that customers don't need to do anything for the credit* |

1. Select **New Chat** (so the weak prompt's history doesn't influence the result).
2. Type the prompt below. Where it says `#file:outage_facts.md`, type `#` and pick the file from the list, or drag `outage_facts.md` from the Explorer into the chat box.

   ```text
   You are a customer communications writer for a B2B software company.

   Context: the facts about the KaveriPay outage are in #file:outage_facts.md

   Task: write an apology and update email to our customers about this outage.

   Audience and tone: payroll managers at customer companies. They are not technical. Be calm, honest
   and apologetic, without making excuses.

   Output format:
   - A subject line
   - The email body in at most 150 words
   - A short bulleted list for "what happened" and "what we are doing about it"
   - Sign off as the sender named in the facts

   Constraints:
   - Use only the facts in the file. If a detail is not in the file, leave it out.
   - Do not mention internal team names, employee names or internal tools.
   - No technical jargon.
   - Make it clear that customers don't need to do anything to get the credit.
   ```

3. Compare the two emails side by side. Check the facts against `outage_facts.md`: date, times, the 10% credit, the support contacts, the sender.
4. Score your structured prompt and note what improved in your worksheet.

**Checkpoint:** the new email has a subject line, is about 150 words or less, uses **only** facts from the file (09:40-12:15 IST, 10% credit, no data lost), and is signed by Ananya Rao. The prompt scores **10-12**.

> **Delimiters and labels** (`Context:`, `Task:`, bullets) aren't magic words. They help the model (and the next human) see where each part starts and ends.

## Task 3: Iterate, with Copilot reviewing your prompt (8 min)

Good prompts are rarely right the first time. You improve them in a loop: **prompt, check, refine**.

1. Ask Copilot to review your *prompt* (not the email). In the same chat, send:

   ```text
   Act as a prompt engineering reviewer. Score the prompt I used above against #file:scorecard.md.
   Then ask me up to 3 questions whose answers would make the email better.
   ```

2. Answer its questions in your next message (for example: *mention that payroll was still on time in the first sentence*, or *add a line on how to contact support*).
3. Now refine the **output** with short follow-ups, one at a time. Watch how each changes the email:

   ```text
   Move the reassurance that all salaries were paid on time into the first two sentences.
   ```

   ```text
   Now write a version for an SMS of at most 160 characters.
   ```

4. Copy your final prompt into the worksheet.

**Checkpoint:** you have an SMS version of 160 characters or less, and it still says salaries were paid on time.

> **Iterative prompting in short:** change **one thing at a time**, check the result against the facts, and keep the version that works.
> When a follow-up chain gets long, start a **New Chat** with one improved prompt instead. Long chats carry old mistakes along.

## Task 4: Zero-shot, one-shot and few-shot (12 min)

The support team wants every message in `customer_messages.md` sorted into a category with a priority. Open the file and read the 8 messages. Messages 4, 7 and 8 are tricky on purpose.

**Zero-shot: instructions only, no examples**

1. **New Chat**, **Ask** mode. Send:

   ```text
   Classify each customer message in #file:customer_messages.md
   Categories: Bug, Billing, Feature request, How-to, Praise.
   Priority: High, Medium or Low.
   ```

2. Note the answers for messages 4, 7 and 8 in your worksheet. Look at the **format** too: list, table, or paragraphs?

**One-shot: add one example of the exact output you want**

3. **New Chat**. Send:

   ```text
   Classify each customer message in #file:customer_messages.md
   Categories: Bug, Billing, Feature request, How-to, Praise.
   Priority: High, Medium or Low.
   Answer with only a Markdown table with the columns #, Category, Priority, Reason (max 8 words).

   Example:
   Message: "I can't find where to change our company's bank account."
   | # | Category | Priority | Reason |
   | 0 | How-to | Low | Asking where a setting is |
   ```

   The format is now fixed. Are 4, 7 and 8 right?

**Few-shot: several examples that show the tricky cases and the rules**

4. **New Chat**. Send:

   ```text
   You triage customer messages for KaveriPay, a payroll product.
   Classify each message in #file:customer_messages.md

   Categories: Bug, Billing, Feature request, How-to, Praise.
   Priority rules:
   - High: payroll or payslips are blocked, or many people are affected
   - Medium: wrong data or wrong money, but work can continue
   - Low: questions, ideas and praise
   If a message has two issues, give both categories joined with " + " and the higher priority.

   Answer with only a Markdown table with the columns #, Category, Priority, Reason (max 8 words).

   Examples:
   Message: "I can't find where to change our company's bank account."
   | 0 | How-to | Low | Asking where a setting is |

   Message: "Wonderful, the app logged everyone out in the middle of payroll approval. Brilliant work."
   | 0 | Bug | High | Sarcastic complaint; payroll approval blocked |

   Message: "Our renewal price went up without notice, and the leave calendar shows the wrong holidays."
   | 0 | Billing + Bug | Medium | Unexpected price rise and wrong holidays |

   Message: "Salary slip mein galat PAN number aa raha hai."
   | 0 | Bug | Medium | Hindi-English: wrong PAN on payslip |
   ```

5. Fill in the comparison table in your worksheet.

**Checkpoint:** with few-shot, message 4 is a **Bug** (not Praise), message 7 is **Billing + Bug**, and message 8 is a **High** priority **Bug**. The table format is identical every time.

| Technique | What you give the model | Use it when |
|---|---|---|
| **Zero-shot** | Instructions only | The task is common and the format doesn't matter much |
| **One-shot** | Instructions + 1 example | You need an exact output format |
| **Few-shot** | Instructions + 2-5 varied examples | There are edge cases (sarcasm, two issues, other languages) or house rules the model can't guess |

> Few-shot examples should be **varied** and **realistic**. If all your examples are easy, the model learns nothing about the hard cases.
> And examples cost tokens on every call: use as few as you need.

## Task 5: The same ideas for code (10 min)

`leave_report.py` works, but it's hard to read: single-letter names, one long function, magic numbers like `21` and `10`.

1. Run it first, from the repository root, and keep the output on screen:

   ```powershell
   .\.venv\Scripts\python.exe day3\lab08-prompting-patterns\leave_report.py
   ```

2. **Weak code prompt.** **New Chat**, **Ask** mode, attach `leave_report.py` and send:

   ```text
   improve this code
   ```

   Look at what you get: Copilot guesses what "improve" means. It might change the behaviour, the output, or nothing important.

3. **Structured code prompt.** **New Chat**, switch to **Agent** mode, and send:

   ```text
   You are a senior Python developer writing code that beginners will maintain.

   Task: refactor #file:leave_report.py into a NEW file leave_report_clean.py in the same folder.
   Do not change leave_report.py.

   Apply these practices:
   - Naming: descriptive names for every variable and function, no single letters.
   - Modularity: separate small functions to calculate one employee's leave balance, build the report rows,
     and print the report. Each function does one thing.
   - Readability: a module docstring, a one-line docstring per function, type hints, and named constants
     for the 21 days of annual leave, the 10-day carry-over limit and the 3-day warning threshold.
   - Use a NamedTuple for an employee record instead of tuple indexes like x[2].

   Constraints:
   - The printed output must stay exactly the same.
   - Standard library only. Keep the same sample data.

   When you are done, run both files and confirm that their outputs match.
   ```

4. The agent creates the file and asks to **run commands** in the terminal. Read each command, then select **Allow**. Review the new file, then select **Keep**.
5. Run the new file yourself and compare it with the original output:

   ```powershell
   .\.venv\Scripts\python.exe day3\lab08-prompting-patterns\leave_report_clean.py
   ```

**Checkpoint:** `leave_report_clean.py` prints exactly the same report (2 employees with less than 3 days left), and contains the constants, the NamedTuple and several small, well-named functions.

> **Best practices that apply in every language:** ask for them **by name** (naming, modularity, readability, tests), give a way to
> **check** the result ("output must stay exactly the same"), and **verify it yourself**. Copilot's "they match" is a claim; your test run is the proof.

---

## Stretch (optional)

* **Compare models.** Re-send your Task 2 prompt in a New Chat with a different model from the model picker. Do they follow your format and constraints equally well?
* **Reuse your template.** Fill in the template at the end of your worksheet for a different message, for example *an email inviting customers to a KaveriPay webinar on the new tax rules*. Score it before you send it.

## Summary

* A prompt is a **specification**. Every gap you leave, the model fills by guessing.
* Six building blocks: **Role, Context, Task, Audience and tone, Output format, Constraints**. Attach facts as files instead of retyping them.
* Improve in a loop, one change at a time. Start a new chat when the history gets in the way.
* **Zero-shot** for simple tasks, **one-shot** to fix the format, **few-shot** to teach edge cases and house rules.
* For code, name the practices you want and give a way to verify the result.

Next: **[Lab 9](../lab09-mcp-server/README.md)**, where you give Copilot new tools by building an MCP server.