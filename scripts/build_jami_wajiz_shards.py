#!/usr/bin/env python3
"""Create per-surah delivery shards from the verbatim canonical Jami Wajiz file."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tafsir/al-jami-al-wajiz/ar-jami-al-wajiz.json"
OUT = ROOT / "tafsir/al-jami-al-wajiz/surahs"
MANIFEST = ROOT / "tafsir/al-jami-al-wajiz/surah-manifest.json"


def write_json(path: Path, value: object) -> bytes:
    raw = (json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


def main() -> None:
    canonical = json.loads(SOURCE.read_text(encoding="utf-8"))
    if canonical.get("license") != "CC BY-ND 4.0" or len(canonical.get("items", [])) != 6236:
        raise SystemExit("Unexpected canonical Jami Wajiz dataset; refusing to build shards.")

    manifest = {
        "schemaVersion": 1,
        "edition": canonical["edition"],
        "language": canonical["language"],
        "title": canonical["title"],
        "author": canonical["author"],
        "source": canonical["source"],
        "sourceCommit": canonical["sourceCommit"],
        "license": canonical["license"],
        "licenseUrl": canonical["licenseUrl"],
        "surahs": {},
    }

    all_items: dict[int, list[dict[str, object]]] = {number: [] for number in range(1, 115)}
    for item in canonical["items"]:
        number = int(item["surah_number"])
        if number not in all_items:
            raise SystemExit(f"Invalid surah number in canonical dataset: {number}")
        all_items[number].append(item)

    for number in range(1, 115):
        surah_meta = next((row for row in canonical["surahs"] if int(row["number"]) == number), None)
        items = all_items[number]
        if not surah_meta or len(items) != int(surah_meta["ayah_count"]):
            raise SystemExit(f"Unexpected coverage for surah {number}: {len(items)}")
        if [int(row["ayah_number"]) for row in items] != list(range(1, len(items) + 1)):
            raise SystemExit(f"Ayah sequence is incomplete or unordered in surah {number}")

        filename = f"surah-{number:03d}.json"
        shard = {
            "edition": canonical["edition"],
            "language": canonical["language"],
            "title": canonical["title"],
            "author": canonical["author"],
            "source": canonical["source"],
            "sourceCommit": canonical["sourceCommit"],
            "license": canonical["license"],
            "licenseUrl": canonical["licenseUrl"],
            "surah": surah_meta,
            "items": items,
        }
        raw = write_json(OUT / filename, shard)
        manifest["surahs"][str(number)] = {
            "file": f"surahs/{filename}",
            "itemCount": len(items),
            "sizeBytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }

    manifest_raw = write_json(MANIFEST, manifest)
    print(f"Created {len(manifest['surahs'])} verbatim delivery shards.")
    print(f"Manifest SHA-256: {hashlib.sha256(manifest_raw).hexdigest()}")
    print(f"Manifest bytes: {len(manifest_raw)}")


if __name__ == "__main__":
    main()
