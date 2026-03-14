"""
Phase 2: Structured Data Extraction via Groq API (FREE)
Converts raw page text into structured JSON observations per area/section.
Uses LLaMA 3 via Groq - completely free.
"""

import json
import os
import re
from groq import Groq

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"  # Current Groq model (free, fast, high quality)

# ── Prompts ───────────────────────────────────────────────────────────────────

INSPECTION_EXTRACTION_PROMPT = """You are a building inspection data analyst.

Extract ALL observations from the following inspection report text.
For each distinct area or issue mentioned, produce a JSON object.

Return ONLY a valid JSON array (no markdown, no explanation, no extra text) with this structure:
[
  {{
    "area_name": "string (e.g. Roof, Basement, Kitchen)",
    "observations": ["list of specific observations as strings"],
    "defect_types": ["crack", "leak", "moisture", etc.],
    "severity_hint": "critical | high | medium | low | unknown",
    "measurements": ["any numeric readings, dimensions, percentages"],
    "notes": "any additional context"
  }}
]

Rules:
- Extract every area and issue mentioned, even briefly
- If area name is unclear, use "General" or the closest descriptor
- severity_hint should reflect language used (e.g. "severe" means critical)
- If a field has no data, use null or []
- Do NOT invent data not present in the text
- Return ONLY the JSON array, nothing else

Text to analyse:
---
{text}
---"""


THERMAL_EXTRACTION_PROMPT = """You are a thermal imaging inspection analyst.

Extract ALL thermal findings from the following thermal report text.
For each area or anomaly, produce a JSON object.

Return ONLY a valid JSON array (no markdown, no explanation, no extra text) with this structure:
[
  {{
    "area_name": "string (e.g. Roof, East Wall, Window Frame)",
    "temperature_readings": {{
      "min_celsius": null,
      "max_celsius": null,
      "ambient_celsius": null,
      "delta": null
    }},
    "thermal_anomalies": ["list of anomalies described"],
    "probable_cause_hint": "moisture | heat loss | electrical | structural | unknown",
    "severity_hint": "critical | high | medium | low | unknown",
    "notes": "any additional context"
  }}
]

Rules:
- Extract every area and thermal finding mentioned
- If temperature units are Fahrenheit, record them and note the unit in notes
- If a field has no data, use null or []
- Do NOT invent data not present in the text
- Return ONLY the JSON array, nothing else

Text to analyse:
---
{text}
---"""


# ── Core extraction function ──────────────────────────────────────────────────

def extract_structured_data(text: str, prompt_template: str, label: str) -> list[dict]:
    """
    Send text to Groq LLaMA3 and parse the returned JSON array.
    Returns list of structured observation dicts.
    """
    if not text.strip():
        return []

    prompt = prompt_template.format(text=text)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise building inspection analyst. Always respond with valid JSON only. No markdown, no explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent structured output
            max_tokens=4096,
        )

        raw = response.choices[0].message.content.strip()

        # Strip any accidental markdown fences
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()

        # Find JSON array in response
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            parsed = [parsed]

        print(f"  [{label}] Extracted {len(parsed)} observation block(s)")
        return parsed

    except json.JSONDecodeError as e:
        print(f"  [{label}] JSON parse error: {e}")
        print(f"  Raw response snippet: {raw[:300]}")
        return []
    except Exception as e:
        print(f"  [{label}] Groq API error: {e}")
        return []


# ── Page chunking ─────────────────────────────────────────────────────────────

def chunk_pages(pages: list[dict], max_chars: int = 5000) -> list[str]:
    """
    Group pages into chunks within max_chars limit.
    Groq has context limits so we keep chunks smaller.
    """
    chunks = []
    current_chunk = ""

    for page in pages:
        page_text = f"\n[PAGE {page['page_number']}]\n{page['text']}\n"
        if len(current_chunk) + len(page_text) > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = page_text
        else:
            current_chunk += page_text

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# ── Main extraction for each document ────────────────────────────────────────

def extract_inspection_observations(inspection_data: dict) -> list[dict]:
    """Run extraction over all pages of the inspection document."""
    print("\n[Phase 2] Extracting inspection observations via Groq...")
    chunks = chunk_pages(inspection_data["pages"])
    all_observations = []

    for i, chunk in enumerate(chunks):
        print(f"  Processing chunk {i+1}/{len(chunks)}...")
        obs = extract_structured_data(chunk, INSPECTION_EXTRACTION_PROMPT, "Inspection")
        all_observations.extend(obs)

    return all_observations


def extract_thermal_observations(thermal_data: dict) -> list[dict]:
    """Run extraction over all pages of the thermal document."""
    print("\n[Phase 2] Extracting thermal observations via Groq...")
    chunks = chunk_pages(thermal_data["pages"])
    all_findings = []

    for i, chunk in enumerate(chunks):
        print(f"  Processing chunk {i+1}/{len(chunks)}...")
        findings = extract_structured_data(chunk, THERMAL_EXTRACTION_PROMPT, "Thermal")
        all_findings.extend(findings)

    return all_findings


def run_phase2(inspection_data: dict, thermal_data: dict, output_dir: str = "ddr_workspace") -> tuple[list, list]:
    """Full Phase 2 run. Returns (inspection_observations, thermal_findings)."""
    insp_obs = extract_inspection_observations(inspection_data)
    therm_findings = extract_thermal_observations(thermal_data)

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "extracted_inspection_obs.json"), "w") as f:
        json.dump(insp_obs, f, indent=2)
    with open(os.path.join(output_dir, "extracted_thermal_obs.json"), "w") as f:
        json.dump(therm_findings, f, indent=2)

    print(f"\n[Phase 2] Done. Inspection blocks: {len(insp_obs)} | Thermal blocks: {len(therm_findings)}")
    return insp_obs, therm_findings