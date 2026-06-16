# ADS Online Agent — Deployable Cloud Run app

This folder is the deployable web app for Challenge 5: the Alaska Department of Snow (ADS)
virtual assistant. It's a small Flask app (`app.py`) that serves a chat UI and runs the full
RAG + weather + Model Armor pipeline, packaged with a `Dockerfile` and `requirements.txt`.

## Files

| File | Purpose |
|---|---|
| `app.py` | Flask app: chat UI (`/`), chat API (`/chat`), health check (`/health`), and the agent pipeline |
| `Dockerfile` | Container image definition (Python 3.12 slim, runs `app.py` on `$PORT`) |
| `requirements.txt` | Python dependencies |

## Deploy to Cloud Run

The easiest way to run this is straight from **Cloud Shell**:

1. Open the **Cloud Shell Editor** in the Google Cloud console.
2. Copy this entire `ads-agent` folder into your home directory (so it lives at `~/ads-agent`).
3. Deploy from source — Cloud Run builds the container for you (via Cloud Build / Artifact
   Registry), no manual `docker build` needed:

   ```bash
   cd ~/ads-agent
   gcloud run deploy alaska-dept-of-snow \
     --source . \
     --region us-east4 \
     --allow-unauthenticated \
     --project qwiklabs-gcp-04-a13cec945fb9
   ```

   > Swap in your own `--project` if you're not using the workshop Qwiklabs project.

4. When the deploy finishes, `gcloud` prints the **Service URL** (e.g.
   `https://alaska-dept-of-snow-<hash>-uc.a.run.app`). Open it in a browser to use the agent.

## Prerequisites

The deploying account/project needs these APIs enabled and the Cloud Run runtime service
account needs access to them:

- **Vertex AI** (`aiplatform.googleapis.com`) — Gemini generation, in `us-central1`
- **Vertex AI Search / Discovery Engine** (`discoveryengine.googleapis.com`) — the
  `alaska-dept-of-snow` data store must already exist and be indexed (created in
  `../challenge-5-timothy-kempster.ipynb`)
- **Model Armor** (`modelarmor.googleapis.com`) — the app creates its prompt/response
  templates on startup if they don't exist; it **fails open** if Model Armor is unavailable
- **Cloud Run**, **Cloud Build**, and **Artifact Registry** for `--source` deploys

The app reads its project from Application Default Credentials, so no keys or env vars are
required when running on Cloud Run. The only configuration constants (data store ID, regions,
model) are at the top of `app.py`.

## Local sanity check (optional)

```bash
cd ~/ads-agent
pip install -r requirements.txt
python app.py          # serves on http://localhost:8080
```

Running locally still calls the live Google Cloud services, so you must be authenticated
(`gcloud auth application-default login`) and have the data store already created.
