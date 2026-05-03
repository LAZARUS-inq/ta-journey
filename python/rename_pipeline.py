# rename_pipeline.py
# Asset naming pipeline — validates and renames objects to studio standard
# Author: LAZARUS-inq
# Part of TA learning journey

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
    rename_objects(objects, prefix)
    print("--- Done ---")

# Тесты
run_pipeline(["Box", "Sphere", "Cone"])
run_pipeline(["Box", "Box"])
run_pipeline([])
