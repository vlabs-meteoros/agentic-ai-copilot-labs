# Lab 6: Prompt Variations and Grounding with Azure OpenAI

| | |
|---|---|
| **Duration** | 30 minutes |
| **Topic** | Generative AI Fundamentals: how LLMs generate responses, strengths and limitations, Responsible AI, API-based AI interactions |
| **You need** | The Azure values in `.env` from Day 1 Lab 1 (the same resource now also serves **gpt-4.1-mini**) |
| **Notebook** | `Lab06_Prompt_Variations_and_Grounding.ipynb` |

## Objectives

* Call Azure OpenAI from Python and read token usage and cost
* Explain response variation with token probabilities, `temperature`, `top_p` and `n`
* Improve a prompt step by step (role, constraints, format, delimiters) and get schema-checked **JSON** output
* Recognise hallucinations and **ground** answers in company documents, with citations
* Compare "put everything in the prompt" with retrieval on token cost
* See content filters, jailbreak detection and prompt-injection defences in action
* Call the model with a plain REST request

---

## Task 1: Check `.env` (2 min)

Lab 6 reuses the Lab 1 settings. Open `.env` at the repository root and check that these lines have real values:

```ini
AZURE_AI_ENDPOINT=https://agenticaicopilot-ai-sea.cognitiveservices.azure.com/
AZURE_AI_KEY=<your key>
AZURE_AI_REGION=southeastasia
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
```

If `AZURE_OPENAI_DEPLOYMENT` is missing, add it. If the key is missing, get it as in Lab 1 (Azure portal > `agenticaicopilot-ai-sea` > **Keys and Endpoint**) or from your trainer.

Optional check from the terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python setup\verify_env.py --azure
```

**Checkpoint:** the last lines include `Azure OpenAI chat call (gpt-4.1-mini): HTTP 200`.

## Task 2: Part 1, your first API call (4 min)

Open the notebook, select the **.venv** kernel, run the setup cell and Part 1.

**Checkpoint:** the answer is two sentences; the follow-up ("an everyday analogy") makes sense only because the history was sent again. Each call costs a small fraction of a cent.

## Task 3: Part 2, response variation (6 min)

**Checkpoint:**

* One first-token candidate (probably `Pal`, as in *Palace*) has almost all the probability. The model is very sure how to start.
* At `temperature=0`, the five coffee-shop names are identical or nearly so; at 1.2-1.8 all five differ.

Do the `top_p` **Try it**.

## Task 4: Part 3, prompt variations and structured output (7 min)

**Checkpoint:**

* Prompt A and B replies are long and generic (placeholders like `[Your Name]`, offers you didn't approve). Prompt C is under 120 words, quotes `KS-88213`, offers exactly the two options and is signed *Priya, Customer Care*.
* The `Ticket` object has `urgency` as an integer and `order_id = "KS-88213"`: code can use it directly.

## Task 5: Part 4, hallucination vs grounding (8 min)

**Checkpoint:**

* Closed book: the model says it can't know Kaveri's policy and finds no such paper (good), but the **Cricket World Cup** answer is stuck at its training cutoff and may contradict itself.
* Grounded: correct answers with `[KB-...]` citations, and *"I couldn't find that in the knowledge base"* for the CEO question.
* The **Bengaluru** answer depends on whether the model *assumes* Bengaluru is a metro. After the knowledge-base fix it's INR 7,000 / INR 1,200.
* Retrieval sends ~85-90% fewer input tokens than putting the whole knowledge base in the prompt.

## Task 6: Part 5, Responsible AI (5 min)

**Checkpoint:**

* The haiku request shows every filter category as `safe`.
* The "DAN" jailbreak is blocked with HTTP 400 and `jailbreak=DETECTED`.
* The **blatant** injected email is blocked; the **subtle** one passes the filters, fools the naive prompt, and is flagged with a `WARNING:` by the defended prompt.

## Task 7: Part 6, plain REST (2 min)

**Checkpoint:** HTTP 200 and a Kannada greeting. The same request (URL, `api-key` header, JSON body) works from PowerShell, Postman or a Power Automate **HTTP** action:

```powershell
$body = @{ model = "gpt-4.1-mini"; messages = @(@{ role = "user"; content = "Say hello in Hindi" }) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri "$env:ENDPOINT/openai/v1/chat/completions" `
  -Headers @{ "api-key" = $env:KEY } -ContentType "application/json; charset=utf-8" -Body $body
```

(Set `$env:ENDPOINT` and `$env:KEY` in that terminal first; don't save the key in a script.)

---

## Discussion

1. Which tasks in your work need `temperature=0`, and which benefit from variation?
2. The model guessed which cities are "metros". Where else might a grounded answer hide an assumption?
3. Prompt Shields blocked the blatant attack but not the subtle one. What other layers would you add before letting an LLM act on emails?

## Troubleshooting

| Problem | Fix |
|---|---|
| `RuntimeError: AZURE_AI_ENDPOINT / AZURE_AI_KEY are missing` | Fill `.env` (Task 1), save it, then **Restart** the kernel and re-run the setup cell |
| `401 Access denied` | Wrong or rotated key. Copy Key 1 again from the portal |
| `404 DeploymentNotFound` | `AZURE_OPENAI_DEPLOYMENT` must match the deployment name exactly: `gpt-4.1-mini` |
| `429 Too Many Requests` | The class is sharing one deployment. The client retries automatically; wait a few seconds |
| A cell shows `BLOCKED by Azure` where you didn't expect it | Content filters are probabilistic. That's a teaching point, not an error |
