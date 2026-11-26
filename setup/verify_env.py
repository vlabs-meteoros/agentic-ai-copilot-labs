"""
Check that a lab machine is ready for the labs.

    python setup\\verify_env.py                    # packages, hardware, network
    python setup\\verify_env.py --azure            # + live calls to the shared Azure AI resource (Lab 1, Lab 6, Labs 11 and 13)
    python setup\\verify_env.py --mongo            # + connect to the shared MongoDB Atlas cluster (Day 8 Lab 23)

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
            "langchain_community", "langchain_huggingface", "langgraph", "langchain_neo4j", "neo4j", "pinecone",
            # Day 3
            "mcp",
            # Day 4
            "fastapi", "uvicorn", "pydantic",
            # Day 5
            "pytest", "pytest_cov",
            # Day 6
            "pytest_bdd", "bandit",
            # Day 8
            "redis", "fakeredis", "httpx", "pymongo", "langgraph.checkpoint.mongodb", "mem0"]
    # Day 7: Spec Kit's CLI (specify-cli) is checked as a tool in check_tools(); it needs Python 3.11+
    for name in pkgs:
        try:
            mod = importlib.import_module(name)
            report(OK, f"{name:<32} {getattr(mod, '__version__', '')}")
        except Exception as e:
            report(FAIL, f"{name:<32} not importable: {e}")
    try:  # optional: only Lab 12 --mic needs it, and it needs a working audio system
        import sounddevice
        report(OK, f"{'sounddevice':<32} {sounddevice.__version__}")
    except Exception as e:
        report(WARN, f"{'sounddevice':<32} not usable ({type(e).__name__}): Lab 12 works without --mic")


def check_tools():
    """Command-line tools the labs call: ruff and bandit (Day 6) and specify (Day 7) from the .venv, git, and Node.js (Days 6-7)."""
    import re
    import shutil
    import subprocess
    # Look in the .venv's Scripts (or bin) folder too, so this works when setup runs it without activating the .venv,
    # and in .speckit-venv, where setup puts Spec Kit when the .venv is Python 3.10
    speckit_bin = ROOT / ".speckit-venv" / ("Scripts" if os.name == "nt" else "bin")
    search_path = os.pathsep.join([str(Path(sys.executable).parent), str(speckit_bin), os.environ.get("PATH", "")])
    tools = [("ruff", "Day 6 Lab 17"), ("bandit", "Day 6 Lab 18"), ("specify", "Day 7 Lab 19 (Spec Kit)"),
             ("git", "Days 4-7"), ("node", "Day 6 Lab 16 Task 6 and Day 7 Lab 19")]
    for name, needed_for in tools:
        exe = shutil.which(name, path=search_path)
        if not exe:
            if name == "specify" and sys.version_info < (3, 11):
                report(WARN, f"{name:<32} not installed: it needs Python 3.11+ and this .venv is {platform.python_version()}. "
                             "Re-run setup\\setup-windows.ps1 (it puts Spec Kit in .speckit-venv), or ask your trainer: Day 7 Lab 19")
                continue
            status = WARN if name == "node" else FAIL
            hint = ": re-run setup\\setup-windows.ps1, then open a NEW terminal" if name in ("node", "specify") else ""
            report(status, f"{name:<32} not found on PATH (needed for {needed_for}){hint}")
            continue
        try:
            out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60).stdout.strip().splitlines()
            version = out[0] if out else ""
            if name == "node":
                major = re.match(r"v(\d+)", version)
                if major and int(major.group(1)) < 18:
                    report(FAIL, f"{name:<32} {version} is too old: the labs need Node.js 18 or later. Re-run setup\\setup-windows.ps1")
                    continue
            report(OK, f"{name:<32} {version}")
        except Exception as e:
            report(WARN, f"{name:<32} found but '--version' failed: {e}")


def check_garnet():
    """Day 8 Lab 22: Garnet installed by setup (Windows), and whether it's running now."""
    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", ""))
        exes = sorted((local / "Programs" / "garnet").glob("*/net10.0/GarnetServer.exe"))
        runtimes = list((local / "Programs" / "dotnet10" / "shared" / "Microsoft.NETCore.App").glob("10.*")) + \
            list((Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "dotnet" / "shared" / "Microsoft.NETCore.App").glob("10.*"))
        if not exes:
            report(WARN, f"{'Garnet':<32} not installed (Day 8 Lab 22): re-run setup\\setup-windows.ps1")
            return
        report(OK if runtimes else WARN, f"{'Garnet':<32} {exes[-1].parents[1].name}" + ("" if runtimes else ", but no .NET 10 runtime: re-run setup"))
    try:
        import redis
        from dotenv import dotenv_values

        url = (dotenv_values(ROOT / ".env") if (ROOT / ".env").exists() else {}).get("REDIS_URL") or "redis://localhost:6379/0"
        info = redis.Redis.from_url(url, socket_connect_timeout=2).info("server")
        report(OK, f"{'Garnet/Redis server':<32} running at {url} (Garnet {info.get('garnet_version', '?')})")
    except Exception:
        report(OK, f"{'Garnet/Redis server':<32} not running now (start it in Lab 22: day8\\start-garnet.ps1)")


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
    # Day 5, Lab 13: the same deployment must accept an image (vision)
    receipt = ROOT / "day5" / "kavericlaims" / "receipts" / "CCW-2026-11873.png"
    if receipt.exists():
        import base64
        image_url = "data:image/png;base64," + base64.b64encode(receipt.read_bytes()).decode("ascii")
        try:
            r = requests.post(f"{endpoint}/openai/v1/chat/completions",
                              headers={"api-key": key},
                              json={"model": deployment, "max_tokens": 10,
                                    "messages": [{"role": "user", "content": [
                                        {"type": "text", "text": "What is the first word printed on this receipt? One word."},
                                        {"type": "image_url", "image_url": {"url": image_url, "detail": "low"}}]}]},
                              timeout=60)
            report(OK if r.ok else FAIL, f"Azure OpenAI image input ({deployment}): HTTP {r.status_code}"
                   + (f" -> {r.json()['choices'][0]['message']['content']!r}" if r.ok else " (Lab 13 needs it)"))
            if not r.ok:
                print("      ", r.text[:300])
        except Exception as e:
            report(FAIL, f"Azure OpenAI image call failed: {e}")
    # Day 4, Lab 12: Azure AI Speech (text to speech) on the same resource, then the regional endpoint
    ssml = ("<speak version='1.0' xml:lang='en-IN'><voice name='en-IN-NeerjaNeural'>Ready.</voice></speak>")
    for url in (f"{endpoint}/tts/cognitiveservices/v1", f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"):
        try:
            r = requests.post(url, data=ssml.encode(), timeout=30,
                              headers={"Ocp-Apim-Subscription-Key": key, "Content-Type": "application/ssml+xml",
                                       "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
                                       "User-Agent": "agentic-ai-copilot-labs"})
            if r.ok:
                report(OK, f"Azure Speech text to speech: HTTP {r.status_code} ({len(r.content)} bytes of audio)")
                break
        except Exception as e:
            r = e
    else:
        detail = f"HTTP {r.status_code}" if hasattr(r, "status_code") else type(r).__name__
        report(FAIL, f"Azure Speech text to speech failed: {detail} (Lab 12 needs it)")


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


def check_mongo():
    """Day 8 Lab 23: the shared MongoDB Atlas cluster in MONGODB_URI, and the database this participant will use."""
    from dotenv import dotenv_values
    vals = dotenv_values(ROOT / ".env") if (ROOT / ".env").exists() else {}
    uri = vals.get("MONGODB_URI") or ""
    if not uri or "<" in uri:
        report(WARN, "MONGODB_URI not set in .env (Day 8 Lab 23, Task 1: your trainer gives you the value)")
        return
    import re
    import socket
    who = vals.get("PARTICIPANT_ID") or ""
    who = re.sub(r"[^a-z0-9]+", "_", (who if who and "<" not in who else os.environ.get("COMPUTERNAME") or socket.gethostname()).lower()).strip("_")[:30]
    try:
        from pymongo import MongoClient
        client = MongoClient(uri, appname="verify_env", serverSelectionTimeoutMS=10000)
        version = client.server_info()["version"]
        report(OK, f"MongoDB connection: OK (MongoDB {version}); your checkpoints go to database kavericode_{who}")
    except Exception as e:
        report(FAIL, f"MongoDB connection failed: {type(e).__name__}: {str(e)[:200]}")
        print("       Is MONGODB_URI copied exactly? Does the cluster's Network Access allow this VM? (ask your trainer)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--azure", action="store_true", help="also make live calls to the Azure resource")
    p.add_argument("--neo4j", action="store_true", help="also connect to the Neo4j instance in .env")
    p.add_argument("--mongo", action="store_true", help="also connect to the MongoDB cluster in .env (Day 8)")
    args = p.parse_args()

    print("=" * 64)
    print(" Agentic AI with Copilot - lab environment check")
    print("=" * 64)
    check_python()
    check_packages()
    check_tools()
    check_garnet()
    check_hardware()
    check_network()
    check_env_file(args.azure)
    if args.neo4j:
        check_neo4j()
    if args.mongo:
        check_mongo()
    print("=" * 64)
    if failures:
        print(f" {failures} problem(s) found - fix the [FAIL] lines above.")
        sys.exit(1)
    print(" Ready for the labs!  ([WARN] lines are worth a look but not blockers.)")


if __name__ == "__main__":
    main()