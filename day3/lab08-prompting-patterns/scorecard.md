# Prompt scorecard

Score each prompt from 0 to 2 on every line (0 = missing, 1 = partly there, 2 = clear). Maximum: **12**.

| # | Criterion | The question to ask | 0 | 1 | 2 |
|---|---|---|---|---|---|
| 1 | **Role** | Does the prompt say who the AI should act as? | | | |
| 2 | **Context** | Does it give the facts the AI needs (or attach them), so the AI doesn't have to guess? | | | |
| 3 | **Task** | Is there one clear instruction with an action verb ("Write", "Classify", "Summarise")? | | | |
| 4 | **Audience and tone** | Does it say who will read the result and how it should sound? | | | |
| 5 | **Output format** | Does it say the shape of the answer (length, sections, table, bullets, subject line)? | | | |
| 6 | **Constraints** | Does it say what to avoid and what "done" looks like (only use given facts, word limit, no jargon)? | | | |

**How to read the score**

* 0-4: the AI has to guess most things. Expect generic text and invented details.
* 5-8: usable, but you'll need several follow-ups.
* 9-12: a structured prompt. The first answer is usually close to what you want.
