"""
================================================================================
  material_audit.py — UE5 Material Audit Tool
================================================================================
  Author  : LAZARUS-inq
  GitHub  : https://github.com/LAZARUS-inq
  Version : 1.0.0

  HOW TO RUN
  ----------
  Inside Unreal Engine 5 Editor:
    Tools → Execute Python Script → select this file

  DESCRIPTION
  -----------
  A pipeline utility that scans all Material and MaterialInstance assets in a
  UE5 project and produces a detailed audit report. Designed to catch common
  asset hygiene issues before they reach production.

  CHECKS PERFORMED
  ----------------
  - Broken textures   : Material expressions or Instance parameters that
                        reference a missing or null texture asset
  - Empty materials   : Materials with no texture samples connected at all
  - Naming violations : Assets that do not follow the M_ / MI_ prefix
                        convention; suggested correct names are included
  - Duplicates        : Multiple assets sharing the same name across
                        different content folders

  SETTINGS
  --------
  SCAN_PATH    Path to scan (default: entire project "/Game").
               Narrow to "/Game/Materials" to speed up large projects.
  REPORT_PATH  Folder where the JSON report will be saved.
               Created automatically if it does not exist.
  FIX_NAMING   Set to True to automatically rename naming violations
               using EditorAssetLibrary. Set to False for report-only mode.
================================================================================
"""

import unreal
import json
import os
import re
from datetime import datetime
from collections import defaultdict

# ─── Settings ─────────────────────────────────────────────────────────────────

SCAN_PATH   = "/Game"           # Root scan path; narrow to "/Game/Materials" for speed
REPORT_PATH = "C:/UE5_Reports"  # Output folder for JSON report; created if missing
FIX_NAMING  = False             # True = auto-rename naming violations; False = report only

# Naming convention: Materials must start with "M_", Instances with "MI_"
MATERIAL_PREFIX  = "M_"
INSTANCE_PREFIX  = "MI_"


EXCLUDE_EMPTY_CHECK = ["M_Hologram", "M_Dissolve", "M_Rain", "M_Water", "M_Particle"]

# ─── Logging helpers ───────────────────────────────────────────────────────────

def log(msg: str) -> None:
    unreal.log(f"[MaterialAudit] {msg}")

def log_warning(msg: str) -> None:
    unreal.log_warning(f"[MaterialAudit] {msg}")

def log_error(msg: str) -> None:
    unreal.log_error(f"[MaterialAudit] {msg}")

# ─── Asset discovery ──────────────────────────────────────────────────────────

def get_all_materials(scan_path: str) -> dict:
    """
    Returns a dict:
      {
        "materials": [list of UE asset_data for Material],
        "instances": [list of UE asset_data for MaterialInstanceConstant]
      }
    """
    registry = unreal.AssetRegistryHelpers.get_asset_registry()

    ar_filter = unreal.ARFilter(
        package_paths=[scan_path],
        recursive_paths=True,
        class_names=["Material", "MaterialInstanceConstant"]
    )

    all_assets = registry.get_assets(ar_filter)

    materials = []
    instances = []

    for asset_data in all_assets:
        cls = str(asset_data.asset_class_path.asset_name)
        if cls == "Material":
            materials.append(asset_data)
        elif cls == "MaterialInstanceConstant":
            instances.append(asset_data)

    log(f"Found: {len(materials)} Material, {len(instances)} MaterialInstance")
    return {"materials": materials, "instances": instances}

# ─── Texture reference checks ─────────────────────────────────────────────────

def check_texture_references(asset_data) -> dict:
    """
    Loads the asset and checks all texture parameters/expressions.
    Returns:
      {
        "broken": [list of parameter names with missing texture references],
        "empty":  True/False — no texture samples connected at all
      }
    """
    broken = []
    has_any_texture = False

    try:
        asset = unreal.EditorAssetLibrary.load_asset(str(asset_data.package_name))
    except Exception as e:
        log_error(f"Failed to load {asset_data.asset_name}: {e}")
        return {"broken": ["LOAD_FAILED"], "empty": True}

    if isinstance(asset, unreal.MaterialInstanceConstant):
        # Check texture parameters on the instance
        try:
            params = unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)
            for param in params:
                tex = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(
                    asset, param
                )
                if tex is None:
                    broken.append(str(param))
                else:
                    has_any_texture = True
        except Exception:
            pass

        # Check parent material reference
        parent = asset.get_editor_property("parent")
        if parent is None:
            broken.append("MISSING_PARENT")

    elif isinstance(asset, unreal.Material):
        # Method 1: named texture parameters via MaterialEditingLibrary
        try:
            param_names = unreal.MaterialEditingLibrary.get_texture_parameter_names(asset)
            for param in param_names:
                tex = unreal.MaterialEditingLibrary.get_material_default_texture_parameter_value(
                    asset, param
                )
                if tex is None:
                    broken.append(str(param))
                else:
                    has_any_texture = True
        except Exception:
            pass

        # Method 2: get_used_textures catches non-parameter TextureSample nodes
        if not has_any_texture:
            try:
                used = unreal.MaterialEditingLibrary.get_used_textures(asset)
                if used:
                    has_any_texture = True
            except Exception:
                pass

    return {"broken": broken, "empty": not has_any_texture}

# ─── Naming convention check ──────────────────────────────────────────────────

def check_naming(asset_data, expected_prefix: str) -> dict:
    """
    Validates the asset name against the expected prefix convention.
    Returns:
      {
        "ok":        True/False,
        "name":      current asset name,
        "suggested": corrected name
      }
    """
    name = str(asset_data.asset_name)
    ok = name.startswith(expected_prefix)

    suggested = name
    if not ok:
        # Strip any existing known prefix before adding the correct one
        clean = re.sub(r"^(MI_|M_|T_|SM_|MF_|MPC_)", "", name)
        suggested = expected_prefix + clean

    return {"ok": ok, "name": name, "suggested": suggested}

# ─── Duplicate detection ──────────────────────────────────────────────────────

def find_duplicates(assets: list) -> dict:
    """
    Finds assets sharing the same name regardless of folder path.
    Returns: {name: [list of full asset paths]}
    """
    name_map = defaultdict(list)
    for asset_data in assets:
        name = str(asset_data.asset_name)
        name_map[name].append(str(asset_data.package_name))

    return {name: paths for name, paths in name_map.items() if len(paths) > 1}

# ─── Auto-fix naming ──────────────────────────────────────────────────────────

def fix_naming(asset_data, suggested_name: str) -> bool:
    """
    Renames an asset to match the naming convention.
    Returns True on success.
    """
    old_path     = str(asset_data.package_name)
    package_path = old_path.rsplit("/", 1)[0]
    new_path     = f"{package_path}/{suggested_name}"

    try:
        result = unreal.EditorAssetLibrary.rename_asset(old_path, new_path)
        if result:
            log(f"Renamed: {asset_data.asset_name} -> {suggested_name}")
        else:
            log_warning(f"Failed to rename: {asset_data.asset_name}")
        return result
    except Exception as e:
        log_error(f"Error renaming {asset_data.asset_name}: {e}")
        return False

# ─── Main audit ───────────────────────────────────────────────────────────────

def run_audit(scan_path: str, fix_naming_flag: bool) -> dict:
    log("=" * 60)
    log(f"Starting Material Audit: {scan_path}")
    log("=" * 60)

    start_time = datetime.now()
    all_assets = get_all_materials(scan_path)

    report = {
        "meta": {
            "timestamp":   start_time.isoformat(),
            "scan_path":   scan_path,
            "fix_naming":  fix_naming_flag,
        },
        "summary": {},
        "broken_textures":   [],
        "empty_materials":   [],
        "naming_violations": [],
        "duplicates":        [],
        "fixed":             [],
    }

    # ── Duplicates ────────────────────────────────────────────────────────────
    all_combined = all_assets["materials"] + all_assets["instances"]
    duplicates = find_duplicates(all_combined)

    for name, paths in duplicates.items():
        report["duplicates"].append({"name": name, "paths": paths})
        log_warning(f"Duplicate: {name} ({len(paths)} copies)")

    # ── Scan Material ─────────────────────────────────────────────────────────
    for asset_data in all_assets["materials"]:
        name = str(asset_data.asset_name)

        # Naming
        naming = check_naming(asset_data, MATERIAL_PREFIX)
        if not naming["ok"]:
            entry = {
                "name":      naming["name"],
                "path":      str(asset_data.package_name),
                "suggested": naming["suggested"],
                "type":      "Material",
            }
            report["naming_violations"].append(entry)
            log_warning(f"Naming violation: {name} -> suggested {naming['suggested']}")

            if fix_naming_flag:
                ok = fix_naming(asset_data, naming["suggested"])
                if ok:
                    report["fixed"].append({"old": name, "new": naming["suggested"]})

        # Textures
        tex = check_texture_references(asset_data)
        if tex["broken"]:
            report["broken_textures"].append({
                "name":   name,
                "path":   str(asset_data.package_name),
                "type":   "Material",
                "params": tex["broken"],
            })
            log_error(f"Broken textures in {name}: {tex['broken']}")

        if tex["empty"]:
            report["empty_materials"].append({
                "name": name,
                "path": str(asset_data.package_name),
                "type": "Material",
            })
            log_warning(f"Material has no textures: {name}")

    # ── Scan MaterialInstance ─────────────────────────────────────────────────
    for asset_data in all_assets["instances"]:
        name = str(asset_data.asset_name)

        # Naming
        naming = check_naming(asset_data, INSTANCE_PREFIX)
        if not naming["ok"]:
            entry = {
                "name":      naming["name"],
                "path":      str(asset_data.package_name),
                "suggested": naming["suggested"],
                "type":      "MaterialInstance",
            }
            report["naming_violations"].append(entry)
            log_warning(f"Naming violation: {name} -> suggested {naming['suggested']}")

            if fix_naming_flag:
                ok = fix_naming(asset_data, naming["suggested"])
                if ok:
                    report["fixed"].append({"old": name, "new": naming["suggested"]})

        # Textures
        tex = check_texture_references(asset_data)
        if tex["broken"]:
            report["broken_textures"].append({
                "name":   name,
                "path":   str(asset_data.package_name),
                "type":   "MaterialInstance",
                "params": tex["broken"],
            })
            log_error(f"Broken textures in {name}: {tex['broken']}")

    # ── Summary ───────────────────────────────────────────────────────────────
    duration = (datetime.now() - start_time).total_seconds()

    report["summary"] = {
        "total_materials":     len(all_assets["materials"]),
        "total_instances":     len(all_assets["instances"]),
        "broken_textures":     len(report["broken_textures"]),
        "empty_materials":     len(report["empty_materials"]),
        "naming_violations":   len(report["naming_violations"]),
        "duplicate_groups":    len(report["duplicates"]),
        "fixed":               len(report["fixed"]),
        "scan_duration_sec":   round(duration, 2),
    }

    return report

# ─── Save report ──────────────────────────────────────────────────────────────

def save_report(report: dict, report_path: str) -> str:
    os.makedirs(report_path, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"material_audit_{timestamp}.json"
    filepath  = os.path.join(report_path, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    log(f"Report saved: {filepath}")
    return filepath

# ─── Print summary to Output Log ──────────────────────────────────────────────

def print_summary(report: dict) -> None:
    s = report["summary"]
    log("")
    log("╔══════════════════════════════════════════╗")
    log("║         MATERIAL AUDIT — RESULTS          ║")
    log("╠══════════════════════════════════════════╣")
    log(f"║  Materials scanned         : {s['total_materials']:<13}║")
    log(f"║  MaterialInstances scanned : {s['total_instances']:<13}║")
    log(f"║  Broken textures           : {s['broken_textures']:<13}║")
    log(f"║  Empty materials           : {s['empty_materials']:<13}║")
    log(f"║  Naming violations         : {s['naming_violations']:<13}║")
    log(f"║  Duplicate groups          : {s['duplicate_groups']:<13}║")
    log(f"║  Fixed (naming)            : {s['fixed']:<13}║")
    log(f"║  Scan duration             : {s['scan_duration_sec']:.2f}s          ║")
    log("╚══════════════════════════════════════════╝")

# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    report    = run_audit(SCAN_PATH, FIX_NAMING)
    filepath  = save_report(report, REPORT_PATH)
    print_summary(report)

    log("")
    log(f"Done! Report saved to: {filepath}")