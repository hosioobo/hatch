---
name: hatch
description: Create or manage a Hatch lifecycle workspace when a project needs a private workbench, a public-safe product repo, and evidence for publication: initialize a new workspace or promote selected work into a public-ready product snapshot with a brief, audit, version log, evidence, and readiness check. Use for an explicit `$hatch` lifecycle request, or implicitly only inside a workspace with a `hatch.toml` marker and one of those lifecycle intents. Do not use for ordinary coding, builds, tests, Git operations, deployments/releases, generic skill creation or installation, or Codex animated-pet work. Bootstrap Hatch itself only after an explicit self-hosting request.
---

# Hatch

## Overview

Use Hatch to keep exploratory work, canonical product source, and real-world
evidence distinct. Treat promotion as a deliberate decision backed by one
concise brief, not as synchronization between repositories.

## Start a project

For a new project, resolve the container path, lowercase workspace name, and
public Git identity. Run `scripts/hatch.py init` to create the workspace. Use
`--dry-run` only when the user asks to inspect the planned paths first.

`init` creates a local container, independent workbench/product/evals Git
repositories, a private audit policy, `VERSION` at `0.0.0`, and an empty
`CHANGELOG.md`. It never creates a remote, commits, pushes, releases, or
deploys. Do not use it to reorganize an existing project.

## Resolve the workspace

- Read `hatch.toml` before acting. Resolve its `workbench`, `product`, and
  `evals` paths relative to the marker directory.
- Require both a valid marker and a clear lifecycle intent before inferring
  Hatch. Otherwise, use the ordinary relevant skill or workflow.
- Treat `workbench` as private and disposable, `product` as the sole
  canonical public-safe source, and `evals` as the private record of real use.
  Preserve exploratory artifacts there; a commit-bound `hatch.evidence` record
  always names an exact product commit.
- Keep product tests distinct from evidence. Tests may contribute evidence;
  human observations, generated outputs, screenshots, and failure cases may
  contribute too.
- Never create a second completed-product copy, auto-sync workbench into
  product, auto-commit, push, release, or deploy.

## Recognize lifecycle intents

Use Hatch for clear requests such as:

- "이 실험을 product로 올릴 준비해줘."
- "이 계획대로 product에 반영해줘."
- "이 결과를 evidence에 남기고 평가해줘."
- "이 commit 공개 전 점검해줘."
- "새 프로젝트용 Hatch workspace를 만들어줘."
- "이번 공개 버전을 정리해줘."

Do not infer Hatch from "build", "test", "review", "commit", "publish", or
"deploy" alone.

## Promote

1. Inspect the candidate, product state, and relevant evidence without changing
   product.
2. Create or update one private Promotion Brief with
   `scripts/hatch.py brief new` and
   [promotion-brief.md](references/promotion-brief.md). Infer its draft from
   the work already done; ask only about genuinely ambiguous scope, exclusions,
   acceptance evidence, or public provenance. Run `scripts/hatch.py brief check`.
3. Present the brief, expected product impact, exclusions, and required
   evidence. Do not apply the promotion without an explicit confirmation such
   as "이 계획대로 반영해줘."
4. After confirmation, implement only the approved scope in product. Adapt or
   reimplement workbench code when appropriate; never blindly copy or sync it.
5. For a public candidate, add a stable version, release kind, one-line summary,
   and one-line rationale to the brief, then run `scripts/hatch.py version
   apply`. Run the relevant native product tests and show the staged diff.
6. Once an exact product commit exists, audit that commit's history, messages,
   identities, paths, and files. Record the relevant human or automated
   evidence, then run the internal readiness check. Do not push automatically.

## Version

Use [versioning.md](references/versioning.md) when a public candidate needs a
version. Put the chosen stable version, `patch`/`minor`/`major` release kind,
one-line public summary, and one-line rationale in the Promotion Brief. Hatch
checks that the target is the exact next version for that kind from the brief's
product base. After explicit confirmation, `version apply` writes `VERSION` and
a matching `CHANGELOG.md` entry. After the product commit exists, run `version
check` against that exact commit.

Never create a tag, GitHub release, or push as part of versioning.

## Record evidence

Keep exploratory results—human notes, generated outputs, screenshots, and
failure cases—as private eval artifacts or summarize them in a Promotion Brief.
They may inform a workbench candidate, but do not satisfy a readiness check.

Use [evidence-record.md](references/evidence-record.md) only after the exact
product commit is known. A gateable record names that commit and lists the
evidence and acceptance IDs it supports. Include human, automated, or mixed
observations as appropriate.

If an output is worth productizing, create a new Promotion Brief or add it to
the current brief. Do not promote raw eval output automatically.

## Audit and readiness

Run `scripts/hatch.py audit` against the exact product commit selected by the
promotion.
Use the workspace's private audit policy for project-specific terms.
It scans tracked file contents and paths, commit messages, and Git identities.
Report mechanical findings and coverage gaps plainly. An audit `PASS` means no
mechanical finding in the scanned scope; never call that a safety guarantee.

For intentional binary product assets, configure one tracked product manifest
in the audit policy and follow [binary-manifest.md](references/binary-manifest.md).
Hatch checks its path, byte count, SHA-256, source, purpose, and review
attestation in every audited commit. An absent, stale, malformed, or mismatched
entry remains a blocking coverage gap.

The readiness check is the last internal step of Promote, not another workflow
for the user to remember. Run `scripts/hatch.py ready` only for the exact
product commit. It does not re-decide scope or change files: it verifies that
the approved brief, audit, version log, and required evidence all refer to the
same commit. Report `READY TO PUSH`, `NOT READY`, or `NEEDS EVIDENCE`; do not
push.

## Bootstrap Hatch

Allow an absent marker only when the user explicitly asks to self-host Hatch.
First establish the marker and independent boundaries, then apply the normal
workflow. Do not extend this exception to arbitrary unmarked projects.
