# texture_checker.py
# UE5 Texture Naming Convention Validator & Auto-Fix Tool
# Scans Texture2D assets under /Game/, checks T_ prefix and common suffixes,
# and optionally renames non-compliant textures.
#
# Usage:
#   DRY_RUN = True  → Report only, no changes made
#   DRY_RUN = False → Apply prefix fixes in-engine
#
# Run inside UE5: Tools → Execute Python Script
#
# Author: LAZARUS-inq
# Part of TA learning journey

import json
import os
import re

import unreal

# ── CONFIG ────────────────────────────────────────────────────────────────────

DRY_RUN = True
SCAN_PATH = "/Game"
CHECK_SUFFIXES = True
VALID_SUFFIXES = (
    "_D", "_N", "_S", "_M", "_E", "_H",
    "_ORM", "_MRA", "_RMA", "_ARM",
    "_Mask", "_ORMH",
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "reports", "texture_report.json"))

KNOWN_PREFIX_RE = re.compile(r"^(T_|M_|MI_|SM_|SK_|MF_|MPC_)")


def log(msg):
    unreal.log(f"[TextureChecker] {msg}")


def suggested_texture_name(name):
    clean = KNOWN_PREFIX_RE.sub("", name)
    return f"T_{clean}" if not clean.startswith("T_") else clean


def suffix_ok(name):
    if not CHECK_SUFFIXES:
        return True
    return any(name.endswith(suffix) for suffix in VALID_SUFFIXES)


def scan_textures(scan_path, dry_run):
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = asset_registry.get_assets_by_class(
        unreal.TopLevelAssetPath("/Script/Engine", "Texture2D")
    )

    valid = []
    invalid = []
    renamed = []

    for asset in assets:
        path = str(asset.package_path)
        if not path.startswith(scan_path):
            continue

        name = str(asset.asset_name)
        issues = []
        new_name = name

        if not name.startswith("T_"):
            issues.append("BAD NAME — missing T_ prefix")
            new_name = suggested_texture_name(name)
            status = "SUGGESTED"
            if not dry_run:
                try:
                    unreal.EditorUtilityLibrary.rename_asset(asset.get_asset(), new_name)
                    status = "RENAMED"
                except Exception as exc:
                    status = "FAILED"
                    issues.append(f"RENAME FAILED: {exc}")
            renamed.append({
                "old": name,
                "new": new_name,
                "path": path,
                "status": status,
            })

        if not suffix_ok(name):
            issues.append(
                "SUFFIX — expected one of " + ", ".join(VALID_SUFFIXES)
            )

        entry = {"name": name, "path": path, "issues": issues}
        if issues:
            invalid.append(entry)
        else:
            valid.append(entry)

    return valid, invalid, renamed


def save_report(report, report_path):
    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    log(f"Report saved to: {report_path}")


def run(scan_path=SCAN_PATH, dry_run=DRY_RUN, report_path=REPORT_PATH):
    valid, invalid, renamed = scan_textures(scan_path, dry_run)
    mode = "DRY RUN" if dry_run else "FIX MODE"

    log(f"=== TEXTURE CHECKER REPORT [{mode}] ===")
    log(f"Total scanned : {len(valid) + len(invalid)}")
    log(f"Valid         : {len(valid)}")
    log(f"Invalid       : {len(invalid)}")

    if renamed:
        log("--- Renames ---")
        for item in renamed:
            log(f"  [{item['status']}] {item['old']} → {item['new']}")
    else:
        log("No prefix renames required.")

    report = {
        "mode": mode,
        "scan_path": scan_path,
        "summary": {
            "total": len(valid) + len(invalid),
            "valid": len(valid),
            "invalid": len(invalid),
            "renamed": len(renamed),
        },
        "valid": valid,
        "invalid": invalid,
        "renames": renamed,
    }
    save_report(report, report_path)
    return report


if __name__ == "__main__":
    run()
