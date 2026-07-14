from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "hatch" / "SKILL.md"
INTERFACE = ROOT / "hatch" / "agents" / "openai.yaml"


class SkillStructureTests(unittest.TestCase):
    def test_required_skill_metadata_is_present_and_complete(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)
        self.assertIn("name: hatch", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertNotIn("TODO", text)
        self.assertIn("hatch.toml", body)
        self.assertIn("Never create a second completed-product copy", body)

    def test_ui_metadata_mentions_the_exact_skill_name(self) -> None:
        text = INTERFACE.read_text(encoding="utf-8")
        self.assertIn('display_name: "Hatch / 해치"', text)
        self.assertIn("$hatch", text)


if __name__ == "__main__":
    unittest.main()
