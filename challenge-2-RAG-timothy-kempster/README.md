# Challenge 2 — Programming a RAG System in BigQuery (20 pts)

**Goal (slides):** Demonstrate a RAG system that uses BigQuery to generate embeddings and
perform a vector search.

**Artifact:** [`challenge-2-RAG-timothy-kempster.ipynb`](./challenge-2-RAG-timothy-kempster.ipynb)

## Requirement traceability

| Requirement | Where it's met |
|---|---|
| Load the Aurora Bay FAQ data into a BigQuery table | Step 1 — load `gs://labs.roitraining.com/aurora-bay-faqs/aurora-bay-faqs.csv` (50 rows) |
| Create embeddings for each record, stored in BigQuery | Steps 2–5 — Cloud Resource connection → `text-embedding-005` remote model → `ML.GENERATE_EMBEDDING` into `aurora_bay_faqs_embedded` |
| Chatbot that searches the embeddings to answer accurately | Step 6 `search_faqs()` (`VECTOR_SEARCH`) + Step 7 `ask_aurora_bay()` (Gemini, grounded) |
| Coded in Python and well-documented | Markdown per step + docstrings; Summary table at the end |

## Demonstrated tests in the notebook

In-corpus question (accurate), out-of-corpus question (declines instead of hallucinating), raw
retrieval inspection with cosine distances, and a multi-turn chat.

## How to run

Open the notebook in Colab Enterprise, set `PROJECT_ID` / region constants in the
**Configuration** cell, and run all cells top-to-bottom. Requires Vertex AI and BigQuery
(including the BigQuery Connection API) enabled.
