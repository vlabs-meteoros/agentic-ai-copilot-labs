"""
Lab 11, Task 3 - Structured output: from "please answer in JSON" to a schema the model must follow.

    python day4\\lab11-voice-agent\\structured_output.py --part 1   # ask for JSON in the prompt, then check it
    python day4\\lab11-voice-agent\\structured_output.py --part 2   # enforce a Pydantic model
"""
import argparse
import json

from pydantic import BaseModel, Field, ValidationError

from voice_helpers import get_llm_client

QUESTION = "How do I remove duplicates from a Python list but keep the original order?"


# The shape we want back. Field descriptions are sent to the model as part of the JSON schema,
# so write them for the model, like the docstring of an MCP tool (Day 3, Lab 10).
class CodeAnswer(BaseModel):
    summary: str = Field(description="One sentence that answers the question")
    code: str = Field(description="A short, runnable Python example. Code only, no Markdown fences")
    steps: list[str] = Field(description="2 to 4 short steps that explain the code")
    # TODO (Lab 11, Task 3): add a field here, then run --part 2 again


def part1(client, deployment, runs=3):
    print("PART 1: we only ASK for JSON in the prompt\n")
    prompt = (
        f"{QUESTION}\n\nAnswer in JSON with the keys summary, code and steps (a list of strings)."
    )
    for i in range(1, runs + 1):
        r = client.chat.completions.create(
            model=deployment, temperature=1.0,
            messages=[{"role": "user", "content": prompt}],
        )
        text = r.choices[0].message.content
        print(f"--- Run {i}: the first 120 characters the model returned:")
        print(text[:120].replace("\n", "\\n"))
        try:
            data = json.loads(text)
            CodeAnswer.model_validate(data)
            print("    json.loads: OK   Pydantic validation: OK")
        except json.JSONDecodeError as e:
            print(f"    json.loads FAILED: {e.msg} (line {e.lineno}). Your program would crash here.")
        except ValidationError as e:
            print(f"    Valid JSON, but the wrong shape: {e.error_count()} validation error(s)")
            print("     ", str(e).splitlines()[1:3])
        print()


def part2(client, deployment):
    print("PART 2: the Pydantic model becomes a JSON schema the model MUST follow\n")
    print("Schema sent with the request:")
    print(json.dumps(CodeAnswer.model_json_schema(), indent=2)[:900], "\n")
    r = client.chat.completions.parse(
        model=deployment,
        messages=[{"role": "user", "content": QUESTION}],
        response_format=CodeAnswer,
    )
    answer = r.choices[0].message.parsed      # already a CodeAnswer object, not a string
    print(f"type: {type(answer).__name__}")
    print(f"summary: {answer.summary}")
    print("code:")
    print(answer.code)
    print("steps:")
    for n, step in enumerate(answer.steps, 1):
        print(f"  {n}. {step}")
    extra = {k: v for k, v in answer.model_dump().items() if k not in ("summary", "code", "steps")}
    if extra:
        print("your new field(s):", extra)
    print(f"\n[tokens: {r.usage.prompt_tokens} in + {r.usage.completion_tokens} out]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=["1", "2", "all"], default="all")
    args = parser.parse_args()
    client, deployment = get_llm_client()
    if args.part in ("1", "all"):
        part1(client, deployment)
    if args.part in ("2", "all"):
        part2(client, deployment)


if __name__ == "__main__":
    main()
