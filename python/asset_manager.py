# asset_manager.py
# Asset scanning, validation, renaming and reporting pipeline
# Author: LAZARUS-inq
# Part of TA learning journey

import json
import os

from rename_pipeline import run_pipeline

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPORT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "reports", "asset_report.json"))
VALID_PREFIXES = ("SM_", "ENV_")


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

        if not os.path.isdir(self.folder):
            print(f"ERROR: Folder does not exist: {self.folder}")
            return

        for root, _dirs, files in os.walk(self.folder):
            for file in files:
                if not file.lower().endswith(".fbx"):
                    continue
                rel = os.path.relpath(os.path.join(root, file), self.folder)
                name = os.path.splitext(os.path.basename(file))[0]
                if name.startswith(VALID_PREFIXES):
                    self.valid.append(rel)
                else:
                    self.invalid.append(rel)

        print(f"\n--- Scan Results: {self.folder} ---")
        print(f"Valid   ({len(self.valid)}):   {self.valid}")
        print(f"Invalid ({len(self.invalid)}): {self.invalid}")

    def fix(self, dry_run=True):
        """Rename invalid FBX files to studio naming standard.

        dry_run=True (default) prints planned renames without touching disk.
        """
        if not self.invalid:
            print("Nothing to fix.")
            return

        mode = "DRY RUN" if dry_run else "FIX"
        print(f"\n--- Fixing Invalid Assets [{mode}] ---")
        for i, rel in enumerate(self.invalid):
            old_path = os.path.join(self.folder, rel)
            parent = os.path.dirname(old_path)
            name = os.path.splitext(os.path.basename(rel))[0]
            new_name = f"{self.prefix}_{name}_{i+1:03d}.fbx"
            new_path = os.path.join(parent, new_name)
            if dry_run:
                print(f"Would rename: {rel} → {os.path.join(os.path.dirname(rel), new_name).lstrip('./')}")
            else:
                if os.path.exists(new_path):
                    print(f"SKIP (target exists): {new_name}")
                    continue
                os.rename(old_path, new_path)
                print(f"Renamed: {rel} → {new_name}")

        if dry_run:
            print(f"Planned: {len(self.invalid)} files. Call fix(dry_run=False) to apply.")
        else:
            print(f"Fixed: {len(self.invalid)} files renamed.")
            self.scan()

    def report(self, filename=DEFAULT_REPORT):
        """Save scan results to a JSON report file."""
        report = {
            "folder": self.folder,
            "total": len(self.valid) + len(self.invalid),
            "valid_count": len(self.valid),
            "invalid_count": len(self.invalid),
            "valid": self.valid,
            "invalid": self.invalid,
        }
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        print(f"Report saved to: {os.path.abspath(filename)}")


if __name__ == "__main__":
    run_pipeline(["Box", "Sphere", "Cone"])

    # Point this at a local FBX folder to test the scanner.
    test_folder = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "test_assets"))
    if os.path.isdir(test_folder):
        manager = AssetManager(test_folder)
        manager.scan()
        manager.fix(dry_run=True)
        manager.report()
    else:
        print(f"\nSkip folder scan — create {test_folder} (or pass another path) to test AssetManager.")
