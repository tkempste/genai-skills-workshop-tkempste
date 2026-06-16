# Challenge 5 — Alaska Department of Snow (ADS) Online Agent (40 pts)

**Goal (slides):** Demonstrate a secure, accurate, production-quality generative AI agent that
can be deployed online, built for the ADS case study.

The full design write-up — solution diagrams, the Google Cloud services/deployment topology,
the request flow, and how the design answers ADS's security / privacy / accuracy / cost
concerns — lives in the architecture doc. This README is just the index + requirement
traceability.

> **Full architecture & design write-up:** [`architecture.md`](./architecture.md)
> **Deploy instructions for the web app:** [`ads-agent/README.md`](./ads-agent/README.md)

## Artifacts in this folder

| Artifact | What it is |
|---|---|
| [`challenge-5-timothy-kempster.ipynb`](./challenge-5-timothy-kempster.ipynb) | Full build: data store, RAG, weather API, security, unit tests, evaluation |
| [`architecture.md`](./architecture.md) | Solution diagrams (runtime + topology + offline gates) and case-study Q&A |
| [`ads-agent/`](./ads-agent) | Deployable Flask app (`app.py`, `Dockerfile`, `requirements.txt`) running on Cloud Run |
| `screenshot-of-agent.png` | The live agent at `alaska-dept-of-snow-…us-east4.run.app` |
| `app-logs-screenshot.png` | Cloud Run logs showing prompts / pipeline steps being logged |

## Requirement traceability

| Requirement | Where it's met |
|---|---|
| Create a diagram of the solution | [`architecture.md`](./architecture.md) (runtime, topology & offline-quality diagrams) |
| Backend data store for RAG (using `gs://labs.roitraining.com/alaska-dept-of-snow`) | Vertex AI Search / Discovery Engine data store `alaska-dept-of-snow`, imported + verified in the notebook |
| Access to backend API functionality | National Weather Service API integration (`get_weather*`, live forecasts per Alaska city) |
| Unit tests for agent functionality | 16 pytest tests (RAG, Weather, Security, Agent) — all passing in outputs |
| Evaluation data via the Google Evaluation service API | `EvalTask` with groundedness / coherence / helpfulness metrics |
| Prompt filtering and response validation | Model Armor `check_prompt()` + `check_response()` (fail-open + logged) |
| Log all prompts and responses | `log_step()` → Cloud Logging; see `app-logs-screenshot.png` |
| Generative AI agent deployed to a website | Flask chat app on **Cloud Run** (`ads-agent/`); live URL shown in `screenshot-of-agent.png` |

## Demonstrated in the live screenshot

Weather grounding ("is it going to snow?"), a RAG/road-conditions answer, and an off-topic
question ("Should I invest in SpaceX?") being correctly refused — confirming grounding + scope
control on the deployed service.

## Note on the data-store import

The import log shows expected, benign errors for the `.DS_Store` macOS metadata file and the
`.csv` (the bucket also contains a CSV form of the same FAQs); the supported `.txt` FAQ
documents import and serve correctly, as the verification search confirms.
