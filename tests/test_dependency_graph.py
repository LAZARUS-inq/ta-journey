# Lightweight checks for the dependency graph (no Unreal required).
import os
import sys
import unittest

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "python")))

from dependency_graph import DependencyGraph


def _sample_graph():
    graph = DependencyGraph()
    graph.add_node("/Game/Maps/Lvl_Hangar", name="Lvl_Hangar", asset_class="World")
    graph.add_node("/Game/Meshes/SM_Crate", name="SM_Crate", asset_class="StaticMesh")
    graph.add_node("/Game/Materials/M_Crate", name="M_Crate", asset_class="Material")
    graph.add_node("/Game/Materials/M_DecalDirt", name="M_DecalDirt", asset_class="Material")
    graph.add_node("/Game/Textures/T_Crate_D", name="T_Crate_D", asset_class="Texture2D")
    graph.add_node("/Game/Textures/T_Crate_N", name="T_Crate_N", asset_class="Texture2D")
    graph.add_node("/Game/Textures/T_Old_D", name="T_Old_D", asset_class="Texture2D")
    graph.add_node("/Game/Materials/MI_Ping", name="MI_Ping", asset_class="MaterialInstanceConstant")
    graph.add_node("/Game/Materials/MI_Pong", name="MI_Pong", asset_class="MaterialInstanceConstant")

    graph.add_edge("/Game/Maps/Lvl_Hangar", "/Game/Meshes/SM_Crate", "hard")
    graph.add_edge("/Game/Maps/Lvl_Hangar", "/Game/Materials/M_DecalDirt", "soft")
    graph.add_edge("/Game/Meshes/SM_Crate", "/Game/Materials/M_Crate", "hard")
    graph.add_edge("/Game/Materials/M_Crate", "/Game/Textures/T_Crate_D", "hard")
    graph.add_edge("/Game/Materials/M_Crate", "/Game/Textures/T_Crate_N", "hard")
    graph.add_edge("/Game/Materials/M_DecalDirt", "/Game/Textures/T_Crate_D", "hard")
    graph.add_edge("/Game/Materials/M_Crate", "/Game/Textures/T_Broken_D", "hard")
    graph.add_edge("/Game/Materials/MI_Ping", "/Game/Materials/MI_Pong", "hard")
    graph.add_edge("/Game/Materials/MI_Pong", "/Game/Materials/MI_Ping", "hard")
    return graph


class DependencyGraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = _sample_graph()

    def test_unused_skips_maps_and_finds_orphans(self):
        unused = {node["package"] for node in self.graph.unused_assets()}
        self.assertIn("/Game/Textures/T_Old_D", unused)
        self.assertIn("/Game/Materials/MI_Ping", unused)
        self.assertIn("/Game/Materials/MI_Pong", unused)
        self.assertNotIn("/Game/Maps/Lvl_Hangar", unused)
        self.assertNotIn("/Game/Materials/M_DecalDirt", unused)
        self.assertNotIn("/Game/Textures/T_Crate_D", unused)

    def test_missing_game_reference(self):
        missing = self.graph.missing_dependencies()
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["to"], "/Game/Textures/T_Broken_D")
        self.assertEqual(missing[0]["from"], "/Game/Materials/M_Crate")

    def test_hard_cycle(self):
        cycles = self.graph.cycles()
        packages = {frozenset(cycle[:-1]) for cycle in cycles}
        self.assertIn(frozenset({"/Game/Materials/MI_Ping", "/Game/Materials/MI_Pong"}), packages)

    def test_hub_texture(self):
        hubs = self.graph.most_referenced(limit=3)
        self.assertEqual(hubs[0]["package"], "/Game/Textures/T_Crate_D")
        self.assertEqual(hubs[0]["referencers"], 2)

    def test_query_who_uses_albedo(self):
        refs = self.graph.referencers("/Game/Textures/T_Crate_D")
        sources = {item["from"] for item in refs}
        self.assertEqual(sources, {"/Game/Materials/M_Crate", "/Game/Materials/M_DecalDirt"})

    def test_no_maps_falls_back_to_inbound_degree(self):
        graph = DependencyGraph()
        graph.add_node("/Game/Textures/T_Used_D", name="T_Used_D", asset_class="Texture2D")
        graph.add_node("/Game/Textures/T_Orphan_D", name="T_Orphan_D", asset_class="Texture2D")
        graph.add_node("/Game/Materials/M_Used", name="M_Used", asset_class="Material")
        graph.add_edge("/Game/Materials/M_Used", "/Game/Textures/T_Used_D", "hard")
        unused = {node["package"] for node in graph.unused_assets()}
        self.assertEqual(unused, {"/Game/Textures/T_Orphan_D", "/Game/Materials/M_Used"})

    def test_report_counts(self):
        report = self.graph.build_report(query_package="/Game/Textures/T_Crate_D")
        self.assertEqual(report["summary"]["unused"], 3)
        self.assertEqual(report["summary"]["missing"], 1)
        self.assertGreaterEqual(report["summary"]["cycles"], 1)
        self.assertTrue(report["query"]["known"])
        self.assertEqual(len(report["query"]["referencers"]), 2)


if __name__ == "__main__":
    unittest.main()
