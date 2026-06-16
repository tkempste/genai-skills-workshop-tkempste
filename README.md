# GenAI Delivery Excellence — Skills Validation Workshop

**Participant:** Timothy Kempster

**Workshop:** Public Sector GenAI Delivery Excellence — Skills Validation Workshop (Google), June 15–16, 2026

**Google Cloud project used for all work:** `qwiklabs-gcp-04-a13cec945fb9`

This repository is my submission for grading. It contains the artifacts for all five
challenges defined in the workshop slide deck,
[`Public Sector GenAI Delivery Excellence_ Skills Validation Workshop.pdf`](./Public%20Sector%20GenAI%20Delivery%20Excellence_%20Skills%20Validation%20Workshop.pdf),
which is included here as the authoritative source of each challenge's goal and requirements.

---

## For Doug (or anyone else :D)

Each challenge is either a **Jupyter notebook** meant to run in **Agent Platform / Colab
Enterprise** in a Google Cloud project, or a set of **screenshots + exported config** where
the proof is the console artifact. None of the notebooks need to run on your local machine —
they are written to run top-to-bottom in Colab Enterprise using the notebook runtime's
ambient (Application Default) credentials.

**To reproduce a notebook challenge:**
1. Open the notebook in Colab Enterprise in a project where the relevant APIs are enabled
   (Vertex AI, BigQuery, Discovery Engine / AI Applications, Model Armor, DLP as applicable).
2. Update the `PROJECT_ID` (and region constants) in the **Configuration** cell to your project.
3. Run all cells top-to-bottom.

> The `PROJECT_ID` values committed in the notebooks point at the Qwiklabs project I used
> during the workshop (`qwiklabs-gcp-04-a13cec945fb9`). Swap in your own project ID to re-run.

Environment notes that affect reproduction are called out per-challenge below (e.g. the
Qwiklabs DLP API restriction in Challenge 1).

---

## Repository layout

| Path | Challenge | Type of proof |
|---|---|---|
| [`challenge-1-gemini-prompt-security-Timothy-Kempster.ipynb`](./challenge-1-gemini-prompt-security-Timothy-Kempster.ipynb) | 1 — Gemini Prompt Security | Runnable notebook |
| [`challenge-2-RAG-timothy-kempster.ipynb`](./challenge-2-RAG-timothy-kempster.ipynb) | 2 — RAG in BigQuery | Runnable notebook |
| [`challenge-3-testing-and-prompt-evaluation-Timothy-Kempster.ipynb`](./challenge-3-testing-and-prompt-evaluation-Timothy-Kempster.ipynb) | 3 — Testing & Evaluation | Runnable notebook |
| [`challenge-4-agent-ai-app-timothy-kempster/`](./challenge-4-agent-ai-app-timothy-kempster) | 4 — Agent Builder (bonus) | Screenshots + exported agent JSON |
| [`challenge-5-alaska-DoS-timothy-kempster/`](./challenge-5-alaska-DoS-timothy-kempster) | 5 — Alaska Dept. of Snow agent | Notebook + deployed Cloud Run app + diagram + screenshots |


---

## Challenge 1 — Gemini Prompt Security

**Goal (slides):** Demonstrate how to program a secure and safe generative AI system.

**Artifact:** [`challenge-1-gemini-prompt-security-Timothy-Kempster.ipynb`](./challenge-1-gemini-prompt-security-Timothy-Kempster.ipynb)

A `SecureChatSession` "CodingBot" assistant runs every turn through a 4-layer pipeline.

| Requirement | Where it's met |
|---|---|
| Python chat app using the latest Gemini | `SecureChatSession` on `gemini-2.5-flash` |
| System instructions with goals **and** restrictions | `SYSTEM_INSTRUCTION` (goals + explicit "must NEVER" list) |
| Prompt filtering to validate user input (Model Armor) | `sanitize_user_prompt()` → Model Armor PI/jailbreak template |
| Gemini safety filters | `SAFETY_SETTINGS` (`BLOCK_LOW_AND_ABOVE` on all 4 harm categories) |
| Validate model responses; only return safe responses | `sanitize_model_response()` + finish-reason/safety-rating checks |
| **Bonus:** Model Armor + Sensitive Data Protection for response filtering | `redact_sensitive_data()` (Cloud DLP) + response Model Armor template |

**Demonstrated tests in the notebook:** normal coding question (passes), prompt injection /
DAN jailbreak (blocked), out-of-scope question (declined by system instruction), malicious-code
request (blocked), multi-turn context, and an interactive session with several attack attempts.

**Environment note:** In the Qwiklabs project the DLP (Sensitive Data Protection) API call
returned `SERVICE_DISABLED` at the org level despite project-level enablement, so the DLP layer
**fails open** (documented in the notebook's Summary). The Model Armor and Gemini safety layers
(steps 1–3) fail closed and are fully functional in the run outputs.

---

## Challenge 2 — Programming a RAG System in BigQuery

**Goal (slides):** Demonstrate a RAG system that uses BigQuery to generate embeddings and
perform a vector search.

**Artifact:** [`challenge-2-RAG-timothy-kempster.ipynb`](./challenge-2-RAG-timothy-kempster.ipynb)

| Requirement | Where it's met |
|---|---|
| Load the Aurora Bay FAQ data into a BigQuery table | Step 1 — load `gs://labs.roitraining.com/aurora-bay-faqs/aurora-bay-faqs.csv` (50 rows) |
| Create embeddings for each record, stored in BigQuery | Steps 2–5 — Cloud Resource connection → `text-embedding-005` remote model → `ML.GENERATE_EMBEDDING` into `aurora_bay_faqs_embedded` |
| Chatbot that searches the embeddings to answer accurately | Step 6 `search_faqs()` (`VECTOR_SEARCH`) + Step 7 `ask_aurora_bay()` (Gemini, grounded) |
| Coded in Python and well-documented | Markdown per step + docstrings; Summary table at the end |

**Demonstrated tests:** in-corpus question (accurate), out-of-corpus question (declines instead
of hallucinating), raw retrieval inspection with cosine distances, and a multi-turn chat.

---

## Challenge 3 — Testing and Evaluation

**Goal (slides):** Demonstrate your ability to write tests and evaluate responses from LLMs.

**Artifact:** [`challenge-3-testing-and-prompt-evaluation-Timothy-Kempster.ipynb`](./challenge-3-testing-and-prompt-evaluation-Timothy-Kempster.ipynb)

| Requirement | Where it's met |
|---|---|
| Function that classifies questions into Employment / General Information / Emergency Services / Tax Related | `classify_question()` |
| Function that generates social-media posts for government announcements | `generate_social_post()` (+ `does_post_follow_rules()` LLM checker) |
| Unit tests for each function using **pytest** | `TestClassifyQuestion` (12 tests) + `TestGenerateSocialPost` (8 tests) via `ipytest` — all passing in outputs |
| Use the Google Evaluation API to evaluate/compare prompts | `EvalTask` comparing prompt **V1 (baseline)** vs **V2 (detailed)** on coherence/fluency/rule-compliance |

**Result:** V2 (detailed, rule-bearing prompt) beats V1 on `rule_compliance` (3.8 → 5.0) with
equal coherence/fluency — documented in the comparison table and the closing markdown.

---

## Challenge 4 — Building Agents with AI Applications

**Goal (slides):** Use Google AI Applications to create a Conversational Agent that uses a
Playbook and a Data Store to answer user questions.

**Artifacts:** [`challenge-4-agent-ai-app-timothy-kempster/`](./challenge-4-agent-ai-app-timothy-kempster)

### Full write-up with each screenshot: [`proof.md`](./challenge-4-agent-ai-app-timothy-kempster/proof.md).


| Requirement | Where it's met |
|---|---|
| Create a conversational agent using AI Applications | "Aurora Bay Agent" (Conversational Agents / Gemini Enterprise) — `Screenshot1.png` |
| Create an AI Applications data store | Data store sourced from `gs://labs.roitraining.com/aurora-bay-faqs` (100 docs) — `datastore.png`, `image.png` |
| Playbook with goal, instructions, and data store | Default Generative Playbook configured for agent "Alice" — `screenshot-desc-goals.png`; FAQ-lookup example — `example-run.png` |
| Export the agent as JSON | [`exported_agent_Aurora Bay Agent.zip`](./challenge-4-agent-ai-app-timothy-kempster/exported_agent_Aurora%20Bay%20Agent.zip) — contains `agent.json`, `playbooks/`, `tools/Data Store/`, `intents/`, `flows/` |


---

## Challenge 5 — Alaska Department of Snow (ADS) Online Agent

**Goal (slides):** Demonstrate a secure, accurate, production-quality generative AI agent that
can be deployed online, built for the ADS case study.

**Artifacts:** [`challenge-5-alaska-DoS-timothy-kempster/`](./challenge-5-alaska-DoS-timothy-kempster)
- [`challenge-5-timothy-kempster.ipynb`](./challenge-5-alaska-DoS-timothy-kempster/challenge-5-timothy-kempster.ipynb) — full build, tests, and evaluation
- [`architecture.md`](./challenge-5-alaska-DoS-timothy-kempster/architecture.md) — solution diagram + how it answers ADS's security/privacy/accuracy/cost concerns
- [`ads-agent/`](./challenge-5-alaska-DoS-timothy-kempster/ads-agent) — the deployable Flask app (`app.py`, `Dockerfile`, `requirements.txt`) running on Cloud Run
- `screenshot-of-agent.png` — the live agent at `alaska-dept-of-snow-131669982938.us-east4.run.app`
- `app-logs-screenshot.png` — Cloud Run logs showing prompts/pipeline steps being logged

| Requirement | Where it's met |
|---|---|
| Create a diagram of the solution (Instruction 1) | [`architecture.md`](./challenge-5-alaska-DoS-timothy-kempster/architecture.md) (Mermaid runtime + offline-quality diagrams) |
| Backend data store for RAG (using `gs://labs.roitraining.com/alaska-dept-of-snow`) | Vertex AI Search / Discovery Engine data store `alaska-dept-of-snow`, imported + verified in the notebook |
| Access to backend API functionality | National Weather Service API integration (`get_weather*`, live forecasts per Alaska city) |
| Unit tests for agent functionality | 16 pytest tests (RAG, Weather, Security, Agent) — all passing in outputs |
| Evaluation data via the Google Evaluation service API | `EvalTask` with groundedness / coherence / helpfulness metrics |
| Prompt filtering and response validation | Model Armor `check_prompt()` + `check_response()` (fail-open + logged) |
| Log all prompts and responses | `log_step()` → Cloud Logging; see `app-logs-screenshot.png` |
| Generative AI agent deployed to a website | Flask chat app on **Cloud Run** (`ads-agent/`); live URL shown in `screenshot-of-agent.png` |

**Demonstrated in the live screenshot:** weather grounding ("is it going to snow?"), a
RAG/road-conditions answer, and an off-topic question ("Should I invest in SpaceX?") being
correctly refused — confirming grounding + scope control on the deployed service.

**Note on the data-store import:** the import log shows expected, benign errors for the
`.DS_Store` macOS metadata file and the `.csv` (the bucket also contains a CSV form of the
same FAQs); the supported `.txt` FAQ documents import and serve correctly, as the verification
search confirms.

---

## Cross-challenge notes

- **Model used:** `gemini-2.5-flash` for generation across challenges; `text-embedding-005`
  for BigQuery embeddings (Challenge 2).
- **Regions:** Vertex AI in `us-central1`; Model Armor templates in `us-east4`; the Cloud Run
  service in `us-east4`; BigQuery in the `US` multi-region.
- **Honest environment caveats** (DLP org policy in Challenge 1; benign import errors in
  Challenge 5) are documented inline in the notebooks rather than hidden, so the run outputs
  match what a grader will see in this Qwiklabs-style environment.
