# Lab 2: Transfer Learning with the Hugging Face Trainer

| | |
|---|---|
| **Duration** | 45 minutes (about 6 minutes of it is training time on a CPU) |
| **Topic** | Neural Networks and Deep Learning: transfer learning, fine-tuning, learning rate, training loop |
| **You need** | Internet access to Hugging Face, or assets prefetched during setup. No GPU required. |
| **Notebook** | `Lab02_Transfer_Learning_with_Trainer.ipynb` |

## Objectives

* Explain transfer learning as a **pre-trained body + a new task head**
* Use the Hugging Face **Trainer** interface: `TrainingArguments`, `Trainer`, `train()`, `evaluate()`, `save_model()`
* Compare **feature extraction** (frozen body) with **full fine-tuning**
* Use a fine-tuned model through a `pipeline` and recognise its limits

## The experiment

We teach **DistilBERT** (pre-trained on Wikipedia and books, never shown a sentiment label) to classify movie-review sentences from **SST-2** as positive or negative, using only 2,000 labelled examples.

---

## Task 1: Open the notebook (2 min)

1. Open `day1/lab02-transfer-learning/Lab02_Transfer_Learning_with_Trainer.ipynb`.
2. **Select Kernel** > **.venv (Python 3.12)**.
3. Run the first cell.

**Checkpoint:** it prints the transformers and torch versions and `Training will run on: CPU (n cores)`, or the GPU name.

## Task 2: Load the data and inspect the model (8 min)

Run the cells for **Configuration**, **Step 1** and **Step 2**.

**Checkpoint:**

* SST-2 has 67,349 training sentences; we use 2,000.
* The model has a ~66.4M-parameter **pre-trained body** and a ~0.6M-parameter **new head**.

## Task 3: Baseline (3 min)

Run **3a**. The untrained model's random head is guessing.

**Checkpoint:** accuracy is around **45-55%**.

## Task 4: Feature extraction, frozen body (8 min, ~1.5-3 min of training)

Run **3b**. Only 0.88% of the parameters are trainable.
While it trains, read the log: `loss` should fall from ~0.69 to ~0.4.

**Checkpoint:** accuracy is about **80-83%**.

## Task 5: Full fine-tuning (8 min, ~2-4 min of training)

Run **3c**, then the comparison table.

**Checkpoint:** accuracy is about **85-87%**, and the model is saved to `outputs/full/final`.

| Run | Accuracy | Trainable params | Train time (2-core CPU) |
|---|---|---|---|
| Untrained | ~45-50% | 0 | 0 |
| Frozen body | ~82% | 0.6 M | ~90 s |
| Full fine-tune | ~86% | 67 M | ~105 s |

## Task 6: Use and probe the model (10 min)

Run **Step 4**. Note the sentences the model gets **wrong**:

* *"Not bad at all."* (negation)
* *"I expected to hate it, but it won me over."* (contrast)
* *"This app crashes every time I open it."* (not a movie review, yet the model is confident)

Pick one **Try it** exercise from the notebook.

---

## Discussion questions

1. Why does freezing the body need a much **larger** learning rate than full fine-tuning?
2. When would you choose feature extraction even though it's less accurate?
3. The model confidently labels text from a domain it never saw. What does that mean for production use?

## Optional: run as scripts

```powershell
cd day1\lab02-transfer-learning
..\..\.venv\Scripts\Activate.ps1
python 01_baseline.py
python 02_finetune.py --mode frozen
python 02_finetune.py --mode full
python 03_compare_and_predict.py --interactive
```

`02_finetune.py --help` lists options such as `--train-size` and `--epochs`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Training is very slow (> 10 min) | Lower `TRAIN_SIZE` to 1000 in the configuration cell. Close other programs on the VM. |
| `OSError: Can't load tokenizer` / connection errors | No access to huggingface.co. Ask the trainer, or run `python setup\prefetch_assets.py` when the network is available. |
| `HTTP 429` from Hugging Face | Too many anonymous downloads from one IP. Add a free `HF_TOKEN=` line to `.env` and restart the kernel. |
| Kernel dies during training | The VM is low on memory. Restart the kernel, set `TRAIN_SIZE = 1000`, and change `per_device_train_batch_size` to 8 in `make_trainer`. |
| Warning *"Some weights were newly initialized"* | Expected: that is the new classification head. |
