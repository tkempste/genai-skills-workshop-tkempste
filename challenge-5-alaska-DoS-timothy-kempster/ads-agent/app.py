import os
import logging
import requests
import google.auth

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from flask import Flask, request, jsonify, render_template_string

# ── CONFIG ───────────────────────────────────────────────────────
credentials, PROJECT_ID = google.auth.default()

LOCATION      = "global"
DATA_STORE_ID = "alaska-dept-of-snow"
GEMINI_MODEL  = "gemini-2.5-flash"
GEMINI_REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=GEMINI_REGION)
model = GenerativeModel(GEMINI_MODEL)

# ── LOGGING ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ADS-Agent")


def log_step(step: str, detail: str = ""):
    msg = f"{step}" + (f": {detail}" if detail else "")
    logger.info(msg)

# ── MODEL ARMOR ──────────────────────────────────────────────────
MODEL_ARMOR_ENDPOINT = "modelarmor.us-east4.rep.googleapis.com"
PROMPT_TEMPLATE      = f"projects/{PROJECT_ID}/locations/us-east4/templates/coding-it-prompt-template"
RESPONSE_TEMPLATE    = f"projects/{PROJECT_ID}/locations/us-east4/templates/coding-it-response-template"

try:
    from google.cloud import modelarmor_v1
    model_armor_client = modelarmor_v1.ModelArmorClient(
        client_options=ClientOptions(api_endpoint=MODEL_ARMOR_ENDPOINT)
    )
    MODEL_ARMOR_AVAILABLE = True
    log_step("Model Armor", "Client initialized successfully")
except Exception as e:
    MODEL_ARMOR_AVAILABLE = False
    log_step("Model Armor", f"Unavailable — running fail-open ({e})")


def setup_model_armor_templates():
    """
    Create Model Armor prompt and response templates if they don't already exist.
    Called once at startup — safe to run repeatedly (AlreadyExists is swallowed).
    """
    if not MODEL_ARMOR_AVAILABLE:
        log_step("Model Armor setup", "Skipped — client unavailable")
        return

    from google.api_core.exceptions import AlreadyExists

    parent = f"projects/{PROJECT_ID}/locations/us-east4"

    # ── Prompt template: PI / jailbreak filter ────────────────────
    try:
        prompt_template = modelarmor_v1.Template(
            filter_config=modelarmor_v1.FilterConfig(
                pi_and_jailbreak_filter_settings=modelarmor_v1.PiAndJailbreakFilterSettings(
                    filter_enforcement=modelarmor_v1.PiAndJailbreakFilterSettings.PiAndJailbreakFilterEnforcement.ENABLED,
                    confidence_level=modelarmor_v1.DetectionConfidenceLevel.MEDIUM_AND_ABOVE,
                ),
            )
        )
        model_armor_client.create_template(
            parent=parent,
            template=prompt_template,
            template_id="coding-it-prompt-template",
        )
        log_step("Model Armor setup", "Prompt template created: coding-it-prompt-template")
    except AlreadyExists:
        log_step("Model Armor setup", "Prompt template already exists — skipping")
    except Exception as e:
        log_step("Model Armor setup", f"Prompt template creation failed — continuing ({e})")

    # ── Response template: SDP sensitive data filter ──────────────
    try:
        response_template = modelarmor_v1.Template(
            filter_config=modelarmor_v1.FilterConfig(
                sdp_settings=modelarmor_v1.SdpFilterSettings(
                    basic_config=modelarmor_v1.SdpBasicConfig(
                        filter_enforcement=modelarmor_v1.SdpBasicConfig.SdpBasicConfigEnforcement.ENABLED,
                    ),
                ),
            )
        )
        model_armor_client.create_template(
            parent=parent,
            template=response_template,
            template_id="coding-it-response-template",
        )
        log_step("Model Armor setup", "Response template created: coding-it-response-template")
    except AlreadyExists:
        log_step("Model Armor setup", "Response template already exists — skipping")
    except Exception as e:
        log_step("Model Armor setup", f"Response template creation failed — continuing ({e})")


# Run template setup at import / startup time
setup_model_armor_templates()


def check_prompt(user_text: str) -> tuple:
    if not MODEL_ARMOR_AVAILABLE:
        log_step("Model Armor (prompt check)", "SKIPPED — unavailable")
        return True, "ok"
    try:
        request_obj = modelarmor_v1.SanitizeUserPromptRequest(
            name=PROMPT_TEMPLATE,
            user_prompt_data=modelarmor_v1.DataItem(text=user_text),
        )
        response = model_armor_client.sanitize_user_prompt(request=request_obj)
        result = response.sanitization_result
        if result.filter_match_state == modelarmor_v1.FilterMatchState.NO_MATCH_FOUND:
            log_step("Model Armor (prompt check)", "PASSED")
            return True, "ok"
        log_step("Model Armor (prompt check)", "BLOCKED")
        return False, "Blocked by Model Armor prompt filter"
    except Exception as e:
        log_step("Model Armor (prompt check)", f"ERROR — fail-open ({e})")
        return True, "ok"


def check_response(response_text: str) -> tuple:
    if not MODEL_ARMOR_AVAILABLE:
        log_step("Model Armor (response check)", "SKIPPED — unavailable")
        return True, response_text
    try:
        request_obj = modelarmor_v1.SanitizeModelResponseRequest(
            name=RESPONSE_TEMPLATE,
            model_response_data=modelarmor_v1.DataItem(text=response_text),
        )
        response = model_armor_client.sanitize_model_response(request=request_obj)
        result = response.sanitization_result
        if result.filter_match_state == modelarmor_v1.FilterMatchState.NO_MATCH_FOUND:
            log_step("Model Armor (response check)", "PASSED")
            return True, response_text
        log_step("Model Armor (response check)", "BLOCKED")
        return False, "I'm unable to provide that response."
    except Exception as e:
        log_step("Model Armor (response check)", f"ERROR — fail-open ({e})")
        return True, response_text


# ── RAG SEARCH ───────────────────────────────────────────────────
def search_data_store(query: str, num_results: int = 5) -> dict:
    client = discoveryengine.SearchServiceClient()
    serving_config = (
        f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"
        f"/dataStores/{DATA_STORE_ID}/servingConfigs/default_config"
    )
    req = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=num_results,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True,
                max_snippet_count=3,
            ),
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=num_results,
                include_citations=True,
                ignore_adversarial_query=True,
                ignore_non_summary_seeking_query=False,
            ),
        ),
    )
    response = client.search(req)

    rag_summary = ""
    if response.summary and response.summary.summary_text:
        rag_summary = response.summary.summary_text

    documents = []
    for result in response.results:
        doc = result.document
        snippets = []
        title = "Unknown"
        if doc.derived_struct_data:
            for s in doc.derived_struct_data.get("snippets", []):
                if s.get("snippet"):
                    snippets.append(s["snippet"])
            title = doc.derived_struct_data.get("title", "Unknown")
        documents.append({"id": doc.id, "title": title, "snippets": snippets})

    return {"rag_summary": rag_summary, "documents": documents}


# ── WEATHER API ──────────────────────────────────────────────────
ALASKA_CITIES = {
    "fairbanks":  (64.8378, -147.7164),
    "anchorage":  (61.2181, -149.9003),
    "juneau":     (58.3005, -134.4197),
    "wasilla":    (61.5814, -149.4411),
    "palmer":     (61.5994, -149.1129),
    "kodiak":     (57.7900, -152.4072),
    "homer":      (59.6425, -151.5483),
    "kenai":      (60.5544, -151.2583),
    "sitka":      (57.0531, -135.3300),
    "ketchikan":  (55.3422, -131.6461),
    "bethel":     (60.7922, -161.7558),
    "nome":       (64.5011, -165.4064),
    "utqiagvik":  (71.2906, -156.7887),
    "barrow":     (71.2906, -156.7887),
    "valdez":     (61.1308, -146.3483),
    "soldotna":   (60.4878, -151.0569),
}

WEATHER_KEYWORDS = [
    "weather", "snow", "forecast", "temperature", "storm", "blizzard",
    "wind", "conditions", "roads", "plowing", "closure", "alert",
    "warning", "ice", "visibility", "freezing",
]


def is_weather_question(text: str) -> bool:
    return any(kw in text.lower() for kw in WEATHER_KEYWORDS)


def extract_city(text: str):
    text_lower = text.lower()
    for city in ALASKA_CITIES:
        if city in text_lower:
            return city
    return None


def get_weather_for_question(question: str):
    if not is_weather_question(question):
        return None
    city = extract_city(question) or "fairbanks"
    try:
        lat, lon = ALASKA_CITIES[city]
        headers = {"User-Agent": "ADS-Chatbot/1.0 (alaska-dept-of-snow@alaska.gov)"}
        points = requests.get(
            f"https://api.weather.gov/points/{lat},{lon}",
            headers=headers, timeout=10
        ).json()
        forecast_url = points["properties"]["forecast"]
        periods = requests.get(
            forecast_url, headers=headers, timeout=10
        ).json()["properties"]["periods"][:3]
        lines = [f"Current NWS weather for {city.title()}, AK:"]
        for p in periods:
            lines.append(
                f"\n{p['name']}: {p['temperature']}°{p['temperatureUnit']}, "
                f"Wind: {p['windSpeed']} {p['windDirection']}"
            )
            lines.append(p["detailedForecast"])
        return "\n".join(lines)
    except Exception:
        return f"Weather data temporarily unavailable for {city.title()}, AK."


# ── AGENT ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are the Alaska Department of Snow (ADS) virtual assistant.
Your job is to help Alaska residents with questions about snow removal, road conditions,
school closures, and ADS services.

Rules:
1. Only answer questions related to the Alaska Department of Snow and its services.
2. Use information from the provided context when available.
3. If weather data is provided, incorporate it into your answer.
4. If you don't know something, say so — do not make up information.
5. Keep responses concise, clear, and helpful for Alaska residents."""


def ask_ads_agent(user_message: str) -> str:
    log_step("User asked question", user_message)

    passed, reason = check_prompt(user_message)
    if not passed:
        log_step("Result", "BLOCKED by Model Armor")
        return f"I'm unable to process that request. {reason}"

    weather_context = ""
    if is_weather_question(user_message):
        log_step("Weather API", "Calling NWS...")
        weather_context = get_weather_for_question(user_message) or ""
        log_step("Weather API", "Data retrieved" if weather_context else "No data returned")
    else:
        log_step("Weather API", "Not a weather question — skipping")

    log_step("RAG search", "Querying ADS data store...")
    try:
        rag_results = search_data_store(user_message, num_results=3)
        log_step("RAG search", f"{len(rag_results['documents'])} documents retrieved")
        if rag_results["rag_summary"]:
            rag_context = rag_results["rag_summary"]
            log_step("RAG search", "Using grounded summary")
        else:
            rag_context = ""
            for i, doc in enumerate(rag_results["documents"], 1):
                snippets = " ".join(doc.get("snippets", []))
                if snippets:
                    rag_context += f"\nDocument {i} — {doc['title']}:\n{snippets}\n"
            log_step("RAG search", "Using raw document snippets")
    except Exception as e:
        log_step("RAG search", f"ERROR ({e}) — continuing without context")
        rag_context = ""

    prompt_parts = [SYSTEM_PROMPT]
    if rag_context:
        prompt_parts.append(f"\nRelevant ADS Information:\n{rag_context}")
    if weather_context:
        prompt_parts.append(f"\nCurrent NWS Weather Data:\n{weather_context}")
    prompt_parts.append(f"\nCitizen Question: {user_message}\nResponse:")

    log_step("Gemini", "Generating response...")
    try:
        gemini_response = model.generate_content("\n".join(prompt_parts))
        response_text = gemini_response.text.strip()
        log_step("Gemini", "Response generated successfully")
    except Exception as e:
        log_step("Gemini", f"ERROR: {e}")
        return "I'm sorry, I encountered an error. Please try again."

    passed, final_response = check_response(response_text)
    if not passed:
        log_step("Result", "Response BLOCKED by Model Armor")
        return final_response

    log_step("Result", "Response delivered to user")
    return final_response


# ── FLASK APP ────────────────────────────────────────────────────
app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Alaska Department of Snow — Virtual Assistant</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f0f4f8;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
    }
    header {
      width: 100%;
      background: #1a3a5c;
      color: white;
      padding: 16px 24px;
    }
    header h1 { font-size: 1.2rem; font-weight: 600; }
    header p  { font-size: 0.85rem; opacity: 0.8; margin-top: 2px; }
    #chat-container {
      width: 100%;
      max-width: 760px;
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 24px 16px;
      gap: 12px;
    }
    #messages {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
      max-height: 65vh;
    }
    .message {
      max-width: 80%;
      padding: 12px 16px;
      border-radius: 12px;
      line-height: 1.5;
      font-size: 0.95rem;
      white-space: pre-wrap;
    }
    .message.user {
      align-self: flex-end;
      background: #1a3a5c;
      color: white;
      border-bottom-right-radius: 4px;
    }
    .message.agent {
      align-self: flex-start;
      background: white;
      color: #1a1a1a;
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .message.thinking { color: #888; font-style: italic; }
    #input-row { display: flex; gap: 8px; margin-top: 8px; }
    #user-input {
      flex: 1;
      padding: 12px 16px;
      border: 1px solid #ccd6e0;
      border-radius: 24px;
      font-size: 0.95rem;
      outline: none;
    }
    #user-input:focus { border-color: #1a3a5c; }
    #send-btn {
      padding: 12px 24px;
      background: #1a3a5c;
      color: white;
      border: none;
      border-radius: 24px;
      font-size: 0.95rem;
      cursor: pointer;
    }
    #send-btn:hover    { background: #254f7a; }
    #send-btn:disabled { background: #aaa; cursor: not-allowed; }
  </style>
</head>
<body>
<header>
  <h1>❄️ Alaska Department of Snow — Virtual Assistant</h1>
  <p>Ask about snow removal, road conditions, school closures, and ADS services</p>
</header>
<div id="chat-container">
  <div id="messages">
    <div class="message agent">Hello! I'm the Alaska Department of Snow virtual assistant. I can help you with questions about snow removal schedules, road conditions, school closures, and other ADS services. How can I help you today?</div>
  </div>
  <div id="input-row">
    <input id="user-input" type="text" placeholder="Ask a question about ADS services..." autocomplete="off"/>
    <button id="send-btn">Send</button>
  </div>
</div>
<script>
  const messagesEl = document.getElementById("messages");
  const inputEl    = document.getElementById("user-input");
  const sendBtn    = document.getElementById("send-btn");

  function addMessage(text, role) {
    const div = document.createElement("div");
    div.className = "message " + role;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    sendBtn.disabled = true;
    addMessage(text, "user");
    const thinking = addMessage("Thinking...", "agent thinking");
    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      thinking.remove();
      addMessage(data.response || data.error, "agent");
    } catch (err) {
      thinking.remove();
      addMessage("Sorry, something went wrong. Please try again.", "agent");
    } finally {
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  inputEl.addEventListener("keydown", e => { if (e.key === "Enter") sendMessage(); });
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = (data or {}).get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    response = ask_ads_agent(user_message)
    return jsonify({"response": response})


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)