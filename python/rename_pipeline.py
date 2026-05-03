# rename_pipeline.py
# Asset naming pipeline — validates and renames objects to studio standard
# Author: LAZARUS-inq
# Part of TA learning journey
import json
import os

def validate_objects(objects):
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

def rename_objects(objects, prefix="SM"):
    result = []
    for i, name in enumerate(objects):
        new_name = f"{prefix}_{name}_{i+1:03d}"
        result.append(new_name)
        print(new_name)
    print(f"Total: {len(objects)}")
    return result

def run_pipeline(objects, prefix="SM"):
    print("--- Validating ---")
    if not validate_objects(objects):
        print("Pipeline stopped.")
        return
    print("--- Renaming ---")
    renamed = rename_objects(objects, prefix)
    print("--- Saving Report ---")
    save_report(objects, prefix, filename="E:\\PythonScripts\\report.json")
    print("--- Done ---")
    return renamed

def save_report(objects, prefix="SM", filename="report.json"):
    renamed = [f"{prefix}_{name}_{i+1:03d}" for i, name in enumerate(objects)]
    
    report = {
        "total": len(objects),
        "prefix": prefix,
        "objects": renamed
    }
    
    with open(filename, "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"Report saved to: {os.path.abspath(filename)}")

run_pipeline(["Box", "Sphere", "Cone"])
