# Promotion Brief

Create a private JSON brief with:

```text
python3 scripts/hatch.py brief new --workspace <root> --id <id>
```

The agent fills the meaningful fields after inspecting the candidate. Do not
make the user complete a blank form when the answer is already in context.

| Field | Purpose |
| --- | --- |
| `source` | Fixed workbench snapshot and selected source paths. |
| `intent` | One or two sentences describing the user-visible change. |
| `in_scope` / `out_of_scope` | What crosses the boundary and what stays behind. |
| `acceptance` | The smallest requirements that make this promotion sufficient. |
| `evidence_required` | Human, automated, or mixed proof required for the resulting commit. |
| `public_assessment` / `risk_decisions` | Privacy, provenance, attribution, and accepted-risk decisions. |
| `product` | Base commit before promotion and exact target commit after it. |

Each `evidence_required` item names the acceptance IDs it proves. A gateable
evidence record must repeat those IDs; this keeps the final gate traceable
without turning the brief into a checklist for the user.

Validate before applying a promotion:

```text
python3 scripts/hatch.py brief check --workspace <root> --brief <brief.json>
```

The brief is a contract, not a copy plan. Product may reimplement the useful
idea cleanly rather than move workbench files verbatim.
