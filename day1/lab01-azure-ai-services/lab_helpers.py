"""
Helpers for Lab 1 - Azure AI services.

Reads the shared resource details from a .env file and provides a small
REST helper that retries politely when the service says "slow down" (HTTP 429).
"""
import json
import os
import sys
import time
import uuid
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TRANSLATOR_GLOBAL_ENDPOINT = "https://api.cognitive.microsofttranslator.com"


def _find_env_file():
    """Look for .env in the current folder and up to 4 parent folders."""
    here = Path.cwd()
    for folder in [here, *here.parents][:5]:
        candidate = folder / ".env"
        if candidate.exists():
            return candidate
    return None


def load_config(verbose=True):
    """Return (endpoint, key, region) for the shared Azure AI resource."""
    from dotenv import load_dotenv

    env_file = _find_env_file()
    if env_file:
        load_dotenv(env_file, override=True)

    endpoint = os.getenv("AZURE_AI_ENDPOINT", "").strip().rstrip("/")
    key = os.getenv("AZURE_AI_KEY", "").strip()
    region = os.getenv("AZURE_AI_REGION", "").strip()

    problems = []
    if not endpoint or "<" in endpoint:
        problems.append("AZURE_AI_ENDPOINT is missing")
    if not key or "<" in key:
        problems.append("AZURE_AI_KEY is missing")
    if not region or "<" in region:
        problems.append("AZURE_AI_REGION is missing")
    if problems:
        where = env_file or "the repository root (copy .env.example to .env)"
        raise RuntimeError(
            "Azure settings not found: " + "; ".join(problems)
            + f".\nEdit the .env file in {where} with the values from your trainer.")

    if verbose:
        print("Using .env file :", env_file)
        print("Endpoint        :", endpoint)
        print("Region          :", region)
        print("Key             :", key[:4] + "*" * 8 + key[-4:], "(never print or commit the full key!)")
    return endpoint, key, region


def translator_endpoint():
    return os.getenv("AZURE_TRANSLATOR_ENDPOINT", TRANSLATOR_GLOBAL_ENDPOINT).rstrip("/")


def post_json(url, key, body, region=None, params=None, max_retries=5):
    """POST JSON to an Azure AI REST API, retrying on HTTP 429 (rate limit)."""
    import requests

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }
    if region:
        headers["Ocp-Apim-Subscription-Region"] = region

    for attempt in range(max_retries):
        resp = requests.post(url, headers=headers, params=params, json=body, timeout=30)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 2 ** attempt))
            print(f"  (rate limited - retrying in {wait}s)")
            time.sleep(wait)
            continue
        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        return resp.json()
    raise RuntimeError("Gave up after repeated HTTP 429 responses. Wait a minute and try again.")


def pretty(obj, limit=2500):
    """Pretty-print JSON, trimmed so huge responses don't flood the screen."""
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    print(text if len(text) <= limit else text[:limit] + "\n  ... (truncated)")


def chunks(items, size):
    """Synchronous Language APIs accept a limited number of documents per call."""
    for i in range(0, len(items), size):
        yield items[i:i + size]
