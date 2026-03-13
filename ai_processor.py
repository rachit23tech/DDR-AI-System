import os
import json
from typing import Dict, Any

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Choose provider (default = groq)
PROVIDER = os.getenv("AI_PROVIDER", "groq").lower()


def initialize_client():
    """Initialize the AI client depending on provider."""
    if PROVIDER == "groq":
        from groq import Groq

        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set")

        return Groq(api_key=key)

    elif PROVIDER == "openai":
        import openai

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")

        openai.api_key = key
        return openai

    else:
        raise RuntimeError(f"Unsupported AI_PROVIDER: {PROVIDER}")


def generate_ddr_report(extracted: Dict[str, Any]) -> Dict[str, str]:
    """Generate DDR report using an LLM."""

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
- If information is missing, write "Not Available".
- If information conflicts, mention the conflict.
- Use clear, client-friendly language.

Return STRICT JSON with these keys:

property_issue_summary  
area_wise_observations  
root_cause  
severity  
recommended_actions  
additional_notes  
missing_information
"""

    # GROQ
    if PROVIDER == "groq":
        client = initialize_client()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You generate structured diagnostic reports."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
        )

        text = response.choices[0].message.content.strip()

    # OPENAI
    elif PROVIDER == "openai":
        openai = initialize_client()

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You generate structured diagnostic reports."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1000,
        )

        text = response.choices[0].message.content.strip()

    # Parse JSON safely
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}