"""
Phase 3: Data Merging, Deduplication & Conflict Detection
Combines inspection + thermal observations by area name using fuzzy matching.
"""

import json
import os
from difflib import SequenceMatcher


# ── Fuzzy area name matching ──────────────────────────────────────────────────

def normalize_area(name: str) -> str:
    """Lowercase, strip, remove common filler words for better matching."""
    if not name:
        return "general"
    name = name.lower().strip()
    for word in ["the", "area", "zone", "section", "room", "floor"]:
        name = name.replace(word, "").strip()
    return " ".join(name.split())  # collapse whitespace


def similarity_score(a: str, b: str) -> float:
    """0.0 to 1.0 string similarity score."""
    return SequenceMatcher(None, normalize_area(a), normalize_area(b)).ratio()


def find_best_thermal_match(area_name: str, thermal_findings: list[dict], threshold: float = 0.6) -> dict | None:
    """
    Find the thermal finding whose area_name most closely matches the inspection area.
    Returns the match dict or None if no good match found.
    """
    best_score = 0.0
    best_match = None

    for finding in thermal_findings:
        score = similarity_score(area_name, finding.get("area_name", ""))
        if score > best_score:
            best_score = score
            best_match = finding

    if best_score >= threshold:
        return best_match
    return None


# ── Conflict detection ────────────────────────────────────────────────────────

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}


def detect_conflicts(insp_obs: dict, therm_finding: dict) -> list[str]:
    """
    Compare an inspection observation with a thermal finding and report conflicts.
    Returns a list of conflict descriptions (empty = no conflicts).
    """
    conflicts = []

    insp_sev = insp_obs.get("severity_hint", "unknown")
    therm_sev = therm_finding.get("severity_hint", "unknown")

    insp_rank = SEVERITY_ORDER.get(insp_sev, 0)
    therm_rank = SEVERITY_ORDER.get(therm_sev, 0)

    # Severity gap of 2+ levels = conflict worth flagging
    if abs(insp_rank - therm_rank) >= 2:
        conflicts.append(
            f"Severity mismatch: Inspection rated '{insp_sev}' but thermal analysis rated '{therm_sev}'"
        )

    # Probable cause vs defect type check
    therm_cause = therm_finding.get("probable_cause_hint", "")
    insp_defects = [d.lower() for d in insp_obs.get("defect_types", [])]

    # e.g. thermal says electrical but inspection says moisture
    CAUSE_DEFECT_MAP = {
        "electrical": ["electrical", "wiring", "short"],
        "moisture": ["moisture", "leak", "water", "damp"],
        "structural": ["crack", "settlement", "structural"],
        "heat loss": ["insulation", "draft", "gap"],
    }

    if therm_cause in CAUSE_DEFECT_MAP:
        expected_keywords = CAUSE_DEFECT_MAP[therm_cause]
        found = any(kw in " ".join(insp_defects) for kw in expected_keywords)
        if not found and insp_defects:
            conflicts.append(
                f"Cause mismatch: Thermal suggests '{therm_cause}' but inspection defect types are {insp_defects}"
            )

    return conflicts


# ── Deduplication within inspection/thermal separately ────────────────────────

def deduplicate_observations(obs_list: list[dict]) -> list[dict]:
    """
    Merge duplicate area entries (same area appearing across multiple pages).
    Combines their observations lists and picks worst severity.
    """
    merged: dict[str, dict] = {}

    for obs in obs_list:
        key = normalize_area(obs.get("area_name", "general"))
        if key not in merged:
            merged[key] = {
                "area_name": obs.get("area_name", "General"),
                "observations": list(obs.get("observations") or []),
                "defect_types": list(obs.get("defect_types") or []),
                "severity_hint": obs.get("severity_hint", "unknown"),
                "measurements": list(obs.get("measurements") or []),
                "notes": obs.get("notes", ""),
                "temperature_readings": obs.get("temperature_readings"),
                "thermal_anomalies": list(obs.get("thermal_anomalies") or []),
                "probable_cause_hint": obs.get("probable_cause_hint", ""),
            }
        else:
            existing = merged[key]
            # Merge lists, avoid exact duplicates
            for item in (obs.get("observations") or []):
                if item not in existing["observations"]:
                    existing["observations"].append(item)
            for item in (obs.get("defect_types") or []):
                if item not in existing["defect_types"]:
                    existing["defect_types"].append(item)
            for item in (obs.get("measurements") or []):
                if item not in existing["measurements"]:
                    existing["measurements"].append(item)
            for item in (obs.get("thermal_anomalies") or []):
                if item not in existing["thermal_anomalies"]:
                    existing["thermal_anomalies"].append(item)

            # Take worst severity
            old_rank = SEVERITY_ORDER.get(existing["severity_hint"], 0)
            new_rank = SEVERITY_ORDER.get(obs.get("severity_hint", "unknown"), 0)
            if new_rank > old_rank:
                existing["severity_hint"] = obs["severity_hint"]

            # Append notes
            if obs.get("notes"):
                existing["notes"] = (existing["notes"] + " | " + obs["notes"]).strip(" | ")

    return list(merged.values())


# ── Main merge function ───────────────────────────────────────────────────────

def merge_documents(
    inspection_obs: list[dict],
    thermal_findings: list[dict]
) -> list[dict]:
    """
    Merge inspection observations with thermal findings area by area.
    Returns a unified list of merged area records.
    """
    print("\n[Phase 3] Deduplicating and merging...")

    # Step 1: Deduplicate within each document
    insp_deduped = deduplicate_observations(inspection_obs)
    therm_deduped = deduplicate_observations(thermal_findings)
    print(f"  Inspection areas (deduped): {len(insp_deduped)}")
    print(f"  Thermal areas (deduped): {len(therm_deduped)}")

    # Step 2: Track which thermal findings were matched
    matched_thermal_keys = set()
    merged_records = []

    for obs in insp_deduped:
        thermal_match = find_best_thermal_match(obs["area_name"], therm_deduped)
        conflicts = []

        if thermal_match:
            matched_thermal_keys.add(normalize_area(thermal_match.get("area_name", "")))
            conflicts = detect_conflicts(obs, thermal_match)

        record = {
            "area_name": obs["area_name"],
            "inspection": {
                "observations": obs.get("observations", []),
                "defect_types": obs.get("defect_types", []),
                "severity_hint": obs.get("severity_hint", "unknown"),
                "measurements": obs.get("measurements", []),
                "notes": obs.get("notes", "")
            },
            "thermal": None,
            "conflicts": conflicts,
            "images": []  # filled in Phase 4
        }

        if thermal_match:
            record["thermal"] = {
                "temperature_readings": thermal_match.get("temperature_readings"),
                "thermal_anomalies": thermal_match.get("thermal_anomalies", []),
                "probable_cause_hint": thermal_match.get("probable_cause_hint", "unknown"),
                "severity_hint": thermal_match.get("severity_hint", "unknown"),
                "notes": thermal_match.get("notes", "")
            }

        merged_records.append(record)

    # Step 3: Add unmatched thermal findings as standalone records
    for finding in therm_deduped:
        key = normalize_area(finding.get("area_name", ""))
        if key not in matched_thermal_keys:
            merged_records.append({
                "area_name": finding["area_name"],
                "inspection": None,
                "thermal": {
                    "temperature_readings": finding.get("temperature_readings"),
                    "thermal_anomalies": finding.get("thermal_anomalies", []),
                    "probable_cause_hint": finding.get("probable_cause_hint", "unknown"),
                    "severity_hint": finding.get("severity_hint", "unknown"),
                    "notes": finding.get("notes", "")
                },
                "conflicts": [],
                "images": []
            })

    print(f"  Final merged area records: {len(merged_records)}")
    return merged_records


def run_phase3(
    inspection_obs: list[dict],
    thermal_findings: list[dict],
    output_dir: str = "ddr_workspace"
) -> list[dict]:
    """Full Phase 3 run."""
    merged = merge_documents(inspection_obs, thermal_findings)

    with open(os.path.join(output_dir, "merged_data.json"), "w") as f:
        json.dump(merged, f, indent=2)

    conflicts_found = sum(1 for r in merged if r.get("conflicts"))
    print(f"[Phase 3] Done. Areas with conflicts: {conflicts_found}")
    return merged
