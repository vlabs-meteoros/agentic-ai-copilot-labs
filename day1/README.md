# Day 1 Labs: AI Fundamentals, Neural Networks and Pre-trained Models

Start with **Lab 0**. It installs everything the other labs need.

| # | Lab | Topic it supports | Time | Needs |
|---|---|---|---|---|
| 0 | [Set Up Your Lab Environment](lab00-environment-setup/README.md) | One-time setup | 20 min | Internet |
| 1 | [Try Out Azure AI Services](lab01-azure-ai-services/README.md) | AI Fundamentals and Machine Learning | 40 min | Your lab account (agentuserN) for the Azure portal |
| 2 | [Transfer Learning with the Trainer](lab02-transfer-learning/README.md) | Neural Networks and Deep Learning | 45 min | Internet or prefetched models; CPU is fine |
| 3 | [Datasets and Tokenizers](lab03-datasets-tokenizers/README.md) | Pre-trained Models (LLMs, tokens, cost) | 40 min | Internet or prefetched assets |

## How the labs connect

```
Lab 1  Use pre-trained models as a service       ->  "AI without training"
Lab 2  Adapt a pre-trained model to a new task   ->  "transfer learning"
Lab 3  Look inside: data, tokens, and token cost ->  "how LLM inputs really work"
```

Each lab folder contains:

* `README.md`: the step-by-step lab guide
* `Lab0X_*.ipynb`: the notebook you run in VS Code (**main path**)
* `*.py` (Labs 2 and 3): the same lab as terminal scripts, an optional alternative
