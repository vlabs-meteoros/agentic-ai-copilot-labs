# Lab 0: Set Up Your Lab Environment

| | |
|---|---|
| **Duration** | 20 minutes (mostly waiting for downloads, so start it early) |
| **When** | At the very start of Day 1, before Lab 1 |
| **You need** | Your lab VM (Windows, VS Code installed) and internet access |

Your VM has VS Code but **not** the right Python or libraries yet (it ships with Python 3.6, which is too old).
In this lab you install everything the course needs with a single script.

> **Tip:** start Task 3 as soon as you can. The script downloads ~1.5 GB and keeps working while the trainer
> introduces the first topic.

---

## Task 1: Open VS Code and a terminal (2 min)

1. Sign in to your lab VM.
2. Double-click **Visual Studio Code** on the desktop.
3. Open a terminal: menu **Terminal > New Terminal**, or press <kbd>Ctrl</kbd>+``.
   A **PowerShell** prompt like `PS C:\Users\...>` appears at the bottom.

## Task 2: Download the lab files (3 min)

In the terminal, copy and paste these commands and press <kbd>Enter</kbd>:

```powershell
cd $HOME\Desktop
git clone https://github.com/vlabs-meteoros/agentic-ai-copilot-labs.git
cd agentic-ai-copilot-labs
```

<details>
<summary><b>If you see "git is not recognized..."</b>, use the ZIP download instead</summary>

```powershell
cd $HOME\Desktop
Invoke-WebRequest https://github.com/vlabs-meteoros/agentic-ai-copilot-labs/archive/refs/heads/main.zip -OutFile labs.zip
Expand-Archive labs.zip -DestinationPath .
Rename-Item agentic-ai-copilot-labs-main agentic-ai-copilot-labs
cd agentic-ai-copilot-labs
```

</details>

**Checkpoint:** the prompt ends with `\Desktop\agentic-ai-copilot-labs>`.

## Task 3: Run the setup script (10-15 min, mostly waiting)

In the same terminal, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1 -Prefetch
```

The script works through these steps, printing `==>` as it starts each one:

| Step | What happens | Typical time |
|---|---|---|
| Looking for Python 3.10 or newer | Installs **Python 3.12** for your user (Python 3.6 is ignored) | 1-3 min |
| Creating virtual environment | Creates `.venv` inside the lab folder | < 1 min |
| Installing packages | PyTorch, Hugging Face, Azure SDKs, Jupyter | 4-8 min |
| Installing VS Code extensions | Python and Jupyter | < 1 min |
| Registering Jupyter kernel | "Python (agentic-ai-labs)" | < 1 min |
| Preparing .env | Creates your settings file (used in Lab 1) | instant |
| Pre-downloading models and datasets | Models and datasets for Labs 2 and 3 | 2-5 min |
| Checking the environment | Prints a report | < 1 min |

**Checkpoint:** the report ends with:

```
 Ready for the labs!
```

A line or two marked `[WARN]` (for example ".env still has placeholders") is fine. Any `[FAIL]` line is not: raise your hand.

## Task 4: Open the lab folder in VS Code (2 min)

1. Menu **File > Open Folder...**
2. Go to **Desktop > agentic-ai-copilot-labs** and click **Select Folder**.
3. If VS Code asks *"Do you trust the authors of the files in this folder?"*, click **Yes, I trust the authors**.
4. If VS Code suggests installing extensions or selecting an interpreter, you can accept.

## Task 5: Test a notebook (3 min)

1. In the **Explorer** (left side), open `day1/lab00-environment-setup/Lab00_Check_Setup.ipynb`.
2. Click **Select Kernel** (top right) > **Python Environments...** > **.venv (Python 3.12.x)**.
   - Don't see `.venv`? Choose **Jupyter Kernel...** > **Python (agentic-ai-labs)**.
   - Still nothing? Press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd>, run **Developer: Reload Window**, and try again.
3. Click into the code cell and press <kbd>Shift</kbd>+<kbd>Enter</kbd>.

**Checkpoint:** the output shows a Python path ending in `agentic-ai-copilot-labs\.venv\Scripts\python.exe`
and finishes with **Ready for the labs!**

You're done. Continue with [Lab 1](../lab01-azure-ai-services/README.md).

---

## Troubleshooting

| Symptom | What to do |
|---|---|
| `running scripts is disabled on this system` | Make sure you typed the full command, starting with `powershell -ExecutionPolicy Bypass -File ...` |
| `Python 3.10+ could not be installed automatically` | Tell your trainer. Python 3.12 can be installed from python.org; then re-run the script. |
| `pip install failed` / SSL or timeout errors | Network hiccup: just re-run the same setup command. It skips steps that already succeeded. |
| `Some downloads failed` at the prefetch step | Re-run `.\.venv\Scripts\python.exe setup\prefetch_assets.py` |
| The terminal shows Python 3.6 when you type `python` | That's expected and fine. The labs use `.venv`, never the system Python. |
| Notebook says *"Running cells requires the ipykernel package"* | You picked the wrong kernel. Select **.venv** as in Task 5. |
| VS Code shows **Restricted Mode** | Click **Manage** in the banner and choose **Trust**. |
