"""
Check that a lab machine is ready for the labs.

    python setup\\verify_env.py                    # packages, hardware, network
    python setup\\verify_env.py --azure            # + live calls to the shared Azure AI resource (Lab 1, Labs 6-7)
    python setup\\verify_env.py --neo4j            # + a live connection to your Neo4j AuraDB instance (Lab 7)

Exit code 0 = ready, 1 = something needs fixing.
"""
import argparse
import importlib
import os
import platform
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
OK, WARN, FAIL = "[ OK ]", "[WARN]", "[FAIL]"
failures = 0


def report(status, msg):
    global failures
    if status == FAIL:
        failures += 1
    print(f"{status} {msg}")


def check_python():
    v = sys.version_info
    status = OK if v >= (3, 10) else FAIL
    report(status, f"Python {platform.python_version()} at {sys.executable}")
    if status == FAIL:
        print("       Python 3.10+ is required. Re-run setup\\setup-windows.ps1")
    if not os.environ.get("VIRTUAL_ENV") and ".venv" not in sys.executable:
        report(WARN, "Not running inside the lab .venv - activate it: .\\.venv\\Scripts\\Activate.ps1")


def check_packages():
    pkgs = ["torch", "transformers", "datasets", "accelerate", "tokenizers", "tiktoken",
            "sklearn", "pandas", "azure.ai.textanalytics", "azure.ai.vision.imageanalysis",
            "dotenv", "requests", "ipykernel",
            # Day 2
            "huggingface_hub", "sentence_transformers", "faiss", "openai", "langchain", "langchain_openai",
            "langchain_community", "langchain_huggingface", "langgraph", "langchain_neo4j", "neo4j", "pinecone"]
    for name in pkgs:
        try:
            mod = importlib.import_module(name)
            report(OK, f"{name:<32} {getattr(mod, '__version__', '')}")
        except Exception as e:
            report(FAIL, f"{name:<32} not importable: {e}")


def check_hardware():
    try:
        import torch
        if torch.cuda.is_available():
            report(OK, f"GPU: {torch.cuda.get_device_name(0)} (Lab 2 will use it automatically)")
        else:
            report(OK, f"CPU only: {os.cpu_count()} logical cores (Lab 2 is sized for CPU)")
    except Exception as e:
        report(FAIL, f"torch problem: {e}")
    try:
        import shutil
        free_gb = shutil.disk_usage(ROOT).free / 1e9
        report(OK if free_gb > 6 else WARN, f"Free disk space: {free_gb:.1f} GB (need ~4.5 GB for models + datasets)")
    except Exception:
        pass


def check_network():
    import requests
    targets = {
        "Hugging Face Hub": "https://huggingface.co/api/models/distilbert/distilbert-base-uncased",
        "tiktoken files": "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken",
        "Azure Translator": "https://api.cognitive.microsofttranslator.com/languages?api-version=3.0&scope=translation",
        "Neo4j Aura console": "https://console.neo4j.io",
    }
    for name, url in targets.items():
        try:
            r = requests.get(url, timeout=15, stream=True)
            report(OK if r.status_code < 400 else WARN, f"{name:<18} reachable (HTTP {r.status_code})")
            r.close()
        except Exception as e:
            report(WARN, f"{name:<18} NOT reachable: {type(e).__name__}. Ask your trainer (prefetch / proxy).")


def check_env_file(live):
    env = ROOT / ".env"
    if not env.exists():
        report(WARN, ".env not found - copy .env.example to .env and add the Azure values (Lab 1)")
        return
    from dotenv import dotenv_values
    vals = dotenv_values(env)
    missing = [k for k in ["AZURE_AI_ENDPOINT", "AZURE_AI_KEY", "AZURE_AI_REGION"]
               if not vals.get(k) or "<" in (vals.get(k) or "")]
    if missing:
        report(WARN, f".env exists but these values are still placeholders: {', '.join(missing)}")
        return
    report(OK, ".env has Azure endpoint, key and region")
    if not live:
        return

    import requests
    endpoint = vals["AZURE_AI_ENDPOINT"].rstrip("/")
    key, region = vals["AZURE_AI_KEY"], vals["AZURE_AI_REGION"]
    try:
        r = requests.post(f"{endpoint}/language/:analyze-text", params={"api-version": "2024-11-01"},
                          headers={"Ocp-Apim-Subscription-Key": key},
                          json={"kind": "LanguageDetection",
                                "analysisInput": {"documents": [{"id": "1", "text": "Namaste, Mysuru!"}]}},
                          timeout=20)
        report(OK if r.ok else FAIL, f"Azure Language call: HTTP {r.status_code}")
        if not r.ok:
            print("      ", r.text[:300])
    except Exception as e:
        report(FAIL, f"Azure Language call failed: {e}")
    try:
        r = requests.post("https://api.cognitive.microsofttranslator.com/translate",
                          params={"api-version": "3.0", "to": "kn"},
                          headers={"Ocp-Apim-Subscription-Key": key, "Ocp-Apim-Subscription-Region": region},
                          json=[{"Text": "Welcome to the lab"}], timeout=20)
        report(OK if r.ok else FAIL, f"Azure Translator call: HTTP {r.status_code}"
               + (f" -> {r.json()[0]['translations'][0]['text']}" if r.ok else ""))
        if not r.ok:
            print("      ", r.text[:300])
    except Exception as e:
        report(FAIL, f"Azure Translator call failed: {e}")
    deployment = (vals.get("AZURE_OPENAI_DEPLOYMENT") or "gpt-4.1-mini").strip()
    try:
        r = requests.post(f"{endpoint}/openai/v1/chat/completions",
                          headers={"api-key": key},
                          json={"model": deployment, "max_tokens": 5,
                                "messages": [{"role": "user", "content": "Reply with: ok"}]},
                          timeout=30)
        report(OK if r.ok else FAIL, f"Azure OpenAI chat call ({deployment}): HTTP {r.status_code}"
               + (f" -> {r.json()['choices'][0]['message']['content']!r}" if r.ok else ""))
        if not r.ok:
            print("      ", r.text[:300])
    except Exception as e:
        report(FAIL, f"Azure OpenAI call failed: {e}")


def check_neo4j():
    from dotenv import dotenv_values
    vals = dotenv_values(ROOT / ".env") if (ROOT / ".env").exists() else {}
    uri, user, pw = vals.get("NEO4J_URI") or "", vals.get("NEO4J_USERNAME") or "neo4j", vals.get("NEO4J_PASSWORD") or ""
    if not uri or "<" in uri or not pw or "<" in pw:
        report(WARN, "NEO4J_URI / NEO4J_PASSWORD not set in .env (Lab 7, Task 1)")
        return
    try:
        from neo4j import GraphDatabase
        with GraphDatabase.driver(uri, auth=(user, pw)) as driver:
            driver.verify_connectivity()
            info = driver.get_server_info()
            report(OK, f"Neo4j connection: OK ({info.agent} at {info.address})")
    except Exception as e:
        report(FAIL, f"Neo4j connection failed: {type(e).__name__}: {str(e)[:200]}")
        print("       Is the instance Running (not paused) in console.neo4j.io? Are URI/user/password copied exactly?")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--azure", action="store_true", help="also make live calls to the Azure resource")
    p.add_argument("--neo4j", action="store_true", help="also connect to the Neo4j instance in .env")
    args = p.parse_args()

    print("=" * 64)
    print(" Agentic AI with Copilot - lab environment check")
    print("=" * 64)
    check_python()
    check_packages()
    check_hardware()
    check_network()
    check_env_file(args.azure)
    if args.neo4j:
        check_neo4j()
    print("=" * 64)
    if failures:
        print(f" {failures} problem(s) found - fix the [FAIL] lines above.")
        sys.exit(1)
    print(" Ready for the labs!  ([WARN] lines are worth a look but not blockers.)")


if __name__ == "__main__":
    main()
