import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "templates" / "scripts" / "check-mutable-inputs.py"
spec = importlib.util.spec_from_file_location("mutable_guard", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MutableInputGuardTests(unittest.TestCase):
    def test_accepts_pinned_action_and_versioned_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "workflow.yml"
            p.write_text(
                "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
                "image: aquasec/trivy:0.69.3\n",
                encoding="utf-8",
            )
            self.assertEqual(module.scan_file(p), [])

    def test_rejects_latest_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "values.yml"
            p.write_text("image: aquasec/trivy:latest\n", encoding="utf-8")
            failures = module.scan_file(p)
            self.assertTrue(any(item[1] == "container latest tag" for item in failures))

    def test_rejects_latest_release_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "install.sh"
            p.write_text("curl -L https://github.com/acme/tool/releases/latest/download/tool\n", encoding="utf-8")
            failures = module.scan_file(p)
            self.assertTrue(any(item[1] == "latest release download" for item in failures))

    def test_rejects_floating_action_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "workflow.yml"
            p.write_text("uses: actions/checkout@v4\n", encoding="utf-8")
            failures = module.scan_file(p)
            self.assertTrue(any("40-char commit SHA" in item[1] for item in failures))

    def test_ignores_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "notes.yml"
            p.write_text("# old example: image: demo:latest\n", encoding="utf-8")
            self.assertEqual(module.scan_file(p), [])


if __name__ == "__main__":
    unittest.main()
