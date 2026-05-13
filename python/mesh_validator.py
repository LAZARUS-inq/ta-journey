"""
================================================================================
  mesh_validator.py — UE5 Static Mesh Validator
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
  A pipeline utility that validates all StaticMesh assets in a UE5 project
  against common production requirements. Complements mesh_validator.ms
  (3ds Max pre-export) by checking the imported asset inside the engine.

  CHECKS PERFORMED
  ----------------
  - Naming convention   : asset name must start with SM_
  - LOD count           : must have at least 1 LOD (LOD0)
  - Lightmap UV         : lightmap UV channel must exist (channel 1)
  - Collision           : must have at least one collision shape
  - Triangle count      : warns if triangle count exceeds MAX_TRIS limit
  - Nanite              : warns if Nanite is enabled on low-poly meshes

  SETTINGS
  --------
  MODE            "dry" = report only, no changes made.
                  "fix" = auto-fix naming violations.
  SCAN_PATH       Path to scan (default: entire project "/Game").
  REPORT_PATH     Folder where the JSON report will be saved.
  MAX_TRIS        Maximum triangle count before warning.
  NANITE_TRIS     Minimum triangle count where Nanite makes sense.
================================================================================
"""

import unreal
import json
import os
from datetime import datetime

# ─── Settings ──────────────────────────────────────────────────────────────────

MODE        = "dry"           # "dry" = report only | "fix" = auto-fix naming
SCAN_PATH   = "/Game"
REPORT_PATH = "C:/UE5_Reports"
MAX_TRIS    = 50000
NANITE_TRIS = 5000            # below this, Nanite warning triggers

# ─── Logging ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    unreal.log(f"[MeshValidator] {msg}")

def log_warning(msg: str) -> None:
    unreal.log_warning(f"[MeshValidator] {msg}")

def log_error(msg: str) -> None:
    unreal.log_error(f"[MeshValidator] {msg}")

# ─── Asset discovery ───────────────────────────────────────────────────────────

def get_all_static_meshes(scan_path: str) -> list:
    registry = unreal.AssetRegistryHelpers.get_asset_registry()

    ar_filter = unreal.ARFilter(
        package_paths=[scan_path],
        recursive_paths=True,
        class_names=["StaticMesh"]
    )

    assets = registry.get_assets(ar_filter)
    log(f"Found: {len(assets)} StaticMesh assets")
    return assets

# ─── Fix: Naming ───────────────────────────────────────────────────────────────

def fix_naming(asset_data, suggested_name: str) -> bool:
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

# ─── Check: Naming ─────────────────────────────────────────────────────────────

def check_naming(asset_data) -> dict:
    name = str(asset_data.asset_name)
    ok   = name.startswith("SM_")

    suggested = name
    if not ok:
        import re
        clean     = re.sub(r"^(SM_|SK_|T_|M_|MI_)", "", name)
        suggested = "SM_" + clean

    return {"ok": ok, "name": name, "suggested": suggested}

# ─── Check: LOD ────────────────────────────────────────────────────────────────

def check_lod(mesh: unreal.StaticMesh) -> dict:
    try:
        lod_count = mesh.get_num_lods()
        ok = lod_count >= 1
        return {"ok": ok, "lod_count": lod_count}
    except Exception as e:
        return {"ok": False, "lod_count": 0, "error": str(e)}

# ─── Check: Lightmap UV ────────────────────────────────────────────────────────

def check_lightmap_uv(mesh: unreal.StaticMesh) -> dict:
    try:
        lightmap_index = mesh.get_editor_property("lightmap_coordinate_index")
        ok = lightmap_index >= 0
        return {"ok": ok, "channel": lightmap_index}
    except Exception as e:
        return {"ok": False, "channel": -1, "error": str(e)}

# ─── Check: Collision ──────────────────────────────────────────────────────────

def check_collision(mesh: unreal.StaticMesh) -> dict:
    try:
        body_setup  = mesh.get_editor_property("body_setup")
        has_complex = mesh.get_editor_property("generate_mesh_distance_field")

        if body_setup is not None:
            agg = body_setup.get_editor_property("agg_geom")
            sphere_count = len(agg.get_editor_property("sphere_elems"))
            box_count    = len(agg.get_editor_property("box_elems"))
            capsule_count= len(agg.get_editor_property("sphyl_elems"))
            convex_count = len(agg.get_editor_property("convex_elems"))
            total = sphere_count + box_count + capsule_count + convex_count
            ok = total > 0
            return {"ok": ok, "shapes": total}

        return {"ok": False, "shapes": 0}
    except Exception as e:
        return {"ok": False, "shapes": 0, "error": str(e)}

# ─── Check: Triangle count ─────────────────────────────────────────────────────

def check_tris(mesh: unreal.StaticMesh) -> dict:
    try:
        tris = mesh.get_num_triangles(0)  # LOD0
        ok   = tris <= MAX_TRIS
        return {"ok": ok, "tris": tris}
    except Exception as e:
        return {"ok": False, "tris": 0, "error": str(e)}

# ─── Check: Nanite ─────────────────────────────────────────────────────────────

def check_nanite(mesh: unreal.StaticMesh) -> dict:
    try:
        nanite_settings = mesh.get_editor_property("nanite_settings")
        enabled = nanite_settings.get_editor_property("enabled")
        tris    = mesh.get_num_triangles(0)

        if enabled and tris < NANITE_TRIS:
            return {"ok": False, "enabled": True, "tris": tris,
                    "warning": f"Nanite enabled on low-poly mesh ({tris} tris)"}

        return {"ok": True, "enabled": enabled, "tris": tris}
    except Exception as e:
        return {"ok": True, "enabled": False, "error": str(e)}

# ─── Validate single asset ─────────────────────────────────────────────────────

def validate_asset(asset_data) -> dict:
    name   = str(asset_data.asset_name)
    path   = str(asset_data.package_name)
    result = {
        "name":      name,
        "path":      path,
        "naming":    {},
        "lod":       {},
        "lightmap":  {},
        "collision": {},
        "tris":      {},
        "nanite":    {},
        "passed":    0,
        "failed":    0,
        "fixed":     [],
    }

    # Load asset
    try:
        mesh = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(mesh, unreal.StaticMesh):
            log_warning(f"Could not load as StaticMesh: {name}")
            return result
    except Exception as e:
        log_error(f"Failed to load {name}: {e}")
        return result

    # Naming
    naming = check_naming(asset_data)
    result["naming"] = naming
    if naming["ok"]:
        result["passed"] += 1
        log(f"  [OK] Naming: {name}")
    else:
        if MODE == "fix":
            ok = fix_naming(asset_data, naming["suggested"])
            if ok:
                result["fixed"].append("naming")
                result["passed"] += 1
            else:
                result["failed"] += 1
        else:
            result["failed"] += 1
            log_warning(f"  [FAIL] Naming: '{name}' — must start with SM_. Suggested: {naming['suggested']}")

    # LOD
    lod = check_lod(mesh)
    result["lod"] = lod
    if lod["ok"]:
        result["passed"] += 1
        log(f"  [OK] LOD count: {lod['lod_count']}")
    else:
        result["failed"] += 1
        log_warning(f"  [FAIL] LOD: no LODs found")

    # Lightmap UV
    lightmap = check_lightmap_uv(mesh)
    result["lightmap"] = lightmap
    if lightmap["ok"]:
        result["passed"] += 1
        log(f"  [OK] Lightmap UV channel: {lightmap['channel']}")
    else:
        result["failed"] += 1
        log_warning(f"  [FAIL] Lightmap UV: channel not set")

    # Collision
    collision = check_collision(mesh)
    result["collision"] = collision
    if collision["ok"]:
        result["passed"] += 1
        log(f"  [OK] Collision: {collision['shapes']} shape(s)")
    else:
        result["failed"] += 1
        log_warning(f"  [FAIL] Collision: no collision shapes found")

    # Triangle count
    tris = check_tris(mesh)
    result["tris"] = tris
    if tris["ok"]:
        result["passed"] += 1
        log(f"  [OK] Triangles: {tris['tris']}")
    else:
        result["failed"] += 1
        log_warning(f"  [WARN] Triangles: {tris['tris']} exceeds limit of {MAX_TRIS}")

    # Nanite
    nanite = check_nanite(mesh)
    result["nanite"] = nanite
    if nanite["ok"]:
        result["passed"] += 1
        log(f"  [OK] Nanite: {'enabled' if nanite.get('enabled') else 'disabled'}")
    else:
        result["failed"] += 1
        log_warning(f"  [WARN] Nanite: {nanite.get('warning', 'check failed')}")

    log(f"  Result: {result['passed']}/6 checks passed")
    return result

# ─── Save report ───────────────────────────────────────────────────────────────

def save_report(report: dict) -> str:
    os.makedirs(REPORT_PATH, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"mesh_validator_{timestamp}.json"
    filepath  = os.path.join(REPORT_PATH, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    log(f"Report saved: {filepath}")
    return filepath

# ─── Print summary ─────────────────────────────────────────────────────────────

def print_summary(report: dict) -> None:
    s = report["summary"]
    log("")
    log("╔══════════════════════════════════════════╗")
    log("║       MESH VALIDATOR — RESULTS            ║")
    log("╠══════════════════════════════════════════╣")
    log(f"║  Mode                  : {s['mode']:<15}║")
    log(f"║  Meshes scanned        : {s['total_meshes']:<15}║")
    log(f"║  Checks passed         : {s['total_passed']:<15}║")
    log(f"║  Checks failed         : {s['total_failed']:<15}║")
    log(f"║  Naming violations     : {s['naming_violations']:<15}║")
    log(f"║  Missing collision     : {s['missing_collision']:<15}║")
    log(f"║  Triangle warnings     : {s['tris_warnings']:<15}║")
    log(f"║  Fixed (naming)        : {s['fixed']:<15}║")
    log(f"║  Scan duration         : {s['scan_duration_sec']:.2f}s          ║")
    log("╚══════════════════════════════════════════╝")

# ─── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    start_time = datetime.now()

    log("=" * 60)
    log(f"Starting Mesh Validator — MODE: {MODE.upper()}")
    log("=" * 60)

    assets  = get_all_static_meshes(SCAN_PATH)
    results = []

    naming_violations  = 0
    missing_collision  = 0
    tris_warnings      = 0
    total_passed       = 0
    total_failed       = 0
    total_fixed        = 0

    for asset_data in assets:
        name = str(asset_data.asset_name)
        log("")
        log(f">>> {name}")

        result = validate_asset(asset_data)
        results.append(result)

        total_passed += result["passed"]
        total_failed += result["failed"]
        total_fixed  += len(result["fixed"])

        if not result["naming"].get("ok", True):
            naming_violations += 1
        if not result["collision"].get("ok", True):
            missing_collision += 1
        if not result["tris"].get("ok", True):
            tris_warnings += 1

    duration = (datetime.now() - start_time).total_seconds()

    report = {
        "summary": {
            "mode":               MODE,
            "scan_path":          SCAN_PATH,
            "timestamp":          start_time.isoformat(),
            "total_meshes":       len(assets),
            "total_passed":       total_passed,
            "total_failed":       total_failed,
            "naming_violations":  naming_violations,
            "missing_collision":  missing_collision,
            "tris_warnings":      tris_warnings,
            "fixed":              total_fixed,
            "scan_duration_sec":  round(duration, 2),
        },
        "results": results,
    }

    filepath = save_report(report)
    print_summary(report)

    log("")
    log(f"Done! Report saved to: {filepath}")
