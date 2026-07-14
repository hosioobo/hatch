# Evidence Record

Store one private JSON record per human, automated, or mixed evaluation under
the workspace's `records.evidence` path.

```json
{
  "schema": 1,
  "kind": "hatch.evidence",
  "target_commit": "<full product commit>",
  "mode": "human",
  "case": "What was tried",
  "acceptance_ids": ["A1"],
  "result": "pass",
  "observations": "What happened, including uncertainty",
  "artifacts": []
}
```

Use `result: "not-applicable"` only when the corresponding acceptance item
explicitly permits it and the observation explains why. Generated outputs may
be evidence; promote one only through a new or updated Promotion Brief.
