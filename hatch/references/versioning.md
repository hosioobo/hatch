# Versioning

For a public candidate, add this to its private Promotion Brief:

```json
"version": {
  "target": "0.2.0",
  "summary": "Add the public workflow."
}
```

Use stable semantic versions only: `MAJOR.MINOR.PATCH`. Keep the summary to one
public-safe line. After explicit confirmation, run:

```text
python3 scripts/hatch.py version apply --workspace <root> --brief <brief.json>
```

This writes the product's `VERSION` and a matching top entry in `CHANGELOG.md`.
Commit those changes with the product, then verify the exact commit with
`version check` or `gate`. Tags, releases, and pushes remain separate actions.
