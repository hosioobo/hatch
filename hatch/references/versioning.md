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
| `patch` | `MAJOR.MINOR.(PATCH + 1)` | Fixes and corrections without a new public capability. |
| `minor` | `MAJOR.(MINOR + 1).0` | A new backward-compatible public capability. |
| `major` | `(MAJOR + 1).0.0` | An intentional breaking public contract change. |

Hatch compares the target to the Promotion Brief's product base commit. It does
not infer a release kind from the diff. After explicit confirmation, run:

```text
python3 scripts/hatch.py version apply --workspace <root> --brief <brief.json>
```

This writes the product's `VERSION` and a matching top entry in `CHANGELOG.md`.
Commit those changes with the product, then verify the exact commit with
`version check` or `ready`. Tags, releases, and pushes remain separate actions.
