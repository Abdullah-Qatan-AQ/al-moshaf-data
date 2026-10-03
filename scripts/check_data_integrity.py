#!/usr/bin/env python3
"""Verify repository checksums and essential Quran/tafsir dataset invariants."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SHA256SUMS.txt"


def fail(message: str) -> None:
    raise SystemExit(f"DATA INTEGRITY FAILURE: {message}")


def tracked_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return {name.decode("utf-8") for name in result.stdout.split(b"\0") if name}


def main() -> None:
    tracked = tracked_files()
    if "SHA256SUMS.txt" not in tracked:
        fail("SHA256SUMS.txt is not tracked")

    entries: dict[str, str] = {}
    for line_number, line in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            fail(f"invalid manifest row {line_number}")
        digest, relative = match.groups()
        if relative.startswith("./"):
            relative = relative[2:]
        if relative in entries:
            fail(f"duplicate manifest entry: {relative}")
        entries[relative] = digest

    expected = tracked - {"SHA256SUMS.txt"}
    if set(entries) != expected:
        missing = sorted(expected - set(entries))
        extra = sorted(set(entries) - expected)
        fail(f"manifest coverage mismatch; missing={missing[:10]}, extra={extra[:10]}")

    for relative, expected_digest in entries.items():
        path = ROOT / relative
        if not path.is_file():
            fail(f"tracked file is missing: {relative}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected_digest:
            fail(f"SHA-256 mismatch: {relative}")

    json_files = sorted(name for name in tracked if name.endswith(".json"))
    parsed: dict[str, object] = {}
    for relative in json_files:
        try:
            parsed[relative] = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"invalid JSON in {relative}: {exc}")

    page_files = sorted((ROOT / "quran/pages/ar").glob("page-*.json"))
    if len(page_files) != 604:
        fail(f"expected 604 Arabic Quran pages, found {len(page_files)}")
    for number, path in enumerate(page_files, 1):
        if path.name != f"page-{number:03d}.json":
            fail(f"unexpected or missing Quran page number near {path.name}")
        document = parsed.get(path.relative_to(ROOT).as_posix())
        if not isinstance(document, dict) or not isinstance(document.get("ayahs"), list) or not document["ayahs"]:
            fail(f"Quran page has no ayahs: {path.relative_to(ROOT)}")

    tafsir_files = sorted((ROOT / "tafsir").glob("*-mukhtasar.json"))
    if len(tafsir_files) != 2:
        fail(f"expected Arabic and English Tafsir Center datasets, found {len(tafsir_files)}")
    jami_path = ROOT / "tafsir/al-jami-al-wajiz/ar-jami-al-wajiz.json"
    jami = parsed.get(jami_path.relative_to(ROOT).as_posix())
    if not isinstance(jami, dict) or jami.get("edition") != "ar-tafsir-al-jami-al-wajiz" or jami.get("language") != "ar":
        fail("Al-Jami Al-Wajiz metadata is invalid")
    if jami.get("license") != "CC BY-ND 4.0" or jami.get("licenseUrl") != "https://creativecommons.org/licenses/by-nd/4.0/":
        fail("Al-Jami Al-Wajiz license metadata is invalid")
    if jami.get("author") != "الشيخ الدكتور أيمن فاتح آل عامر" or len(jami.get("items", [])) != 6236 or len(jami.get("surahs", [])) != 114:
        fail("Al-Jami Al-Wajiz coverage is incomplete")
    keys = {(int(row.get("surah_number")), int(row.get("ayah_number"))) for row in jami["items"]}
    if len(keys) != 6236 or any(not row.get("tafsir_text") or not row.get("tafsir_html") for row in jami["items"]):
        fail("Al-Jami Al-Wajiz contains duplicate, empty, or incomplete ayah records")
    for path in tafsir_files:
        document = parsed.get(path.relative_to(ROOT).as_posix())
        if not isinstance(document, dict):
            fail(f"tafsir dataset is not a JSON object: {path.relative_to(ROOT)}")
        if document.get("license") != "CC BY 4.0":
            fail(f"unexpected tafsir license in {path.relative_to(ROOT)}")
        if document.get("source") != "Tafsir Center for Quranic Studies (https://tafsir.net)":
            fail(f"unexpected tafsir source in {path.relative_to(ROOT)}")
        if not isinstance(document.get("items"), list) or len(document["items"]) != 6236:
            fail(f"tafsir dataset has incorrect item count: {path.relative_to(ROOT)}")

    print(
        f"Data integrity passed: {len(entries)} checksums, {len(json_files)} valid JSON files, "
        "604 Quran pages, 2 complete CC BY 4.0 tafsir datasets, and 1 complete CC BY-ND 4.0 tafsir dataset."
    )


if __name__ == "__main__":
    main()
