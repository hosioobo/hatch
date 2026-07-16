# Binary Manifest

Use a manifest only for intentional opaque product assets such as PNG files.
Keep it tracked in the product repository and configure its repository-relative
path in the private audit policy:

```toml
[binary_manifest]
path = "assets/manifest.json"
```

The audit reads the manifest from each audited product commit. It must be a
regular UTF-8 JSON file with this shape:

```json
{
  "schema": 1,
  "kind": "hatch.binary-manifest",
  "assets": [
    {
      "path": "assets/portrait.png",
      "sha256": "<lowercase SHA-256>",
      "bytes": 12345,
      "source": "Where the asset came from.",
      "purpose": "Why the product includes it.",
      "reviewed": true
    }
  ]
}
```

`reviewed: true` is an attestation that the asset received the required visual
review. Record the review itself as ordinary human or mixed evidence for the
same product commit.

An entry covers an asset only when its path, byte count, and SHA-256 match that
commit exactly. Missing, malformed, stale, or mismatched entries remain audit
coverage gaps; a manifest is not a blanket exemption for binary files.
