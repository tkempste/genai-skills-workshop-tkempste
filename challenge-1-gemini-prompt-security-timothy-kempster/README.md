# Challenge 1 — Gemini Prompt Security (20 pts)

**Goal (slides):** Demonstrate how to program a secure and safe generative AI system.

**Artifact:** [`challenge-1-gemini-prompt-security-Timothy-Kempster.ipynb`](./challenge-1-gemini-prompt-security-Timothy-Kempster.ipynb)

A `SecureChatSession` "CodingBot" assistant runs every turn through a 4-layer pipeline.

## Requirement traceability

| Requirement | Where it's met |
|---|---|
| Python chat app using the latest Gemini | `SecureChatSession` on `gemini-2.5-flash` |
| System instructions with goals **and** restrictions | `SYSTEM_INSTRUCTION` (goals + explicit "must NEVER" list) |
| Prompt filtering to validate user input (Model Armor) | `sanitize_user_prompt()` → Model Armor PI/jailbreak template |
| Gemini safety filters | `SAFETY_SETTINGS` (`BLOCK_LOW_AND_ABOVE` on all 4 harm categories) |
| Validate model responses; only return safe responses | `sanitize_model_response()` + finish-reason/safety-rating checks |
| **Bonus:** Model Armor + Sensitive Data Protection for response filtering | `redact_sensitive_data()` (Cloud DLP) + response Model Armor template |

## Demonstrated tests in the notebook

Normal coding question (passes), prompt injection / DAN jailbreak (blocked), out-of-scope
question (declined by system instruction), malicious-code request (blocked), multi-turn
context, and an interactive session with several attack attempts.

## How to run

Open the notebook in Colab Enterprise, set `PROJECT_ID` / region constants in the
**Configuration** cell, and run all cells top-to-bottom. Requires Vertex AI, Model Armor, and
(for the bonus) DLP / Sensitive Data Protection enabled.

## Environment note

In the Qwiklabs project the DLP (Sensitive Data Protection) API call returned `SERVICE_DISABLED`
at the org level despite project-level enablement, so the DLP layer **fails open** (documented
in the notebook's Summary). The Model Armor and Gemini safety layers (steps 1–3) fail closed
and are fully functional in the run outputs.
