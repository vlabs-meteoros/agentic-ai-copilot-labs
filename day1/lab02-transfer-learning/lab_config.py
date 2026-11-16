"""
Shared settings for Lab 2 - Transfer Learning with the Hugging Face Trainer.

Every script in this lab imports from here, so you only change values in ONE place.
"""
import os
import sys

# Windows terminals sometimes choke on non-ASCII output; force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Optional settings (e.g. HF_TOKEN) from the repository's .env file
try:
    from pathlib import Path
    from dotenv import load_dotenv
    for _folder in [Path.cwd(), *Path.cwd().parents][:4]:
        if (_folder / ".env").exists():
            load_dotenv(_folder / ".env")
            break
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Model and data
# ---------------------------------------------------------------------------
# DistilBERT: a 66M-parameter, 6-layer "distilled" version of BERT.
# It was pre-trained on English Wikipedia + BookCorpus to understand language.
# It has NEVER seen a sentiment label. We transfer its knowledge to a new task.
BASE_MODEL = "distilbert/distilbert-base-uncased"

# SST-2 (Stanford Sentiment Treebank): short movie-review sentences
# labelled 0 = negative, 1 = positive.
DATASET = "stanfordnlp/sst2"
TEXT_COLUMN = "sentence"

LABELS = {0: "NEGATIVE", 1: "POSITIVE"}

# ---------------------------------------------------------------------------
# Size of the experiment (tuned so the full lab runs on a CPU-only VM)
# ---------------------------------------------------------------------------
TRAIN_SIZE = 2000      # training sentences sampled from 67k available
EVAL_SIZE = 872        # the full SST-2 validation split
MAX_LENGTH = 64        # SST-2 sentences are short; 64 tokens covers ~99%
SEED = 42

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "results.json")


def describe_device():
    """Print what hardware the Trainer will use and return its name."""
    import torch

    if torch.cuda.is_available():
        name = f"cuda ({torch.cuda.get_device_name(0)})"
    else:
        name = f"cpu ({os.cpu_count()} logical cores)"
    print(f"[device] Training will run on: {name}")
    return name


def load_splits(tokenizer, train_size=TRAIN_SIZE, eval_size=EVAL_SIZE):
    """Download SST-2, take a reproducible sample, and tokenize it."""
    from datasets import load_dataset

    raw = load_dataset(DATASET)
    train = raw["train"].shuffle(seed=SEED).select(range(train_size))
    evaluation = raw["validation"].select(range(min(eval_size, len(raw["validation"]))))

    def tokenize(batch):
        # Padding is NOT done here. The Trainer's data collator pads each
        # batch dynamically to the longest sentence in that batch (faster).
        return tokenizer(batch[TEXT_COLUMN], truncation=True, max_length=MAX_LENGTH)

    train = train.map(tokenize, batched=True, remove_columns=["idx", TEXT_COLUMN])
    evaluation = evaluation.map(tokenize, batched=True, remove_columns=["idx", TEXT_COLUMN])
    return train, evaluation


def compute_metrics(eval_pred):
    """Called by the Trainer after each evaluation pass."""
    import numpy as np
    from sklearn.metrics import accuracy_score, f1_score

    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": round(float(accuracy_score(labels, preds)), 4),
        "f1": round(float(f1_score(labels, preds)), 4),
    }


def save_result(name, metrics):
    """Append a run's metrics to outputs/results.json so we can compare runs."""
    import json

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    data[name] = metrics
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
