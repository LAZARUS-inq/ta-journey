# asset_manager.py
# Asset scanning, validation, renaming and reporting pipeline
# Author: LAZARUS-inq
# Part of TA learning journey

import os
import json


# ── VALIDATION ──────────────────────────────────────────────────────────────

def validate_objects(objects):
    """Check that a list of object names is valid before processing."""
    if len(objects) == 0:
        print("ERROR: List is empty.")
        return False
    if len(objects) != len(set(objects)):
        print("ERROR: Duplicate names found.")
        return False
    for i, obj in enumerate(objects):
        if not isinstance(obj, str):
            print(f"ERROR: Invalid name at index {i}.")
            return False
    print(f"OK: {len(objects)} objects validated.")
    return True


# ── RENAMING ─────────────────────────────────────────────────────────────────

def rename_objects(objects, prefix="SM"):
    """Rename a list of objects to studio naming standard (e.g. SM_Box_001)."""
    result = []
    for i, name in enumerate(objects):
        new_name = f"{prefix}_{name}_{i+1:03d}"
        result.append(new_name)
        print(new_name)
    print(f"Total: {len(objects)}")
    return result


# ── REPORTING ────────────────────────────────────────────────────────────────

def save_report(objects, prefix="SM", filename="report.json"):
    """Save renamed asset list to a JSON report file."""
    renamed = [f"{prefix}_{name}_{i+1:03d}" for i, name in enumerate(objects)]

    report = {
        "total": len(objects),
        "prefix": prefix,
        "objects": renamed
    }

    with open(filename, "w") as f:
        json.dump(report, f, indent=4)

    print(f"Report saved to: {os.path.abspath(filename)}")


# ── PIPELINE ─────────────────────────────────────────────────────────────────

def run_pipeline(objects, prefix="SM", report_path="report.json"):
    """Run full pipeline: validate → rename → save report."""
    print("--- Validating ---")
    if not validate_objects(objects):
        print("Pipeline stopped.")
        return None

    print("--- Renaming ---")
    renamed = rename_objects(objects, prefix)

    print("--- Saving Report ---")
    save_report(objects, prefix, filename=report_path)

    print("--- Done ---")
    return renamed


# ── FILE SYSTEM ──────────────────────────────────────────────────────────────

def scan_assets(folder):
    """Scan a folder for FBX files and split into valid/invalid by naming convention."""
    valid = []
    invalid = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".fbx"):
                name = os.path.splitext(file)[0]
                if name.startswith("SM_") or name.startswith("ENV_"):
                    valid.append(file)
                else:
                    invalid.append(file)

    print(f"\n--- Scan Results: {folder} ---")
    print(f"Valid ({len(valid)}):")
    for f in valid:
        print(f"  ✓ {f}")
    print(f"Invalid ({len(invalid)}):")
    for f in invalid:
        print(f"  ✗ {f}")

    return valid, invalid


def fix_assets(folder):
    """Rename invalid FBX files in a folder to studio naming standard."""
    valid, invalid = scan_assets(folder)

    print("\n--- Fixing Invalid Assets ---")
    for i, file in enumerate(invalid):
        old_path = os.path.join(folder, file)
        name = os.path.splitext(file)[0]
        new_name = f"SM_{name}_{i+1:03d}.fbx"
        new_path = os.path.join(folder, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {file} → {new_name}")

    print(f"Fixed: {len(invalid)} files renamed.")


# ── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Pipeline test
    run_pipeline(["Box", "Sphere", "Cone"])

    # File system test — change path to your assets folder
    # scan_assets("E:\\TestAssets")
    # fix_assets("E:\\TestAssets")