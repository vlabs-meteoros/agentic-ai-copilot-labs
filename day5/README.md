# Day 5 Labs: Copilot Chat & Agent Mode on Legacy Code, Refactoring, and Unit Tests

Today you take over **KaveriClaims**, a 2015 expense-claims app nobody wants to touch.
You understand it with the right **context** (including a receipt **image**), **refactor** it without changing what it does, and then **test** it until it does what the policy says.

## Before you start (10 min, do this first)

In a VS Code terminal at the repository root:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1
```

Day 5 adds only `pytest` and `pytest-cov`, so there's no `-Prefetch` today. The script takes 2-3 minutes and keeps your `.venv` and `.env`.

**While it runs**, check that Copilot is signed in (the Copilot icon in the Status Bar), and that your `.env` still has the Azure values from Day 4
(`AZURE_AI_ENDPOINT`, `AZURE_AI_KEY`, `AZURE_OPENAI_DEPLOYMENT`). Lab 13, Task 6 needs them.

## Labs

| # | Lab | Topic it supports | Time | Needs |
|---|---|---|---|---|
| 13 | [Context, Legacy Code and Images in Copilot Chat](lab13-context-multimodal/README.md) | Copilot Chat & Agent Mode | 45 min | Copilot. Azure values in `.env` for Task 6 |
| 14 | [Develop Unit Tests with GitHub Copilot](lab14-unit-tests/README.md) | Using GitHub Copilot | 60 min | Copilot, your `kavericlaims` copy from Lab 13 |

## How the labs connect

```
Lab 13  Meet KaveriClaims: context (#file vs #codebase), instructions files, explain legacy code,
          |     a receipt image in Copilot Chat, and image + text from Python with gpt-4.1-mini
          |                                    (your own copy in Desktop\kavericlaims, opened in a second VS Code window)
Lab 14  Test it with pytest: generated tests, tests from the policy (they find 2 bugs), a stack trace fixed test-first,
                fixtures, integration tests and coverage
```

The same copy of KaveriClaims carries through all three labs. If yours gets into a mess:

```powershell
powershell -ExecutionPolicy Bypass -File .\day5\start-kavericlaims.ps1 -Reset              # a fresh copy (before Lab 13 and 14)
```

Run these from the labs repository window, after closing the KaveriClaims window (**File > Close Window**): Windows can't move a folder that VS Code has open.
`-Reset` keeps your old copy as `kavericlaims-old-<date-time>`.

## Two VS Code windows today

| Window | Folder | Used in |
|---|---|---|
| **Labs repository** | `Desktop\agentic-ai-copilot-labs` | To start Lab 13, and Lab 13 Task 6 |
| **KaveriClaims** | `Desktop\kavericlaims` (created in Lab 13, Task 1) | Labs 13 and 14 |

## Tips for the day

* **Keep the model on Auto** unless a step says otherwise. If a model can't read the receipt image in Lab 13, pick another model for that one chat.
* **New Chat** gives Copilot a clean start. Old messages in a chat change the next answer.
* Run `python -m pytest` after **every** change Copilot makes. A refactoring that breaks the golden test isn't a refactoring.
* In Agent mode, **read every command before you select Allow**, and review every diff before you select **Keep**.
* **Commit** after every task that ends green (Source Control, sparkle for the message). Then **Undo** is never more than one task away.