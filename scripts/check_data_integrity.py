#!/usr/bin/env python3
"""Verify checksums, exact Jami Wajiz shards, and core Quran data invariants."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SHA256SUMS.txt"
JAMI_DIR = ROOT / "tafsir/al-jami-al-wajiz"
JAMI_SOURCE = JAMI_DIR / "ar-jami-al-wajiz.json"
JAMI_SHARD_MANIFEST = JAMI_DIR / "surah-manifest.json"
JAMI_LICENSE = JAMI_DIR / "LICENSE.txt"
EXPECTED_JAMI_COMMIT = "9ebcb53f813f538aa0d5ed483d67ac7cc7f67660"
ALLOWED_HTML_TAGS = {"p", "em", "a", "div"}
ALLOWED_HTML_ATTRS = {"class", "style", "href", "data-book", "data-chapter"}
ALLOWED_CLASSES = {"para", "q-cite", "hadith-cite", "qref-link", "asbab-cite", "qiraat-note", "faida-title", "faida-box"}


def fail(message: str) -> None:
    raise SystemExit(f"DATA INTEGRITY FAILURE: {message}")


def tracked_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return {name.decode("utf-8") for name in result.stdout.split(b"\0") if name}


class TafsirMarkupAudit(HTMLParser):
    """Fail closed if upstream markup grows beyond the reviewed HTML subset."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links = 0
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in ALLOWED_HTML_TAGS:
            self.errors.append(f"unreviewed HTML tag <{tag}>")
        values = dict(attrs)
        for name, value in attrs:
            if name not in ALLOWED_HTML_ATTRS:
                self.errors.append(f"unreviewed HTML attribute {name!r}")
            if name == "class" and any(part not in ALLOWED_CLASSES for part in (value or "").split()):
                self.errors.append(f"unreviewed HTML class {value!r}")
            if name == "style":
                for decl in (value or "").split(";"):
                    if not decl.strip():
                        continue
                    prop, sep, val = decl.partition(":")
                    if not sep or prop.strip().lower() not in {"color", "font-weight", "font-family", "font-size"}:
                        self.errors.append(f"unreviewed inline style {decl!r}")
                    elif prop.strip().lower() == "color" and not re.fullmatch(r"#[0-9a-fA-F]{6}", val.strip()):
                        self.errors.append(f"unreviewed color style {val!r}")
                    elif prop.strip().lower() == "font-weight" and val.strip() not in {"600", "700"}:
                        self.errors.append(f"unreviewed font-weight style {val!r}")
                    elif prop.strip().lower() == "font-family" and val.strip() != "'KFGQPC Uthman','Amiri Quran',serif":
                        self.errors.append(f"unreviewed font-family style {val!r}")
                    elif prop.strip().lower() == "font-size" and val.strip() != "1.08em":
                        self.errors.append(f"unreviewed font-size style {val!r}")
        if tag == "a":
            self.links += 1
            if values.get("href") != "javascript:void(0)" or not values.get("data-book") or not re.fullmatch(r"سورة-.+", values.get("data-book") or ""):
                self.errors.append("unreviewed source cross-reference link")
            if not re.fullmatch(r"ayah-[1-9][0-9]*", values.get("data-chapter") or ""):
                self.errors.append("unreviewed source cross-reference target")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


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
    canonical = parsed.get(JAMI_SOURCE.relative_to(ROOT).as_posix())
    if not isinstance(canonical, dict) or canonical.get("edition") != "ar-tafsir-al-jami-al-wajiz" or canonical.get("language") != "ar":
        fail("Al-Jami Al-Wajiz canonical metadata is invalid")
    if canonical.get("license") != "CC BY-ND 4.0" or canonical.get("licenseUrl") != "https://creativecommons.org/licenses/by-nd/4.0/":
        fail("Al-Jami Al-Wajiz license metadata is invalid")
    if canonical.get("author") != "الشيخ الدكتور أيمن فاتح آل عامر" or canonical.get("sourceCommit") != EXPECTED_JAMI_COMMIT:
        fail("Al-Jami Al-Wajiz attribution or upstream commit is invalid")
    if len(canonical.get("items", [])) != 6236 or len(canonical.get("surahs", [])) != 114:
        fail("Al-Jami Al-Wajiz coverage is incomplete")
    ayah_keys = [(int(row["surah_number"]), int(row["ayah_number"])) for row in canonical["items"]]
    if len(set(ayah_keys)) != 6236 or any(not row.get("tafsir_text") or not row.get("tafsir_html") for row in canonical["items"]):
        fail("Al-Jami Al-Wajiz contains duplicate, empty, or incomplete ayah records")

    by_surah: dict[int, list[dict[str, object]]] = {number: [] for number in range(1, 115)}
    for row in canonical["items"]:
        by_surah[int(row["surah_number"])].append(row)
    canonical_surahs = {int(row["number"]): row for row in canonical["surahs"]}
    source_markup = TafsirMarkupAudit()
    for row in canonical["items"]:
        source_markup.feed(row["tafsir_html"])
    for row in canonical["surahs"]:
        source_markup.feed(row["content_html"])
    if source_markup.errors:
        fail("unreviewed source HTML: " + "; ".join(source_markup.errors[:8]))
    if source_markup.links != 3355:
        fail(f"unexpected cross-reference count: {source_markup.links}")

    shard_manifest = parsed.get(JAMI_SHARD_MANIFEST.relative_to(ROOT).as_posix())
    if not isinstance(shard_manifest, dict) or shard_manifest.get("schemaVersion") != 1:
        fail("Al-Jami Al-Wajiz shard manifest is missing or unsupported")
    for key in ("edition", "language", "author", "source", "sourceCommit", "license", "licenseUrl"):
        if shard_manifest.get(key) != canonical.get(key):
            fail(f"Al-Jami Al-Wajiz shard manifest metadata mismatch: {key}")
    shard_entries = shard_manifest.get("surahs")
    if not isinstance(shard_entries, dict) or set(shard_entries) != {str(n) for n in range(1, 115)}:
        fail("Al-Jami Al-Wajiz manifest must list all 114 surahs")

    for number in range(1, 115):
        expected_items = by_surah[number]
        meta = canonical_surahs.get(number)
        if not meta or len(expected_items) != int(meta["ayah_count"]):
            fail(f"canonical verse count mismatch for surah {number}")
        if [int(row["ayah_number"]) for row in expected_items] != list(range(1, len(expected_items) + 1)):
            fail(f"canonical verse sequence is incomplete for surah {number}")
        info = shard_entries[str(number)]
        expected_file = f"surahs/surah-{number:03d}.json"
        if info.get("file") != expected_file.removeprefix("tafsir/al-jami-al-wajiz/") or info.get("itemCount") != len(expected_items):
            fail(f"shard manifest path or count mismatch for surah {number}")
        shard_path = JAMI_DIR / info["file"]
        try:
            raw = shard_path.read_bytes()
            shard = json.loads(raw)
        except Exception as exc:
            fail(f"invalid shard for surah {number}: {exc}")
        if hashlib.sha256(raw).hexdigest() != info.get("sha256"):
            fail(f"shard SHA-256 mismatch for surah {number}")
        for key in ("edition", "language", "author", "source", "sourceCommit", "license", "licenseUrl"):
            if shard.get(key) != canonical.get(key):
                fail(f"shard metadata mismatch for surah {number}: {key}")
        if shard.get("surah") != meta or shard.get("items") != expected_items:
            fail(f"shard is not verbatim to canonical source for surah {number}")

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
        "604 Quran pages, 2 complete CC BY 4.0 tafsir datasets, and 1 verbatim CC BY-ND 4.0 tafsir "
        f"dataset with 114 verified shards and {source_markup.links} safe cross-reference records."
    )


if __name__ == "__main__":
    main()
