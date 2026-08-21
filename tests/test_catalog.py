from pathlib import Path
import json
import unittest


ROOT = Path(__file__).parents[1]


class CatalogTests(unittest.TestCase):
    def test_domain_engine_ids_are_unique_and_status_is_explicit(self):
        value = json.loads((ROOT / "catalog/domain-engines.json").read_text(encoding="utf-8"))
        engines = value["engines"]
        ids = [item["plugin_id"] for item in engines]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item["status"] in {"source_pinned", "architecture_only", "planned"} for item in engines))

    def test_source_pinned_engines_have_exact_commits(self):
        value = json.loads((ROOT / "catalog/domain-engines.json").read_text(encoding="utf-8"))
        for engine in value["engines"]:
            if engine["status"] == "source_pinned":
                self.assertEqual(len(engine["commit"]), 40)
                int(engine["commit"], 16)

    def test_architecture_only_engines_are_not_misrepresented_as_repositories(self):
        value = json.loads((ROOT / "catalog/domain-engines.json").read_text(encoding="utf-8"))
        for engine in value["engines"]:
            if engine["status"] != "source_pinned":
                self.assertNotIn("repository", engine)


if __name__ == "__main__":
    unittest.main()
