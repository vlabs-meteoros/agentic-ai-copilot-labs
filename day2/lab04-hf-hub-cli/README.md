# Lab 4: Hugging Face Hub and CLI

| | |
|---|---|
| **Duration** | 30 minutes |
| **Topic** | Tools and Ecosystems for LLM Agents: Hugging Face Hub, `hf` CLI, the Hub's Git interface |
| **You need** | A free Hugging Face account (created in Task 1), internet access, your Day 1 Lab 2 model (optional) |
| **Files** | This README (main path, terminal) + `Lab04_HF_Hub_Companion.ipynb` (Python steps) |

## Objectives

* Create a Hugging Face access token and log in from the command line
* Search, inspect and download models with the `hf` CLI, and manage the local cache
* Publish your Day 1 fine-tuned model to the Hub with a proper **model card**, and tag a version
* Load your model back from the Hub by its repo id
* Use the Hub as a plain **Git** server: clone, commit and push

---

## Task 1: Create a Hugging Face account and an access token (5 min)

1. In the VM browser, go to **https://huggingface.co/join** and sign up (any email you can open; a personal one is fine).
2. Open the verification email and click the link. **Uploads fail until your email is verified.**
3. Click your avatar (top right) > **Access Tokens** > **+ Create new token**.
4. Choose the **Write** tab, name it `agentic-labs`, and click **Create token**.
5. Copy the token (it starts with `hf_`). You can't see it again; you can always create a new one.

> **Token safety:** a write token can change or delete your repos. Never paste it into code, a notebook, chat or Git.
> For real projects, prefer **fine-grained** tokens limited to specific repos.

## Task 2: Log in with the CLI (3 min)

Open a terminal in VS Code (<kbd>Ctrl</kbd>+<kbd>`</kbd>) at the repository root and activate the lab environment:

```powershell
.\.venv\Scripts\Activate.ps1
hf version
hf auth login --add-to-git-credential
```

Paste your token when asked (nothing appears as you paste; that's normal) and press <kbd>Enter</kbd>.
`--add-to-git-credential` also stores it for Git, which you'll need in Task 6.

```powershell
hf auth whoami
```

**Checkpoint:** `hf auth whoami` prints your username.
The token is saved in `%USERPROFILE%\.cache\huggingface\token`, so Python code (and Labs 5-7) can use it without `.env`.

## Task 3: Explore the Hub from the terminal (6 min)

Run each command and read the output.

```powershell
# Search: the five most-downloaded models matching "sentiment"
hf models ls --search sentiment --sort downloads --limit 5

# Details about one model (only the fields we ask for)
hf models info distilbert/distilbert-base-uncased-finetuned-sst-2-english --expand downloads,likes,pipeline_tag,tags

# The files inside a model repo (the LLM you'll run in Lab 5)
hf models ls Qwen/Qwen2.5-0.5B-Instruct

# Read its model card (README) without opening a browser
hf models card Qwen/Qwen2.5-0.5B-Instruct

# Download just two small files into a folder (not the 988 MB weights)
hf download Qwen/Qwen2.5-0.5B-Instruct config.json generation_config.json --local-dir day2\lab04-hf-hub-cli\outputs\qwen-config
Get-Content day2\lab04-hf-hub-cli\outputs\qwen-config\config.json

# Datasets live on the Hub too
hf datasets ls --search imdb --limit 3

# What's already in your local cache, biggest first?
hf cache ls --sort size
```

**Checkpoint / questions:**

* `config.json` for Qwen2.5-0.5B shows `num_hidden_layers` (24) and `vocab_size` (151,936). Compare with DistilBERT's 6 layers and ~30k vocabulary from Day 1.
* `hf cache ls` lists the models and datasets from Day 1 (`distilbert`, `stanfordnlp/imdb`, ...). This cache is why the second load of a model is instant.

> `hf download` without `--local-dir` puts files in the shared cache, which is what `from_pretrained` uses.
> With `--local-dir` you get a plain folder copy, useful for shipping a model with an app.

## Task 4: Publish your Day 1 model (8 min)

### 4a. Prepare the folder and model card (notebook)

1. Open `Lab04_HF_Hub_Companion.ipynb`, select the **.venv** kernel.
2. Run **Part 1** (checks your login) and **Part 2** (copies your Day 1 model to `outputs/model-to-publish` and writes a model card).

If you didn't finish Day 1 Lab 2, Part 2 uses a public sentiment model instead, and says so in the card.

### 4b. Create the repo and upload (terminal)

Replace `YOUR-USERNAME` with your Hugging Face username:

```powershell
cd day2\lab04-hf-hub-cli

hf repos create YOUR-USERNAME/distilbert-sst2-lab --private

hf upload YOUR-USERNAME/distilbert-sst2-lab outputs\model-to-publish . --commit-message "Upload Day 1 fine-tuned DistilBERT"

hf repos tag create YOUR-USERNAME/distilbert-sst2-lab v1.0

hf models ls YOUR-USERNAME/distilbert-sst2-lab
```

Open `https://huggingface.co/YOUR-USERNAME/distilbert-sst2-lab` in the browser:

* The **model card** renders from `README.md`, with metadata tags (license, dataset, base model) and your accuracy.
* **Files and versions** shows each file and the commit history. The 268 MB `model.safetensors` is stored with large-file storage (Xet).
* The repo is **private**: only you can see it. Change that under **Settings** if you want to share it.

**Checkpoint:** `hf models ls YOUR-USERNAME/distilbert-sst2-lab` lists `README.md`, `config.json`, `model.safetensors` and the tokenizer files.

## Task 5: Use your model from the Hub (3 min)

Run notebook **Part 3**. It loads the model by repo id with `pipeline(...)` (exactly how anyone else would use it), then lists the commits and tags.

**Checkpoint:** the three test sentences are classified, and the commit list shows your upload with tag `v1.0`.

## Task 6: The Hub is a Git server (5 min)

Every Hub repo is a Git repository. Clone yours, change the model card, and push, using nothing but Git.

```powershell
# Still in day2\lab04-hf-hub-cli. Skip downloading the big weights file: we only want to edit text.
$env:GIT_LFS_SKIP_SMUDGE = "1"
git clone https://huggingface.co/YOUR-USERNAME/distilbert-sst2-lab outputs\hf-clone
cd outputs\hf-clone
git log --oneline
Get-Item model.safetensors | Select-Object Name, Length
```

`model.safetensors` is only ~135 bytes: it's a **pointer** file. The real weights stay on the Hub's large-file storage until you need them.

Add a line to the model card and push it:

```powershell
Add-Content README.md "`n## Changelog`n* v1.0: first upload from the Agentic AI with Copilot training."
git add README.md
git commit -m "Add changelog to model card"
git push
cd ..\..
```

If Git asks for credentials: **username** = your Hugging Face username, **password** = your `hf_` token.

**Checkpoint:** refresh the model page; the card shows the **Changelog** section. Run the commit-history cell in notebook Part 3 again: your `git push` is the newest commit.

> **CLI or Git?** Use `hf upload` / `hf download` for models and data: they handle multi-GB files, resume, and don't need a full clone.
> Use Git when you want normal code workflows (branches, diffs, pull requests) on small files.

---

## Optional: clean up

```powershell
hf repos delete YOUR-USERNAME/distilbert-sst2-lab      # asks for confirmation; deletes the repo on the Hub
hf cache rm model/Qwen/Qwen2.5-0.5B-Instruct            # only if you need disk space (Lab 5 uses it!)
```

Keep the repo if you want to use it in Lab 5 (`MY_REPO`).

## Troubleshooting

| Problem | Fix |
|---|---|
| `hf` is not recognised | Activate the environment first: `.\.venv\Scripts\Activate.ps1` (if blocked: `Set-ExecutionPolicy -Scope Process Bypass`) |
| `403 Forbidden` on upload | The token is **Read** only, or your email isn't verified. Create a **Write** token and run `hf auth login --force` |
| `401` / "Invalid credentials" on `git push` | Use the token as the password, not your account password. Clear an old saved entry in **Windows Credential Manager** (search "Credential Manager" > Windows Credentials > `git:https://huggingface.co`) |
| `git clone` downloads 268 MB | You forgot `$env:GIT_LFS_SKIP_SMUDGE = "1"` in that terminal; delete `outputs\hf-clone` and try again |
| `Repository not found` | Check the username spelling, and that you're logged in as the repo owner (`hf auth whoami`) |
