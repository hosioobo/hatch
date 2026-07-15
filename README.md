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
