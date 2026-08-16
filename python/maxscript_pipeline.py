# maxscript_pipeline.py
# Python pipeline for 3ds Max — rename selected objects and save JSON report
# Requires: pymxs (built into 3ds Max)
# Author: LAZARUS-inq
# Part of TA learning journey

import json
import os
import re

import pymxs

rt = pymxs.runtime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPORT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "reports", "maxscript_report.json"))
PREFIX_RE = re.compile(r"^(SM_|ENV_|SK_)")
SUFFIX_RE = re.compile(r"[_\d]+$")


def process_selected(prefix="SM", report_path=DEFAULT_REPORT):
    selected = rt.getCurrentSelection()

    if len(selected) == 0:
        print("ERROR: Nothing selected.")
        return None

    renamed = []
    for i, obj in enumerate(selected):
        old_name = obj.name
        clean_name = PREFIX_RE.sub("", old_name)
        clean_name = SUFFIX_RE.sub("", clean_name) or old_name
        obj.name = f"{prefix}_{clean_name}_{i+1:03d}"
        renamed.append(obj.name)
        print(f"Renamed: {old_name} ? {obj.name}")

    print(f"Total: {len(selected)} objects renamed.")

    report_dir = os.path.dirname(report_path)
    if report_dir:
        os.makedirs(report_dir, exist_ok=True)
    report = {
        "total": len(renamed),
        "prefix": prefix,
        "objects": renamed,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to: {report_path}")
    return renamed


if __name__ == "__main__":
    process_selected()
