# Lab 3: Datasets and Tokenizers

| | |
|---|---|
| **Duration** | 40 minutes (+ optional stretch) |
| **Topic** | Pre-trained Models: LLM inputs, tokenization, token and cost optimisation |
| **You need** | Internet access to Hugging Face, or assets prefetched during setup |
| **Notebook** | `Lab03_Datasets_and_Tokenizers.ipynb` |

## Objectives

* Load, inspect, transform, split, save and stream datasets with Hugging Face `datasets`
* Explain tokens, token IDs, special tokens, attention masks, padding and truncation
* Compare WordPiece, BPE and SentencePiece tokenizers, and measure the **language tax**
* Choose a `max_length` and padding strategy based on real token statistics
* **Estimate LLM cost** and apply budgeting, batching and caching strategies

---

## Task 1: Open the notebook (2 min)

Open `day1/lab03-datasets-tokenizers/Lab03_Datasets_and_Tokenizers.ipynb`, select the **.venv** kernel, and run the setup cell.

## Task 2: Part 1, explore a dataset (10 min)

Run the Part 1 cells.

**Checkpoint:**

* IMDB has `train` (25,000), `test` (25,000) and `unsupervised` (50,000) splits.
* Labels are balanced, 12,500 `neg` and 12,500 `pos`, in train and test.
* The median review is ~174 words; the 95th percentile is ~600 words.
* `outputs/imdb_small` and `outputs/imdb_small_train.csv` are created.

Complete the two **Try it** questions.

## Task 3: Part 2, how a tokenizer works (8 min)

**Checkpoint:**

* `Tokenization` becomes `token` + `##ization`
* Every encoded sequence starts with `[CLS]` and ends with `[SEP]`
* The emoji becomes `[UNK]`
* In the batch example, padded positions have `attention_mask = 0`

## Task 4: Part 3, compare tokenizers (8 min)

**Checkpoint:** the token-count table shows the Hindi and Kannada sentences costing **7-10x** the English tokens on GPT-2 and **4-7x** on `cl100k`, but only about **1.5x** on `o200k`.

Try your own language or a code snippet in the **Try it** cell.

## Task 5: Part 4, tokenize a dataset and choose `max_length` (6 min)

**Checkpoint:**

* With `max_length=128`, about **90%** of reviews are truncated. With `512`, about **13%** are.
* Length-grouped batches cut padding from **~46%** to **under 1%**.

## Task 6: Part 5, token budgeting (8 min)

You estimate the cost of labelling 25,000 reviews with an LLM under seven strategies.

**Checkpoint:** the cost falls by roughly **90%+** from strategy A (naive) to G (all optimisations).
The dollar figures use **example prices**. Update `PRICE` to your provider's current rates for a real estimate.

Discuss the trade-off table with your neighbour, then do the **Try it** exercises.

## Task 7 (stretch): Part 6, train your own tokenizer

Train a 32k-vocabulary BPE tokenizer on 20,000 reviews in about 5 seconds. Notice it learns whole-word tokens like `_cinematography`, and that it is worse on code.

---

## Optional: run as scripts

```powershell
cd day1\lab03-datasets-tokenizers
..\..\.venv\Scripts\Activate.ps1
python 01_explore_dataset.py
python 02_tokenizer_basics.py
python 03_compare_tokenizers.py
python 04_tokenize_dataset.py
python 05_token_budget.py
python 06_train_custom_tokenizer.py
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Hindi or Kannada show as boxes in the terminal | It's a font issue only; the counts are correct. Notebook output renders them properly. |
| `tiktoken` hangs or fails on first use | It downloads encodings from `openaipublic.blob.core.windows.net`. Run `setup\prefetch_assets.py` on a network that allows it. |
| `datasets` errors about scripts / `trust_remote_code` | You're using an old dataset name. Use `stanfordnlp/imdb` exactly as written. |
| Very slow first run | The IMDB download (~85 MB) happens once, then it's cached. |
