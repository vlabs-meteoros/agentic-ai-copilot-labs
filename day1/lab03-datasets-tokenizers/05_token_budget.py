"""
Lab 3 - Step 5: Token budgeting - what would this cost on an LLM API?

Scenario: your team wants to use an LLM to label the sentiment of all 25,000
IMDB test reviews. Before sending a single request, we COUNT tokens with
tiktoken and estimate cost for several strategies:

  A. Naive                - one request per review, verbose JSON answer
  B. Constrained output   - ask for a single word label
  C. Truncate input       - cap each review at a token budget
  D. Batch many per call  - 20 reviews per request, instructions sent once
  E. + Prompt caching     - long, identical prefix billed at a cached rate
  F. + Batch API          - asynchronous batch jobs at a discount
  G. + Response cache     - never pay twice for an identical review

No API calls are made - this is pure arithmetic on real token counts.

Run:  python 05_token_budget.py
      python 05_token_budget.py --sample 1000     (faster)
"""
import argparse
from collections import Counter

from lab_utils import DATASET, banner

# ---------------------------------------------------------------------------
# EXAMPLE prices in USD per 1 million tokens. These are ILLUSTRATIVE numbers
# for a small "mini"-class model. Replace them with the current figures from
# your provider's pricing page before using this for a real estimate.
# ---------------------------------------------------------------------------
PRICE = {
    "input": 0.40,          # normal input tokens
    "cached_input": 0.10,   # input tokens served from the prompt cache
    "output": 1.60,         # generated tokens
}
BATCH_API_DISCOUNT = 0.50   # many providers discount async batch jobs ~50%
CACHE_MIN_PREFIX = 1024     # prompt caching usually needs a prefix >= 1024 tokens

ENCODING = "o200k_base"     # tokenizer of GPT-4o-family models
REVIEWS_PER_BATCH = 20
TRUNCATE_TO = 300

INSTRUCTIONS = """You are a sentiment analysis service for a film studio.
Classify each movie review as positive or negative.
Rules:
- Judge the reviewer's overall opinion of the film, not the plot's mood.
- Sarcasm counts as the opinion it expresses.
- Mixed reviews: choose the side the reviewer ends on.
"""


def build_few_shot(examples, enc, per_example_tokens=110):
    """Few-shot examples make the prompt longer (and better). Trim each one."""
    lines = ["Examples:"]
    for ex in examples:
        ids = enc.encode(ex["text"])[:per_example_tokens]
        label = "positive" if ex["label"] == 1 else "negative"
        lines.append(f"Review: {enc.decode(ids)}\nLabel: {label}")
    return "\n\n".join(lines)


def cost(n_input, n_output, n_cached=0, batch_api=False):
    usd = ((n_input - n_cached) * PRICE["input"]
           + n_cached * PRICE["cached_input"]
           + n_output * PRICE["output"]) / 1_000_000
    return usd * (1 - BATCH_API_DISCOUNT) if batch_api else usd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", type=int, default=2500,
                   help="reviews to measure (results are scaled to the full split)")
    args = p.parse_args()

    import tiktoken
    from datasets import load_dataset

    enc = tiktoken.get_encoding(ENCODING)
    test = load_dataset(DATASET, split="test")
    train = load_dataset(DATASET, split="train")
    N = len(test)
    sample = test.shuffle(seed=1).select(range(min(args.sample, N)))
    scale = N / len(sample)

    few_shot = build_few_shot(train.shuffle(seed=7).select(range(10)), enc)
    system_short = INSTRUCTIONS
    system_long = INSTRUCTIONS + "\n" + few_shot

    t_short = len(enc.encode(system_short))
    t_long = len(enc.encode(system_long))
    review_tokens = [len(enc.encode(t)) for t in sample["text"]]
    review_trunc = [min(n, TRUNCATE_TO) for n in review_tokens]
    avg_review = sum(review_tokens) / len(review_tokens)

    banner("1. Measure before you spend")
    print(f"  Tokenizer             : {ENCODING}")
    print(f"  Reviews to label      : {N:,}")
    print(f"  Avg tokens per review : {avg_review:.0f}  (max {max(review_tokens):,})")
    print(f"  Instructions only     : {t_short} tokens")
    print(f"  Instructions + 10-shot: {t_long} tokens "
          f"({'eligible' if t_long >= CACHE_MIN_PREFIX else 'too short'} for prompt caching)")
    print(f"  Prices used (USD / 1M): {PRICE}  <- EXAMPLE values, update them!")

    OVERHEAD = 8           # per-message formatting tokens (role markers etc.)
    VERBOSE_OUT = 60       # {"label": "...", "confidence": 0.9, "reason": "..."}
    LABEL_OUT = 2          # "positive"

    rows = []

    # A. naive: 1 request per review, long few-shot prompt, verbose output
    inp = sum(t_long + n + OVERHEAD for n in review_tokens) * scale
    out = VERBOSE_OUT * N
    rows.append(("A. Naive (1 call/review, verbose JSON)", N, inp, out, cost(inp, out)))

    # B. constrained output
    out_b = LABEL_OUT * N
    rows.append(("B. + one-word label output", N, inp, out_b, cost(inp, out_b)))

    # C. truncate reviews
    inp_c = sum(t_long + n + OVERHEAD for n in review_trunc) * scale
    rows.append((f"C. + truncate reviews to {TRUNCATE_TO} tokens", N, inp_c, out_b, cost(inp_c, out_b)))

    # D. batch 20 reviews per request: prompt paid once per request
    calls = -(-N // REVIEWS_PER_BATCH)
    per_review_in = sum(n + 6 for n in review_trunc) * scale    # +"[17] " numbering
    inp_d = calls * (t_long + OVERHEAD) + per_review_in
    out_d = N * (LABEL_OUT + 3)                                   # "17: positive\n"
    rows.append((f"D. + {REVIEWS_PER_BATCH} reviews per request", calls, inp_d, out_d, cost(inp_d, out_d)))

    # E. prompt caching on the identical long prefix (all calls after the first)
    cached = (calls - 1) * t_long if t_long >= CACHE_MIN_PREFIX else 0
    rows.append(("E. + prompt caching of the prefix", calls, inp_d, out_d, cost(inp_d, out_d, cached)))

    # F. batch API discount
    rows.append(("F. + async Batch API discount", calls, inp_d, out_d,
                 cost(inp_d, out_d, cached, batch_api=True)))

    # G. response cache: identical reviews are labelled once
    dupes = sum(c - 1 for c in Counter(test["text"]).values() if c > 1)
    keep = (N - dupes) / N
    rows.append((f"G. + response cache ({dupes} duplicate reviews)", int(calls * keep),
                 inp_d * keep, out_d * keep, cost(inp_d * keep, out_d * keep, cached * keep, True)))

    banner(f"2. Estimated cost to label {N:,} reviews")
    print(f"  {'Strategy':<44}{'Calls':>8}{'Input tok':>14}{'Output tok':>13}{'USD':>9}")
    print("  " + "-" * 86)
    base = rows[0][4]
    for name, c, i, o, usd in rows:
        print(f"  {name:<44}{c:>8,}{int(i):>14,}{int(o):>13,}{usd:>9.2f}")
    print("  " + "-" * 86)
    print(f"  From A to G the bill drops by {1 - rows[-1][4] / base:.0%}.")

    banner("3. Trade-offs to discuss")
    print("  * One-word output: cheaper and easier to parse, but no explanation.")
    print("  * Truncation: may cut the sentence that decides the sentiment.")
    print("  * Batching per request: fewer calls, but one bad answer can spoil the batch.")
    print("  * Prompt caching: needs an IDENTICAL prefix - keep variable text at the end.")
    print("  * Batch API: much cheaper but results can take hours - not for live users.")
    print("  * Response cache: only helps when inputs really repeat.")

    banner("4. A budget guard you can reuse")
    budget = 4000
    review = test[0]["text"]
    request_tokens = t_long + len(enc.encode(review)) + OVERHEAD
    verdict = "OK to send" if request_tokens <= budget else "REJECT or truncate"
    print(f"  Request needs {request_tokens} input tokens; budget is {budget} -> {verdict}")

    print("\nDone. Optional stretch: python 06_train_custom_tokenizer.py")


if __name__ == "__main__":
    main()
