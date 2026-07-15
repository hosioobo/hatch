from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "hatch" / "scripts" / "hatch.py"


class HatchCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "demo"
        self.workbench = self.root / "demo-workbench"
        self.product = self.root / "demo"
        self.evals = self.root / "demo-evals"
        for repo in (self.workbench, self.product, self.evals):
            repo.mkdir(parents=True)
            self.git(repo, "init", "-b", "main")
            self.git(repo, "config", "user.name", "public-author")
            self.git(repo, "config", "user.email", "public@example.invalid")
        (self.root / "hatch.toml").write_text(
            """schema = 1

[repos]
workbench = "demo-workbench"
product = "demo"
evals = "demo-evals"

[records]
briefs = "demo-workbench/promotions"
audits = "demo-evals/audits"
evidence = "demo-evals/evidence"
gates = "demo-evals/gates"

[policy]
audit = "demo-workbench/hatch-policy.toml"
""",
            encoding="utf-8",
        )
        (self.workbench / "hatch-policy.toml").write_text(
            """schema = 1

[identity]
expected_name = "public-author"
expected_email = "public@example.invalid"

[terms]
literal = ["private-name"]
""",
            encoding="utf-8",
        )
        (self.workbench / "idea.txt").write_text("A tracked workbench idea.\n", encoding="utf-8")
        self.commit(self.workbench, "seed workbench")
        (self.product / "product.txt").write_text("A public-safe product.\n", encoding="utf-8")
        (self.product / "VERSION").write_text("0.0.0\n", encoding="utf-8")
        (self.product / "CHANGELOG.md").write_text("# Changelog\n\n", encoding="utf-8")
        self.commit(self.product, "seed product")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            text=True,
            capture_output=True,
        )

    def commit(self, repo: Path, message: str) -> str:
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-m", message)
        return self.git(repo, "rev-parse", "HEAD").stdout.strip()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
        )

    def fill_brief(
        self,
        path: Path,
        target: str | None = None,
        version: str = "0.1.0",
        summary: str = "First public release.",
    ) -> None:
        brief = json.loads(path.read_text(encoding="utf-8"))
        brief.update(
            {
                "state": "planned",
                "intent": "Promote the tracked idea.",
                "in_scope": ["The public implementation."],
                "out_of_scope": ["Private notes."],
                "acceptance": [{"id": "A1", "description": "The product is sufficient."}],
                "evidence_required": [
                    {
                        "id": "E1",
                        "description": "A human review.",
                        "acceptance_ids": ["A1"],
                    }
                ],
                "public_assessment": "No known private material belongs in product.",
                "risk_decisions": [],
                "version": {"target": version, "summary": summary},
            }
        )
        if target is not None:
            brief["product"]["target_commit"] = target
        path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")

    def test_brief_is_pinned_to_a_tracked_snapshot(self) -> None:
        result = self.run_cli(
            "brief",
            "new",
            "--workspace",
            str(self.root),
            "--id",
            "demo-v1",
            "--item",
            "idea.txt",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        brief_path = self.workbench / "promotions" / "demo-v1" / "brief.json"
        self.fill_brief(brief_path)
        checked = self.run_cli(
            "brief",
            "check",
            "--workspace",
            str(self.root),
            "--brief",
            "demo-workbench/promotions/demo-v1/brief.json",
        )
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        (self.workbench / "idea.txt").write_text("Changed but uncommitted.\n", encoding="utf-8")
        checked_again = self.run_cli(
            "brief",
            "check",
            "--workspace",
            str(self.root),
            "--brief",
            "demo-workbench/promotions/demo-v1/brief.json",
        )
        self.assertEqual(checked_again.returncode, 0, checked_again.stdout + checked_again.stderr)

    def test_init_plans_then_creates_independent_repositories(self) -> None:
        parent = Path(self.temporary.name) / "projects"
        parent.mkdir()
        planned = self.run_cli("init", "--parent", str(parent), "--name", "luna")
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertIn("INIT PLAN", planned.stdout)
        root = parent / "luna"
        self.assertFalse(root.exists())
        applied = self.run_cli(
            "init",
            "--parent",
            str(parent),
            "--name",
            "luna",
            "--public-name",
            "public-author",
            "--public-email",
            "public@example.invalid",
            "--apply",
        )
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        self.assertIn("INIT CREATED", applied.stdout)
        for name in ("luna-workbench", "luna-product", "luna-evals"):
            repo = root / name
            self.assertEqual(self.git(repo, "rev-parse", "--show-toplevel").stdout.strip(), str(repo.resolve()))
        self.assertEqual((root / "luna-product" / "VERSION").read_text(encoding="utf-8"), "0.0.0\n")
        self.assertEqual((root / "luna-product" / "CHANGELOG.md").read_text(encoding="utf-8"), "# Changelog\n\n")
        repeated = self.run_cli("init", "--parent", str(parent), "--name", "luna")
        self.assertEqual(repeated.returncode, 1)
        self.assertIn("already exists", repeated.stderr)

    def test_audit_scans_history_without_echoing_the_secret(self) -> None:
        base = self.git(self.product, "rev-parse", "HEAD").stdout.strip()
        secret = "sk-" + "a" * 24
        (self.product / "bad.txt").write_text(secret + "\n", encoding="utf-8")
        target = self.commit(self.product, "add temporary credential")
        (self.product / "bad.txt").unlink()
        target = self.commit(self.product, "remove temporary credential")
        result = self.run_cli(
            "audit",
            "--workspace",
            str(self.root),
            "--repo",
            "product",
            "--ref",
            target,
            "--base",
            base,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("openai-api-key", result.stdout)
        self.assertNotIn(secret, result.stdout + result.stderr)
        report = self.evals / "audits" / f"{target[:12]}.json"
        self.assertNotIn(secret, report.read_text(encoding="utf-8"))

    def test_audit_scans_commit_messages(self) -> None:
        base = self.git(self.product, "rev-parse", "HEAD").stdout.strip()
        (self.product / "public.txt").write_text("Public content.\n", encoding="utf-8")
        target = self.commit(self.product, "mention private-name in the message")
        result = self.run_cli(
            "audit",
            "--workspace",
            str(self.root),
            "--repo",
            "product",
            "--ref",
            target,
            "--base",
            base,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("configured-term at commit message", result.stdout)
        self.assertNotIn("private-name", result.stdout + result.stderr)

    def test_gate_accepts_exact_commit_with_matching_evidence(self) -> None:
        created = self.run_cli(
            "brief",
            "new",
            "--workspace",
            str(self.root),
            "--id",
            "demo-gate",
            "--item",
            "idea.txt",
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        brief_relative = "demo-workbench/promotions/demo-gate/brief.json"
        brief_path = self.root / brief_relative
        self.fill_brief(brief_path)
        applied_version = self.run_cli(
            "version",
            "apply",
            "--workspace",
            str(self.root),
            "--brief",
            brief_relative,
        )
        self.assertEqual(applied_version.returncode, 0, applied_version.stdout + applied_version.stderr)
        target = self.commit(self.product, "publish version 0.1.0")
        self.fill_brief(brief_path, target)
        checked_version = self.run_cli(
            "version",
            "check",
            "--workspace",
            str(self.root),
            "--commit",
            target,
            "--brief",
            brief_relative,
        )
        self.assertEqual(checked_version.returncode, 0, checked_version.stdout + checked_version.stderr)
        audited = self.run_cli(
            "audit",
            "--workspace",
            str(self.root),
            "--repo",
            "product",
            "--ref",
            target,
            "--base",
            "EMPTY",
        )
        self.assertEqual(audited.returncode, 0, audited.stdout + audited.stderr)
        evidence = {
            "schema": 1,
            "kind": "hatch.evidence",
            "target_commit": target,
            "mode": "human",
            "case": "Review the product.",
            "evidence_ids": ["E1"],
            "result": "pass",
            "observations": "The product meets the brief.",
            "artifacts": [],
        }
        unlinked_path = self.evals / "evidence" / "unlinked.json"
        unlinked_path.parent.mkdir(parents=True)
        unlinked_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        unlinked = self.run_cli(
            "gate",
            "--workspace",
            str(self.root),
            "--commit",
            target,
            "--brief",
            brief_relative,
            "--audit",
            f"demo-evals/audits/{target[:12]}.json",
            "--evidence",
            "demo-evals/evidence/unlinked.json",
            "--out",
            "demo-evals/gates/unlinked.json",
        )
        self.assertEqual(unlinked.returncode, 2, unlinked.stdout + unlinked.stderr)
        self.assertIn("evidence-acceptance-ids-invalid:E1", unlinked.stdout)
        evidence["acceptance_ids"] = ["A1"]
        evidence_path = self.evals / "evidence" / "review.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        gated = self.run_cli(
            "gate",
            "--workspace",
            str(self.root),
            "--commit",
            target,
            "--brief",
            brief_relative,
            "--audit",
            f"demo-evals/audits/{target[:12]}.json",
            "--evidence",
            "demo-evals/evidence/review.json",
        )
        self.assertEqual(gated.returncode, 0, gated.stdout + gated.stderr)
        self.assertIn("GATE READY", gated.stdout)


if __name__ == "__main__":
    unittest.main()
