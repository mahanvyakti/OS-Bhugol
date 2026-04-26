from __future__ import annotations

import unittest
from pathlib import Path

import build_homepage_index as builder


class BuildHomepageIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.manifest, cls.map_geojson = builder.build_payload(cls.repo_root)

    def test_discovers_expected_municipalities(self):
        names = {item["name"] for item in self.manifest["municipalities"]}
        self.assertIn("Pune Municipal Corporation", names)
        self.assertIn("Parbhani Municipal Corporation", names)
        self.assertTrue(any("Nanded" in name for name in names))

    def test_geometry_source_policy(self):
        for municipality in self.manifest["municipalities"]:
            self.assertIn(municipality["map"]["geometry_source"], {"boundary", "dissolved_wards"})

    def test_no_ward_paths_in_map_geometry_path(self):
        for municipality in self.manifest["municipalities"]:
            if municipality["map"]["geometry_source"] == "boundary":
                continue
            self.assertIn("ward", municipality["map"]["geometry_path"].lower())

    def test_manifest_paths_exist(self):
        for municipality in self.manifest["municipalities"]:
            root = self.repo_root / municipality["paths"]["root"]
            self.assertTrue(root.exists())

            if municipality["paths"]["meta"]:
                self.assertTrue((self.repo_root / municipality["paths"]["meta"]).is_file())

            if municipality["paths"]["boundary"]:
                self.assertTrue((self.repo_root / municipality["paths"]["boundary"]).is_file())

            for path in municipality["paths"]["wards"]:
                self.assertTrue((self.repo_root / path).is_file())

    def test_map_feature_count_matches_manifest(self):
        self.assertEqual(
            len(self.map_geojson["features"]),
            len(self.manifest["municipalities"]),
        )


if __name__ == "__main__":
    unittest.main()
