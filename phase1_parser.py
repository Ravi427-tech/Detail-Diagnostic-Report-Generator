"""
Phase 1: Document Ingestion & Parsing
Extracts text (page-by-page) and images from PDF files.
Works with pdfplumber (text) + pypdfium2 (images).
"""

import os
import json
import pdfplumber
import pypdfium2 as pdfium
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from each page of a PDF.
    Returns a list of dicts: {page_number, text}
    """
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []

            # Flatten any tables into readable text
            table_text = ""
            for table in tables:
                for row in table:
                    if row:
                        table_text += " | ".join(
                            str(cell) if cell else "" for cell in row
                        ) + "\n"

            combined = text.strip()
            if table_text:
                combined += "\n[TABLE DATA]\n" + table_text.strip()

            pages.append({
                "page_number": i + 1,
                "text": combined
            })
    return pages


def extract_images_from_pdf(pdf_path: str, output_dir: str, source_tag: str) -> list[dict]:
    """
    Extract images from a PDF using pypdfium2.
    Renders each page as an image (compatible with all pypdfium2 versions).
    Returns: [{page_number, image_index, file_path, source}]
    """
    os.makedirs(output_dir, exist_ok=True)
    image_records = []

    try:
        pdf = pdfium.PdfDocument(pdf_path)
        for page_idx in range(len(pdf)):
            try:
                page = pdf[page_idx]

                # Try object-level extraction first (newer pypdfium2)
                extracted = False
                try:
                    for obj_idx, obj in enumerate(page.get_objects()):
                        # type == 1 means image object in pdfium
                        obj_type = getattr(obj, 'type', None)
                        is_image = False

                        if obj_type is not None:
                            # Handle both int and enum forms
                            try:
                                is_image = (int(obj_type) == 1)
                            except Exception:
                                is_image = str(obj_type).upper() in ("IMAGE", "1")

                        if is_image:
                            try:
                                bitmap = obj.get_bitmap()
                                pil_image = bitmap.to_pil()
                                filename = f"{source_tag}_page{page_idx+1}_img{obj_idx}.png"
                                filepath = os.path.join(output_dir, filename)
                                pil_image.save(filepath)
                                image_records.append({
                                    "page_number": page_idx + 1,
                                    "image_index": obj_idx,
                                    "file_path": filepath,
                                    "source": source_tag
                                })
                                extracted = True
                            except Exception as e:
                                print(f"  [Warning] Could not extract obj image p{page_idx+1}: {e}")
                except Exception:
                    pass  # Fall through to page-render fallback

                # Fallback: render entire page as image if no objects extracted
                # Only render pages that likely have images (skip text-only pages)
                if not extracted:
                    try:
                        bitmap = page.render(scale=1.5)
                        pil_image = bitmap.to_pil()
                        # Only save if page has meaningful image content
                        # (skip nearly-blank pages to avoid saving text-only pages)
                        pixels = list(pil_image.convert("L").getdata())
                        unique = len(set(pixels))
                        if unique > 50:  # More than 50 unique grey values = likely has images
                            filename = f"{source_tag}_page{page_idx+1}_render.png"
                            filepath = os.path.join(output_dir, filename)
                            pil_image.save(filepath)
                            image_records.append({
                                "page_number": page_idx + 1,
                                "image_index": 0,
                                "file_path": filepath,
                                "source": source_tag
                            })
                    except Exception as e:
                        print(f"  [Warning] Could not render page {page_idx+1}: {e}")

            except Exception as e:
                print(f"  [Warning] Skipping page {page_idx+1}: {e}")

        pdf.close()

    except Exception as e:
        print(f"  [Warning] pypdfium2 could not open {pdf_path}: {e}")

    return image_records


def parse_document(pdf_path: str, source_tag: str, image_output_dir: str) -> dict:
    """
    Full parse of one document. Returns:
    {
        source: str,
        pages: [{page_number, text}],
        images: [{page_number, image_index, file_path, source}]
    }
    """
    print(f"\n[Parser] Processing: {pdf_path} (tag={source_tag})")
    pages = extract_text_from_pdf(pdf_path)
    print(f"  → Extracted text from {len(pages)} pages")

    images = extract_images_from_pdf(pdf_path, image_output_dir, source_tag)
    print(f"  → Extracted {len(images)} images")

    return {
        "source": source_tag,
        "pages": pages,
        "images": images
    }


def parse_both_documents(
    inspection_pdf: str,
    thermal_pdf: str,
    output_dir: str = "ddr_workspace"
) -> tuple[dict, dict]:
    """
    Parse both the inspection and thermal PDFs.
    Returns (inspection_data, thermal_data)
    """
    image_dir = os.path.join(output_dir, "extracted_images")
    os.makedirs(image_dir, exist_ok=True)

    inspection_data = parse_document(inspection_pdf, "inspection", image_dir)
    thermal_data = parse_document(thermal_pdf, "thermal", image_dir)

    # Save raw parse results for debugging
    with open(os.path.join(output_dir, "parsed_inspection.json"), "w") as f:
        json.dump(inspection_data, f, indent=2)
    with open(os.path.join(output_dir, "parsed_thermal.json"), "w") as f:
        json.dump(thermal_data, f, indent=2)

    print(f"\n[Parser] Raw parse results saved to {output_dir}/")
    return inspection_data, thermal_data


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python phase1_parser.py <inspection.pdf> <thermal.pdf>")
        sys.exit(1)

    insp, therm = parse_both_documents(sys.argv[1], sys.argv[2])
    print("\n[Done] Inspection pages:", len(insp["pages"]),
          "| Thermal pages:", len(therm["pages"]))
    print("Images found:", len(insp["images"]) + len(therm["images"]))