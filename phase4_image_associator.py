"""
Phase 4: Image Association (Groq Version)
Links extracted images to area records using filename + page context.
Note: Groq's LLaMA3 does not support vision/image input,
so we use smart filename + page-number heuristics instead.
"""

import json
import os
from difflib import SequenceMatcher


def normalize(text: str) -> str:
    return text.lower().strip()


def filename_area_score(filename: str, area_name: str) -> float:
    """Score how likely a filename belongs to an area based on keyword overlap."""
    fname = normalize(filename)
    area = normalize(area_name)
    area_words = area.split()
    matches = sum(1 for word in area_words if word in fname and len(word) > 3)
    return matches / max(len(area_words), 1)


def page_proximity_score(img_page: int, area_pages: list[int]) -> float:
    """Score based on how close the image page is to known area pages."""
    if not area_pages:
        return 0.0
    min_dist = min(abs(img_page - p) for p in area_pages)
    if min_dist == 0:
        return 1.0
    elif min_dist == 1:
        return 0.6
    elif min_dist == 2:
        return 0.3
    return 0.0


def classify_image_by_source(source: str, image_type_hint: str = "") -> str:
    """Classify image type based on its source document."""
    if source == "thermal":
        return "thermal_scan"
    elif source == "inspection":
        return "photo"
    return "other"


def associate_images_to_areas(
    merged_records: list[dict],
    all_images: list[dict],
    output_dir: str = "ddr_workspace"
) -> list[dict]:
    """
    Associate images to area records using:
    1. Filename keyword matching against area names
    2. Source document (thermal images → thermal areas)
    3. Page proximity heuristic
    """
    # Ensure every record has an images list
    for record in merged_records:
        if "images" not in record or record["images"] is None:
            record["images"] = []

    if not all_images:
        print("\n[Phase 4] No images to associate.")
        return merged_records

    if not merged_records:
        print("\n[Phase 4] No area records found — skipping image association.")
        return merged_records

    print(f"\n[Phase 4] Associating {len(all_images)} image(s) to {len(merged_records)} area(s)...")
    print("  (Using heuristic matching — Groq does not support image input)")

    # Split images by source
    thermal_images = [img for img in all_images if img.get("source") == "thermal"]
    inspection_images = [img for img in all_images if img.get("source") == "inspection"]

    def assign_image(img: dict, preferred_source: str):
        """Assign a single image to the best matching area record."""
        fname = os.path.basename(img.get("file_path", ""))
        img_page = img.get("page_number", 0)
        source = img.get("source", "")

        best_score = -1.0
        best_idx = 0  # Default to first area

        for i, record in enumerate(merged_records):
            area_name = record.get("area_name", "")

            # Score 1: filename keyword match
            f_score = filename_area_score(fname, area_name)

            # Score 2: source preference
            s_score = 0.0
            if source == "thermal" and record.get("thermal"):
                s_score = 0.4
            elif source == "inspection" and record.get("inspection"):
                s_score = 0.4

            total = f_score + s_score
            if total > best_score:
                best_score = total
                best_idx = i

        # Safety check — should never fail but guards against empty list edge case
        if best_idx >= len(merged_records):
            best_idx = 0

        image_entry = {
            "file_path": img.get("file_path", ""),
            "source": source,
            "page_number": img_page,
            "image_type": classify_image_by_source(source),
            "description": f"{source.title()} image from page {img_page}",
            "confidence": "medium" if best_score > 0.3 else "low"
        }

        # Ensure images list exists before appending
        if "images" not in merged_records[best_idx]:
            merged_records[best_idx]["images"] = []

        merged_records[best_idx]["images"].append(image_entry)
        print(f"  -> {fname} assigned to '{merged_records[best_idx]['area_name']}' (score={best_score:.2f})")

    # Assign thermal images first (more specific)
    for img in thermal_images:
        try:
            assign_image(img, "thermal")
        except Exception as e:
            print(f"  [Warning] Could not assign thermal image: {e}")

    # Then inspection images
    for img in inspection_images:
        try:
            assign_image(img, "inspection")
        except Exception as e:
            print(f"  [Warning] Could not assign inspection image: {e}")

    # Save updated merged data
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "merged_data_with_images.json"), "w") as f:
        json.dump(merged_records, f, indent=2)

    total_associated = sum(len(r.get("images", [])) for r in merged_records)
    print(f"[Phase 4] Done. Total images associated: {total_associated}")
    return merged_records


def run_phase4(
    merged_records: list[dict],
    inspection_data: dict,
    thermal_data: dict,
    output_dir: str = "ddr_workspace"
) -> list[dict]:
    """Full Phase 4 run."""
    all_images = inspection_data.get("images", []) + thermal_data.get("images", [])
    return associate_images_to_areas(merged_records, all_images, output_dir)