# DDR Report Generator — Groq Version (FREE)

Generate a professional Detailed Diagnostic Report (DDR) from inspection + thermal PDFs.
Uses **Groq + LLaMA3-70B** — completely free.

---

## Quick Start

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Set your FREE Groq API key

Get a free key at: https://console.groq.com

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY="gsk_your-key-here"
```

**Mac/Linux:**
```bash
export GROQ_API_KEY=gsk_your-key-here
```

### Step 3 — Run

**Command Line:**
```bash
python main.py inspection.pdf thermal.pdf --property-name "Your Site Name"
```

**Web UI:**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

---

## Project Structure

```
ddr_pipeline_groq/
├── main.py                     # CLI entry point
├── app.py                      # Streamlit web UI
├── phase1_parser.py            # PDF text + image extraction
├── phase2_extractor.py         # Groq LLaMA3 structured extraction
├── phase3_merger.py            # Area merging + conflict detection
├── phase4_image_associator.py  # Heuristic image-to-area linking
├── phase5_generator.py         # Groq LLaMA3 DDR text generation
├── phase6_assembler.py         # ReportLab PDF assembly
└── requirements.txt
```

---

## Differences from Anthropic Version

| Feature | Anthropic Version | Groq Version (This) |
|---------|------------------|---------------------|
| API Cost | Paid (~$0.10/report) | FREE |
| LLM Model | Claude Sonnet | LLaMA3-70B |
| Image Classification | Claude Vision | Heuristic matching |
| Speed | Fast | Very Fast |
| Quality | Highest | Very Good |

---

## Output Files

After running, your output folder contains:
```
ddr_output/
├── DDR_Report.pdf              ← Final report (share this)
├── ddr_report_text.md          ← Raw markdown
├── merged_data_with_images.json
├── extracted_inspection_obs.json
├── extracted_thermal_obs.json
└── extracted_images/           ← Images from PDFs
```
