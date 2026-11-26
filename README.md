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
| **6** | Debugging (TDD/BDD, static analysis, security), Code Understanding and Migration, Code Review | [Day 6 labs](day6/README.md) (start with *Before you start*) |
| **7** | GitHub Copilot with JavaScript (Spec Kit) and Python, GitHub Copilot Agents | [Day 7 labs](day7/README.md) (start with *Before you start*) |
| 8-10 | *coming soon* | |

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
├── README.md                       <-- you are here
├── requirements.txt
├── .env.example                    <-- copied to .env by setup (never commit .env)
│
├── setup/
│   ├── setup-windows.ps1           <-- one-time VM setup
│   ├── verify_env.py               <-- environment check (--azure, --neo4j)
│   ├── prefetch_assets.py          <-- pre-download models and datasets
│   └── requirements-tested.txt
│
├── copilot-studio-labs/
│   ├── Resources/
│   │   └── Modules/
│   │       ├── lab00-ILT-setup.md
│   │       ├── lab01-create-agents.md
│   │       └── lab02-manage-topics.md
│   └── media/
│
├── day1/
│   ├── lab00-environment-setup/
│   ├── lab01-azure-ai-services/
│   ├── lab02-transfer-learning/
│   └── lab03-datasets-tokenizers/
│
├── day2/
│   ├── data/                       <-- Kaveri Systems helpdesk knowledge base (Labs 5-6, 9)
│   ├── lab04-hf-hub-cli/
│   ├── lab05-llm-usage/
│   └── lab06-prompt-variations/
│
├── day3/
│   ├── lab07-copilot-in-vscode/
│   ├── lab08-prompting-patterns/
│   └── lab09-mcp-server/
│
├── day4/
│   ├── start-kaveridesk.ps1        <-- copies KaveriDesk to Desktop\kaveridesk (Labs 10, 12)
│   ├── kaveridesk/                 <-- KaveriDesk helpdesk app (starting point, don't edit here)
│   ├── lab10-analyze-document-code/
│   ├── lab11-voice-agent/
│   └── lab12-agent-mode/
│
├── day5/
│   ├── start-kavericlaims.ps1      <-- copies KaveriClaims to Desktop\kavericlaims (Labs 13, 14)
│   ├── kavericlaims/               <-- KaveriClaims expense-claims app (starting point, don't edit here)
│   ├── lab13-context-multimodal/
│   └── lab14-unit-tests/
│
├── day6/
│   ├── start-kavericlaims-day6.ps1 <-- copies KaveriClaims 2.0 to Desktop\kavericlaims-day6 (Labs 15, 16)
│   ├── kavericlaims/               <-- KaveriClaims 2.0 (starting point, don't edit here)
│   ├── lab15-consolidate-refactor/
│   └── lab16-debug-tdd-sca/
│
└── day7/
    ├── start-kaverirooms.ps1       <-- copies KaveriRooms (JavaScript) to Desktop\kaverirooms (Lab 19)
    ├── start-kaveriassets.ps1      <-- copies KaveriAssets (Python) to Desktop\kaveriassets (Labs 20-21)
    ├── kaverirooms/                <-- meeting-room booking: Node.js, no packages (starting point)
    ├── kaveriassets/               <-- IT asset register (starting point, don't edit here)
    ├── lab19-spec-kit/              
    ├── lab20-add-features/
    └── lab21-ai-agent/
```