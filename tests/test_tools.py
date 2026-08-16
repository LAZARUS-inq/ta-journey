# Lightweight checks for the vanilla-Python tools (no 3ds Max / UE5 required).
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "python")))

from asset_manager import AssetManager
from rename_pipeline import run_pipeline, validate_objects


class RenamePipelineTests(unittest.TestCase):
    def test_validate_rejects_empty_and_duplicates(self):
        self.assertFalse(validate_objects([]))
        self.assertFalse(validate_objects(["Box", "Box"]))
        self.assertFalse(validate_objects(["Box", 1]))
        self.assertTrue(validate_objects(["Box", "Sphere"]))

    def test_pipeline_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = os.path.join(tmp, "report.json")
            renamed = run_pipeline(["Box", "Sphere"], report_path=report)
            self.assertEqual(renamed, ["SM_Box_001", "SM_Sphere_002"])
            self.assertTrue(os.path.isfile(report))


class AssetManagerTests(unittest.TestCase):
    def test_scan_and_dry_run_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            open(os.path.join(tmp, "crate.fbx"), "wb").close()
            open(os.path.join(tmp, "SM_Door.fbx"), "wb").close()
            nested = os.path.join(tmp, "props")
            os.makedirs(nested)
            open(os.path.join(nested, "barrel.FBX"), "wb").close()

            manager = AssetManager(tmp)
            manager.scan()
            self.assertEqual(manager.valid, ["SM_Door.fbx"])
            self.assertCountEqual(manager.invalid, ["crate.fbx", os.path.join("props", "barrel.FBX")])

            manager.fix(dry_run=True)
            self.assertTrue(os.path.isfile(os.path.join(tmp, "crate.fbx")))

            manager.fix(dry_run=False)
            manager.scan()
            self.assertEqual(manager.invalid, [])
            self.assertEqual(len(manager.valid), 3)


if __name__ == "__main__":
    unittest.main()
