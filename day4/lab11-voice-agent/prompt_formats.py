"""
Lab 11, Task 2 - Prompt formats: the same conversation in Alpaca, ChatML and Llama-2 format.

A chat API takes a LIST of messages (system, user, assistant...). The model itself only sees ONE long
string. Each model family was trained with its own way of turning the list into that string: its
prompt format (also called its chat template). Use the wrong one and a raw model answers badly.

    python day4\\lab11-voice-agent\\prompt_formats.py            # print the three formats
    python day4\\lab11-voice-agent\\prompt_formats.py --check    # also compare with a real model's template
                                                                # (uses the Qwen tokenizer from Day 2, Lab 5)
"""
import argparse
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# One short conversation: a system message, a first question, the answer, and a follow-up question.
CONVERSATION = [
    {"role": "system", "content": "You are a concise Python tutor."},
    {"role": "user", "content": "How do I reverse a list?"},
    {"role": "assistant", "content": "Use my_list[::-1] for a new list, or my_list.reverse() to reverse it in place."},
    {"role": "user", "content": "Which one is faster?"},
]


def alpaca(messages):
    """Alpaca (Stanford, 2023): ONE instruction and ONE response. It has no real turns,
    so the system message and the history have to be squeezed into the instruction."""
    system = next(m["content"] for m in messages if m["role"] == "system")
    history = [m for m in messages if m["role"] != "system"]
    *previous, last = history
    context = "\n".join(f"{m['role'].title()}: {m['content']}" for m in previous)
    return (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        f"### Instruction:\n{system} {last['content']}\n\n"
        f"### Input:\n{context}\n\n"
        "### Response:\n"
    )


def chatml(messages):
    """ChatML (OpenAI, also used by Qwen and others): every message is wrapped in
    <|im_start|>role ... <|im_end|>. The prompt ends by opening the assistant's turn."""
    text = ""
    for m in messages:
        text += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    return text + "<|im_start|>assistant\n"


def llama2(messages):
    """Llama-2 chat (Meta, 2023): each user turn sits inside [INST] ... [/INST], the system
    message sits inside <<SYS>> ... <</SYS>> in the FIRST user turn, and every finished
    exchange is closed with </s> and a new one opened with <s>."""
    system = next(m["content"] for m in messages if m["role"] == "system")
    turns = [m for m in messages if m["role"] != "system"]
    text = ""
    for i in range(0, len(turns), 2):
        user = turns[i]["content"]
        if i == 0:
            user = f"<<SYS>>\n{system}\n<</SYS>>\n\n{user}"
        text += f"<s>[INST] {user} [/INST]"
        if i + 1 < len(turns):
            text += f" {turns[i + 1]['content']} </s>"
    return text


def check_against_real_template(formats):
    """Compare our ChatML string with the template stored in a real model's tokenizer."""
    from transformers import AutoTokenizer

    name = "Qwen/Qwen2.5-0.5B-Instruct"
    try:
        tok = AutoTokenizer.from_pretrained(name)
    except Exception as e:
        print(f"Could not load the {name} tokenizer ({type(e).__name__}). Was Day 2 prefetch run? Skipping the check.")
        return
    try:
        real = tok.apply_chat_template(CONVERSATION, tokenize=False, add_generation_prompt=True)
    except Exception as e:
        print(f"Could not apply the chat template ({type(e).__name__}: {e}). Skipping the check.")
        return
    print("=" * 70)
    print(f"Real chat template of {name} (tokenizer.apply_chat_template):")
    print("=" * 70)
    print(real)
    print("Same as our ChatML string?", "YES" if real == formats["ChatML"] else "NO - compare them")
    print("\nTokens per format (counted with the Qwen tokenizer):")
    for label, text in formats.items():
        print(f"  {label:<8} {len(tok(text)['input_ids']):>4} tokens")
    print("The words are the same; the format adds the overhead. You pay for it on every call.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="compare with a real model's chat template")
    args = parser.parse_args()

    formats = {"Alpaca": alpaca(CONVERSATION), "ChatML": chatml(CONVERSATION), "Llama-2": llama2(CONVERSATION)}
    for label, text in formats.items():
        print("=" * 70)
        print(label)
        print("=" * 70)
        print(text)
        print()
    if args.check:
        check_against_real_template(formats)


if __name__ == "__main__":
    main()
