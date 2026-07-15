# Hatch

[English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Français](README.fr.md) | [Español](README.es.md)

## Build messily. Publish cleanly.

Hatch gives solo makers a private workbench for exploration and a clean product
space for sharing. It makes the boundary between them explicit, so a public
release does not depend on reconstructing the same requirements every time.

## Quickstart

After installing Hatch, start a project with `$hatch`. It creates separate
local Git repositories for the workbench, product, and evaluation evidence.

When a product version is ready, use `$hatch` again to promote it. Hatch
confirms the scope, records the version and changelog, audits the exact commit,
and decides whether it is ready to push.

## Workspace layout

`$hatch init` creates this local container. The three sibling directories are
independent Git repositories.

```text
my-project/
├── hatch.toml                  # describes the three boundaries
├── my-project-workbench/       # private drafts, experiments, and briefs
├── my-project-product/         # the public-safe product source
└── my-project-evals/           # private human or automated evidence
```

## Commands

Hatch has two user-facing commands. The later steps are deliberate parts of
`promote`, not extra commands to remember.

### `init`

Use `$hatch init` when starting a new project.

1. Resolve the parent directory, project name, and public Git identity.
2. With `--dry-run`, print the container and three repository paths only.
3. Otherwise create the container, then initialize `workbench`, `product`, and
   `evals` as separate Git repositories on `main`.
4. Write `hatch.toml`, private workbench audit policy, repository instructions,
   ignore files, and the product's initial `VERSION` (`0.0.0`) and
   `CHANGELOG.md`.
5. Configure the product repository with the public Git identity.

It never creates a remote, commits, pushes, tags, releases, or deploys.

### `promote`

Use `$hatch promote` when selected work is ready to become a product snapshot.

1. Inspect the candidate, current product state, and existing evidence without
   changing the product.
2. Create a source-pinned Promotion Brief that records intent, included and
   excluded work, public-safety decisions, acceptance criteria, evidence, and
   the next stable version.
3. Show the brief and get confirmation before changing the product.
4. Apply only the confirmed scope to the product; never synchronize the whole
   workbench automatically.
5. Write `VERSION` and the matching `CHANGELOG.md` entry, run relevant product
   checks, and create one exact product commit.
6. Audit that exact commit's reachable history, commit messages, Git identities,
   paths, and file contents against the private policy.
7. Record human, automated, or mixed evaluation evidence against the same
   commit.
8. Run the ready check. It verifies that the brief, version log, audit, and
   evidence all name the same commit, then reports `READY TO PUSH`,
   `NOT READY`, or `NEEDS EVIDENCE`.

`promote` never pushes, tags, creates a release, or deploys by itself.

## Why Hatch Exists

### The workbench is not the product

**The problem.** A project needs a place for drafts, experiments, notes, and
half-finished work. A public repository needs a focused, safe snapshot. Mixing
the two turns every release into a cleanup project.

**The fix.** Keep them in independent Git repositories. Develop freely in the
workbench, then promote only the work that belongs in the product.

### Promotion should be repeatable

**The problem.** Each promotion invites the same questions: What is included?
Is it safe to publish? What version is this? Was it actually tested?

**The fix.** Hatch makes those questions one workflow: brief, version, audit,
evaluation evidence, and a readiness decision tied to one exact product commit.

### Summary

Hatch keeps private exploration and public product work separate, then makes
the move between them small, deliberate, and verifiable.
