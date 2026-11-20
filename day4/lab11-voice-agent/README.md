# Lab 11 A Conversational Voice Coding Assistant (STT + GPT + TTS)

| | |
|---|---|
| **Duration** | 55 minutes |
| **Topic** | Developer Productivity: prompt formats (Alpaca, ChatML, Llama-2), structured output with Pydantic, conversational voice AI |
| **You need** | Day 4 setup done. Your `.env` with the shared Azure values from Day 1-2 (`AZURE_AI_ENDPOINT`, `AZURE_AI_KEY`, `AZURE_AI_REGION`, `AZURE_OPENAI_DEPLOYMENT`). A microphone and speakers are **optional** |
| **Files** | `prompt_formats.py`, `structured_output.py`, `speech_demo.py`, `voice_agent.py`, `voice_helpers.py`, sample questions in `audio\`. Your results go to `outputs\` (Git ignores it) |

> **Work in the labs repository window** (not the `kaveridesk` window from Lab 10). Run every command from the repository root,
> with the environment active: `.\.venv\Scripts\Activate.ps1`

## Objectives

* See how a chat (a list of messages) becomes one string in three **prompt formats**: Alpaca, ChatML and Llama-2
* Make an LLM's output **reliable to parse**: from "please answer in JSON" to a **Pydantic** schema the model must follow
* Turn speech into text (**STT**) and text into speech (**TTS**) with Azure AI Speech
* Build a voice assistant that **remembers the conversation**, and see why voice needs structured output

## How the voice assistant works

```
  your voice ──> [ STT ] ──text──> [ GPT + conversation history ] ──VoiceReply──> spoken ──> [ TTS ] ──> audio
  (or a .wav)    Azure Speech       Azure OpenAI (gpt-4.1-mini)        │                      Azure Speech
                                                                       └──> code ──> shown on screen
```

Everything uses the **same shared Azure resource and key** you've used since Day 1. Speech and Azure OpenAI are both services of that resource.

> **No microphone or speakers on your VM?** That's fine. The lab uses the recorded questions in `audio\` by default and saves every reply as a
> `.wav` file in `outputs\`. Options marked `--mic` and `--play` are for machines with audio.

---

## Task 1: Check your connection (5 min)

1. Open `.env` at the repository root and check the four Azure values are filled in (they are the same as Day 2).
2. Make your first speech:

   ```powershell
   python day4\lab11-voice-agent\speech_demo.py tts "Hello! I am Kavi, your voice coding assistant." --play
   ```

**Checkpoint:** the terminal prints `Saved ...\outputs\tts_demo.wav (about 3 s of audio ...)`. If your VM has speakers, you hear an Indian English voice.
Without speakers you'll see `could not play audio`, which is fine.

> `speech_demo.py` calls Azure Speech's **REST API** with the `requests` package. Text to speech is **one HTTP POST** with a small XML document
> (SSML) that names the voice. Open `voice_helpers.py` and find `build_ssml` and `text_to_speech` to see it.

## Task 2: Prompt formats: Alpaca, ChatML, Llama-2 (10 min)

When you call a chat API you send a **list of messages**. But a language model only reads **one long string** of tokens.
Each model family was trained with its own way of writing a conversation as a string: its **prompt format** (or **chat template**).

1. Run:

   ```powershell
   python day4\lab11-voice-agent\prompt_formats.py
   ```

   You see the same conversation (system message, question, answer, follow-up) three times. Compare them:

   | Format | Where it comes from | How it marks the turns |
   |---|---|---|
   | **Alpaca** | Stanford Alpaca (2023), many early fine-tunes | `### Instruction:` / `### Input:` / `### Response:` headings. Only **one** turn: the history has to be squeezed into `Input` |
   | **ChatML** | OpenAI; also Qwen and many open models | `<|im_start|>role ... <|im_end|>` around every message |
   | **Llama-2** | Meta Llama 2 Chat | `<s>[INST] ... [/INST] answer </s>`, with the system message inside `<<SYS>>` in the first turn |

2. Notice how **each format ends**: with `### Response:`, `<|im_start|>assistant` or `[/INST]`. That's the cue for the model to start writing **its** turn.
3. Check our ChatML against a real model. The Qwen tokenizer you downloaded on Day 2 stores its chat template:

   ```powershell
   python day4\lab11-voice-agent\prompt_formats.py --check
   ```

**Checkpoint:** the output says `Same as our ChatML string? YES`, and Alpaca needs the most tokens for the same conversation.

> **Why it matters:** with Azure OpenAI, the service applies the template for you. When you run an open model yourself
> (Hugging Face on Day 2, Ollama on Day 8), the **wrong template** makes a good model answer badly. It might continue
> *your* message, ignore the system prompt, or never stop. Use `tokenizer.apply_chat_template()` instead of building strings by hand.

## Task 3: Structured output with Pydantic (12 min)

Your program needs data it can use (`answer.code`, `answer.steps`), not a paragraph. Let's see how reliable "just ask for JSON" is.

1. **Asking nicely.** Run part 1. It asks three times for JSON and tries to parse each answer:

   ```powershell
   python day4\lab11-voice-agent\structured_output.py --part 1
   ```

   Look at the first characters of each answer. The model often wraps the JSON in Markdown fences (```` ```json ````), and `json.loads` fails.

2. **Enforcing a schema.** Open `structured_output.py` and read the `CodeAnswer` class. It's a **Pydantic** model: field names, types and descriptions.
   Run part 2:

   ```powershell
   python day4\lab11-voice-agent\structured_output.py --part 2
   ```

   `client.chat.completions.parse(..., response_format=CodeAnswer)` sends the model's **JSON schema** with the request. The service then makes the model
   follow it, and the SDK hands you a `CodeAnswer` **object**: `answer.summary`, `answer.code`, `answer.steps`.

3. **Add a field with Copilot.** In `structured_output.py`, put the cursor on the `# TODO (Lab 11, Task 3)` line. Press <kbd>Ctrl</kbd>+<kbd>I</kbd> and send:

   ```text
   Replace this TODO with a field "difficulty" that can only be beginner, intermediate or advanced,
   with a description for the model. Add any import you need.
   ```

   Keep the change and run part 2 again.

**Checkpoint:** part 1 fails to parse in at least one run (usually all three). Part 2 prints `type: CodeAnswer`, a clean code block, numbered steps,
and `your new field(s): {'difficulty': 'beginner'}` (or another of the three values).

> **Output enforcement in short:** describe the shape with Pydantic, let the API enforce it, and get typed objects back.
> The field **descriptions** are instructions too: the model reads them. If you can't use `parse()` (some models don't support it), validate with
> `Model.model_validate_json(text)` and retry when it fails.

## Task 4: Speech to text and text to speech (10 min)

1. **Speech to text** on all the sample questions:

   ```powershell
   python day4\lab11-voice-agent\speech_demo.py stt --all
   ```

   Look at the last one, `q5_tricky_terms.wav`. The speaker said *"pip install python-dotenv"* and *"load_dotenv"*. What did STT write?

2. **Text to speech** with different voices. List the Indian English voices, then try two:

   ```powershell
   python day4\lab11-voice-agent\speech_demo.py voices --locale en-IN
   python day4\lab11-voice-agent\speech_demo.py tts "Your build passed. Two tests were skipped." --voice en-IN-PrabhatNeural --out prabhat.wav --play
   python day4\lab11-voice-agent\speech_demo.py tts "Your build passed. Two tests were skipped." --voice en-IN-NeerjaNeural --rate slow --out neerja_slow.wav --play
   ```

3. **Optional, with a microphone:** record a question yourself (press <kbd>Enter</kbd>, speak, press <kbd>Enter</kbd> again):

   ```powershell
   python day4\lab11-voice-agent\speech_demo.py mic --play
   ```

**Checkpoint:** q1-q4 come back word for word. q5 has mistakes in the code words (for example *python dot env*, *load underscore dot env*).
Each STT call takes well under a second for a few seconds of audio.

> **Voice and code don't mix well.** STT is trained on everyday speech, so symbols and package names come out wrong, and TTS reads code badly too.
> A voice coding assistant should **talk about** code in plain words and **show** the code on screen. That's the design in Task 5.

## Task 5: The voice assistant (12 min)

Open `voice_agent.py` and find the three parts of the loop: **1. Speech to text**, **2. The LLM, with the conversation so far**, **3. Text to speech**.
Look at `SYSTEM_PROMPT` and the `VoiceReply` model: `spoken` is what the voice says, `code` is what the screen shows.

1. Run a three-question conversation from the sample files:

   ```powershell
   python day4\lab11-voice-agent\voice_agent.py
   ```

   Question 3 (*"Now make it ignore spaces and capital letters"*) never says **what** "it" is. Does the assistant know?

2. Run the same kind of question **without** structured output, where the model's whole answer goes to TTS:

   ```powershell
   python day4\lab11-voice-agent\voice_agent.py --plain --files day4\lab11-voice-agent\audio\q2_palindrome.wav
   ```

   Compare the line in square brackets with the structured run: **characters spoken**, **seconds of audio** and the **TTS** time.
   If you have speakers, add `--play` to both runs and listen.

3. Talk to it yourself:
   * **with a microphone:** `python day4\lab11-voice-agent\voice_agent.py --mic --play`. Say *"goodbye"* or type `q` to stop.
   * **without one:** `python day4\lab11-voice-agent\voice_agent.py --text` and type your questions (`q` to stop).

**Checkpoint:**
* In the structured run, answer 3 changes the **palindrome function from answer 2**. The assistant remembered it, because `history` holds the earlier turns.
* Every `Assistant says:` line is 1-3 short sentences without code. The code appears under `On screen:`.
* The `--plain` run speaks **several times more characters** (code, backticks, Markdown) and makes a much longer audio file.

> **Latency is the user experience in voice.** Look at the timings: STT + LLM + TTS all happen while the user waits in silence.
> Real voice products **stream** each stage (recognise while the user is still speaking, speak the first sentence while the model is still writing),
> or use a speech-to-speech model that does all three. Short `spoken` text is the cheapest speed-up you have.

## Task 6: Make it yours with Copilot (6 min)

Pick **one** of these and ask Copilot **Agent** mode to do it (attach `#file:voice_agent.py`). Then run the assistant again to test it.

* **Suggested next question:** *"Add a field suggested_next_question to VoiceReply (a short question the user could ask next). Print it after the
  code but don't speak it. Replace the TODO for Task 6."*
* **Save the code:** *"When a reply has code, also save it to outputs\snippet_<turn>.py and print the path."*
* **Answer in Hindi:** *"Add a field language (en or hi) to VoiceReply. If the user asks for Hindi, answer 'spoken' in Hindi and use the
  voice hi-IN-SwaraNeural for that reply."* Test it with `--text`: *"Explain what a list is, in Hindi please."*

**Checkpoint:** your change works in a new run, and the original three-question run still works.

---

## Summary

* A **prompt format** (chat template) turns a list of messages into the one string a model reads. APIs apply it for you; for open models, use the model's own template.
* "Answer in JSON" is a request. A **Pydantic schema** with `parse()` is a contract: typed objects, no parsing code, no fences.
* A voice agent is **STT → LLM → TTS** plus **conversation history**. Structured output splits **what to say** from **what to show**, which keeps speech short, clear and fast.

Next: **[Lab 12](../lab12-agent-mode/README.md)**, back in the `kaveridesk` window.