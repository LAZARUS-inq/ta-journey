"""
================================================================================
  asset_dependency_checker.py — UE5 Asset Dependency Graph
================================================================================
  Author  : LAZARUS-inq
  GitHub  : https://github.com/LAZARUS-inq
  Version : 1.0.0

  HOW TO RUN
  ----------
  Inside Unreal Engine 5 Editor:
    Tools → Execute Python Script → select this file
  Or: TA Journey menu → Asset Dependency Checker (after register_ta_menu.py)

  DESCRIPTION
  -----------
  Builds a package dependency graph for /Game via AssetRegistry and reports
  production hygiene issues that naming validators cannot see:

  - Unused assets     : nothing in the scanned set references them
                        (maps / level sequences are treated as roots)
  - Missing refs      : /Game package referenced but not in the registry
  - Hard-ref cycles   : A → B → A load-time loops
  - Hubs              : most-referenced packages (shared textures/materials)
  - Heaviest assets   : packages with the most outgoing dependencies

  This tool never deletes or renames. It only writes a JSON report.

  SETTINGS
  --------
  SCAN_PATH       Root content path (default "/Game").
  QUERY_PACKAGE   Optional package to inspect, e.g. "/Game/Textures/T_Crate_D".
  TOP_N           How many hub / heaviest rows to keep.
  INCLUDE_SOFT    Include soft package references (level streams, etc.).
================================================================================
"""

import json
import os
import sys
from datetime import datetime

import unreal

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from dependency_graph import ROOT_CLASSES_DEFAULT, DependencyGraph

SCAN_PATH = "/Game"
QUERY_PACKAGE = ""
TOP_N = 15
INCLUDE_SOFT = True
REPORT_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "reports"))


def log(msg):
    unreal.log(f"[DependencyChecker] {msg}")


def log_warning(msg):
    unreal.log_warning(f"[DependencyChecker] {msg}")


def log_error(msg):
    unreal.log_error(f"[DependencyChecker] {msg}")


def _asset_class(asset_data):
    try:
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return str(getattr(asset_data, "asset_class", "Unknown"))


def _dep_options():
    options = unreal.AssetRegistryDependencyOptions()
    options.include_soft_package_references = INCLUDE_SOFT
    options.include_hard_package_references = True
    options.include_searchable_names = False
    options.include_soft_management_references = False
    options.include_hard_management_references = False
    return options


def collect_assets(scan_path):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    ar_filter = unreal.ARFilter(
        package_paths=[scan_path],
        recursive_paths=True,
    )
    assets = list(registry.get_assets(ar_filter))
    log(f"Registry returned {len(assets)} assets under {scan_path}")
    return registry, assets


def build_graph(registry, assets, scan_path):
    graph = DependencyGraph(root_classes=ROOT_CLASSES_DEFAULT)
    options = _dep_options()
    hard_options = _dep_options()
    hard_options.include_soft_package_references = False

    for asset_data in assets:
        package = str(asset_data.package_name)
        if not package.startswith(scan_path):
            continue
        graph.add_node(
            package,
            name=str(asset_data.asset_name),
            asset_class=_asset_class(asset_data),
            path=str(asset_data.package_path),
        )

    for package in list(graph.nodes):
        pkg_name = unreal.Name(package)
        try:
            hard = [str(n) for n in registry.get_dependencies(pkg_name, hard_options)]
        except Exception as exc:
            log_warning(f"Hard deps failed for {package}: {exc}")
            hard = []
        hard_set = set(hard)
        for dest in hard:
            if dest.startswith(scan_path):
                graph.add_edge(package, dest, kind="hard")

        if INCLUDE_SOFT:
            try:
                all_deps = [str(n) for n in registry.get_dependencies(pkg_name, options)]
            except Exception as exc:
                log_warning(f"Soft deps failed for {package}: {exc}")
                all_deps = []
            for dest in all_deps:
                if dest in hard_set or not dest.startswith(scan_path):
                    continue
                graph.add_edge(package, dest, kind="soft")

    return graph


def save_report(report, report_path):
    os.makedirs(report_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(report_path, f"dependency_report_{timestamp}.json")
    with open(filepath, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    log(f"Report saved: {filepath}")
    return filepath


def print_summary(report):
    summary = report["summary"]
    log("")
    log("╔══════════════════════════════════════════╗")
    log("║     ASSET DEPENDENCY CHECKER — RESULTS    ║")
    log("╠══════════════════════════════════════════╣")
    log(f"║  Assets scanned        : {summary['assets']:<15}║")
    log(f"║  Edges                 : {summary['edges']:<15}║")
    log(f"║  Unused (no refs)      : {summary['unused']:<15}║")
    log(f"║  Missing /Game refs    : {summary['missing']:<15}║")
    log(f"║  Hard-ref cycles       : {summary['cycles']:<15}║")
    log("╚══════════════════════════════════════════╝")

    unused = report.get("unused") or []
    if unused:
        log("--- Unused (first 20) ---")
        for node in unused[:20]:
            log(f"  {node['class']:22} {node['package']}")

    missing = report.get("missing") or []
    if missing:
        log("--- Missing ---")
        for edge in missing[:20]:
            log_error(f"  {edge['from']} → {edge['to']} ({edge['kind']})")

    cycles = report.get("cycles") or []
    if cycles:
        log("--- Cycles ---")
        for cycle in cycles[:10]:
            log_warning("  " + " → ".join(cycle["packages"]))

    query = report.get("query")
    if query:
        log(f"--- Query {query['package']} ---")
        if not query.get("known"):
            log_warning("  Package not in scanned set")
        log(f"  Dependencies : {len(query.get('dependencies') or [])}")
        log(f"  Referencers  : {len(query.get('referencers') or [])}")
        for ref in (query.get("referencers") or [])[:20]:
            log(f"    used by {ref['from']} ({ref['kind']})")


def run(scan_path=SCAN_PATH, query_package=QUERY_PACKAGE, report_path=REPORT_PATH):
    start = datetime.now()
    log("=" * 60)
    log(f"Starting Asset Dependency Checker: {scan_path}")
    log("=" * 60)

    registry, assets = collect_assets(scan_path)
    graph = build_graph(registry, assets, scan_path)
    report = graph.build_report(
        scan_path=scan_path,
        query_package=query_package,
        top_n=TOP_N,
    )
    report["meta"] = {
        "timestamp": start.isoformat(),
        "include_soft": INCLUDE_SOFT,
        "root_classes": list(ROOT_CLASSES_DEFAULT),
        "scan_duration_sec": round((datetime.now() - start).total_seconds(), 2),
    }

    filepath = save_report(report, report_path)
    print_summary(report)
    log(f"Done! Report saved to: {filepath}")
    return report


if __name__ == "__main__":
    run()
