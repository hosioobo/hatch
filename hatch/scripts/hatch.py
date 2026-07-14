#!/usr/bin/env python3
"""Create and verify the durable records used by a Hatch workspace.

This tool deliberately does not copy source, commit, push, release, or deploy.
It only writes explicitly requested records below the private record roots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA = 1
MAX_TEXT_BYTES = 1_000_000
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
REQUIREMENT_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")


class HatchError(Exception):
    """Report a safe, user-actionable error without leaking scanned data."""


@dataclass(frozen=True)
class Workspace:
    root: Path
    workbench: Path
    product: Path
    evals: Path
    briefs: Path
    audits: Path
    evidence: Path
    gates: Path
    policy: Path | None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(128 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_json_constant,
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise HatchError(f"Could not read valid JSON: {path.name}") from exc
    if not isinstance(loaded, dict):
        raise HatchError(f"JSON record must be an object: {path.name}")
    return loaded


def write_json_new(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise HatchError(f"Refusing to overwrite existing record: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise HatchError("Refusing to write through a symlinked record directory")
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded)
        os.replace(temporary, path)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise HatchError(f"Could not write record: {path.name}") from exc


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_relative(root: Path, value: str, label: str, *, must_exist: bool = False) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise HatchError(f"{label} must be a relative path inside the workspace")
    resolved = (root / candidate).resolve(strict=False)
    if not is_within(resolved, root):
        raise HatchError(f"{label} resolves outside the workspace")
    if must_exist and not resolved.exists():
        raise HatchError(f"{label} does not exist")
    return resolved


def config_string(table: dict[str, Any], key: str, label: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value:
        raise HatchError(f"hatch.toml requires {label}")
    return value


def load_workspace(root_value: str) -> Workspace:
    root = Path(root_value).expanduser().resolve(strict=False)
    marker = root / "hatch.toml"
    if not marker.is_file() or marker.is_symlink():
        raise HatchError("Workspace must contain a regular hatch.toml marker")
    try:
        config = tomllib.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise HatchError("Could not read hatch.toml") from exc
    if config.get("schema") != SCHEMA:
        raise HatchError("Unsupported hatch.toml schema")
    repos = config.get("repos")
    records = config.get("records")
    if not isinstance(repos, dict) or not isinstance(records, dict):
        raise HatchError("hatch.toml requires [repos] and [records]")
    workbench = resolve_relative(root, config_string(repos, "workbench", "repos.workbench"), "workbench")
    product = resolve_relative(root, config_string(repos, "product", "repos.product"), "product")
    evals = resolve_relative(root, config_string(repos, "evals", "repos.evals"), "evals")
    for name, path in (("workbench", workbench), ("product", product), ("evals", evals)):
        if not path.is_dir() or path.is_symlink():
            raise HatchError(f"Configured {name} must be a regular directory")
        if not (path / ".git").exists():
            raise HatchError(f"Configured {name} is not a Git repository")
    briefs = resolve_relative(root, config_string(records, "briefs", "records.briefs"), "briefs")
    audits = resolve_relative(root, config_string(records, "audits", "records.audits"), "audits")
    evidence = resolve_relative(root, config_string(records, "evidence", "records.evidence"), "evidence")
    gates = resolve_relative(root, config_string(records, "gates", "records.gates"), "gates")
    policy: Path | None = None
    policy_table = config.get("policy", {})
    if policy_table:
        if not isinstance(policy_table, dict):
            raise HatchError("[policy] must be a table")
        policy_value = policy_table.get("audit")
        if policy_value is not None:
            if not isinstance(policy_value, str):
                raise HatchError("policy.audit must be a relative path")
            policy = resolve_relative(root, policy_value, "policy.audit", must_exist=True)
            if policy.is_symlink():
                raise HatchError("policy.audit must not be a symlink")
    return Workspace(root, workbench, product, evals, briefs, audits, evidence, gates, policy)


def git_result(repo: Path, args: list[str]) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["LC_ALL"] = "C"
    return subprocess.run(
        ["git", "-C", str(repo), "--no-pager", *args],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=environment,
    )


def git(repo: Path, *args: str) -> bytes:
    result = git_result(repo, list(args))
    if result.returncode != 0:
        raise HatchError(f"Git operation failed: {args[0] if args else 'unknown'}")
    return result.stdout


def git_commit(repo: Path, ref: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode("ascii").strip()


def git_head_or_none(repo: Path) -> str | None:
    result = git_result(repo, ["rev-parse", "--verify", "HEAD^{commit}"])
    return result.stdout.decode("ascii").strip() if result.returncode == 0 else None


def git_tree(repo: Path, commit: str) -> str:
    return git(repo, "rev-parse", "--verify", f"{commit}^{{tree}}").decode("ascii").strip()


def git_is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    result = git_result(repo, ["merge-base", "--is-ancestor", ancestor, descendant])
    if result.returncode in (0, 1):
        return result.returncode == 0
    raise HatchError("Git ancestry check failed")


def git_relative_path(value: str, label: str) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or value in ("", "."):
        raise HatchError(f"{label} must be a non-empty repository-relative path")
    return path.as_posix()


def parse_tree_entries(raw: bytes) -> list[tuple[str, str, str, str]]:
    entries: list[tuple[str, str, str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            left, raw_path = record.split(b"\t", 1)
            mode, kind, object_id = left.decode("ascii").split(" ", 2)
            path = raw_path.decode("utf-8", "surrogateescape")
        except (ValueError, UnicodeDecodeError) as exc:
            raise HatchError("Could not parse Git tree entry") from exc
        entries.append((mode, kind, object_id, path))
    return entries


def tree_entry(repo: Path, commit: str, relative_path: str) -> tuple[str, str, str, str]:
    entries = parse_tree_entries(git(repo, "ls-tree", "-z", commit, "--", relative_path))
    if len(entries) != 1 or entries[0][3] != relative_path:
        raise HatchError(f"Source item is not tracked at its snapshot: {relative_path}")
    return entries[0]


def safe_output(workspace: Workspace, root: Path, value: str | None, default: Path) -> Path:
    candidate = default if value is None else resolve_relative(workspace.root, value, "output path")
    resolved_root = root.resolve(strict=False)
    resolved_candidate = candidate.resolve(strict=False)
    if not is_within(resolved_candidate, resolved_root):
        raise HatchError("Output path must stay inside its configured record directory")
    return resolved_candidate


def record_relative(workspace: Workspace, path: Path) -> str:
    return path.resolve(strict=False).relative_to(workspace.root).as_posix()


def brief_output(workspace: Workspace, brief_id: str, value: str | None) -> Path:
    return safe_output(workspace, workspace.briefs, value, workspace.briefs / brief_id / "brief.json")


def validate_text(value: Any, label: str, issues: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        issues.append(f"missing {label}")


def validate_requirement_list(
    value: Any, label: str, issues: list[str], *, evidence: bool = False
) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list) or not value:
        issues.append(f"missing {label}")
        return ids
    for item in value:
        if not isinstance(item, dict):
            issues.append(f"invalid {label} item")
            continue
        identifier = item.get("id")
        description = item.get("description")
        if not isinstance(identifier, str) or not REQUIREMENT_ID_RE.fullmatch(identifier):
            issues.append(f"invalid {label} id")
            continue
        if identifier in ids:
            issues.append(f"duplicate {label} id: {identifier}")
        ids.add(identifier)
        validate_text(description, f"{label} description", issues)
        if evidence:
            acceptance_ids = item.get("acceptance_ids")
            if not isinstance(acceptance_ids, list) or not all(
                isinstance(entry, str) for entry in acceptance_ids
            ):
                issues.append(f"invalid {label} acceptance_ids")
            if "allow_not_applicable" in item and not isinstance(item["allow_not_applicable"], bool):
                issues.append(f"invalid {label} allow_not_applicable")
    return ids


def validate_brief(
    workspace: Workspace, brief: dict[str, Any], *, complete: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    incomplete: list[str] = []
    if brief.get("schema") != SCHEMA or brief.get("kind") != "hatch.brief":
        errors.append("unsupported brief schema or kind")
    identifier = brief.get("id")
    if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
        errors.append("invalid brief id")
    source = brief.get("source")
    if not isinstance(source, dict):
        errors.append("missing source")
    else:
        commit = source.get("commit")
        tree = source.get("tree")
        items = source.get("items")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            errors.append("invalid source commit")
        if not isinstance(tree, str) or not re.fullmatch(r"[0-9a-f]{40}", tree):
            errors.append("invalid source tree")
        if not isinstance(items, list) or not items:
            errors.append("missing source items")
        elif not errors:
            try:
                if git_tree(workspace.workbench, commit) != tree:
                    errors.append("source tree does not match source commit")
                for item in items:
                    if not isinstance(item, dict):
                        errors.append("invalid source item")
                        continue
                    path = item.get("path")
                    digest = item.get("sha256")
                    if not isinstance(path, str) or not isinstance(digest, str):
                        errors.append("invalid source item fields")
                        continue
                    relative_path = git_relative_path(path, "source item")
                    mode, kind, object_id, _ = tree_entry(workspace.workbench, commit, relative_path)
                    if kind != "blob" or mode != "100644":
                        errors.append(f"unsupported source item type: {relative_path}")
                        continue
                    if sha256_bytes(git(workspace.workbench, "cat-file", "blob", object_id)) != digest:
                        errors.append(f"source hash changed: {relative_path}")
            except HatchError as exc:
                errors.append(str(exc))
    product = brief.get("product")
    if not isinstance(product, dict):
        errors.append("missing product")
    else:
        for key in ("base_commit", "target_commit"):
            value = product.get(key)
            if value is not None and (not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value)):
                errors.append(f"invalid product {key}")
    if complete:
        validate_text(brief.get("intent"), "intent", incomplete)
        for key in ("in_scope", "out_of_scope"):
            value = brief.get(key)
            if not isinstance(value, list):
                incomplete.append(f"missing {key}")
            elif key == "in_scope" and not value:
                incomplete.append("missing in_scope")
        acceptance_ids = validate_requirement_list(brief.get("acceptance"), "acceptance", incomplete)
        evidence_ids = validate_requirement_list(
            brief.get("evidence_required"), "evidence requirement", incomplete, evidence=True
        )
        if evidence_ids and acceptance_ids:
            for requirement in brief["evidence_required"]:
                for acceptance_id in requirement.get("acceptance_ids", []):
                    if acceptance_id not in acceptance_ids:
                        incomplete.append(f"unknown acceptance id: {acceptance_id}")
        validate_text(brief.get("public_assessment"), "public_assessment", incomplete)
        if not isinstance(brief.get("risk_decisions"), list):
            incomplete.append("missing risk_decisions")
    return errors, incomplete


def command_brief_new(args: argparse.Namespace) -> int:
    workspace = load_workspace(args.workspace)
    if not ID_RE.fullmatch(args.id):
        raise HatchError("brief id must use lowercase letters, digits, dots, underscores, or hyphens")
    head = git_head_or_none(workspace.workbench)
    if head is None:
        raise HatchError("Workbench needs a committed snapshot before creating a brief")
    tree = git_tree(workspace.workbench, head)
    items: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_path in args.item:
        relative_path = git_relative_path(raw_path, "source item")
        if relative_path in seen:
            raise HatchError(f"Duplicate source item: {relative_path}")
        seen.add(relative_path)
        mode, kind, object_id, _ = tree_entry(workspace.workbench, head, relative_path)
        if kind != "blob" or mode != "100644":
            raise HatchError(f"Source item must be a regular tracked file: {relative_path}")
        content = git(workspace.workbench, "cat-file", "blob", object_id)
        items.append({"path": relative_path, "sha256": sha256_bytes(content)})
    if not items:
        raise HatchError("At least one --item is required")
    product_head = git_head_or_none(workspace.product)
    brief = {
        "schema": SCHEMA,
        "kind": "hatch.brief",
        "id": args.id,
        "state": "draft",
        "source": {"repo": "workbench", "commit": head, "tree": tree, "items": items},
        "product": {"base_commit": product_head, "target_commit": None},
        "intent": "",
        "in_scope": [],
        "out_of_scope": [],
        "acceptance": [],
        "evidence_required": [],
        "public_assessment": "",
        "risk_decisions": [],
    }
    output = brief_output(workspace, args.id, args.out)
    write_json_new(output, brief)
    print(f"BRIEF CREATED {record_relative(workspace, output)}")
    return 0


def command_brief_check(args: argparse.Namespace) -> int:
    workspace = load_workspace(args.workspace)
    path = safe_output(workspace, workspace.briefs, args.brief, workspace.briefs / "unused")
    if not path.is_file() or path.is_symlink():
        raise HatchError("Brief must be a regular file inside records.briefs")
    errors, incomplete = validate_brief(workspace, read_json(path), complete=True)
    if errors:
        print("BRIEF ERROR")
        for issue in errors:
            print(f"- {issue}")
        return 1
    if incomplete:
        print("BRIEF INCOMPLETE")
        for issue in sorted(set(incomplete)):
            print(f"- {issue}")
        return 2
    print("BRIEF COMPLETE")
    return 0


def load_policy(workspace: Workspace) -> tuple[dict[str, Any], str | None]:
    if workspace.policy is None:
        return {}, None
    try:
        raw = workspace.policy.read_bytes()
        policy = tomllib.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise HatchError("Could not read audit policy") from exc
    if policy.get("schema") != SCHEMA:
        raise HatchError("Unsupported audit policy schema")
    return policy, sha256_bytes(raw)


def configured_terms(policy: dict[str, Any]) -> list[str]:
    terms = policy.get("terms", {})
    literals = terms.get("literal", []) if isinstance(terms, dict) else []
    if not isinstance(literals, list) or not all(isinstance(value, str) and value for value in literals):
        raise HatchError("Audit policy terms.literal must be a list of non-empty strings")
    return literals


def make_finding(rule: str, severity: str, object_id: str, path: str | None, line: int | None) -> dict[str, Any]:
    stable = "|".join((rule, object_id, path or "", str(line or 0))).encode("utf-8", "surrogateescape")
    return {
        "id": hashlib.sha256(stable).hexdigest()[:16],
        "rule": rule,
        "severity": severity,
        "object": object_id,
        "path": path,
        "line": line,
    }


TEXT_RULES: list[tuple[str, str, re.Pattern[str]]] = [
    ("private-key", "fail", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("github-token", "fail", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai-api-key", "fail", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("aws-access-key", "fail", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("absolute-path", "warn", re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/")),
]


def line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def scan_text(
    text: str,
    object_id: str,
    path: str | None,
    terms: Iterable[str],
    findings: list[dict[str, Any]],
) -> None:
    for rule, severity, pattern in TEXT_RULES:
        match = pattern.search(text)
        if match:
            findings.append(make_finding(rule, severity, object_id, path, line_for(text, match.start())))
    for term in terms:
        offset = text.find(term)
        if offset >= 0:
            findings.append(make_finding("configured-term", "warn", object_id, path, line_for(text, offset)))


def scan_path(path: str, object_id: str, terms: Iterable[str], findings: list[dict[str, Any]]) -> None:
    parts = Path(path).parts
    if any(part == ".env" or part.startswith(".env.") for part in parts):
        findings.append(make_finding("dotenv-path", "fail", object_id, path, None))
    for term in terms:
        if term in path:
            findings.append(make_finding("configured-term", "warn", object_id, path, None))


def commit_metadata(repo: Path, commit: str) -> tuple[str, str, str, str, str]:
    raw = git(repo, "show", "-s", "--format=%B%x00%an%x00%ae%x00%cn%x00%ce", commit)
    parts = raw.split(b"\0")
    if len(parts) < 5:
        raise HatchError("Could not read commit metadata")
    message = parts[0].decode("utf-8", "replace")
    identity = tuple(part.decode("utf-8", "replace").strip() for part in parts[1:5])
    return (message, *identity)  # type: ignore[return-value]


def audit_commits(repo: Path, ref: str, base: str | None) -> tuple[list[str], str, list[dict[str, str]]]:
    gaps: list[dict[str, str]] = []
    if base is None:
        return [ref], "snapshot_only", [{"kind": "history", "reason": "base-not-provided"}]
    if base == "EMPTY":
        return git(repo, "rev-list", ref).decode("ascii").splitlines(), "history", gaps
    base_commit = git_commit(repo, base)
    if not git_is_ancestor(repo, base_commit, ref):
        raise HatchError("Audit base must be an ancestor of the target commit")
    commits = git(repo, "rev-list", f"{base_commit}..{ref}").decode("ascii").splitlines()
    return commits, "history", gaps


def command_audit(args: argparse.Namespace) -> int:
    workspace = load_workspace(args.workspace)
    if args.repo != "product":
        raise HatchError("V1 audit supports only --repo product")
    ref = git_commit(workspace.product, args.ref)
    base_value: str | None = args.base
    base_commit: str | None
    if base_value not in (None, "EMPTY"):
        base_commit = git_commit(workspace.product, base_value)
    else:
        base_commit = base_value
    policy, policy_hash = load_policy(workspace)
    terms = configured_terms(policy)
    commits, coverage, gaps = audit_commits(workspace.product, ref, base_commit)
    findings: list[dict[str, Any]] = []
    identity = policy.get("identity", {}) if isinstance(policy.get("identity", {}), dict) else {}
    expected_name = identity.get("expected_name")
    expected_email = identity.get("expected_email")
    if expected_name is not None and not isinstance(expected_name, str):
        raise HatchError("identity.expected_name must be a string")
    if expected_email is not None and not isinstance(expected_email, str):
        raise HatchError("identity.expected_email must be a string")
    blob_paths: dict[tuple[str, str], None] = {}
    for commit in commits:
        message, author_name, author_email, committer_name, committer_email = commit_metadata(
            workspace.product, commit
        )
        scan_text(message, commit, None, terms, findings)
        scan_text(author_name, commit, None, terms, findings)
        scan_text(author_email, commit, None, terms, findings)
        scan_text(committer_name, commit, None, terms, findings)
        scan_text(committer_email, commit, None, terms, findings)
        if expected_name and (author_name != expected_name or committer_name != expected_name):
            findings.append(make_finding("identity-name-mismatch", "warn", commit, None, None))
        if expected_email and (author_email != expected_email or committer_email != expected_email):
            findings.append(make_finding("identity-email-mismatch", "warn", commit, None, None))
        for mode, kind, object_id, path in parse_tree_entries(git(workspace.product, "ls-tree", "-r", "-z", commit)):
            if kind == "commit" or mode in ("120000", "160000"):
                gaps.append({"kind": "git-entry", "object": object_id, "path": path, "reason": "unsupported"})
                continue
            if kind != "blob":
                gaps.append({"kind": "git-entry", "object": object_id, "path": path, "reason": "non-blob"})
                continue
            blob_paths[(object_id, path)] = None
    for object_id, path in blob_paths:
        scan_path(path, object_id, terms, findings)
        data = git(workspace.product, "cat-file", "blob", object_id)
        if len(data) > MAX_TEXT_BYTES:
            gaps.append({"kind": "blob", "object": object_id, "path": path, "reason": "oversized"})
            continue
        if b"\0" in data:
            gaps.append({"kind": "blob", "object": object_id, "path": path, "reason": "binary"})
            continue
        text = data.decode("utf-8", "replace")
        if text.startswith("version https://git-lfs.github.com/spec/v1"):
            gaps.append({"kind": "blob", "object": object_id, "path": path, "reason": "lfs-pointer"})
            continue
        scan_text(text, object_id, path, terms, findings)
    deduplicated = {finding["id"]: finding for finding in findings}
    findings = [deduplicated[key] for key in sorted(deduplicated)]
    severities = {finding["severity"] for finding in findings}
    status = "fail" if "fail" in severities else "warn" if "warn" in severities or gaps else "pass"
    report = {
        "schema": SCHEMA,
        "kind": "hatch.audit",
        "target_commit": ref,
        "target_tree": git_tree(workspace.product, ref),
        "base": base_commit,
        "coverage": coverage,
        "policy_hash": policy_hash,
        "findings": findings,
        "coverage_gaps": gaps,
        "status": status,
    }
    output = safe_output(
        workspace,
        workspace.audits,
        args.out,
        workspace.audits / f"{ref[:12]}.json",
    )
    write_json_new(output, report)
    print(f"AUDIT {status.upper()} {record_relative(workspace, output)}")
    for finding in findings:
        location = finding["path"] or "commit metadata"
        suffix = f":{finding['line']}" if finding["line"] else ""
        print(f"- {finding['severity']} {finding['rule']} at {location}{suffix}")
    for gap in gaps:
        print(f"- coverage-gap {gap['reason']} at {gap.get('path', 'history')}")
    return 0 if status == "pass" else 2


def input_record(workspace: Workspace, root: Path, value: str, label: str) -> Path:
    path = resolve_relative(workspace.root, value, label, must_exist=True)
    if not is_within(path.resolve(), root.resolve()) or not path.is_file() or path.is_symlink():
        raise HatchError(f"{label} must be a regular file inside its record directory")
    return path


def risk_decision_ids(brief: dict[str, Any]) -> set[str]:
    decisions = brief.get("risk_decisions", [])
    result: set[str] = set()
    if not isinstance(decisions, list):
        return result
    for decision in decisions:
        if isinstance(decision, dict) and isinstance(decision.get("finding_id"), str):
            result.add(decision["finding_id"])
    return result


def validate_artifacts(workspace: Workspace, record: dict[str, Any], reasons: list[str]) -> None:
    artifacts = record.get("artifacts", [])
    if not isinstance(artifacts, list):
        reasons.append("evidence-artifacts-invalid")
        return
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            reasons.append("evidence-artifact-invalid")
            continue
        path_value = artifact.get("path")
        digest = artifact.get("sha256")
        if not isinstance(path_value, str) or not isinstance(digest, str):
            reasons.append("evidence-artifact-invalid")
            continue
        try:
            path = resolve_relative(workspace.evals, path_value, "evidence artifact", must_exist=True)
        except HatchError:
            reasons.append("evidence-artifact-unavailable")
            continue
        if path.is_symlink() or not path.is_file() or sha256_file(path) != digest:
            reasons.append("evidence-artifact-mismatch")


def command_gate(args: argparse.Namespace) -> int:
    workspace = load_workspace(args.workspace)
    target = git_commit(workspace.product, args.commit)
    target_tree = git_tree(workspace.product, target)
    brief_path = input_record(workspace, workspace.briefs, args.brief, "brief")
    audit_path = input_record(workspace, workspace.audits, args.audit, "audit")
    brief = read_json(brief_path)
    audit = read_json(audit_path)
    reasons: list[str] = []
    warnings: list[str] = []
    errors, incomplete = validate_brief(workspace, brief, complete=True)
    reasons.extend(f"brief-{issue.replace(' ', '-')}" for issue in errors + incomplete)
    product = brief.get("product", {}) if isinstance(brief.get("product", {}), dict) else {}
    if product.get("target_commit") != target:
        reasons.append("brief-target-commit-mismatch")
    base_commit = product.get("base_commit")
    if isinstance(base_commit, str) and not git_is_ancestor(workspace.product, base_commit, target):
        reasons.append("brief-base-is-not-ancestor")
    policy, policy_hash = load_policy(workspace)
    if audit.get("kind") != "hatch.audit" or audit.get("schema") != SCHEMA:
        reasons.append("invalid-audit-record")
    if audit.get("target_commit") != target or audit.get("target_tree") != target_tree:
        reasons.append("audit-target-mismatch")
    if audit.get("coverage") != "history":
        reasons.append("audit-history-coverage-required")
    if audit.get("policy_hash") != policy_hash:
        reasons.append("audit-policy-mismatch")
    coverage_gaps = audit.get("coverage_gaps", [])
    if coverage_gaps:
        reasons.append("audit-coverage-gap")
    findings = audit.get("findings", [])
    if not isinstance(findings, list):
        reasons.append("audit-findings-invalid")
        findings = []
    accepted_risks = risk_decision_ids(brief)
    for finding in findings:
        if not isinstance(finding, dict):
            reasons.append("audit-finding-invalid")
            continue
        finding_id = finding.get("id")
        severity = finding.get("severity")
        if severity == "fail":
            reasons.append("audit-failure")
        elif severity == "warn":
            if isinstance(finding_id, str) and finding_id in accepted_risks:
                warnings.append(f"accepted-risk:{finding_id}")
            else:
                reasons.append("audit-warning-unresolved")
    evidence_paths: list[Path] = []
    for value in args.evidence:
        evidence_paths.append(input_record(workspace, workspace.evidence, value, "evidence"))
    evidence_records: list[tuple[Path, dict[str, Any]]] = [(path, read_json(path)) for path in evidence_paths]
    requirements = brief.get("evidence_required", [])
    if not isinstance(requirements, list):
        requirements = []
    evidence_summary: list[dict[str, Any]] = []
    for path, record in evidence_records:
        evidence_summary.append(
            {
                "path": record_relative(workspace, path),
                "sha256": sha256_file(path),
                "result": record.get("result"),
            }
        )
    for requirement in requirements:
        if not isinstance(requirement, dict) or not isinstance(requirement.get("id"), str):
            reasons.append("invalid-evidence-requirement")
            continue
        requirement_id = requirement["id"]
        required_acceptance_ids = requirement.get("acceptance_ids")
        if not isinstance(required_acceptance_ids, list) or not all(
            isinstance(acceptance_id, str) for acceptance_id in required_acceptance_ids
        ):
            reasons.append("invalid-evidence-requirement")
            continue
        required_acceptance = set(required_acceptance_ids)
        satisfying = False
        failed = False
        linkage_errors: list[str] = []
        for _, record in evidence_records:
            if record.get("schema") != SCHEMA or record.get("kind") != "hatch.evidence":
                continue
            if record.get("target_commit") != target:
                continue
            evidence_ids = record.get("evidence_ids", [])
            if not isinstance(evidence_ids, list) or requirement_id not in evidence_ids:
                continue
            acceptance_ids = record.get("acceptance_ids")
            if not isinstance(acceptance_ids, list) or not all(
                isinstance(acceptance_id, str) for acceptance_id in acceptance_ids
            ):
                linkage_errors.append(f"evidence-acceptance-ids-invalid:{requirement_id}")
                continue
            if not required_acceptance.issubset(set(acceptance_ids)):
                linkage_errors.append(f"evidence-acceptance-link-mismatch:{requirement_id}")
                continue
            result = record.get("result")
            if result == "pass":
                artifact_reasons: list[str] = []
                validate_artifacts(workspace, record, artifact_reasons)
                if artifact_reasons:
                    reasons.extend(artifact_reasons)
                else:
                    satisfying = True
            elif result == "not-applicable":
                if requirement.get("allow_not_applicable") is True and isinstance(record.get("observations"), str) and record["observations"].strip():
                    satisfying = True
                else:
                    reasons.append("evidence-not-applicable-not-allowed")
            elif result == "fail":
                failed = True
        if failed:
            reasons.append(f"evidence-failed:{requirement_id}")
        elif not satisfying:
            reasons.append(f"missing-evidence:{requirement_id}")
            reasons.extend(linkage_errors)
    unique_reasons = sorted(set(reasons))
    if not unique_reasons:
        status = "ready"
    elif all(
        reason.startswith(
            (
                "missing-evidence",
                "evidence-failed",
                "evidence-not-applicable",
                "evidence-acceptance-",
            )
        )
        for reason in unique_reasons
    ):
        status = "needs-evidence"
    else:
        status = "blocked"
    report = {
        "schema": SCHEMA,
        "kind": "hatch.gate",
        "target_commit": target,
        "target_tree": target_tree,
        "status": status,
        "brief": {"path": record_relative(workspace, brief_path), "sha256": sha256_file(brief_path)},
        "audit": {"path": record_relative(workspace, audit_path), "sha256": sha256_file(audit_path)},
        "evidence": evidence_summary,
        "blocking_reasons": unique_reasons,
        "warnings": sorted(set(warnings)),
    }
    brief_id = brief.get("id", "gate") if isinstance(brief.get("id"), str) else "gate"
    output = safe_output(
        workspace,
        workspace.gates,
        args.out,
        workspace.gates / f"{target[:12]}-{brief_id}.json",
    )
    write_json_new(output, report)
    print(f"GATE {status.upper()} {record_relative(workspace, output)}")
    for reason in unique_reasons:
        print(f"- {reason}")
    return 0 if status == "ready" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    brief = subparsers.add_parser("brief", help="create or check promotion briefs")
    brief_subparsers = brief.add_subparsers(dest="brief_command", required=True)
    brief_new = brief_subparsers.add_parser("new", help="create a source-pinned draft brief")
    brief_new.add_argument("--workspace", required=True)
    brief_new.add_argument("--id", required=True)
    brief_new.add_argument("--item", action="append", default=[])
    brief_new.add_argument("--out")
    brief_new.set_defaults(handler=command_brief_new)
    brief_check = brief_subparsers.add_parser("check", help="validate a promotion brief")
    brief_check.add_argument("--workspace", required=True)
    brief_check.add_argument("--brief", required=True)
    brief_check.set_defaults(handler=command_brief_check)
    audit = subparsers.add_parser("audit", help="scan a product commit or history range")
    audit.add_argument("--workspace", required=True)
    audit.add_argument("--repo", required=True, choices=["product"])
    audit.add_argument("--ref", default="HEAD")
    audit.add_argument("--base", help="ancestor commit, or EMPTY for all reachable history")
    audit.add_argument("--out")
    audit.set_defaults(handler=command_audit)
    gate = subparsers.add_parser("gate", help="check a commit against brief, audit, and evidence")
    gate.add_argument("--workspace", required=True)
    gate.add_argument("--commit", required=True)
    gate.add_argument("--brief", required=True)
    gate.add_argument("--audit", required=True)
    gate.add_argument("--evidence", action="append", default=[])
    gate.add_argument("--out")
    gate.set_defaults(handler=command_gate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except HatchError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
