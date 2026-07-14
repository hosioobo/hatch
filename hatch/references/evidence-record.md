# Gateable Evidence Record

Store one private JSON record per human, automated, or mixed evaluation under
the workspace's `records.evidence` path **after the exact product commit is
known**. This is the record that `gate` consumes.

```json
{
  "schema": 1,
  "kind": "hatch.evidence",
  "target_commit": "<full product commit>",
  "mode": "human",
  "case": "What was tried",
  "acceptance_ids": ["A1"],
  "evidence_ids": ["E1"],
  "result": "pass",
  "observations": "What happened, including uncertainty",
  "artifacts": []
}
```

`acceptance_ids` is required: include every acceptance ID named by the linked
evidence requirement. `gate` rejects a passing record that cannot make that
link.

Keep exploratory human notes, generated outputs, and workbench-snapshot
results as ordinary private eval artifacts instead. They can inform a Promotion
Brief, but they do not satisfy a gate until an exact product commit and its
acceptance linkage are recorded here.

Use `result: "not-applicable"` only when the corresponding evidence requirement
explicitly permits it and the observation explains why. Promote a generated
output only through a new or updated Promotion Brief.
