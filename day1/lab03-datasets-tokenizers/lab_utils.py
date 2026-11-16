"""Small helpers shared by the Lab 3 scripts."""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")   # Hindi/Kannada/emoji on Windows
except Exception:
    pass

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Optional settings (e.g. HF_TOKEN) from the repository's .env file
try:
    from pathlib import Path
    from dotenv import load_dotenv
    for _folder in [Path.cwd(), *Path.cwd().parents][:4]:
        if (_folder / ".env").exists():
            load_dotenv(_folder / ".env")
            break
except ImportError:
    pass

DATASET = "stanfordnlp/imdb"     # 50k full-length movie reviews (pos/neg)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def banner(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def show_tokens(tokens, limit=40):
    """Print tokens with visible boundaries: |tok|tok|tok|"""
    shown = tokens[:limit]
    more = f" ... (+{len(tokens) - limit} more)" if len(tokens) > limit else ""
    return "|" + "|".join(shown) + "|" + more
