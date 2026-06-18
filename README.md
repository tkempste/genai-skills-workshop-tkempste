# GenAI Delivery Excellence — Skills Validation Workshop

**Participant:** Timothy Kempster

**Workshop:** Public Sector GenAI Delivery Excellence — Skills Validation Workshop (Google), June 15–16, 2026

**Google Cloud project used for all work:** `qwiklabs-gcp-04-a13cec945fb9`

This repository is my submission for grading. It contains the artifacts for all five
challenges defined in the workshop slide deck,
[`Public Sector GenAI Delivery Excellence_ Skills Validation Workshop.pdf`](./Public%20Sector%20GenAI%20Delivery%20Excellence_%20Skills%20Validation%20Workshop.pdf),
which is included here as the authoritative source of each challenge's goal and requirements.

**Each challenge lives in its own folder with its own README** containing the goal, a
requirement-by-requirement traceability table, and how to run/verify it. Start there for the
details — this top-level README is just the map.

---

## Challenges

| # | Challenge | Points | Folder (has its own README) |
|---|---|---|---|
| 1 | Gemini Prompt Security | 20 | [`challenge-1-gemini-prompt-security-timothy-kempster/`](./challenge-1-gemini-prompt-security-timothy-kempster) |
| 2 | Programming a RAG System in BigQuery | 20 | [`challenge-2-RAG-timothy-kempster/`](./challenge-2-RAG-timothy-kempster) |
| 3 | Testing and Evaluation | 20 | [`challenge-3-testing-and-prompt-evaluation-timothy-kempster/`](./challenge-3-testing-and-prompt-evaluation-timothy-kempster) |
| 4 | Building Agents with AI Applications (bonus) | 10 | [`challenge-4-agent-ai-app-timothy-kempster/`](./challenge-4-agent-ai-app-timothy-kempster) |
| 5 | Alaska Department of Snow Online Agent | 40 | [`challenge-5-alaska-DoS-timothy-kempster/`](./challenge-5-alaska-DoS-timothy-kempster) |

**Total available:** 110 points (80 required to pass).

---

## [For Doug](https://github.com/tkempste/genai-skills-workshop-tkempste/issues/1) (or anyone else :D)

Challenges 1–3 are **Jupyter notebooks** meant to run in **Agent Platform / Colab Enterprise**;
Challenge 4 is **screenshots + an exported agent**; Challenge 5 is a notebook **plus a live
Cloud Run web app**. None of the notebooks need to run on your local machine — they run
top-to-bottom in Colab Enterprise using the runtime's ambient (Application Default) credentials.

**To reproduce a notebook challenge:**
1. Open the notebook in Colab Enterprise in a project with the relevant APIs enabled
   (Vertex AI, BigQuery, Discovery Engine / AI Applications, Model Armor, DLP as applicable).
2. Update the `PROJECT_ID` (and region constants) in the **Configuration** cell to your project.
3. Run all cells top-to-bottom.

> The `PROJECT_ID` values committed in the notebooks point at the Qwiklabs project I used
> during the workshop (`qwiklabs-gcp-04-a13cec945fb9`). Swap in your own project ID to re-run.
> Each challenge's README calls out any environment notes that affect reproduction (e.g. the
> Qwiklabs DLP API restriction in Challenge 1).

---

## Cross-challenge notes

- **Models:** `gemini-2.5-flash` for generation across challenges; `text-embedding-005` for
  BigQuery embeddings (Challenge 2).
- **Regions:** Vertex AI in `us-central1`; Model Armor templates in `us-east4`; the Cloud Run
  service in `us-east4`; BigQuery in the `US` multi-region.
- **Honest environment caveats** (DLP org policy in Challenge 1; benign import errors in
  Challenge 5) are documented inline in the notebooks and the per-challenge READMEs rather than
  hidden, so the run outputs match what a grader will see in this Qwiklabs-style environment.
