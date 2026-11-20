"""
Helpers for Lab 11 - a voice coding assistant (speech to text -> GPT -> text to speech).

Reads the connection settings from the repository's .env file (the same values as Day 1 and Day 2):

    AZURE_AI_ENDPOINT        the shared Azure AI resource (it serves Speech AND Azure OpenAI)
    AZURE_AI_KEY             its key
    AZURE_AI_REGION          its region, for example southeastasia
    AZURE_OPENAI_DEPLOYMENT  the chat model deployment (default: gpt-4.1-mini)

Optional overrides if your trainer gives you a separate Speech resource:
    AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

Speech is called through its REST API with the `requests` package, so you can see exactly what goes
over the wire: speech to text is ONE POST with a WAV file, text to speech is ONE POST with SSML.
"""
import os
import sys
import time
import wave
from contextlib import contextmanager
from pathlib import Path
from xml.sax.saxutils import escape

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import requests
from dotenv import load_dotenv

for _folder in [Path.cwd(), *Path.cwd().parents][:4]:
    if (_folder / ".env").exists():
        load_dotenv(_folder / ".env", override=True)
        break

LAB_DIR = Path(__file__).resolve().parent
AUDIO_DIR = LAB_DIR / "audio"
OUTPUT_DIR = LAB_DIR / "outputs"

DEFAULT_VOICE = "en-IN-NeerjaNeural"
SAMPLE_RATE = 16000  # speech to text for short audio wants 16 kHz, 16-bit, mono PCM WAV


def _setting(*names, default=None):
    for name in names:
        value = os.getenv(name, "").strip()
        if value and not value.startswith("<"):
            return value
    return default


# ------------------------------------------------------------------ Speech connection
def _speech_hosts(kind):
    """Base URLs to try, in order: the resource's own endpoint, then the regional endpoint."""
    hosts = []
    endpoint = _setting("AZURE_AI_ENDPOINT")
    if endpoint and not _setting("AZURE_SPEECH_KEY"):
        hosts.append(endpoint.rstrip("/") + f"/{kind}")
    region = _setting("AZURE_SPEECH_REGION", "AZURE_AI_REGION")
    if region:
        hosts.append(f"https://{region}.{kind}.speech.microsoft.com")
    return hosts


def _speech_key():
    key = _setting("AZURE_SPEECH_KEY", "AZURE_AI_KEY")
    if not key:
        raise RuntimeError(
            "AZURE_AI_KEY is missing from .env. Add the values from Day 1 Lab 1 "
            "(AZURE_AI_ENDPOINT, AZURE_AI_KEY, AZURE_AI_REGION), save .env and run again."
        )
    return key


def _post(kind, path, **kwargs):
    """POST to the first Speech host that accepts the key. Returns the response."""
    hosts = _speech_hosts(kind)
    if not hosts:
        raise RuntimeError("Set AZURE_AI_ENDPOINT or AZURE_AI_REGION in .env")
    headers = kwargs.pop("headers", {})
    headers["Ocp-Apim-Subscription-Key"] = _speech_key()
    last = None
    for host in hosts:
        try:
            last = requests.post(host + path, headers=headers, timeout=60, **kwargs)
        except requests.ConnectionError as e:
            last = e
            continue
        if last.status_code not in (401, 403, 404):
            return last
    if isinstance(last, Exception):
        raise RuntimeError(f"Could not reach the Speech service ({type(last).__name__}). Check the network/proxy.")
    raise RuntimeError(f"Speech service said {last.status_code} {last.reason}: {last.text[:200]} "
                       f"(tried {', '.join(hosts)}). Check AZURE_AI_KEY and AZURE_AI_REGION in .env.")


# ------------------------------------------------------------------ Speech to text
def speech_to_text(wav_path, language="en-US"):
    """Send a short WAV file (up to 60 s, 16 kHz mono) and return the recognised text."""
    data = Path(wav_path).read_bytes()
    r = _post(
        "stt",
        "/speech/recognition/conversation/cognitiveservices/v1",
        params={"language": language, "format": "simple"},
        headers={"Content-Type": f"audio/wav; codecs=audio/pcm; samplerate={SAMPLE_RATE}",
                 "Accept": "application/json"},
        data=data,
    )
    r.raise_for_status()
    result = r.json()
    if result.get("RecognitionStatus") != "Success":
        # NoMatch = speech found but not understood, InitialSilenceTimeout = only silence
        return ""
    return result.get("DisplayText", "")


# ------------------------------------------------------------------ Text to speech
def build_ssml(text, voice=DEFAULT_VOICE, rate=None):
    """SSML is the XML that tells the voice what to say and how (voice, speed, pauses...)."""
    lang = "-".join(voice.split("-")[:2])
    body = escape(text)
    if rate:
        body = f'<prosody rate="{rate}">{body}</prosody>'
    return (f"<speak version='1.0' xml:lang='{lang}'>"
            f"<voice name='{voice}'>{body}</voice></speak>")


def text_to_speech(text, out_path, voice=DEFAULT_VOICE, rate=None):
    """Turn text into a WAV file. Returns the path."""
    r = _post(
        "tts",
        "/cognitiveservices/v1",
        headers={"Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
                 "User-Agent": "agentic-ai-copilot-labs"},
        data=build_ssml(text, voice, rate).encode("utf-8"),
    )
    if r.status_code == 400:
        raise RuntimeError(f"Text to speech rejected the request (400). Is the voice name '{voice}' right?")
    r.raise_for_status()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(r.content)
    return out_path


def list_voices(locale=None):
    hosts = _speech_hosts("tts")
    if not hosts:
        raise RuntimeError("Set AZURE_AI_ENDPOINT or AZURE_AI_REGION in .env")
    for host in hosts:
        r = requests.get(host + "/cognitiveservices/voices/list",
                         headers={"Ocp-Apim-Subscription-Key": _speech_key()}, timeout=60)
        if r.ok:
            voices = r.json()
            return [v for v in voices if not locale or v["Locale"].lower() == locale.lower()]
    raise RuntimeError(f"Could not list voices: {r.status_code} {r.text[:200]}")


# ------------------------------------------------------------------ Audio in and out
def wav_seconds(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def play(path):
    """Play a WAV file on the speakers (Windows). Returns False if it can't."""
    try:
        import winsound
        winsound.PlaySound(str(path), winsound.SND_FILENAME)
        return True
    except ImportError:
        print(f"   (playback only works on Windows; the audio is in {path})")
    except Exception as e:  # no audio device on the VM
        print(f"   (could not play audio: {e}; the audio is in {path})")
    return False


def record_from_mic(out_path, max_seconds=15):
    """Record from the default microphone until Enter is pressed (or max_seconds). Saves a 16 kHz WAV.
    Returns the path, or None if the user typed q."""
    try:
        import numpy as np
        import sounddevice as sd
    except ImportError:
        raise RuntimeError("The sounddevice package is missing. Run setup\\setup-windows.ps1 again.")
    chunks = []

    def callback(indata, frames, t, status):
        if sum(len(c) for c in chunks) < max_seconds * SAMPLE_RATE:
            chunks.append(indata.copy())

    try:
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback)
    except Exception as e:
        raise RuntimeError(f"No microphone available ({e}). Use the sample files instead (run without --mic).")
    if input("   Press Enter and speak (or type q and Enter to quit): ").strip().lower() == "q":
        return None
    with stream:
        input("   Recording... (Enter to stop) ")
    audio = np.concatenate(chunks) if chunks else np.zeros((0, 1), dtype="int16")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(audio.tobytes())
    return out_path


# ------------------------------------------------------------------ LLM
def get_llm_client():
    """Return (client, deployment_name) for the Azure OpenAI v1 API (same as Day 2 Lab 6)."""
    from openai import OpenAI

    endpoint = _setting("AZURE_OPENAI_ENDPOINT", "AZURE_AI_ENDPOINT")
    key = _setting("AZURE_OPENAI_API_KEY", "AZURE_AI_KEY")
    deployment = _setting("AZURE_OPENAI_DEPLOYMENT", default="gpt-4.1-mini")
    if not endpoint or not key:
        raise RuntimeError("AZURE_AI_ENDPOINT / AZURE_AI_KEY are missing from .env (see Day 2 Lab 6, Task 1).")
    client = OpenAI(base_url=endpoint.rstrip("/") + "/openai/v1/", api_key=key, max_retries=5)
    return client, deployment


# ------------------------------------------------------------------ Timing
@contextmanager
def timed(label, timings):
    """with timed("STT", timings): ...   records how long the block took, in milliseconds."""
    start = time.perf_counter()
    yield
    timings[label] = (time.perf_counter() - start) * 1000
