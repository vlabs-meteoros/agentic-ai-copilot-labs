"""
Lab 11, Task 4 - Speech to text and text to speech with Azure AI Speech.

    python day4\\lab11-voice-agent\\speech_demo.py stt day4\\lab11-voice-agent\\audio\\q1_reverse_list.wav
    python day4\\lab11-voice-agent\\speech_demo.py stt --all                 # every sample file
    python day4\\lab11-voice-agent\\speech_demo.py tts "Hello from Kaveri Systems" [--voice ...] [--rate slow] [--play]
    python day4\\lab11-voice-agent\\speech_demo.py voices --locale en-IN
    python day4\\lab11-voice-agent\\speech_demo.py mic [--play]             # record yourself, then transcribe
"""
import argparse
import time

from voice_helpers import (AUDIO_DIR, DEFAULT_VOICE, OUTPUT_DIR, list_voices, play, record_from_mic,
                           speech_to_text, text_to_speech, wav_seconds)


def cmd_stt(args):
    files = sorted(AUDIO_DIR.glob("*.wav")) if args.all else [args.file]
    for f in files:
        start = time.perf_counter()
        text = speech_to_text(f, args.language)
        ms = (time.perf_counter() - start) * 1000
        print(f"{f.name if hasattr(f, 'name') else f}  ({wav_seconds(f):.1f} s of audio, {ms:.0f} ms)")
        print(f"   -> {text or '(nothing recognised)'}")


def cmd_tts(args):
    out = OUTPUT_DIR / args.out
    start = time.perf_counter()
    text_to_speech(args.text, out, voice=args.voice, rate=args.rate)
    ms = (time.perf_counter() - start) * 1000
    print(f"Saved {out}  ({wav_seconds(out):.1f} s of audio, made in {ms:.0f} ms, voice {args.voice})")
    if args.play:
        play(out)


def cmd_voices(args):
    voices = list_voices(args.locale)
    for v in voices:
        print(f"{v['ShortName']:<32} {v['Gender']:<7} {v.get('LocalName', '')}")
    print(f"\n{len(voices)} voice(s)")


def cmd_mic(args):
    wav = record_from_mic(OUTPUT_DIR / "mic_test.wav")
    if wav is None:
        return
    print(f"Recorded {wav_seconds(wav):.1f} s to {wav}")
    if args.play:
        play(wav)
    print("You said:", speech_to_text(wav, args.language) or "(nothing recognised)")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    x = sub.add_parser("stt", help="speech to text from a WAV file")
    x.add_argument("file", nargs="?")
    x.add_argument("--all", action="store_true", help="transcribe every file in audio\\")
    x.add_argument("--language", default="en-US")
    x.set_defaults(fn=cmd_stt)

    x = sub.add_parser("tts", help="text to speech into outputs\\")
    x.add_argument("text")
    x.add_argument("--voice", default=DEFAULT_VOICE)
    x.add_argument("--rate", help="for example slow, fast, +20%%")
    x.add_argument("--out", default="tts_demo.wav")
    x.add_argument("--play", action="store_true")
    x.set_defaults(fn=cmd_tts)

    x = sub.add_parser("voices", help="list the available voices")
    x.add_argument("--locale", default="en-IN")
    x.set_defaults(fn=cmd_voices)

    x = sub.add_parser("mic", help="record from the microphone, then transcribe")
    x.add_argument("--language", default="en-IN")
    x.add_argument("--play", action="store_true")
    x.set_defaults(fn=cmd_mic)

    args = p.parse_args()
    if args.cmd == "stt" and not args.all and not args.file:
        p.error("give a WAV file, or --all")
    args.fn(args)


if __name__ == "__main__":
    main()
