"""
Lab 11, Task 5 - A conversational voice coding assistant: speech to text -> GPT -> text to speech.

    python day4\\lab11-voice-agent\\voice_agent.py                 # 3 sample questions as ONE conversation
    python day4\\lab11-voice-agent\\voice_agent.py --plain         # the same, WITHOUT structured output
    python day4\\lab11-voice-agent\\voice_agent.py --files day4\\lab12-voice-agent\\audio\\q4_index_error.wav
    python day4\\lab11-voice-agent\\voice_agent.py --mic --play    # talk to it (needs a microphone and speakers)
    python day4\\lab11-voice-agent\\voice_agent.py --text          # type instead of speaking (skips STT)

Every reply is saved as outputs\\reply_<n>.wav. Add --play to hear it.
"""
import argparse
from pathlib import Path

from pydantic import BaseModel, Field

from voice_helpers import (AUDIO_DIR, DEFAULT_VOICE, OUTPUT_DIR, get_llm_client, play, record_from_mic,
                           speech_to_text, text_to_speech, timed, wav_seconds)

DEFAULT_FILES = ["q1_reverse_list.wav", "q2_palindrome.wav", "q3_follow_up.wav"]
MAX_HISTORY = 10          # messages kept in memory (5 questions and 5 answers)
GOODBYE = ("goodbye", "bye", "stop", "exit", "quit")

SYSTEM_PROMPT = """You are Kavi, a voice assistant that helps developers at Kaveri Systems with Python.
The user talks to you. Your 'spoken' text is read aloud by a text-to-speech voice, and your 'code' is shown on screen.
Rules for 'spoken':
- At most 3 short sentences, in plain everyday words.
- Never read code, symbols or Markdown aloud. Refer to the code instead ("the function on your screen").
- If the question is unclear, ask one short question back and leave 'code' empty.
Rules for 'code': runnable Python only, no Markdown fences, or null if no code helps."""

PLAIN_SYSTEM_PROMPT = "You are a helpful Python coding assistant."


class VoiceReply(BaseModel):
    spoken: str = Field(description="What to say aloud: 1 to 3 short sentences, no code, no symbols, no Markdown")
    code: str | None = Field(description="Python code to show on screen, or null if no code is needed")
    # TODO (Lab 12, Task 6): add a field, for example a suggested next question


def get_inputs(args):
    """Yield (label, wav_path_or_None, typed_text_or_None) for each turn."""
    if args.text:
        while True:
            typed = input("\nYou (type, or q to quit): ").strip()
            if typed.lower() in ("q", ""):
                return
            yield "typed", None, typed
    elif args.mic:
        n = 0
        while True:
            n += 1
            wav = record_from_mic(OUTPUT_DIR / f"mic_{n}.wav")
            if wav is None:
                return
            yield wav.name, wav, None
    else:
        files = args.files or [AUDIO_DIR / f for f in DEFAULT_FILES]
        for f in files:
            yield Path(f).name, Path(f), None


def ask_llm(client, deployment, history, plain):
    if plain:
        r = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "system", "content": PLAIN_SYSTEM_PROMPT}, *history],
        )
        text = r.choices[0].message.content
        return VoiceReply(spoken=text, code=None), text, r.usage
    r = client.chat.completions.parse(
        model=deployment,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
        response_format=VoiceReply,
    )
    reply = r.choices[0].message.parsed
    # Keep the whole structured reply in the history, so a follow-up question can refer to the code
    return reply, reply.model_dump_json(), r.usage


def main():
    p = argparse.ArgumentParser(description="Voice coding assistant: STT -> GPT -> TTS")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--files", nargs="+", help="WAV files to use as your questions, in order")
    src.add_argument("--mic", action="store_true", help="speak into the microphone")
    src.add_argument("--text", action="store_true", help="type your questions instead (skips speech to text)")
    p.add_argument("--plain", action="store_true", help="no structured output: speak the model's whole answer")
    p.add_argument("--play", action="store_true", help="play each reply on the speakers")
    p.add_argument("--voice", default=DEFAULT_VOICE)
    p.add_argument("--language", default=None, help="speech to text language (default en-US for files, en-IN for --mic)")
    args = p.parse_args()
    language = args.language or ("en-IN" if args.mic else "en-US")

    client, deployment = get_llm_client()
    history = []
    mode = "PLAIN (no structured output)" if args.plain else "STRUCTURED (VoiceReply)"
    print(f"Voice assistant ready. Model: {deployment}. Mode: {mode}. Voice: {args.voice}")

    for turn, (label, wav, typed) in enumerate(get_inputs(args), 1):
        t = {}
        # 1. Speech to text
        if wav is not None:
            with timed("STT", t):
                user_text = speech_to_text(wav, language)
        else:
            user_text = typed
        print(f"\n[{turn}] You said ({label}): {user_text or '(nothing recognised)'}")
        if not user_text:
            continue
        if user_text.lower().strip(" .!?") in GOODBYE:
            text_to_speech("Goodbye! Happy coding.", OUTPUT_DIR / "reply_bye.wav", voice=args.voice)
            print("Assistant: Goodbye! Happy coding.")
            if args.play:
                play(OUTPUT_DIR / "reply_bye.wav")
            break

        # 2. The LLM, with the conversation so far
        history.append({"role": "user", "content": user_text})
        with timed("LLM", t):
            reply, remembered, usage = ask_llm(client, deployment, history, args.plain)
        history.append({"role": "assistant", "content": remembered})
        del history[:-MAX_HISTORY]

        if reply.code:
            print("    On screen:")
            for line in reply.code.splitlines():
                print("    | " + line)
        extra = {k: v for k, v in reply.model_dump().items() if k not in ("spoken", "code")}
        if extra:
            print(f"    Extra fields: {extra}")

        # 3. Text to speech
        out = OUTPUT_DIR / f"reply_{turn}.wav"
        with timed("TTS", t):
            text_to_speech(reply.spoken, out, voice=args.voice)
        print(f"    Assistant says: {reply.spoken}")
        stages = " | ".join(f"{k} {v:.0f} ms" for k, v in t.items())
        print(f"    [{stages} | total {sum(t.values()):.0f} ms | {len(reply.spoken)} characters spoken, "
              f"{wav_seconds(out):.1f} s of audio | tokens {usage.prompt_tokens} in, {usage.completion_tokens} out]")
        if args.play:
            play(out)

    print(f"\nReplies saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
