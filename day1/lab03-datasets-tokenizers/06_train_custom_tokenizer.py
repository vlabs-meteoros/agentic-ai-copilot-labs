"""
Lab 3 - Step 6 (stretch): Train your own BPE tokenizer on movie reviews.

Tokenizers are LEARNED from data. Here we train a small byte-level BPE
tokenizer on 20,000 IMDB reviews and compare it with GPT-2's tokenizer,
which was trained on general web text.

Run:  python 06_train_custom_tokenizer.py
"""
import os
import time

from lab_utils import DATASET, OUTPUT_DIR, banner, show_tokens

VOCAB_SIZE = 32000
TRAIN_REVIEWS = 20000


def main():
    from datasets import load_dataset
    from tokenizers import ByteLevelBPETokenizer
    from transformers import AutoTokenizer

    ds = load_dataset(DATASET, split="train").shuffle(seed=3)
    corpus = ds.select(range(TRAIN_REVIEWS))["text"]
    held_out = load_dataset(DATASET, split="test").shuffle(seed=3).select(range(1000))["text"]

    banner(f"1. Train a byte-level BPE tokenizer (vocab {VOCAB_SIZE:,}) on {TRAIN_REVIEWS:,} reviews")
    tok = ByteLevelBPETokenizer()
    t0 = time.time()
    tok.train_from_iterator(corpus, vocab_size=VOCAB_SIZE, min_frequency=2,
                            special_tokens=["<pad>", "<unk>", "<s>", "</s>"])
    print(f"  Trained in {time.time() - t0:.1f}s")

    out_dir = os.path.join(OUTPUT_DIR, "imdb-bpe")
    os.makedirs(out_dir, exist_ok=True)
    tok.save_model(out_dir)
    print(f"  Saved vocab.json + merges.txt to {out_dir}")

    banner("2. What did it learn? A few of the longest tokens")
    vocab = tok.get_vocab()
    longest = sorted(vocab, key=len, reverse=True)[:15]
    print("  ", [t.replace("Ġ", "_") for t in longest])
    print("  ('_' marks a leading space - byte-level BPE keeps spaces inside tokens)")

    banner("3. Compare with GPT-2 (vocab 50,257, trained on general web text)")
    from transformers.utils import logging as hf_logging
    hf_logging.set_verbosity_error()   # silence "longer than max length" (we only count)
    gpt2 = AutoTokenizer.from_pretrained("openai-community/gpt2")
    ours = sum(len(tok.encode(t).ids) for t in held_out)
    theirs = sum(len(gpt2.encode(t)) for t in held_out)
    print(f"  Tokens for 1,000 unseen reviews -> ours: {ours:,}   GPT-2: {theirs:,}")
    print(f"  Our tokenizer needs {ours / theirs:.0%} of GPT-2's token count, with a vocab "
          f"{VOCAB_SIZE / 50257:.0%} the size.")

    sample = "The cinematography was breathtaking but the screenplay felt underwhelming."
    print("\n  Sample:", sample)
    print("  ours :", show_tokens([t.replace("Ġ", "_") for t in tok.encode(sample).tokens]))
    print("  GPT-2:", show_tokens([t.replace("Ġ", "_") for t in gpt2.tokenize(sample)]))

    off_domain = "def calculate_gst(amount): return amount * 0.18"
    print("\n  Off-domain text:", off_domain)
    print(f"  ours : {len(tok.encode(off_domain).ids)} tokens   GPT-2: {len(gpt2.encode(off_domain))} tokens")
    print("  A domain tokenizer is compact on its domain, and worse outside it.")

    print("\nDone. Lab 3 complete.")


if __name__ == "__main__":
    main()
