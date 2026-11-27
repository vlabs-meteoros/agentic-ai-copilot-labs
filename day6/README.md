# Day 6 Labs: Debugging, Code Understanding and Migration, and Code Review

Today **KaveriClaims 2.0** gets the treatment a real codebase needs before it grows: duplicate logic merged, a large function split, the policy rules
translated to JavaScript, bugs hunted with the debugger, a feature built test first, and security holes found, fixed and reviewed.

> [!IMPORTANT]
> **Lab 18 – Resolve Issues, Fix Security Vulnerabilities, and Review Code** (`lab18-issues-security-review/README.md`) is an optional lab. Feel free to explore them whenever you have some free time. You can skip them if your schedule is tight.

## Before you start (10 min, do this first)

In a VS Code terminal at the repository root:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1
```

Day 6 adds three small packages (`ruff`, `bandit`, `pytest-bdd`), and installs **Node.js** if the VM doesn't have Node.js 18 or later
(Lab 16, Task 6 needs it). It's a per-user copy from nodejs.org, so no admin rights are needed. There's no `-Prefetch` today.
The script takes 2-4 minutes and keeps your `.venv` and `.env`.

**While it runs**, check that Copilot is signed in (the Copilot icon in the Status Bar). There are no Azure calls today.

When setup has finished, check the new tools:

```powershell
.\.venv\Scripts\Activate.ps1
python setup\verify_env.py
```

The `ruff`, `bandit`, `git` and `node` lines should be `[ OK ]`.

If setup had to install Node.js, the terminals that are already open can't see it yet, so the `node` line may say *not found*. That's fine:
the KaveriClaims window you open in Lab 16 is set up to find it. (To use `node` in the labs window too, close VS Code completely and open it again.)
If setup printed **[WARN] Node.js could not be installed**, tell your trainer before Lab 16: the VM probably can't reach nodejs.org.

## Labs

| # | Lab | Topic it supports | Time | Needs |
|---|---|---|---|---|
| 16 | [Consolidate Duplicate Code, Refactor a Large Function, and Migrate to JavaScript](lab16-consolidate-refactor/README.md) | Debugging (duplicate code), Code Understanding and Migration | 50 min | Copilot, Node.js for Task 6 |
| 17 | [Debugging, TDD and BDD, and Static Analysis](lab17-debug-tdd-sca/README.md) | Debugging | 60 min | Copilot, your `kavericlaims-day6` copy from Lab 16 |
| 18 | [Resolve Issues, Fix Security Vulnerabilities, and Review Code](lab18-issues-security-review/README.md) | Code Review with Copilot, Debugging (security) | 55 min | Copilot, your `kavericlaims-day6` copy from Lab 17 |

## How the labs connect

```
Lab 16  KaveriClaims 2.0: close a gap in the safety net, find duplicate logic with #codebase, merge it, split the 81-line process(),
          |     then explain policy.py and translate it to JavaScript until the shared test cases pass
          |                                    (your own copy in Desktop\kavericlaims-day6, opened in a second VS Code window)
Lab 17  The team command: a TypeError, a KeyError, and a mutable-default bug found with the debugger.
          |     Duplicate-claims check built test first from a spec (TDD), the same rules in Gherkin (BDD), then ruff (SCA)
Lab 18  The auditors' archive: bandit, issue #51 (SQL injection) and #52 (path traversal) fixed test first,
                then Copilot code review of a colleague's pull request, with you as the human in the loop
```

The same copy carries through all three labs. Your Day 5 copy (`Desktop\kavericlaims`) isn't used or changed. If your Day 6 copy gets into a mess:

```powershell
powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1 -Reset              # a fresh copy (before Lab 16)
powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1 -Reset -FromLab16   # the Lab 16 solution (to start Lab 17)
powershell -ExecutionPolicy Bypass -File .\day6\start-kavericlaims-day6.ps1 -Reset -FromLab17   # the Lab 17 solution (to start Lab 18)
```

Run these from the labs repository window, after closing the KaveriClaims window (**File > Close Window**): Windows can't move a folder that VS Code has open.
`-Reset` keeps your old copy as `kavericlaims-day6-old-<date-time>`.

## Two VS Code windows today

| Window | Folder | Used in |
|---|---|---|
| **Labs repository** | `Desktop\agentic-ai-copilot-labs` | To start Lab 16, and to copy files from (Labs 16-18) |
| **KaveriClaims 2.0** | `Desktop\kavericlaims-day6` (created in Lab 16, Task 1) | Labs 16, 17 and 18 |

## Tips for the day

* **Keep the model on Auto** unless a step says otherwise.
* **New Chat** gives Copilot a clean start. Old messages in a chat change the next answer.
* Run `python -m pytest` after **every** change Copilot makes. Two golden tests protect the report and the notes: never edit `tests\golden\` to make them pass.
* In Agent mode, **read every command before you select Allow**, and review every diff before you select **Keep**.
* **Commit** after every task that ends green (Source Control, sparkle for the message). Then **Undo** is never more than one task away.
* Copilot's suggestions are a first draft and a first review, not a verdict. Today you check each one with a test, a tool, or the spec.
