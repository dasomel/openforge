from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def active_lines(path: Path) -> list[str]:
    """Return non-empty, non-comment lines outside fenced code blocks."""
    lines: list[str] = []
    fenced = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            continue
        if fenced or not stripped or stripped.startswith("<!--"):
            continue
        lines.append(stripped)
    return lines


class SharedAgentInstructionTests(unittest.TestCase):
    def assert_claude_imports_agents(self, path: Path) -> None:
        self.assertTrue(path.is_file(), f"missing Claude adapter: {path}")
        lines = active_lines(path)
        self.assertIn(
            "@AGENTS.md",
            lines,
            f"{path} must actively import AGENTS.md with @AGENTS.md; a prose/code-block reference is not enough",
        )
        self.assertLessEqual(
            lines.index("@AGENTS.md"),
            1,
            f"{path} should keep @AGENTS.md at the top of the adapter for visibility",
        )

    def test_openforge_root_uses_one_portable_contract(self) -> None:
        self.assertTrue((ROOT / "AGENTS.md").is_file())
        self.assert_claude_imports_agents(ROOT / "CLAUDE.md")

    def test_reusable_claude_template_imports_agents(self) -> None:
        self.assert_claude_imports_agents(ROOT / "templates" / "CLAUDE.md")

    def test_shared_instruction_standard_documents_single_owner(self) -> None:
        text = (ROOT / "docs" / "claude-agents-shared-instructions.md").read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", text)
        self.assertIn("@AGENTS.md", text)
        self.assertIn("do not", text.lower())
        self.assertIn("duplicate", text.lower())


if __name__ == "__main__":
    unittest.main()
