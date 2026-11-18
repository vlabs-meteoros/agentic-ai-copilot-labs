"""
Helpers for Lab 6 - Prompt Variations and Grounding with Azure OpenAI.

Reads the connection settings from the repository's .env file:

    AZURE_AI_ENDPOINT        the shared Azure AI resource from Lab 1 (also serves Azure OpenAI)
    AZURE_AI_KEY             its key
    AZURE_OPENAI_DEPLOYMENT  the model deployment name (default: gpt-4.1-mini)

Optional overrides, if your trainer gives you a separate Azure OpenAI resource:
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY
"""
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv

for _folder in [Path.cwd(), *Path.cwd().parents][:4]:
    if (_folder / ".env").exists():
        load_dotenv(_folder / ".env", override=True)
        break

# Example prices in USD per 1 million tokens (gpt-4.1-mini, Global Standard).
# Check the Azure OpenAI pricing page for current rates before using these for a real estimate.
PRICE_PER_MILLION = {"input": 0.40, "output": 1.60}


def _setting(*names, default=None):
    for name in names:
        value = os.getenv(name, "").strip()
        if value and not value.startswith("<"):
            return value
    return default


def get_client():
    """Return (client, deployment_name) for the Azure OpenAI v1 API."""
    from openai import OpenAI

    endpoint = _setting("AZURE_OPENAI_ENDPOINT", "AZURE_AI_ENDPOINT")
    key = _setting("AZURE_OPENAI_API_KEY", "AZURE_AI_KEY")
    deployment = _setting("AZURE_OPENAI_DEPLOYMENT", default="gpt-4.1-mini")
    if not endpoint or not key:
        raise RuntimeError(
            "AZURE_AI_ENDPOINT / AZURE_AI_KEY are missing from .env. "
            "Add the values from Lab 1 (see the Lab 6 README, Task 1), save .env, and restart the kernel."
        )
    # The Azure OpenAI v1 API is OpenAI-compatible: the standard OpenAI client
    # works by pointing base_url at <endpoint>/openai/v1/
    client = OpenAI(base_url=endpoint.rstrip("/") + "/openai/v1/", api_key=key, max_retries=5)
    return client, deployment


def cost_usd(usage):
    """Estimated cost of one call from its token usage, at the example prices."""
    return (usage.prompt_tokens * PRICE_PER_MILLION["input"]
            + usage.completion_tokens * PRICE_PER_MILLION["output"]) / 1_000_000


def show(response, label=None):
    """Print a chat completion's text plus its token usage and estimated cost."""
    if label:
        print(f"--- {label}")
    print(response.choices[0].message.content)
    u = response.usage
    print(f"[tokens: {u.prompt_tokens} in + {u.completion_tokens} out | "
          f"~${cost_usd(u):.6f} | finish_reason: {response.choices[0].finish_reason}]")


def filter_summary(results):
    """Compact one-line view of Azure content-filter annotations."""
    if not results:
        return "(no annotations)"
    parts = []
    for category, value in results.items():
        if not isinstance(value, dict):
            continue
        if "severity" in value:
            parts.append(f"{category}={value['severity']}")
        elif "detected" in value:
            parts.append(f"{category}={'DETECTED' if value['detected'] else 'no'}")
    return ", ".join(parts)
