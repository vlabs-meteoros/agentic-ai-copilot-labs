"""
Lab 3 - Step 2: How a tokenizer turns text into numbers.

Uses the BERT tokenizer (WordPiece) to show:
  tokens -> ids -> special tokens -> attention mask -> padding/truncation
  -> tensors -> decoding -> offsets (which characters each token came from)

Run:  python 02_tokenizer_basics.py
"""
from lab_utils import banner, show_tokens

MODEL = "google-bert/bert-base-uncased"


def main():
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL)

    banner(f"1. Tokenizer facts: {MODEL}")
    print(f"  Class          : {type(tok).__name__}")
    print(f"  Vocabulary size: {tok.vocab_size:,}")
    print(f"  Max length     : {tok.model_max_length}")
    print(f"  Special tokens : {tok.all_special_tokens}")

    text = "Tokenization isn't magic: transformers read sub-words!"

    banner("2. Text -> tokens -> ids")
    tokens = tok.tokenize(text)
    ids = tok.convert_tokens_to_ids(tokens)
    print("  Text  :", text)
    print("  Tokens:", show_tokens(tokens))
    print("  IDs   :", ids)
    print("  Note '##' = this piece continues the previous word (WordPiece).")

    banner("3. Calling the tokenizer directly adds special tokens")
    enc = tok(text)
    print("  input_ids     :", enc["input_ids"])
    print("  tokens        :", show_tokens(tok.convert_ids_to_tokens(enc["input_ids"])))
    print("  attention_mask:", enc["attention_mask"])
    print("  [CLS] starts every sequence, [SEP] ends it.")

    banner("4. Decoding goes back to text (lower-cased: this model is 'uncased')")
    print("  ", tok.decode(enc["input_ids"]))
    print("  ", tok.decode(enc["input_ids"], skip_special_tokens=True))

    banner("5. Out-of-vocabulary words are split, not lost")
    for word in ["cat", "unbelievably", "Mysuru", "COVID-19", "😀"]:
        print(f"  {word:<14} -> {show_tokens(tok.tokenize(word))}")
    print("  The emoji becomes [UNK]: this vocabulary has no piece for it.")

    banner("6. Batches: padding + truncation + attention mask")
    batch = ["Short one.",
             "A slightly longer sentence than the first.",
             "This third sentence is deliberately much longer than the other two so it gets cut."]
    enc = tok(batch, padding=True, truncation=True, max_length=12)
    for i, ids in enumerate(enc["input_ids"]):
        print(f"  [{i}] {show_tokens(tok.convert_ids_to_tokens(ids))}")
        print(f"      mask {enc['attention_mask'][i]}")
    print("  [PAD] fills short sequences; mask=0 tells the model to ignore them.")
    print("  Sentence [2] was truncated at 12 tokens.")

    banner("7. Ready-made tensors for PyTorch")
    tensors = tok(batch, padding=True, return_tensors="pt")
    print("  input_ids shape:", tuple(tensors["input_ids"].shape), " (batch, sequence_length)")

    banner("8. Offsets: map each token back to the original characters")
    enc = tok("Mysuru Palace glows at night", return_offsets_mapping=True)
    for t, (s, e) in zip(tok.convert_ids_to_tokens(enc["input_ids"]), enc["offset_mapping"]):
        print(f"  {t:<10} chars {s:>2}-{e:<2}")
    print("  Offsets are how NER and question answering highlight spans in the text.")

    print("\nDone. Next: python 03_compare_tokenizers.py")


if __name__ == "__main__":
    main()
