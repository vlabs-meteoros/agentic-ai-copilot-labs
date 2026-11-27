# Day 7 Labs: GitHub Copilot with JavaScript and Python, and GitHub Copilot Agents

Today you add features to two existing apps, in two languages, three ways: a **spec-driven** feature in JavaScript with **GitHub Spec Kit**,
three backlog tickets in Python with **inline chat, Ask and Agent mode**, and finally an **AI agent** built into the Python app.

> [!IMPORTANT]
> **[lab19-spec-kit/README.md](lab19-spec-kit)** and **[lab20-add-features/README.md](lab20-add-features)** are optional. Feel free to explore them whenever you have some free time. You can skip them if your schedule is tight.

## Before you start (10 min, do this first)

In a VS Code terminal at the repository root:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1
```

Day 7 adds one package, **Spec Kit** (`specify-cli`), and installs **Node.js** if the VM doesn't have it (a per-user copy, no admin rights needed).
There's no `-Prefetch` today. The script takes 2-4 minutes and keeps your `.venv` and `.env`.
Spec Kit needs Python 3.11 or newer: if your `.venv` is Python 3.10, setup puts Spec Kit in a separate `.speckit-venv` folder instead
(and installs Python 3.12 for you first if needed, which adds a few minutes).

**While it runs**, check that Copilot is signed in (the Copilot icon in the Status Bar), and that your `.env` still has the Azure values from Day 5
(`AZURE_AI_ENDPOINT`, `AZURE_AI_KEY`, `AZURE_OPENAI_DEPLOYMENT`): Lab 21 needs them.

Setup ends with the environment check: the `node` and `specify` lines should be `[ OK ]`.
If setup had to install Node.js, the terminals that are already open can't see it yet. That's fine: the KaveriRooms window you open in Lab 19
is set up to find it. (To use `node` in the labs window too, close VS Code completely and open it again.)

## Labs

| # | Lab | Topic it supports | Time | Needs |
|---|---|---|---|---|
| 19 | [Implement a Product Feature with GitHub Spec Kit (JavaScript)](lab19-spec-kit/README.md) | Using GitHub Copilot with JavaScript | 70 min | Copilot, Node.js, Spec Kit |
| 20 | [Add New Features to an Existing Python App](lab20-add-features/README.md) | Using GitHub Copilot with Python | 50 min | Copilot |
| 21 | [Integrate an AI Agent into the App](lab21-ai-agent/README.md) | GitHub Copilot Agents | 55 min | Copilot, Azure values in `.env` |

## How the labs connect

```
Lab 19  KaveriRooms (Node.js, no packages): Copilot Chat questions about the JavaScript, then GitHub Spec Kit:
          |     constitution -> specify -> clarify -> plan -> tasks -> implement, checked by an acceptance test
          |                                    (your own copy in Desktop\kaverirooms, opened in a second VS Code window)
Lab 20  KaveriAssets (Python): Copilot Chat questions about the Python, then three backlog tickets:
          |     small (inline chat), medium (Ask, then Agent), large (Plan, then Agent)
          |                                    (your own copy in Desktop\kaveriassets, a third window)
Lab 21  Agents: watch an agent loop step by step, then build an AI assistant INTO KaveriAssets with Agent mode,
                against a test contract with a fake model. Human approval for changes; a record that tries to give the agent orders
```

Labs 20 and 21 use the same KaveriAssets copy. If a copy gets into a mess:

```powershell
powershell -ExecutionPolicy Bypass -File .\day7\start-kaverirooms.ps1 -Reset                # a fresh KaveriRooms (Lab 19)
powershell -ExecutionPolicy Bypass -File .\day7\start-kaveriassets.ps1 -Reset               # a fresh KaveriAssets (before Lab 20)
powershell -ExecutionPolicy Bypass -File .\day7\start-kaveriassets.ps1 -Reset -FromLab20    # the Lab 20 solution (to start Lab 21)
```

Run these from the labs repository window, after closing the app's window (**File > Close Window**): Windows can't move a folder that VS Code has open.
`-Reset` keeps your old copy as `<name>-old-<date-time>`.

## Three VS Code windows today

| Window | Folder | Used in |
|---|---|---|
| **Labs repository** | `Desktop\agentic-ai-copilot-labs` | To start Labs 19 and 20, Lab 21 Task 1, and to copy files from |
| **KaveriRooms** | `Desktop\kaverirooms` (created in Lab 19, Task 1) | Lab 19 |
| **KaveriAssets** | `Desktop\kaveriassets` (created in Lab 20, Task 1) | Labs 20 and 21 |

The terminals in the KaveriRooms and KaveriAssets windows already use the labs' Python: no activation needed there.

## Tips for the day

* **Keep the model on Auto** unless a step says otherwise.
* **New Chat** gives Copilot a clean start. Old messages in a chat change the next answer.
* Run the tests after **every** change Copilot makes: `node --test` in KaveriRooms, `python -m pytest` in KaveriAssets.
* In Agent mode, **read every command before you select Allow**, and review every diff before you select **Keep**.
* **Commit** after every task that ends green (Source Control, sparkle for the message).
* KaveriAssets commands like `assign` change `data\`. After trying one: `git restore data` (and `git clean -f data` once `data\requests.csv` exists).
