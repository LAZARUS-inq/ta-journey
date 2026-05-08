# texture_checker.py
# UE5 Texture Naming Convention Validator & Auto-Fix Tool
# Scans all Texture2D assets in /Game/ folder, checks for T_ prefix,
# and optionally renames non-compliant textures automatically.
#
# Usage:
#   DRY_RUN = True  → Report only, no changes made
#   DRY_RUN = False → Apply fixes, rename assets in-engine
#
# Run inside UE5: Tools → Execute Python Script
# Report saved to: texture_report.json
#
# Author: LAZARUS-inq
# Part of TA learning journey

import unreal
import json

# ── CONFIG ────────────────────────────────────────────────────────────────────

DRY_RUN = True          # Set to False to apply renames
REPORT_PATH = "E:\\PythonScripts\\texture_report.json"

# ── SCAN ──────────────────────────────────────────────────────────────────────

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = asset_registry.get_assets_by_class(
    unreal.TopLevelAssetPath("/Script/Engine", "Texture2D")
)

valid = []
invalid = []
renamed = []

for asset in assets:
    path = str(asset.package_path)

    # Skip engine/plugin textures — only check project assets
    if not path.startswith("/Game/"):
        continue

    name = str(asset.asset_name)
    issues = []

    # ── NAMING CHECK ──────────────────────────────────────────────────────────
    if not name.startswith("T_"):
        issues.append("BAD NAME — missing T_ prefix")
        new_name = f"T_{name}"

        if not DRY_RUN:
            unreal.EditorUtilityLibrary.rename_asset(
                asset.get_asset(), new_name
            )
            status = "RENAMED"
        else:
            status = "SUGGESTED"

        renamed.append({
            "old": name,
            "new": new_name,
            "path": str(path),
            "status": status
        })

    entry = {"name": name, "path": str(path), "issues": issues}
    if issues:
        invalid.append(entry)
    else:
        valid.append(entry)

# ── REPORT ────────────────────────────────────────────────────────────────────

mode = "DRY RUN" if DRY_RUN else "FIX MODE"

print(f"=== TEXTURE CHECKER REPORT [{mode}] ===")
print(f"Total scanned : {len(valid) + len(invalid)}")
print(f"Valid         : {len(valid)}")
print(f"Invalid       : {len(invalid)}")
print("")

if renamed:
    print("--- Renames ---")
    for r in renamed:
        print(f"  [{r['status']}] {r['old']} → {r['new']}")
else:
    print("All textures are correctly named.")

print("==============================")

# ── SAVE JSON ─────────────────────────────────────────────────────────────────

report = {
    "mode": mode,
    "summary": {
        "total": len(valid) + len(invalid),
        "valid": len(valid),
        "invalid": len(invalid),
        "renamed": len(renamed)
    },
    "valid": valid,
    "invalid": invalid,
    "renames": renamed
}

with open(REPORT_PATH, "w") as f:
    json.dump(report, f, indent=4)

print(f"Report saved to: {REPORT_PATH}")