"""
Lab 3 - Step 1: Explore a dataset with the Hugging Face `datasets` library.

Covers: loading from the Hub, splits, features/labels, indexing, slicing,
shuffle/select, filter, map, train/test split, pandas, saving to disk,
and streaming.

Run:  python 01_explore_dataset.py
"""
import os
from collections import Counter

from lab_utils import DATASET, OUTPUT_DIR, banner


def main():
    from datasets import load_dataset

    # ------------------------------------------------------------------ load
    banner(f"1. Load '{DATASET}' from the Hugging Face Hub")
    ds = load_dataset(DATASET)
    print(ds)       # a DatasetDict: one Dataset per split
    print("\nSplits:", list(ds.keys()))

    train = ds["train"]

    # -------------------------------------------------------------- features
    banner("2. Schema: features and label names")
    print(train.features)
    label_feature = train.features["label"]           # a ClassLabel
    print("Label names:", label_feature.names)
    print("int2str(1) ->", label_feature.int2str(1))

    # ------------------------------------------------------- look at records
    banner("3. Looking at records")
    first = train[0]                                  # one row -> dict
    print("Keys:", list(first.keys()))
    print("Label:", label_feature.int2str(first["label"]))
    print("Text (first 300 chars):\n ", first["text"][:300], "...")

    batch = train[:3]                                 # slice -> dict of lists
    print("\nA slice returns a dict of lists:", {k: len(v) for k, v in batch.items()})

    # ---------------------------------------------------- label distribution
    banner("4. Label distribution per split")
    for split in ["train", "test"]:
        counts = Counter(ds[split]["label"])
        pretty = {label_feature.int2str(k): v for k, v in sorted(counts.items())}
        print(f"  {split:<6} {pretty}")
    print("  'unsupervised' split has label -1 (no label) - useful for pre-training.")

    # ----------------------------------------------------------- word length
    banner("5. Add a column with map(): word count per review")
    train = train.map(lambda ex: {"n_words": len(ex["text"].split())})
    lengths = sorted(train["n_words"])
    n = len(lengths)
    print(f"  Words per review  min={lengths[0]}  median={lengths[n // 2]}  "
          f"p95={lengths[int(n * 0.95)]}  max={lengths[-1]}")
    print("  Keep the p95 in mind - it drives tokenizer truncation in Step 4.")

    # ---------------------------------------------------------------- filter
    banner("6. filter(): keep only short reviews (< 50 words)")
    short = train.filter(lambda ex: ex["n_words"] < 50)
    print(f"  {len(short)} of {len(train)} reviews are under 50 words")
    print("  Example:", short[0]["text"][:200])

    # ------------------------------------------------- shuffle/select/split
    banner("7. shuffle + select + train_test_split (build a small working set)")
    small = train.shuffle(seed=42).select(range(2000))
    splits = small.train_test_split(test_size=0.2, seed=42, stratify_by_column="label")
    print(splits)

    # ---------------------------------------------------------------- pandas
    banner("8. Convert to pandas for quick analysis")
    df = small.to_pandas()
    df["label_name"] = df["label"].map(label_feature.int2str)
    print(df.groupby("label_name")["n_words"].describe().round(1))

    # ------------------------------------------------------------------ save
    banner("9. Save the working set to disk (Arrow format) and CSV")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    disk_path = os.path.join(OUTPUT_DIR, "imdb_small")
    splits.save_to_disk(disk_path)
    csv_path = os.path.join(OUTPUT_DIR, "imdb_small_train.csv")
    splits["train"].to_csv(csv_path)
    print("  Saved:", disk_path)
    print("  Saved:", csv_path)
    print("  Reload later with: datasets.load_from_disk(path)")

    # ------------------------------------------------------------- streaming
    banner("10. Streaming: iterate without downloading the whole dataset")
    stream = load_dataset(DATASET, split="test", streaming=True)
    for i, ex in enumerate(stream.take(3)):
        print(f"  [{i}] {label_feature.int2str(ex['label'])}: {ex['text'][:90]}...")
    print("  Streaming is how you work with datasets larger than your disk.")

    print("\nDone. Next: python 02_tokenizer_basics.py")


if __name__ == "__main__":
    main()
