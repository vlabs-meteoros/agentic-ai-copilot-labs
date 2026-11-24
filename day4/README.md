# Day 4 Labs: Prompt Engineering for Code, a Voice Assistant, and Agent Mode

Today you use GitHub Copilot on code you didn't write: you understand and document it, then add features to it with **Agent mode**.
In between, you build a small **voice coding assistant** with speech to text, GPT and text to speech.

## Before you start (10 min, do this first)

In a VS Code terminal at the repository root:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1
```

Day 4 adds a few small packages (`fastapi`, `uvicorn`, `sounddevice`), so there's no `-Prefetch` today. The script takes 2-3 minutes and keeps your `.venv` and `.env`.

**While it runs**, check that Copilot is signed in (the Copilot icon in the Status Bar), and that your `.env` still has the four Azure values from Day 2
(`AZURE_AI_ENDPOINT`, `AZURE_AI_KEY`, `AZURE_AI_REGION`, `AZURE_OPENAI_DEPLOYMENT`). Lab 12 needs them.

## Labs

| # | Lab | Topic It Supports | Time | Needs |
|---|---|---|---|---|
| 10 | [Analyze and Document Unfamiliar Code](lab10-analyze-document-code/README.md) | Prompt Engineering | 40 min | Copilot |
| 11 | [A Conversational Voice Coding Assistant](lab11-voice-agent/README.md) | Developer Productivity | 55 min | Azure values in `.env`. Microphone and speakers are optional. |
| 12 | [Build New Features with Agent Mode](lab12-agent-mode/README.md) | Agent Mode | 50 min | Copilot, your `kaveridesk` copy from Lab 10 |

## How the labs connect

```
Lab 10  Meet KaveriDesk, an undocumented helpdesk app: explain it, find edge cases, add docs, names and tests
          |                                     (your own copy in Desktop\kaveridesk, opened in a second VS Code window)
Lab 11  Developer productivity: prompt formats, Pydantic structured output, and a voice assistant (STT -> GPT -> TTS)
          |                                     (in the labs repository window)
Lab 12  Back to KaveriDesk: inline vs Ask vs Plan vs Agent, a feature from a spec, and a REST API from requirements
```

## Two VS Code windows today

| Window | Folder | Used in |
|---|---|---|
| **Labs repository** | `Desktop\agentic-ai-copilot-labs` | Lab 11, and to start Lab 10 |
| **KaveriDesk** | `Desktop\kaveridesk` (created in Lab 10, Task 1) | Labs 10 and 12 |

Copilot's `#codebase` searches only the folder that's open, so a separate window keeps its answers focused on KaveriDesk.
Your copy lives outside the repository, so your changes never block a `git pull`. To start again from a fresh copy:

```powershell
powershell -ExecutionPolicy Bypass -File .\day4\start-kaveridesk.ps1 -Reset
```

## Tips for the day

* **Keep the model on Auto** unless a step says otherwise.
* **New Chat** gives Copilot a clean start. Old messages in a chat change the next answer.
* In Agent mode, **read every command before you select Allow**, and review every diff before you select **Keep**.
* In the KaveriDesk window, always add `--now "2026-11-20 11:00"` so your results match the checkpoints. After trying a command that changes tickets, run `git restore data`.
