# Challenge 3 — Testing and Evaluation (20 pts)

**Goal (slides):** Demonstrate your ability to write tests and evaluate responses from LLMs.

**Artifact:** [`challenge-3-testing-and-prompt-evaluation-Timothy-Kempster.ipynb`](./challenge-3-testing-and-prompt-evaluation-Timothy-Kempster.ipynb)

## Requirement traceability

| Requirement | Where it's met |
|---|---|
| Function that classifies questions into Employment / General Information / Emergency Services / Tax Related | `classify_question()` |
| Function that generates social-media posts for government announcements | `generate_social_post()` (+ `does_post_follow_rules()` LLM checker) |
| Unit tests for each function using **pytest** | `TestClassifyQuestion` (12 tests) + `TestGenerateSocialPost` (8 tests) via `ipytest` — all passing in outputs |
| Use the Google Evaluation API to evaluate/compare prompts | `EvalTask` comparing prompt **V1 (baseline)** vs **V2 (detailed)** on coherence/fluency/rule-compliance |

## Result

V2 (detailed, rule-bearing prompt) beats V1 on `rule_compliance` (3.8 → 5.0) with equal
coherence/fluency — documented in the comparison table and the closing markdown.

## How to run

Open the notebook in Colab Enterprise, set `PROJECT_ID` / region constants in the top
configuration cell, and run all cells top-to-bottom. Requires Vertex AI (including the Gen AI
Evaluation Service) enabled. The pytest cells run in-notebook via `ipytest`.
