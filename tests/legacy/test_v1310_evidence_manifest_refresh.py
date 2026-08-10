from __future__ import annotations

import hashlib
import json

from beacon.utils.v115_delivery import refresh_evidence_manifest


def test_v1310_refresh_evidence_manifest_should_rehash_existing_entries(tmp_path):
    docs_root = tmp_path / "docs" / "beacon" / "v1.3.10" / "execution"
    docs_root.mkdir(parents=True, exist_ok=True)
    stale_doc = docs_root / "stale.md"
    fresh_doc = docs_root / "fresh.md"
    stale_doc.write_text("old\n", encoding="utf-8")
    fresh_doc.write_text("fresh\n", encoding="utf-8")

    beacon_dir = tmp_path / ".beacon"
    beacon_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = beacon_dir / "evidence-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "version": "v1.3.10",
                "entries": [
                    {
                        "path": "docs/beacon/v1.3.10/execution/stale.md",
                        "sha256": hashlib.sha256(b"outdated").hexdigest(),
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    stale_doc.write_text("new\n", encoding="utf-8")

    refresh_evidence_manifest(
        tmp_path,
        refs=["docs/beacon/v1.3.10/execution/fresh.md"],
        version="v1.3.10",
    )

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = {entry["path"]: entry for entry in payload["entries"]}
    assert entries["docs/beacon/v1.3.10/execution/stale.md"]["sha256"] == hashlib.sha256(
        stale_doc.read_bytes()
    ).hexdigest()
    assert entries["docs/beacon/v1.3.10/execution/fresh.md"]["sha256"] == hashlib.sha256(
        fresh_doc.read_bytes()
    ).hexdigest()
