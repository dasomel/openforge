import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "templates" / "scripts" / "validate-behaviors.sh"


class BehaviorValidatorTests(unittest.TestCase):
    def run_validator(self, root: Path):
        return subprocess.run(
            ["bash", str(VALIDATOR), str(root)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_behavior(self, root: Path, directory: str, content: str):
        behavior_dir = root / directory
        behavior_dir.mkdir(parents=True)
        (behavior_dir / "BEHAVIOR.md").write_text(content, encoding="utf-8")

    def test_accepts_valid_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_behavior(
                root,
                "safe-change",
                """---\nname: safe-change\ndescription: Make changes only within justified scope.\n---\n\n# Safe Change\n""",
            )
            result = self.run_validator(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Validated 1 behavior specification", result.stdout)

    def test_rejects_name_directory_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_behavior(
                root,
                "safe-change",
                """---\nname: unsafe-change\ndescription: Example.\n---\n""",
            )
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must match directory", result.stderr)

    def test_rejects_missing_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_behavior(root, "safe-change", "---\nname: safe-change\n---\n")
            result = self.run_validator(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing frontmatter field 'description'", result.stderr)

    def test_rejects_empty_behavior_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_validator(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("No BEHAVIOR.md files found", result.stderr)


if __name__ == "__main__":
    unittest.main()
