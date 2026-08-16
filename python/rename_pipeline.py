# rename_pipeline.py
# Asset naming pipeline — validates and renames objects to studio standard
# Author: LAZARUS-inq
# Part of TA learning journey

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPORT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "reports", "report.json"))


def validate_objects(objects):
    if len(objects) == 0:
        print("ERROR: List is empty.")
        return False
    if len(objects) != len(set(objects)):
        print("ERROR: Duplicate names found.")
        return False
    for i, obj in enumerate(objects):
        if not isinstance(obj, str) or not obj.strip():
            print(f"ERROR: Invalid name at index {i}.")
            return False
    print(f"OK: {len(objects)} objects validated.")
    return True


def rename_objects(objects, prefix="SM"):
    result = []
    for i, name in enumerate(objects):
        new_name = f"{prefix}_{name}_{i+1:03d}"
        result.append(new_name)
        print(new_name)
    print(f"Total: {len(objects)}")
    return result


def save_report(objects, prefix="SM", filename=DEFAULT_REPORT):
    renamed = [f"{prefix}_{name}_{i+1:03d}" for i, name in enumerate(objects)]
    report = {
        "total": len(objects),
        "prefix": prefix,
        "objects": renamed,
    }
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to: {os.path.abspath(filename)}")


def run_pipeline(objects, prefix="SM", report_path=DEFAULT_REPORT):
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


if __name__ == "__main__":
    run_pipeline(["Box", "Sphere", "Cone"])
