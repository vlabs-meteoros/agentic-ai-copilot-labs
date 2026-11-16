"""
Lab 2 - Step 2: Fine-tune DistilBERT for sentiment with the Trainer API.

Two transfer-learning strategies:

  --mode frozen   Feature extraction. The pre-trained body is FROZEN; only the
                  small classification head learns. Fast, needs little data.
  --mode full     Full fine-tuning. Every weight in the network is updated
                  (with a small learning rate). Slower, usually more accurate.

Examples:
  python 02_finetune.py --mode frozen
  python 02_finetune.py --mode full
  python 02_finetune.py --mode full --train-size 4000 --epochs 2
"""
import argparse
import time

from lab_config import (BASE_MODEL, LABELS, OUTPUT_DIR, SEED, TRAIN_SIZE,
                        compute_metrics, describe_device, load_splits, save_result)

# Sensible defaults for each strategy. The frozen head can use a much larger
# learning rate because it starts from random weights and is tiny.
DEFAULTS = {
    "frozen": {"lr": 1e-3, "epochs": 2},
    "full":   {"lr": 5e-5, "epochs": 1},
}


def parse_args():
    p = argparse.ArgumentParser(description="Fine-tune DistilBERT on SST-2")
    p.add_argument("--mode", choices=["frozen", "full"], required=True)
    p.add_argument("--train-size", type=int, default=TRAIN_SIZE)
    p.add_argument("--epochs", type=float, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--batch-size", type=int, default=16)
    return p.parse_args()


def main():
    import torch
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                              DataCollatorWithPadding, Trainer, TrainingArguments,
                              set_seed)

    args = parse_args()
    lr = args.lr or DEFAULTS[args.mode]["lr"]
    epochs = args.epochs or DEFAULTS[args.mode]["epochs"]
    run_name = f"{args.mode}_{args.train_size}"
    run_dir = f"{OUTPUT_DIR}/{run_name}"

    set_seed(SEED)
    device = describe_device()

    # ------------------------------------------------------------------ model
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=2,
        id2label=LABELS,
        label2id={v: k for k, v in LABELS.items()},
    )

    if args.mode == "frozen":
        # Freeze every parameter of the pre-trained body.
        for param in model.distilbert.parameters():
            param.requires_grad = False

    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[model] Mode: {args.mode.upper()}")
    print(f"[model] Trainable parameters: {trainable:,} of {total:,} "
          f"({trainable / total:.2%})")

    # ------------------------------------------------------------------- data
    train_ds, eval_ds = load_splits(tokenizer, train_size=args.train_size)
    print(f"[data]  Train: {len(train_ds)} sentences | Eval: {len(eval_ds)} sentences")

    # --------------------------------------------------------------- trainer
    # TrainingArguments = every knob of the training loop in one object.
    training_args = TrainingArguments(
        output_dir=run_dir,
        num_train_epochs=epochs,
        learning_rate=lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=64,
        weight_decay=0.01,
        warmup_steps=0.1,            # warm up over the first 10% of steps
        lr_scheduler_type="linear",
        eval_strategy="epoch",       # evaluate at the end of each epoch
        save_strategy="no",          # we save once at the end (saves disk + time)
        logging_steps=10,            # print the loss every 10 steps
        report_to="none",            # no W&B / TensorBoard needed for this lab
        fp16=torch.cuda.is_available(),  # mixed precision only on a GPU
        dataloader_num_workers=0,    # safest choice on Windows
        dataloader_pin_memory=torch.cuda.is_available(),
        seed=SEED,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),  # dynamic padding
        compute_metrics=compute_metrics,
    )

    steps = trainer.get_train_dataloader().__len__() * epochs
    print(f"[train] {epochs} epoch(s) x {len(train_ds)} sentences / batch {args.batch_size}"
          f" = ~{int(steps)} optimisation steps, lr={lr}")
    print("[train] Watch 'loss' go down in the log lines below...\n")

    start = time.time()
    trainer.train()
    train_seconds = time.time() - start

    metrics = trainer.evaluate()

    # Save the fine-tuned model + tokenizer so 03_predict.py can load it.
    final_dir = f"{run_dir}/final"
    trainer.save_model(final_dir)

    print(f"\n================ RESULT: {args.mode.upper()} ================")
    print(f"  Accuracy      : {metrics['eval_accuracy']:.2%}")
    print(f"  F1            : {metrics['eval_f1']:.4f}")
    print(f"  Training time : {train_seconds:.0f}s on {device}")
    print(f"  Saved model to: {final_dir}")
    print("=" * (36 + len(args.mode)))

    save_result(run_name, {
        "accuracy": metrics["eval_accuracy"],
        "f1": metrics["eval_f1"],
        "train_seconds": round(train_seconds, 1),
        "trainable_params": trainable,
        "train_size": len(train_ds),
        "epochs": epochs,
        "learning_rate": lr,
        "model_dir": final_dir,
    })


if __name__ == "__main__":   # required on Windows
    main()
