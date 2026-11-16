# Agentic AI with Copilot: Hands-on Labs

Lab repository for the 10-session *Agentic AI with Copilot* program.
All labs run on the provided **Windows VM in VS Code**.

| Day | Topic | Labs |
|---|---|---|
| **1** | AI Fundamentals, Neural Networks, Pre-trained Models | [Day 1 labs](day1/README.md) (start with [Lab 0](day1/lab00-environment-setup/README.md)) |
| 2-10 | *coming soon* | |

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

### Using the terminal instead of notebooks

Labs 2 and 3 also ship plain Python scripts. Activate the environment first:

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
├── .env.example            <- copied to .env by setup (holds the Azure key - never commit .env)
├── setup/
│   ├── setup-windows.ps1   <- one-time VM setup
│   ├── verify_env.py       <- environment check (add --azure to test the Azure resource)
│   ├── prefetch_assets.py  <- pre-download models and datasets
│   └── requirements-tested.txt
└── day1/
    ├── lab00-environment-setup/
    ├── lab01-azure-ai-services/
    ├── lab02-transfer-learning/
    └── lab03-datasets-tokenizers/
```
