"""
Download every model, tokenizer, dataset and tiktoken file the Day 1 labs use,
so the labs run without waiting on downloads (or offline).

    python setup\\prefetch_assets.py

Total download: roughly 1 GB. Files go to the normal Hugging Face cache
(%USERPROFILE%\\.cache\\huggingface) unless HF_HOME is set.
"""
import os
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FULL_MODELS = ["distilbert/distilbert-base-uncased"]               # Lab 2 + 3 (weights needed)
TOKENIZERS = ["google-bert/bert-base-uncased", "openai-community/gpt2",
              "FacebookAI/xlm-roberta-base"]                         # Lab 3 (tokenizer files only)
DATASETS = ["stanfordnlp/sst2", "stanfordnlp/imdb"]                 # Lab 2, Lab 3
TIKTOKEN = ["cl100k_base", "o200k_base"]                            # Lab 3


def step(label, fn):
    t0 = time.time()
    try:
        fn()
        print(f"  [ OK ] {label} ({time.time() - t0:.0f}s)")
        return True
    except Exception as e:
        print(f"  [FAIL] {label}: {type(e).__name__}: {str(e)[:200]}")
        return False


def main():
    from datasets import load_dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from transformers.utils import logging as hf_logging
    import tiktoken

    hf_logging.set_verbosity_error()
    ok = True
    print("Models:")
    for m in FULL_MODELS:
        ok &= step(m, lambda m=m: (AutoTokenizer.from_pretrained(m),
                                   AutoModelForSequenceClassification.from_pretrained(m, num_labels=2)))
    print("Tokenizers:")
    for m in TOKENIZERS:
        ok &= step(m, lambda m=m: AutoTokenizer.from_pretrained(m))
    print("Datasets:")
    for d in DATASETS:
        ok &= step(d, lambda d=d: load_dataset(d))
    print("tiktoken encodings:")
    for e in TIKTOKEN:
        ok &= step(e, lambda e=e: tiktoken.get_encoding(e).encode("warm-up"))

    print("\nAll assets cached." if ok else "\nSome downloads failed - check network/proxy and re-run.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
