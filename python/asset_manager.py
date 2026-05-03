# asset_manager.py
# Asset scanning, validation, renaming and reporting pipeline
# Author: LAZARUS-inq
# Part of TA learning journey

import os
import json


# ── VALIDATION ───────────────────────────────────────────────────────────────

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


# ── RENAMING ──────────────────────────────────────────────────────────────────

def rename_objects(objects, prefix="SM"):
    """Rename a list of objects to studio naming standard (e.g. SM_Box_001)."""
    result = []
    for i, name in enumerate(objects):
        new_name = f"{prefix}_{name}_{i+1:03d}"
        result.append(new_name)
        print(new_name)
    print(f"Total: {len(objects)}")
    return result


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


# ── ASSET MANAGER CLASS ───────────────────────────────────────────────────────

class AssetManager:
    """Manages FBX assets in a folder — scan, fix naming, and report."""

    def __init__(self, folder, prefix="SM"):
        self.folder = folder
        self.prefix = prefix
        self.valid = []
        self.invalid = []

    def scan(self):
        """Scan folder for FBX files and split into valid/invalid by naming convention."""
        self.valid = []
        self.invalid = []

        for root, dirs, files in os.walk(self.folder):
            for file in files:
                if file.endswith(".fbx"):
                    name = os.path.splitext(file)[0]
                    if name.startswith("SM_") or name.startswith("ENV_"):
                        self.valid.append(file)
                    else:
                        self.invalid.append(file)

        print(f"\n--- Scan Results: {self.folder} ---")
        print(f"Valid   ({len(self.valid)}):   {self.valid}")
        print(f"Invalid ({len(self.invalid)}): {self.invalid}")

    def fix(self):
        """Rename invalid FBX files to studio naming standard."""
        if not self.invalid:
            print("Nothing to fix.")
            return

        print("\n--- Fixing Invalid Assets ---")
        for i, file in enumerate(self.invalid):
            old_path = os.path.join(self.folder, file)
            name = os.path.splitext(file)[0]
            new_name = f"{self.prefix}_{name}_{i+1:03d}.fbx"
            new_path = os.path.join(self.folder, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {file} → {new_name}")

        print(f"Fixed: {len(self.invalid)} files renamed.")
        self.scan()

    def report(self, filename="asset_report.json"):
        """Save scan results to a JSON report file."""
        report = {
            "folder": self.folder,
            "total": len(self.valid) + len(self.invalid),
            "valid_count": len(self.valid),
            "invalid_count": len(self.invalid),
            "valid": self.valid,
            "invalid": self.invalid
        }
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)
        print(f"Report saved to: {os.path.abspath(filename)}")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Pipeline test
    run_pipeline(["Box", "Sphere", "Cone"])

    # File system test — change path to your assets folder
    manager = AssetManager("E:\\TestAssets")
    manager.scan()
    manager.fix()
    manager.report()
