"""
Lab 2 - Step 1: Inspect the pre-trained model and measure a baseline.

What this shows:
  * A pre-trained "body" (DistilBERT) + a brand-new, randomly initialised
    classification "head" bolted on top.
  * Before any training, the head is guessing, so accuracy is around 50%.

Run:  python 01_baseline.py
"""
import time

from lab_config import (BASE_MODEL, LABELS, OUTPUT_DIR, compute_metrics,
                        describe_device, load_splits, save_result)


def count_params(module):
    total = sum(p.numel() for p in module.parameters())
    trainable = sum(p.numel() for p in module.parameters() if p.requires_grad)
    return total, trainable


def main():
    import torch
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                              DataCollatorWithPadding, Trainer, TrainingArguments)
    from transformers.utils import logging as hf_logging

    describe_device()

    print(f"\n[1/4] Loading tokenizer and model: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    # num_labels=2 tells transformers to attach a NEW 2-class head.
    # You will see a message saying some weights were "newly initialized":
    # that is the head. Everything else is reused from pre-training.
    hf_logging.set_verbosity_warning()
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=2,
        id2label=LABELS,
        label2id={v: k for k, v in LABELS.items()},
    )
    hf_logging.set_verbosity_error()

    print("\n[2/4] Model anatomy (body vs head)")
    body_total, _ = count_params(model.distilbert)
    head_total = sum(p.numel() for n, p in model.named_parameters() if not n.startswith("distilbert."))
    print(f"  Pre-trained body (model.distilbert): {body_total:>12,} parameters")
    print(f"  New head (pre_classifier + classifier): {head_total:>9,} parameters")
    print(f"  Transformer layers in the body: {len(model.distilbert.transformer.layer)}")
    print("  Head modules:")
    for name, module in model.named_children():
        if name != "distilbert":
            print(f"    - {name}: {module}")

    print("\n[3/4] Loading and tokenizing SST-2")
    _, eval_ds = load_splits(tokenizer)
    print(f"  Evaluation sentences: {len(eval_ds)}")

    print("\n[4/4] Evaluating the UNTRAINED model (random head)")
    args = TrainingArguments(
        output_dir=f"{OUTPUT_DIR}/baseline",
        per_device_eval_batch_size=64,
        report_to="none",
        dataloader_num_workers=0,   # safest choice on Windows
        dataloader_pin_memory=torch.cuda.is_available(),
    )
    trainer = Trainer(
        model=model,
        args=args,
        eval_dataset=eval_ds,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
        compute_metrics=compute_metrics,
    )
    start = time.time()
    metrics = trainer.evaluate()
    elapsed = time.time() - start

    print("\n================ BASELINE RESULT ================")
    print(f"  Accuracy : {metrics['eval_accuracy']:.2%}")
    print(f"  F1       : {metrics['eval_f1']:.4f}")
    print(f"  Eval time: {elapsed:.1f}s")
    print("  A random 2-class guesser scores about 50%.")
    print("=================================================")

    save_result("baseline_untrained", {
        "accuracy": metrics["eval_accuracy"],
        "f1": metrics["eval_f1"],
        "train_seconds": 0,
        "trainable_params": 0,
    })


if __name__ == "__main__":   # required on Windows
    main()
