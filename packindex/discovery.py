"""Describe a local pack without printing any of its document contents."""

from collections import defaultdict
from pathlib import Path
import csv
import json
import os
from unicodedata import normalize


ANCHORS = ("partial-clinical-hold", "pre-ind-type-b", "pre-ind-type-d", "source-data")


def path_key(value: str) -> str:
    return normalize("NFC", value).casefold()


def markdown(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def index_columns(path: Path) -> tuple[str, list[str]]:
    ext = path.suffix.lower()
    if ext in (".csv", ".tsv"):
        delimiter = "\t" if ext == ".tsv" else ","
        try:
            with path.open(encoding="utf-8-sig", newline="") as file:
                return ext[1:].upper(), next(csv.reader(file, delimiter=delimiter), [])
        except UnicodeDecodeError:
            with path.open(encoding="latin-1", newline="") as file:
                return ext[1:].upper(), next(csv.reader(file, delimiter=delimiter), [])
    if ext == ".json":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict):
            rows = next((v for v in data.values() if isinstance(v, list) and v and isinstance(v[0], dict)), [])
            return "JSON", list(rows[0] if rows else data)
        return "JSON", list(data[0]) if isinstance(data, list) and data and isinstance(data[0], dict) else []
    if ext == ".xlsx":
        from openpyxl import load_workbook

        book = load_workbook(path, read_only=True, data_only=True)
        try:
            row = next(book.worksheets[0].values, ())
            return "XLSX", [str(value) for value in row if value is not None]
        finally:
            book.close()
    return ext[1:].upper() or "unknown", []


def discover(root: Path) -> tuple[str, str]:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Pack root is missing or is a symlink; provide the local extracted pack with --pack.")
    root_files = sorted((p for p in root.iterdir() if p.is_file() and not p.is_symlink()), key=lambda p: normalize("NFC", p.name))
    readme = next((p for p in root_files if path_key(p.name) == "readme.txt"), None)
    if readme is None:
        raise ValueError("Pack README.txt is missing; --pack must point to the extracted pack root.")
    readme_text = path_key(readme.read_bytes().decode("utf-8-sig", errors="replace"))
    candidates = [p for p in root_files if "index" in path_key(p.stem)]
    indexes = []
    for path in candidates:
        try:
            kind, columns = index_columns(path)
        except Exception:
            kind, columns = "unreadable", []
        indexes.append((path.name, kind, columns))

    counts: dict[tuple[str, ...], list[int]] = defaultdict(lambda: [0, 0])
    counts[()]
    seen = set()
    collisions = 0
    top_folders = set()
    for folder, dirs, files in os.walk(root):
        base = Path(folder)
        dirs[:] = sorted(d for d in dirs if d != "__MACOSX" and not d.startswith("._") and not (base / d).is_symlink())
        parts = base.relative_to(root).parts
        if not parts:
            top_folders.update(dirs)
        for level in range(min(len(parts), 3) + 1):
            counts[parts[:level]]
        for name in files:
            if name == ".DS_Store" or name.startswith("._"):
                continue
            file = base / name
            if file.is_symlink() or not file.is_file():
                continue
            key = path_key(file.relative_to(root).as_posix())
            if key in seen:
                collisions += 1
            seen.add(key)
            size = file.stat().st_size
            for level in range(min(len(parts), 3) + 1):
                count = counts[parts[:level]]
                count[0] += 1
                count[1] += size

    found = [anchor for anchor in ANCHORS if anchor in {path_key(part) for part in top_folders}]
    named = [folder for folder in sorted(top_folders, key=path_key) if path_key(folder) in readme_text]
    count, size = counts[()]
    lines = ["# Local pack discovery", "", f"{count} files; {size:,} bytes.", "",
             "Anchors present: " + (", ".join(found) or "none"),
             "Anchors missing: " + (", ".join(a for a in ANCHORS if a not in found) or "none"),
             f"Path collisions after NFC and case folding: {collisions}.", "",
             "## README layout cross-check", "",
             "The root README refers to these top-level folders found on disk: "
             + (", ".join(map(markdown, named)) or "none detected automatically") + ".",
             "", "## Index candidates", ""]
    for name, kind, columns in indexes:
        lines.append(f"- {markdown(name)}: {kind}; columns: " + (", ".join(map(markdown, columns)) or "not detected"))
    if not indexes:
        lines.append("No index-named file found at the pack root.")
    lines.extend(["", "## Folder tree (depth 3; cumulative counts)", "", "| Folder | Files | Bytes |", "| --- | ---: | ---: |"])
    for parts, (files, bytes_) in sorted(counts.items(), key=lambda item: normalize("NFC", "/".join(item[0]))):
        lines.append(f"| {markdown('/'.join(parts) or '.')} | {files} | {bytes_:,} |")
    formats = ", ".join(sorted({kind for _, kind, _ in indexes})) or "not detected"
    return "\n".join(lines) + "\n", f"Anchors found: {', '.join(found) or 'none'}; index format: {formats}; {count} files."
