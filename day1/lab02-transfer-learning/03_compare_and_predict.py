"""
Lab 2 - Step 3: Compare your runs, then use your fine-tuned model.

  python 03_compare_and_predict.py                 # compare + demo sentences
  python 03_compare_and_predict.py --interactive   # type your own sentences
  python 03_compare_and_predict.py --model outputs/frozen_2000/final
"""
import argparse
import json
import os

from lab_config import RESULTS_FILE

DEMO_SENTENCES = [
    "An absolute delight from start to finish.",
    "The plot was predictable and the acting was wooden.",
    "I expected to hate it, but it won me over.",
    "Not bad at all.",
    "The visuals are stunning, yet the story is painfully dull.",
    "This app crashes every time I open it.",          # not a movie review!
]


def print_comparison():
    if not os.path.exists(RESULTS_FILE):
        print("No results yet. Run 01_baseline.py and 02_finetune.py first.")
        return {}
    with open(RESULTS_FILE, encoding="utf-8") as f:
        results = json.load(f)

    print("\n=================== RUN COMPARISON ===================")
    print(f"{'Run':<22}{'Accuracy':>10}{'F1':>8}{'Train s':>9}{'Trainable':>14}")
    print("-" * 63)
    for name, r in results.items():
        print(f"{name:<22}{r['accuracy']:>10.2%}{r['f1']:>8.3f}"
              f"{r['train_seconds']:>9}{r['trainable_params']:>14,}")
    print("=" * 54)
    return results


def pick_model(results, requested):
    if requested:
        return requested
    # Prefer the most accurate run that saved a model.
    candidates = [r for r in results.values() if r.get("model_dir")]
    if not candidates:
        return None
    return max(candidates, key=lambda r: r["accuracy"])["model_dir"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Path to a saved model folder")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    results = print_comparison()
    model_dir = pick_model(results, args.model)
    if not model_dir or not os.path.isdir(model_dir):
        print("\nNo fine-tuned model found. Run: python 02_finetune.py --mode full")
        return

    from transformers import pipeline

    print(f"\nLoading fine-tuned model from: {model_dir}")
    classifier = pipeline("text-classification", model=model_dir, device=-1)

    print("\n--- Predictions on new sentences ---")
    for text, pred in zip(DEMO_SENTENCES, classifier(DEMO_SENTENCES)):
        print(f"  {pred['label']:<9} {pred['score']:.3f}  |  {text}")

    if args.interactive:
        print("\nType a sentence and press Enter (empty line to quit).")
        while True:
            text = input("> ").strip()
            if not text:
                break
            pred = classifier(text)[0]
            print(f"  {pred['label']} ({pred['score']:.3f})")


if __name__ == "__main__":
    main()
