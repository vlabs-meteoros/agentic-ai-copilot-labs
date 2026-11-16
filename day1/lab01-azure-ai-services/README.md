# Lab 1: Try Out Azure AI Services

| | |
|---|---|
| **Duration** | 40 minutes |
| **Topic** | AI Fundamentals and Machine Learning: predictive AI, NLP, pre-trained models as a service |
| **You need** | Your lab account (`agentuserN@meteoros.ai`) to read the shared Azure resource's endpoint and key |
| **Notebook** | `Lab01_Azure_AI_Services.ipynb` |

## Objectives

By the end of this lab you will be able to:

* Explain what an AI service call is: **endpoint + api-version + key + JSON**
* Call the Azure **Language** service via raw REST and via the Python SDK
* Use sentiment analysis, opinion mining, key phrases, entity recognition, entity linking and **PII redaction**
* Caption and tag images, and extract text from a receipt with **Azure Vision**
* Translate and transliterate text with **Azure Translator**
* Combine several services into a small multilingual analytics pipeline

---

## Task 1: Get the endpoint and key, and add them to `.env` (5 min)

**Option A: from the Azure portal (recommended).** This also shows you what an AI resource looks like in Azure.

1. In the VM browser, go to **https://portal.azure.com** and sign in with your lab account (`agentuserN@meteoros.ai`).
2. In the top search bar, type **agenticaicopilot-ai-sea** and open the resource.
   (It sits in resource group `AgenticAICopilot_AI_Resources`, region Southeast Asia.)
3. In the left menu, open **Resource Management > Keys and Endpoint**.
4. Copy **KEY 1**, the **Endpoint** and the **Location/Region**. The region should be `southeastasia`.

**Option B:** use the values your trainer shares.

Then:

1. In VS Code's **Explorer**, open the file `.env` at the root of the repository.
   If it doesn't exist, copy `.env.example` and rename the copy to `.env`.
2. Replace the three placeholder lines with the values you copied:

   ```ini
   AZURE_AI_ENDPOINT=https://<resource-name>.cognitiveservices.azure.com/
   AZURE_AI_KEY=<KEY 1>
   AZURE_AI_REGION=southeastasia
   ```

   Remove the `<` `>` brackets.
3. **Save** the file (<kbd>Ctrl</kbd>+<kbd>S</kbd>).
4. *(Optional)* Check the connection from the terminal:

   ```powershell
   .\.venv\Scripts\python.exe setup\verify_env.py --azure
   ```

   You should see `[ OK ] Azure Language call: HTTP 200` and `[ OK ] Azure Translator call: HTTP 200`.

> The key gives access to a paid resource shared by the whole class.
> Don't share it outside the class, and don't paste it into code or chat.

## Task 2: Open the notebook (2 min)

1. In the Explorer, open `day1/lab01-azure-ai-services/Lab01_Azure_AI_Services.ipynb`.
2. Click **Select Kernel** (top right) and choose **.venv (Python 3.12)**.
3. Run the first two cells with <kbd>Shift</kbd>+<kbd>Enter</kbd>.

**Checkpoint:** the second cell prints your endpoint, region and a masked key (`abcd********wxyz`).

## Task 3: Part 1 — Raw REST call (5 min)

Run the Part 1 cells. You send a `LanguageDetection` request with five greetings and see the raw JSON response.

**Checkpoint:** English, Hindi, Kannada and French are detected with confidence 1.00.
The Hinglish sentence (*"Kal milte hain, office mein."*) is also detected as **Hindi**, even though it's written in Latin script.

## Task 4: Part 2 — Language service with the SDK (10 min)

Run the Part 2 cells:

| Cell | What to look for |
|---|---|
| Sentiment + opinion mining | The camera review is **negative** overall, yet opinion mining finds *camera → excellent* (positive). *"The package arrived on Tuesday"* is **neutral**. |
| Key phrases, entities, linking | *Infosys* is an **Organization**, *Mysuru* a **Location**, *Salil Parekh* a **Person**. Linked entities point to Wikipedia. |
| PII | Name, email and phone number are replaced with `*`. So is *"4417"*, wrongly labelled an **Address**, which is a good example of a false positive. |

Complete the **Try it** exercises in the empty cell under Part 2.

## Task 5: Part 3 — Vision (8 min)

1. Run the image analysis cell. Open the image URL in a browser and compare it with the caption and tags.
2. Run the OCR cells on `data/receipt.png` (open the image in VS Code to see it).

**Checkpoint:** the OCR output contains `CHAMUNDI COFFEE WORKS`, the GSTIN `29ABCDE1234F1Z5` and the total `1097.26`.

> If the caption cell prints *"Caption not available in this region"*, that's expected for some Azure regions.
> Tags, objects and OCR still work.

## Task 6: Part 4 — Translator (5 min)

Run the Part 4 cells. One request translates a sentence into Hindi, Kannada, Tamil, French and Japanese.
Transliteration then rewrites the Hindi in Latin script.

**Checkpoint:** five translations, then the Hindi sentence in Roman letters.

## Task 7: Part 5 — Multilingual feedback pipeline (7 min)

Run the Part 5 cells. Eight customer messages in six languages are translated, analysed and redacted, then shown as one table.

**Checkpoint:**

* Each message has a detected `language` (en, hi, kn, fr, es, ja)
* FB-102, FB-104, FB-105 and FB-108 are **negative**; FB-107 is **mixed**; the rest are positive
* Names, emails and phone numbers are masked in `safe_text`
* The final cell lists **4** messages that need a follow-up today

---

## Discussion questions

1. Which of these services would you trust to run **without** human review? What confidence threshold would you set?
2. These are **predictive** services: each returns a fixed kind of answer. What can't they do that a generative model (an LLM) could?
3. We translated to English before analysing. What might get lost? When would you analyse the original language instead?

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Azure settings not found` | `.env` is missing, unsaved, or still has `<...>` placeholders. |
| `HTTP 401` / `Access denied due to invalid subscription key` | The key was mistyped or has extra spaces. Copy it again. |
| `HTTP 401` from **Translator** only | `AZURE_AI_REGION` must match the resource's region exactly (for example `southeastasia`). |
| `HTTP 404 Resource not found` | The endpoint is wrong. It must look like `https://<name>.cognitiveservices.azure.com/`. |
| `(rate limited - retrying...)` | The whole class shares one resource. The helper waits and retries automatically. |
| `ModuleNotFoundError: lab_helpers` | Open the notebook from **this folder**. The notebook's working directory must be `lab01-azure-ai-services`. |
| Kernel list doesn't show `.venv` | <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> > **Python: Select Interpreter** > `.venv`, then reselect the kernel. |
