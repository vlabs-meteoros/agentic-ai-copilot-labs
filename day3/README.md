# Day 3 Labs: GitHub Copilot, Prompting, and MCP

Today you start working with **GitHub Copilot** in VS Code. You learn to write prompts it can act on, then give it new abilities with your own **MCP server**.

## Before you start (10 min, do this first)

In a VS Code terminal at the repository root:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1
```

Day 3 adds only one small package (`mcp`), so there's no `-Prefetch` today. The script takes 2-3 minutes and keeps your `.venv` and `.env`.

While it runs, complete **[Lab 7, Task 1](lab07-copilot-in-vscode/README.md#task-1-sign-in-to-github-copilot-5-min)**: Sign in to GitHub Copilot using the GitHub account that has your **Copilot Business** seat. Your trainer will let you know which account to use.

## Labs

| # | Lab | Topic it supports | Time | Needs | Availability |
|---|---|---|---|---|---|
| 7 | [Enable and Explore GitHub Copilot in VS Code](lab07-copilot-in-vscode/README.md)| Prompting Fundamentals | 35 min | Copilot Business seat | Available |
| 8 | [From a Weak Prompt to a Structured Prompt](lab08-prompting-patterns/README.md) | Prompting Fundamentals, Prompting Patterns and Language Practices | 45 min | Lab 7 | Available |
| 9 | Build Your Own MCP Server in Python | MCP | 50 min | Lab 7 + Day 3 setup | Will be uploaded once its theory if any and Lab 8 are completed. |

No Azure keys, Hugging Face or Neo4j accounts are needed today.

## How the labs connect

```
Lab 7   Meet Copilot: sign in, settings, Chat (Ask / Agent), completions, Smart Actions
          |
Lab 8   Talk to Copilot well: structured prompts, iteration, zero/one/few-shot, prompts for clean code
          |
Lab 9  Give Copilot new tools: a Python MCP server over the Kaveri Systems knowledge base (from Day 2)
```

> The training outline lists MCP first. We do it last because Lab 9 uses Copilot's **Agent mode**, which you learn in Lab 7.

## Tips for the day

* **Keep the model on Auto** unless a step says otherwise.
* **New Chat** (the **+** in the Chat view) gives you a clean start. Old messages in a chat change the next answer.
* When Copilot asks to run a command or a tool, **read it before you select Allow**.
* Copilot's answers vary from run to run. If yours differs a little from a checkpoint, check the *idea* of the checkpoint, not the exact words.
