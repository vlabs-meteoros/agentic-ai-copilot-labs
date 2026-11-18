# Lab 5: Getting Started with LLM Usage (Hugging Face Transformers)

| | |
|---|---|
| **Duration** | 40 minutes (+ optional Pinecone part) |
| **Topic** | HF Transformers: loading pre-trained models, encoding and predicting, classification, generation, retrieval and semantic search |
| **You need** | Internet access to Hugging Face, or models prefetched during setup (~1.3 GB). CPU is fine. |
| **Notebook** | `Lab05_LLM_Usage_with_Transformers.ipynb` |

## Objectives

* Use `pipeline()` for sentiment and zero-shot classification
* Run the encode → model → logits → softmax steps by hand
* Generate text with a small instruction-tuned LLM (Qwen2.5-0.5B-Instruct) and inspect its **chat template**
* Create sentence **embeddings** and compare meaning with cosine similarity
* Build a **semantic search** index with **FAISS**, directly and through **LangChain**
* Combine retrieval and generation (a mini **RAG**) and see where a small model still fails
* *(Optional)* Store and query the same vectors in **Pinecone**

---

## Task 1: Open the notebook (2 min)

Open `day2/lab05-llm-usage/Lab05_LLM_Usage_with_Transformers.ipynb`, select the **.venv** kernel, and run the setup cell.

**Checkpoint:** it prints library versions and `Knowledge base: 36 articles`.

The knowledge base (`day2/data/helpdesk_kb.json`) is a set of short helpdesk and policy articles for **Kaveri Systems**, a fictional company. You'll use it again in Lab 6.

## Task 2: Part 1, pipelines (6 min)

**Checkpoint:**

* The sentiment model labels the three reviews POSITIVE, NEGATIVE, POSITIVE (it gets *"Not bad at all"* right; Day 1's 2,000-sentence model didn't).
* Zero-shot routes the four tickets to IT support, HR, Finance and Facilities with scores around 0.9, using labels no one trained it on.

If you pushed a model in Lab 4, set `MY_REPO` and run that cell too.

## Task 3: Part 2, under the hood (6 min)

**Checkpoint:** `input_ids shape: (3, 15)`, the logits tensor has shape 3 × 2, and the probabilities match Part 1 exactly.

## Task 4: Part 3, text generation (8 min)

The first run downloads Qwen2.5-0.5B-Instruct (~1 GB) unless it was prefetched.

**Checkpoint:**

* A short answer about vector databases appears in ~5-15 seconds on CPU.
* The chat template shows `<|im_start|>system ... <|im_end|>` markers (ChatML).
* Greedy decoding prints the **same** name three times; sampling gives different names, wilder at `temperature=1.5`.
* The closed-book Kaveri Systems question gets a fluent answer that **isn't based on any real policy**. Discuss with your neighbour: is a hedged guess still a hallucination?

## Task 5: Parts 4 and 5, embeddings and semantic search (12 min)

**Checkpoint:**

* Embeddings have **384** dimensions. "How do I reset my password?" and "I forgot my login credentials" score ~0.68 despite sharing no keywords.
* FAISS returns KB-002 (password reset) for *"I can't remember my login details"*, while keyword search finds **0 hits** for it.
* The LangChain FAISS store filters by category, saves to `outputs/faiss_kb`, and reloads with 36 vectors.

## Task 6: Part 6, retrieval + generation (6 min)

**Checkpoint:**

* With retrieval, the leave question gets the right answer (10 days carry over).
* The Bengaluru hotel answer quotes INR 7,000, but the article never says Bengaluru is a "metro city". The model assumed it.
* For *"Who is the CEO of Kaveri Systems?"* the 0.5B model usually **invents a name**, even though the answer isn't in the context.
* With the alternative system prompt, it usually says "I don't know", and the citations are still missing. Small models are fragile; Lab 6 repeats this with a large model.

Try your own questions with `rag_answer("...")`.

## Task 7 (optional): Part 7, Pinecone

1. Sign up for the free **Starter** plan at https://app.pinecone.io.
2. Copy your API key from **API Keys**.
3. Add `PINECONE_API_KEY=pcsk_...` to `.env` at the repository root, save, **restart the kernel**, and re-run the setup cell plus Parts 4-5.
4. Run the Part 7 cells: create a serverless index (AWS `us-east-1`), upsert 36 vectors with metadata, query with a filter, then delete the index.

**Checkpoint:** the Pinecone scores for the laptop query match the local FAISS scores, because the vectors are the same.

---

## Discussion

1. When would you choose zero-shot classification over fine-tuning (Day 1)? When not?
2. FAISS vs a managed vector database: what changes when 50 microservices need the same index?
3. Retrieval fixed the *facts*, but not the CEO answer. What does that tell you about choosing a model for RAG?

## Troubleshooting

| Problem | Fix |
|---|---|
| Downloads are slow or fail with 429 | Add `HF_TOKEN=hf_...` to `.env` (from Lab 4), or ask your trainer to prefetch |
| Kernel dies while loading Qwen | Low RAM: close other notebooks (Kernel > Shut Down), then re-run from the setup cell |
| `faiss` import error | Re-run `pip install -r requirements.txt` in the activated `.venv` |
| Generation takes > 60 s | Normal on a 2-core VM for the first call; later calls are faster. Reduce `max_new_tokens` |
