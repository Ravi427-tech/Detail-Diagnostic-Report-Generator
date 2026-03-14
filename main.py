"""
DDR Pipeline — Main Orchestrator (Groq Version - FREE)
Uses Groq + LLaMA3-70B instead of Anthropic Claude.

Usage:
    python main.py <inspection.pdf> <thermal.pdf> [--output-dir ddr_output] [--property-name "Site Name"]

Setup:
    pip install -r requirements.txt
    
Windows PowerShell:
    $env:GROQ_API_KEY="your-groq-key-here"

Mac/Linux:
    export GROQ_API_KEY=your-groq-key-here
"""

import argparse
import os
import sys
import time

from phase1_parser import parse_both_documents
from phase2_extractor import run_phase2
from phase3_merger import run_phase3
from phase4_image_associator import run_phase4
from phase5_generator import run_phase5
from phase6_assembler import run_phase6


def validate_inputs(inspection_pdf: str, thermal_pdf: str):
    for path, label in [(inspection_pdf, "Inspection"), (thermal_pdf, "Thermal")]:
        if not os.path.exists(path):
            print(f"[Error] {label} PDF not found: {path}")
            sys.exit(1)


def check_api_key():
    if not os.environ.get("GROQ_API_KEY"):
        print("[Error] GROQ_API_KEY environment variable is not set.")
        print()
        print("  Windows PowerShell:")
        print('    $env:GROQ_API_KEY="your-groq-key-here"')
        print()
        print("  Mac/Linux:")
        print("    export GROQ_API_KEY=your-groq-key-here")
        print()
        print("  Get a free key at: https://console.groq.com")
        sys.exit(1)


def run_pipeline(
    inspection_pdf: str,
    thermal_pdf: str,
    output_dir: str = "ddr_output",
    property_name: str = "Site Inspection"
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()

    print("=" * 60)
    print("  DDR REPORT GENERATION PIPELINE  (Groq - Free)")
    print("=" * 60)
    print(f"  Inspection : {inspection_pdf}")
    print(f"  Thermal    : {thermal_pdf}")
    print(f"  Model      : LLaMA3-70B via Groq")
    print(f"  Output dir : {output_dir}")
    print("=" * 60)

    print("\n▶ PHASE 1: Parsing Documents")
    inspection_data, thermal_data = parse_both_documents(
        inspection_pdf, thermal_pdf, output_dir
    )

    print("\n▶ PHASE 2: Extracting Structured Observations (Groq)")
    inspection_obs, thermal_findings = run_phase2(
        inspection_data, thermal_data, output_dir
    )

    print("\n▶ PHASE 3: Merging & Deduplication")
    merged_records = run_phase3(inspection_obs, thermal_findings, output_dir)

    print("\n▶ PHASE 4: Associating Images to Areas")
    merged_records = run_phase4(
        merged_records, inspection_data, thermal_data, output_dir
    )

    print("\n▶ PHASE 5: Generating DDR Report Text (Groq)")
    report_text, sections = run_phase5(merged_records, output_dir)

    print("\n▶ PHASE 6: Assembling Final PDF Report")
    pdf_path = run_phase6(merged_records, sections, output_dir, property_name)

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"  PIPELINE COMPLETE in {elapsed:.1f}s")
    print(f"  Report: {os.path.abspath(pdf_path)}")
    print("=" * 60)

    return pdf_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a DDR Report from inspection + thermal PDFs using Groq (Free)"
    )
    parser.add_argument("inspection_pdf", help="Path to the Inspection Report PDF")
    parser.add_argument("thermal_pdf", help="Path to the Thermal Report PDF")
    parser.add_argument("--output-dir", default="ddr_output",
                        help="Output directory (default: ddr_output)")
    parser.add_argument("--property-name", default="Site Inspection",
                        help="Property name for the report cover page")

    args = parser.parse_args()

    check_api_key()
    validate_inputs(args.inspection_pdf, args.thermal_pdf)

    run_pipeline(
        inspection_pdf=args.inspection_pdf,
        thermal_pdf=args.thermal_pdf,
        output_dir=args.output_dir,
        property_name=args.property_name
    )
