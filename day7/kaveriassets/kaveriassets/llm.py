"""The shared LLM connection: the Azure OpenAI deployment on the Kaveri Systems (lab) Azure resource.

Reads AZURE_AI_ENDPOINT, AZURE_AI_KEY and AZURE_OPENAI_DEPLOYMENT from a .env file: the one in the current folder
or a parent folder, or the file named by the LABS_ENV environment variable (the start script sets it to the labs
repository's .env for terminals in the KaveriAssets window).
"""
import os
from pathlib import Path


def load_settings() -> None:
    """Load the first .env found into the environment (python-dotenv)."""
    from dotenv import load_dotenv

    candidates = [folder / ".env" for folder in [Path.cwd(), *Path.cwd().parents][:4]]
    if os.getenv("LABS_ENV"):
        candidates.append(Path(os.environ["LABS_ENV"]))
    candidates.append(Path.home() / "Desktop" / "agentic-ai-copilot-labs" / ".env")
    for path in candidates:
        if path.is_file():
            load_dotenv(path, override=True)
            return


def get_llm_client():
    """Return (client, deployment) for the Azure OpenAI v1 API. Raises SystemExit with a clear message if .env isn't set up."""
    from openai import OpenAI

    load_settings()

    def setting(*names, default=None):
        for name in names:
            value = os.getenv(name, "").strip()
            if value and not value.startswith("<"):
                return value
        return default

    endpoint = setting("AZURE_OPENAI_ENDPOINT", "AZURE_AI_ENDPOINT")
    key = setting("AZURE_OPENAI_API_KEY", "AZURE_AI_KEY")
    deployment = setting("AZURE_OPENAI_DEPLOYMENT", default="gpt-4.1-mini")
    if not endpoint or not key:
        raise SystemExit("AZURE_AI_ENDPOINT / AZURE_AI_KEY are missing: check the .env file in the labs repository (same values as Day 5).")
    client = OpenAI(base_url=endpoint.rstrip("/") + "/openai/v1/", api_key=key, max_retries=5)
    return client, deployment
