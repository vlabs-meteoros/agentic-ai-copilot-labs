# Agentic AI with Copilot: Hands-on Labs

Lab repository for the 10-session *Agentic AI with Copilot* program.
All labs run on the provided **Windows VM in VS Code**.

| Day | Topic | Labs |
|---|---|---|
| **1** | AI Fundamentals, Neural Networks, Pre-trained Models | [Day 1 labs](day1/README.md) (start with [Lab 0](day1/lab00-environment-setup/README.md)) |
| **2** | Tools and Ecosystems for LLM Agents, HF Transformers, GenAI Fundamentals | [Day 2 labs](day2/README.md) (start with *Before you start*) |
| **3** | GitHub Copilot, Prompting Fundamentals and Patterns, MCP | [Day 3 labs](day3/README.md) (start with *Before you start*) |
| **4** | Prompt Engineering for code, Developer Productivity (voice AI), Agent Mode | [Day 4 labs](day4/README.md) (start with *Before you start*) |
| **5** | Copilot Chat & Agent Mode on legacy code (context, multi-modal), refactoring, unit tests | [Day 5 labs](day5/README.md) (start with *Before you start*) |
| 6-10 | *coming soon* | |

---

## Getting started

Start with **[Lab 0: Set Up Your Lab Environment](day1/lab00-environment-setup/README.md)**. It takes about 20 minutes and you only do it once per VM.

The short version, in a VS Code PowerShell terminal (<kbd>Ctrl</kbd>+<kbd>`</kbd>):

```powershell
cd $HOME\Desktop
git clone https://github.com/vlabs-meteoros/agentic-ai-copilot-labs.git
cd agentic-ai-copilot-labs
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1 -Prefetch
```

Then **File > Open Folder... > Desktop\agentic-ai-copilot-labs**, open a notebook, and choose the **.venv** kernel.

### New day? Update first

At the start of each day, pull the new labs and re-run setup (it keeps your `.venv` and `.env` values):

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1 -Prefetch
```

### Using the terminal instead of notebooks

Day 1 Labs 2 and 3 also ship plain Python scripts. Activate the environment first:

```powershell
.\.venv\Scripts\Activate.ps1
python setup\verify_env.py
```

If activation is blocked, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal first.

---

## Repository layout

```
agentic-ai-copilot-labs/
├── README.md               <- you are here
├── requirements.txt
├── .env.example            <- copied to .env by setup (holds your keys and passwords - never commit .env)
├── setup/
│   ├── setup-windows.ps1   <- one-time VM setup
│   ├── verify_env.py       <- environment check (--azure: Azure resource, --neo4j: your AuraDB instance)
│   ├── prefetch_assets.py  <- pre-download models and datasets
│   └── requirements-tested.txt
├── day1/
│   ├── lab00-environment-setup/
│   ├── lab01-azure-ai-services/
│   ├── lab02-transfer-learning/
│   └── lab03-datasets-tokenizers/
├── day2/
│   ├── data/                   <- Kaveri Systems helpdesk knowledge base (Labs 5-6, 9)
│   ├── lab04-hf-hub-cli/
│   ├── lab05-llm-usage/
│   ├── lab06-prompt-variations/
├── day3/
│   ├── lab07-copilot-in-vscode/ 
│   ├── lab08-prompting-patterns/
│   └── lab09-mcp-server/
├── day4/
│   ├── start-kaveridesk.ps1    <- copies the KaveriDesk app to Desktop\kaveridesk (Labs 10 and 12)
│   ├── kaveridesk/             <- the KaveriDesk helpdesk app (starting point, don't edit here)
│   ├── lab10-analyze-document-code/
│   ├── lab11-voice-agent/ 
│   └── lab12-agent-mode/ 
└── day5/
    ├── start-kavericlaims.ps1  <- copies the KaveriClaims app to Desktop\kavericlaims (Labs 13-14)
    ├── kavericlaims/           <- the KaveriClaims expense-claims app (starting point, don't edit here)
    ├── lab13-context-multimodal/
    └── lab14-unit-tests/
```
