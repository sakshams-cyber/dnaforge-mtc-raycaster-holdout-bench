"""Phase 0: discover a local pack and initialize its ignored index database."""

from argparse import ArgumentParser, SUPPRESS
from contextlib import closing
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import os
import sqlite3
import subprocess

from .db import initialize
from .discovery import discover


def dependency_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def poppler_version() -> str:
    try:
        result = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    lines = (result.stderr or result.stdout).splitlines()
    return lines[0].removeprefix("pdftotext version ") if result.returncode == 0 and lines else "unavailable"


def build(pack: Path, db: Path) -> str:
    private_dir = (Path(__file__).resolve().parents[1] / "data").absolute()
    if private_dir.resolve() != private_dir or not db.resolve().is_relative_to(private_dir):
        raise ValueError("The index database must stay inside the project's ignored data/ directory.")
    db = db.resolve()
    report = db.with_name("DISCOVERY.md")
    if report.is_symlink() or db.name in {"DISCOVERY.md", "catalog.md"}:
        raise ValueError("Unsafe output path for the index or discovery report.")
    if db.is_relative_to(pack.resolve()):
        raise ValueError("The index database cannot be written inside the pack being inventoried.")
    report_text, summary = discover(pack)
    db.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    prior_umask = os.umask(0o077)
    try:
        with closing(sqlite3.connect(db)) as conn:
            initialize(conn, {
                "pack_root_name": pack.resolve().name,
                "built_at": datetime.now(timezone.utc).isoformat(),
                "extractor": "gradelib",
                "pdfplumber_version": dependency_version("pdfplumber"),
                "pypdf_version": dependency_version("pypdf"),
                "pdftotext_version": poppler_version(),
            })
        report.write_text(report_text, encoding="utf-8")
    finally:
        os.umask(prior_umask)
    return summary


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=Path("data/pack3"))
    parser.add_argument("--db", type=Path, default=Path("data/index/pack.sqlite"))
    sub = parser.add_subparsers(dest="command", required=True)
    phase = sub.add_parser("build", help="Phase 0 only: discovery and database setup")
    phase.add_argument("--phase", type=int, choices=[0], default=0)
    phase.add_argument("--pack", type=Path, default=SUPPRESS)
    phase.add_argument("--db", type=Path, default=SUPPRESS)
    args = parser.parse_args()
    try:
        print(build(args.pack, args.db))
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f"Phase 0: {exc}\n")


if __name__ == "__main__":
    main()
