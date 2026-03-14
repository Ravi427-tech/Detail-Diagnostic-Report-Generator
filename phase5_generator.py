"""
Phase 5: DDR Report Text Generation via Groq API (FREE)
Generates all 7 DDR sections from merged structured data.
Uses LLaMA 3 70B via Groq.
"""

import json
import os
import re
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"  # Current Groq model (free, fast, high quality)


DDR_SYSTEM_PROMPT = """You are a professional building diagnostics report writer.
You write clear, client-friendly Detailed Diagnostic Reports (DDR).
You follow instructions precisely and never invent facts."""


DDR_GENERATION_PROMPT = """Write a Detailed Diagnostic Report (DDR) from the structured inspection data below.

STRICT RULES:
1. Do NOT invent any facts not present in the data
2. If information is missing write exactly: Not Available
3. If there is a data conflict, clearly state both findings and flag it
4. Use simple professional language, avoid heavy jargon
5. Be concise but thorough

Generate the DDR with these exact 7 sections using these exact headers:

## 1. Property Issue Summary
A short executive paragraph (3-5 sentences) summarising overall condition, most critical issues, and number of areas affected.

## 2. Area-wise Observations
For EACH area write:
**[Area Name]**
- Inspection Findings: (bullet list of what was physically observed)
- Thermal Findings: (temperature readings and anomalies, or Not Available)
- Conflicts Noted: (if any conflicts exist describe them, otherwise omit this line)

## 3. Probable Root Cause
For each area with issues, state the most likely root cause in 1-2 sentences. If uncertain say so. Group by area.

## 4. Severity Assessment
Present assessment for each area:
| Area | Severity | Reasoning |
Include reasoning referencing both inspection and thermal evidence where available.
State overall property severity at the bottom.

## 5. Recommended Actions
Group as:
- **Immediate (Critical/High):** actions within days
- **Short-term (Medium):** actions within weeks or months
- **Long-term (Low):** monitoring or preventive measures

## 6. Additional Notes
Any important context, access limitations, conditions during inspection, or remarks.

## 7. Missing or Unclear Information
List every piece of information absent or ambiguous. If nothing is missing write: All required data was available.

STRUCTURED DATA:
{merged_json}"""


def generate_ddr_text(merged_records: list[dict]) -> str:
    """Call Groq LLaMA3 to generate the full DDR report text."""
    print("\n[Phase 5] Generating DDR report text via Groq (LLaMA3-70B)...")

    # Clean data — remove internal image paths for the prompt
    clean_data = []
    for record in merged_records:
        clean_data.append({
            "area_name": record["area_name"],
            "inspection": record.get("inspection"),
            "thermal": record.get("thermal"),
            "conflicts": record.get("conflicts", []),
            "has_images": len(record.get("images", [])) > 0,
            "image_count": len(record.get("images", []))
        })

    # Split into chunks if data is large (Groq has token limits)
    data_str = json.dumps(clean_data, indent=2)

    # If data is very large, summarize per area
    if len(data_str) > 10000:
        print("  [Note] Large dataset - processing in sections...")
        return generate_ddr_chunked(clean_data)

    prompt = DDR_GENERATION_PROMPT.format(merged_json=data_str)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": DDR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    report_text = response.choices[0].message.content.strip()
    print(f"  Generated report: {len(report_text)} characters")
    return report_text


def generate_ddr_chunked(clean_data: list[dict]) -> str:
    """
    For large datasets, generate each section separately and combine.
    This avoids hitting Groq token limits.
    """
    data_str = json.dumps(clean_data, indent=2)
    sections = []

    section_prompts = [
        ("## 1. Property Issue Summary",
         f"Write section 1 (Property Issue Summary) only. 3-5 sentences summarising overall condition.\nData: {data_str}"),

        ("## 2. Area-wise Observations",
         f"Write section 2 (Area-wise Observations) only. For EACH area list inspection and thermal findings as bullets.\nData: {data_str}"),

        ("## 3. Probable Root Cause",
         f"Write section 3 (Probable Root Cause) only. For each area state the likely root cause in 1-2 sentences.\nData: {data_str}"),

        ("## 4. Severity Assessment",
         f"Write section 4 (Severity Assessment) only. Include a markdown table with Area, Severity, Reasoning columns.\nData: {data_str}"),

        ("## 5. Recommended Actions",
         f"Write section 5 (Recommended Actions) only. Group as Immediate, Short-term, Long-term.\nData: {data_str}"),

        ("## 6. Additional Notes",
         f"Write section 6 (Additional Notes) only. Include any relevant context not covered above.\nData: {data_str}"),

        ("## 7. Missing or Unclear Information",
         f"Write section 7 (Missing or Unclear Information) only. List missing or ambiguous data. If nothing is missing write 'All required data was available.'\nData: {data_str}"),
    ]

    for header, prompt in section_prompts:
        print(f"  Generating {header}...")
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": DDR_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
            )
            content = response.choices[0].message.content.strip()
            # Ensure section header is present
            if not content.startswith("##"):
                content = f"{header}\n{content}"
            sections.append(content)
        except Exception as e:
            print(f"  [Warning] Failed to generate {header}: {e}")
            sections.append(f"{header}\nNot Available")

    return "\n\n".join(sections)


def parse_report_sections(report_text: str) -> dict[str, str]:
    """Split the generated report into named sections."""
    section_names = [
        "1. Property Issue Summary",
        "2. Area-wise Observations",
        "3. Probable Root Cause",
        "4. Severity Assessment",
        "5. Recommended Actions",
        "6. Additional Notes",
        "7. Missing or Unclear Information"
    ]

    sections = {}
    current_section = None
    current_content = []

    for line in report_text.split("\n"):
        matched = False
        for name in section_names:
            if re.search(re.escape(name), line, re.IGNORECASE):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = name
                current_content = []
                matched = True
                break
        if not matched and current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def run_phase5(
    merged_records: list[dict],
    output_dir: str = "ddr_workspace"
) -> tuple[str, dict]:
    """Full Phase 5 run. Returns (full_report_text, sections_dict)."""
    report_text = generate_ddr_text(merged_records)
    sections = parse_report_sections(report_text)

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "ddr_report_text.md"), "w") as f:
        f.write(report_text)
    with open(os.path.join(output_dir, "ddr_sections.json"), "w") as f:
        json.dump(sections, f, indent=2)

    print(f"[Phase 5] Done. Sections parsed: {len(sections)}")
    return report_text, sections