"""
Lab 3 - Step 4: Tokenize a whole dataset efficiently and pick a max_length.

Covers:
  * Dataset.map(batched=True) - fast tokenization of thousands of rows
  * Token-length distribution  - how long are reviews in TOKENS?
  * Truncation trade-off       - what % of reviews get cut at 128/256/512?
  * Static vs dynamic padding  - how many [PAD] tokens are wasted compute?

Run:  python 04_tokenize_dataset.py
"""
import time

from lab_utils import DATASET, banner

MODEL = "distilbert/distilbert-base-uncased"
SAMPLE_SIZE = 5000
BATCH_SIZE = 16


def percentile(sorted_vals, p):
    return sorted_vals[min(len(sorted_vals) - 1, int(len(sorted_vals) * p))]


def main():
    from datasets import load_dataset
    from transformers import AutoTokenizer, DataCollatorWithPadding

    tok = AutoTokenizer.from_pretrained(MODEL)
    ds = load_dataset(DATASET, split="train").shuffle(seed=0).select(range(SAMPLE_SIZE))

    # ----------------------------------------------------- batched vs single
    banner(f"1. Tokenize {SAMPLE_SIZE} reviews: one-at-a-time vs batched")
    t0 = time.time()
    ds.select(range(1000)).map(lambda ex: tok(ex["text"]), batched=False)
    single = (time.time() - t0) * SAMPLE_SIZE / 1000
    t0 = time.time()
    tokenized = ds.map(lambda b: tok(b["text"]), batched=True, batch_size=1000)
    batched = time.time() - t0
    print(f"  one-at-a-time (estimated): {single:6.1f}s")
    print(f"  batched=True             : {batched:6.1f}s  (~{single / max(batched, 1e-6):.0f}x faster)")
    print("  Batched calls let the Rust 'fast' tokenizer work on many texts at once.")
    print("  Columns now:", tokenized.column_names)

    # ------------------------------------------------------ length analysis
    banner("2. How long are reviews in tokens?")
    lengths = sorted(len(ids) for ids in tokenized["input_ids"])
    print(f"  min={lengths[0]}  median={percentile(lengths, .5)}  "
          f"p90={percentile(lengths, .9)}  p95={percentile(lengths, .95)}  max={lengths[-1]}")
    print(f"  This model can read at most {tok.model_max_length} tokens.")

    banner("3. Choosing max_length: how much text do we throw away?")
    print(f"  {'max_length':>10}  {'reviews truncated':>18}  {'tokens discarded':>17}")
    total_tokens = sum(lengths)
    for m in [64, 128, 256, 512]:
        cut = sum(1 for n in lengths if n > m)
        lost = sum(n - m for n in lengths if n > m)
        print(f"  {m:>10}  {cut / len(lengths):>17.1%}  {lost / total_tokens:>16.1%}")
    print("  Longer max_length keeps more text but costs memory and time")
    print("  (attention cost grows roughly with the square of sequence length).")

    # --------------------------------------------- static vs dynamic padding
    MAXLEN = 512
    banner(f"4. Padding waste with max_length={MAXLEN}, batch size {BATCH_SIZE}")
    trunc = [min(n, MAXLEN) for n in (len(ids) for ids in tokenized["input_ids"])]
    real = sum(trunc)
    static_total = len(trunc) * MAXLEN
    dynamic_total = 0
    for i in range(0, len(trunc), BATCH_SIZE):
        chunk = trunc[i:i + BATCH_SIZE]
        dynamic_total += max(chunk) * len(chunk)
    sorted_trunc = sorted(trunc)
    bucketed_total = 0
    for i in range(0, len(sorted_trunc), BATCH_SIZE):
        chunk = sorted_trunc[i:i + BATCH_SIZE]
        bucketed_total += max(chunk) * len(chunk)

    def row(name, total):
        print(f"  {name:<34} {total:>10,} tokens   {(total - real) / total:>6.1%} padding")

    row(f"Static (pad everything to {MAXLEN})", static_total)
    row("Dynamic (pad to longest in batch)", dynamic_total)
    row("Dynamic + length-sorted batches", bucketed_total)
    print("  Every [PAD] token is compute you pay for but learn nothing from.")
    print("  Dynamic padding alone barely helps here: IMDB has a long tail, so almost")
    print("  every random batch contains one very long review. Grouping similar")
    print("  lengths together fixes it - in the Trainer that is")
    print("  TrainingArguments(train_sampling_strategy=\"group_by_length\").")

    banner("5. DataCollatorWithPadding does dynamic padding for you")
    collator = DataCollatorWithPadding(tok, return_tensors="pt")
    features = [{"input_ids": ids[:MAXLEN]} for ids in tokenized["input_ids"][:4]]
    batch = collator(features)
    print("  Lengths in this batch :", [len(f["input_ids"]) for f in features])
    print("  Padded batch shape    :", tuple(batch["input_ids"].shape))
    print("  This is exactly what the Trainer used in Lab 2.")

    print("\nDone. Next: python 05_token_budget.py")


if __name__ == "__main__":
    main()
