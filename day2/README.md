# Day 2 Labs: Tools and Ecosystems for LLM Agents, HF Transformers, GenAI Fundamentals

## Before you start (10 min, do this first)

Day 2 adds new packages and settings. In a VS Code terminal at the repository root:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\setup\setup-windows.ps1 -Prefetch
```

The script reuses your `.venv`, installs the Day 2 packages, adds the new Day 2 settings to your existing `.env`
(your Day 1 values are kept), and downloads the Day 2 models (~1.4 GB). It takes 5-10 minutes.

**While it runs**, create the two free accounts you'll need. Both are web sign-ups in the VM browser:

1. **Hugging Face** account and a **Write** token (Lab 4, Task 1): https://huggingface.co/join

## Labs

| # | Lab | Topic it supports | Time | Needs |
|---|---|---|---|---|
| 4 | [Hugging Face Hub and CLI](lab04-hf-hub-cli/README.md) | Tools and Ecosystems for LLM Agents | 30 min | Hugging Face account |
| 5 | [Getting Started with LLM Usage](lab05-llm-usage/README.md) | HF Transformers | 40 min | Prefetched models (or internet). Optional: Pinecone account |
| 6 | [Prompt Variations and Grounding](lab06-prompt-variations/README.md) | Generative AI Fundamentals | 30 min | Azure values from Lab 1 |

## How the labs connect

```
Lab 4  Share models: the Hugging Face Hub          ->  publish your Day 1 model, use it anywhere
Lab 5  Use models locally: pipelines, generation,  ->  embeddings + FAISS search over a company knowledge base
       embeddings, semantic search
Lab 6  Use a large hosted LLM through its API      ->  prompt variations, grounding on the same knowledge base,
                                                       Responsible AI
```

All three labs use the same fictional company, **Kaveri Systems**: its helpdesk knowledge base is in `day2/data/helpdesk_kb.json`.

Each lab folder contains:

* `README.md`: the step-by-step lab guide, with checkpoints
* `Lab0X_*.ipynb`: the notebook you run in VS Code (Lab 4 is mostly terminal; its notebook is a companion)
* `*_helpers.py` (Labs 6 and 7): connection code shared by the notebook cells