# Versioning

For a public candidate, add this to its private Promotion Brief:

```json
"version": {
  "target": "0.2.0",
  "summary": "Add the public workflow.",
  "release_kind": "minor",
  "rationale": "This adds a backward-compatible public capability."
}
```

Use stable semantic versions only: `MAJOR.MINOR.PATCH`. State one of these
release kinds and keep both the summary and rationale to one public-safe line:

| Kind | Exact next version | Use for |
| --- | --- | --- |
| `patch` | `MAJOR.MINOR.(PATCH + 1)` | A fix, correction, documentation, or maintenance update to an existing public promise. |
| `minor` | `MAJOR.(MINOR + 1).0` | A new backward-compatible public capability, workflow, or policy that users can opt into. |
| `major` | `(MAJOR + 1).0.0` | An intentional breaking public contract change. |

Classify the public contract, not the size of the diff. “Regular update” is a
changelog description, not a fourth version tier: use `patch` unless the user
can newly do something or must change how they use the product.

Before 1.0, retain the same distinction: use `0.y.x` for corrections to a
declared contract and `0.(y+1).0` for a new explicit workflow, policy, or
capability. Do not use the pre-1.0 status to turn every ordinary update into a
minor release.

Hatch compares the target to the Promotion Brief's product base commit. It does
not infer a release kind from the diff. After explicit confirmation, run:

```text
python3 scripts/hatch.py version apply --workspace <root> --brief <brief.json>
```

This writes the product's `VERSION` and a matching top entry in `CHANGELOG.md`.
Commit those changes with the product, then verify the exact commit with
`version check` or `ready`. Tags, releases, and pushes remain separate actions.
