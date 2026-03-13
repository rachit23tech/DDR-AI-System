import os
from typing import Dict, Any
import json

# If a .env file is present in this project, load it automatically.
# This ensures keys (e.g., GEMINI_API_KEY) are available even if the env isn't set globally.
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)
except ImportError:
    pass

# provider selection (openai or gemini)
# if AI_PROVIDER is not set, prefer GEMINI if its key exists.
PROVIDER = os.getenv("AI_PROVIDER")
if not PROVIDER:
    PROVIDER = "gemini" if os.getenv("GEMINI_API_KEY") else "openai"
PROVIDER = PROVIDER.lower()


def initialize_client():
    """Read appropriate API key and return it.
    For OpenAI this function also configures the library.
    """
    if PROVIDER == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")
        return key
    else:
        # default to OpenAI
        import openai
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = key
        return key


def generate_ddr_report(extracted: Dict[str, Any]) -> Dict[str, str]:
    """Call LLM to generate structured DDR report from extracted data."""
    key = initialize_client()
    inspection_text = extracted.get("inspection_text", "")
    thermal_text = extracted.get("thermal_text", "")
    images = extracted.get("images", [])

    prompt = f"""
You are an expert assistant that composes a Detailed Diagnostic Report (DDR) based on two input documents: an Inspection Report and a Thermal Report.

Inspection Observations:
{inspection_text}

Thermal Observations:
{thermal_text}

Images:
{', '.join(images) if images else 'No images available'}

Create a structured report with the following sections:
1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment (with reasoning)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

Rules:
- Do not invent information.
- If information is missing, write \"Not Available\".
- If information conflicts, mention the conflict.
- Use clear, client-friendly language.

Provide the output as JSON with keys exactly:
"property_issue_summary", "area_wise_observations", "root_cause", "severity", "recommended_actions", "additional_notes", "missing_information".
"""

    if PROVIDER == "gemini":
        # call Gemini REST API directly
        import requests
        url = "https://api.gemini.ai/v1/completions"
        payload = {
            "model": os.getenv("GEMINI_MODEL", "gemini-1.5"),
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        text = resp.json().get("choices", [{}])[0].get("text", "").strip()
    else:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )
        text = response.choices[0].message.content.strip()

    # assume text is JSON
    try:
        return json.loads(text)
    except Exception:
        # fallback: return entire text under a key
        return {"raw": text}
