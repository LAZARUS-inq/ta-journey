# maxscript_pipeline.py
# Python pipeline for 3ds Max — rename selected objects and save JSON report
# Requires: pymxs (built into 3ds Max)
# Author: LAZARUS-inq
# Part of TA learning journey

import pymxs
import re
import json
import os

rt = pymxs.runtime

def process_selected(prefix="SM", report_path="C:\\Reports\\report.json"):
    selected = rt.getCurrentSelection()

    if len(selected) == 0:
        print("ERROR: Nothing selected.")
        return

    renamed = []
    for i, obj in enumerate(selected):
        old_name = obj.name
        clean_name = re.sub(r'^(SM_|ENV_)', '', old_name)
        clean_name = re.sub(r'[_\d]+$', '', clean_name)
        obj.name = f"{prefix}_{clean_name}_{i+1:03d}"
        renamed.append(obj.name)
        print(f"Renamed: {old_name} ? {obj.name}")

    print(f"Total: {len(selected)} objects renamed.")

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    report = {
        "total": len(renamed),
        "prefix": prefix,
        "objects": renamed
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to: {report_path}")

process_selected()