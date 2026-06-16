# Challenge 4 — Building Agents with AI Applications (bonus, 10 pts)

**Goal (slides):** Use Google AI Applications to create a Conversational Agent that uses a
Playbook and a Data Store to answer user questions.

Because this challenge is built in the Google Cloud console, the proof is a set of screenshots
plus the exported agent configuration.

> **Full step-by-step write-up with every screenshot:** [`proof.md`](./proof.md)

## Requirement traceability

| Requirement | Where it's met |
|---|---|
| Create a conversational agent using AI Applications | "Aurora Bay Agent" (Conversational Agents / Gemini Enterprise) — [`Screenshot1.png`](./Screenshot1.png) |
| Create an AI Applications data store | Data store sourced from `gs://labs.roitraining.com/aurora-bay-faqs` (100 docs) — [`datastore.png`](./datastore.png), [`image.png`](./image.png) |
| Playbook with goal, instructions, and data store | Default Generative Playbook configured for agent "Alice" — [`screenshot-desc-goals.png`](./screenshot-desc-goals.png); FAQ-lookup example — [`example-run.png`](./example-run.png) |
| Export the agent as JSON | [`exported_agent_Aurora Bay Agent.zip`](./exported_agent_Aurora%20Bay%20Agent.zip) — contains `agent.json`, `playbooks/`, `tools/Data Store/`, `intents/`, `flows/` |

## Folder contents

| File | What it shows |
|---|---|
| `proof.md` | Full narrative with all screenshots |
| `Screenshot1.png` | Aurora Bay Agent created |
| `screenshot-desc-goals.png` | Playbook goal + instructions |
| `datastore.png`, `image.png` | Data store creation and linkage |
| `example-run.png` | FAQ-lookup example invoking the data store tool |
| `exported_agent_Aurora Bay Agent.zip` | Exported agent configuration (JSON) |
