---
name: hatch
description: Manage a declared Hatch lifecycle workspace only when work crosses its workbench → product → evidence boundary: prepare or apply a promotion, record human or automated evidence against a candidate or product commit, audit public-safety risks, or make a public-readiness gate decision. Use for an explicit `$hatch` lifecycle request, or implicitly only inside a workspace with a `hatch.toml` marker and one of those lifecycle intents. Do not use for ordinary coding, builds, tests, Git operations, deployments/releases, generic skill creation or installation, or Codex animated-pet work. Bootstrap Hatch itself only after an explicit self-hosting request.
---

# Hatch

## Overview

Use Hatch to keep exploratory work, canonical product source, and real-world
evidence distinct. Treat promotion as a deliberate decision backed by one
concise brief, not as synchronization between repositories.

## Resolve the workspace

- Read `hatch.toml` before acting. Resolve its `workbench`, `product`, and
  `evals` paths relative to the marker directory.
- Require both a valid marker and a clear lifecycle intent before inferring
  Hatch. Otherwise, use the ordinary relevant skill or workflow.
- Treat `workbench` as private and disposable, `product` as the sole
  canonical public-safe source, and `evidence` as records about a candidate or
  exact product commit.
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

Do not infer Hatch from "build", "test", "review", "commit", "publish", or
"deploy" alone.

## Promote

1. Inspect the candidate, product state, and relevant evidence without changing
   product.
2. Create or update one private Promotion Brief with
   `scripts/hatch.py brief new` and
   [promotion-brief.md](references/promotion-brief.md). Infer its draft from
   the work already done; ask only about genuinely ambiguous scope, exclusions,
   acceptance evidence, or public provenance.
3. Run `scripts/hatch.py brief check` and the mechanical audit on the intended
   product scope. Treat findings as
   investigation prompts, not proof of safety.
4. Present the brief, expected product impact, exclusions, and required
   evidence. Do not apply the promotion without an explicit confirmation such
   as "이 계획대로 반영해줘."
5. After confirmation, implement only the approved scope in product. Adapt or
   reimplement workbench code when appropriate; never blindly copy or sync it.
6. Run the relevant native product tests and a staged-diff audit. Show the
   diff and results. Do not commit or push automatically.

## Record evidence

Record one evaluation case with
[evidence-record.md](references/evidence-record.md). Attach evidence to either
a workbench snapshot or an exact product commit. Include human, automated, or
mixed observations as appropriate.

If an output is worth productizing, create a new Promotion Brief or add it to
the current brief. Do not promote raw eval output automatically.

## Audit

Run `scripts/hatch.py audit` against an explicit product ref or history range.
Use the workspace's private audit policy for project-specific terms.
Report `FINDINGS`, `NO MECHANICAL FINDINGS`, or `ERROR`; never say a project is
safe to publish merely because the script found nothing.

## Gate

Run `scripts/hatch.py gate` only for an exact product commit. It verifies that the
brief's required acceptance and evidence items are complete and tied to that
commit. Return `READY`, `BLOCKED`, or `NEEDS EVIDENCE`; do not push.

## Bootstrap Hatch

Allow an absent marker only when the user explicitly asks to self-host Hatch.
First establish the marker and independent boundaries, then apply the normal
workflow. Do not extend this exception to arbitrary unmarked projects.
