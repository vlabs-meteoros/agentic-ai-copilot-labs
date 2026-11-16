"""
Lab 3 - Step 3: Different models, different tokenizers, different token counts.

Compares five tokenizers on the same inputs:
  * BERT            - WordPiece          (encoder models: classification, NER)
  * GPT-2           - byte-level BPE     (the classic GPT tokenizer)
  * XLM-RoBERTa     - SentencePiece      (multilingual, 100 languages)
  * tiktoken cl100k - BPE used by GPT-4 / GPT-3.5-turbo
  * tiktoken o200k  - BPE used by GPT-4o-family models

Why it matters: LLM APIs bill per token and context windows are measured in
tokens. The SAME text can cost very different amounts on different models
and in different languages.

Run:  python 03_compare_tokenizers.py
"""
from lab_utils import banner, show_tokens

SAMPLES = {
    "English":  "The quarterly report shows revenue grew by 12% year over year.",
    "Code":     "def add(a, b):\n    return a + b",
    "Numbers":  "Order #847261 shipped on 2026-11-15 for Rs. 1,24,999.00",
    "JSON":     '{"customer_id": 1042, "status": "active", "tier": "gold"}',
    "Hindi":    "तिमाही रिपोर्ट से पता चलता है कि राजस्व में 12% की वृद्धि हुई।",
    "Kannada":  "ತ್ರೈಮಾಸಿಕ ವರದಿಯು ಆದಾಯ 12% ಹೆಚ್ಚಾಗಿದೆ ಎಂದು ತೋರಿಸುತ್ತದೆ.",
    "Emoji":    "Great service 👍🔥 will order again 😀",
}


def load_tokenizers():
    import tiktoken
    from transformers import AutoTokenizer

    hf = {
        "BERT (WordPiece)": AutoTokenizer.from_pretrained("google-bert/bert-base-uncased"),
        "GPT-2 (BPE)": AutoTokenizer.from_pretrained("openai-community/gpt2"),
        "XLM-R (SentencePiece)": AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-base"),
    }
    tk = {
        "tiktoken cl100k": tiktoken.get_encoding("cl100k_base"),
        "tiktoken o200k": tiktoken.get_encoding("o200k_base"),
    }

    # Uniform interface: name -> (count_fn, pieces_fn)
    out = {}
    for name, t in hf.items():
        out[name] = (
            lambda s, t=t: len(t.encode(s, add_special_tokens=False)),
            lambda s, t=t: t.tokenize(s),
        )
    for name, enc in tk.items():
        out[name] = (
            lambda s, enc=enc: len(enc.encode(s)),
            lambda s, enc=enc: [enc.decode_single_token_bytes(i).decode("utf-8", errors="replace")
                                for i in enc.encode(s)],
        )
    return out


def main():
    banner("Loading tokenizers (first run downloads small vocab files)")
    toks = load_tokenizers()
    names = list(toks)

    banner("1. Token counts for the same text")
    short = {"BERT (WordPiece)": "BERT", "GPT-2 (BPE)": "GPT-2", "XLM-R (SentencePiece)": "XLM-R",
             "tiktoken cl100k": "cl100k", "tiktoken o200k": "o200k"}
    header = f"{'Sample':<9}{'chars':>6}" + "".join(f"{short[n]:>9}" for n in names)
    print(header)
    print("-" * len(header))
    for label, text in SAMPLES.items():
        row = f"{label:<9}{len(text):>6}"
        for n in names:
            row += f"{toks[n][0](text):>9}"
        print(row)

    banner("2. See the pieces: English vs Hindi on GPT-2 vs o200k")
    for label in ["English", "Hindi"]:
        text = SAMPLES[label]
        for n in ["GPT-2 (BPE)", "tiktoken o200k"]:
            pieces = toks[n][1](text)
            print(f"\n  {label} | {n} | {len(pieces)} tokens")
            print("  ", show_tokens(pieces, limit=30))
    print("\n  GPT-2 learned its merges mostly from English web text, so Hindi")
    print("  falls apart into byte fragments. o200k has a far larger, more")
    print("  multilingual vocabulary, so the same sentence costs fewer tokens.")

    banner("3. 'Language tax': tokens relative to the English sentence")
    for n in ["GPT-2 (BPE)", "tiktoken cl100k", "tiktoken o200k"]:
        base = toks[n][0](SAMPLES["English"])
        ratios = {lbl: toks[n][0](SAMPLES[lbl]) / base for lbl in ["Hindi", "Kannada"]}
        print(f"  {n:<17} Hindi x{ratios['Hindi']:.1f}   Kannada x{ratios['Kannada']:.1f}")
    print("  Same meaning, several times the tokens -> several times the cost")
    print("  and a context window that fills up much faster.")

    banner("4. Whitespace and casing are tokens too")
    enc = toks["tiktoken o200k"]
    for s in ["hello", " hello", "Hello", "HELLO", "hello   world"]:
        print(f"  {s!r:<16} -> {enc[1](s)}")

    print("\nDone. Next: python 04_tokenize_dataset.py")


if __name__ == "__main__":
    main()
