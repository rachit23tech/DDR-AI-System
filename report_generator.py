import os
from groq import Groq
from typing import Dict, Any

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def create_report(extracted: Dict[str, Any]) -> Dict[str, Any]:

    inspection_text = extracted.get("inspection_text", "")
    thermal_text = extracted.get("thermal_text", "")

    prompt = f"""
You are an AI system generating a Detailed Diagnostic Report (DDR).

Use the following data:

Inspection Report:
{inspection_text}

Thermal Report:
{thermal_text}

Generate the report in JSON format using this structure:

{{
  "property_issue_summary": "",
  "area_wise_observations": [
      {{
        "area": "",
        "observations": "",
        "related_images": []
      }}
  ],
  "probable_root_cause": "",
  "severity_assessment": "",
  "recommended_actions": "",
  "additional_notes": "",
  "missing_or_unclear_information": ""
}}

Rules:
- Do NOT invent information
- If data is missing write "Not Available"
- Avoid duplicate observations
- Use simple client-friendly language
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You generate structured building inspection reports."},
            {"role": "user", "content": prompt}
        ]
    )

    report = response.choices[0].message.content

    return {
    "report": report,
    "images": extracted.get("images", [])
}