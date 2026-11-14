"""Initialize the local v2 ledger without replacing an existing database."""

from hashlib import sha256
from pathlib import Path
import json
import sqlite3
from unicodedata import normalize


SCHEMA_VERSION = "2"
TABLES = (
    "meta", "documents", "pages", "pages_fts", "sheets", "cells", "sequences",
    "mentions", "version_families", "leads", "gold_items", "runs", "run_criteria",
    "failure_tags",
)


def doc_id(rel_path: str) -> str:
    return "D" + sha256(normalize("NFC", rel_path).encode()).hexdigest()[:10]


def content_hash(conn: sqlite3.Connection) -> str:
    digest = sha256()
    for table in TABLES:
        if table == "pages_fts" and conn.execute(
            "SELECT value FROM meta WHERE key = 'fts5'"
        ).fetchone()[0] != "1":
            continue
        if table == "meta":
            # built_at and the local directory name are provenance, not content.
            rows = conn.execute(
                "SELECT * FROM meta WHERE key NOT IN ('built_at', 'content_hash', 'pack_root_name') ORDER BY key"
            )
        else:
            count = len(conn.execute(f"PRAGMA table_info({table})").fetchall())
            order = ",".join(str(i + 1) for i in range(count))
            rows = conn.execute(f"SELECT * FROM {table} ORDER BY {order}")
        digest.update(f"{table}\n".encode())
        for row in rows:
            digest.update((json.dumps(tuple(row), ensure_ascii=False, separators=(",", ":")) + "\n").encode())
    return digest.hexdigest()


def initialize(conn: sqlite3.Connection, metadata: dict[str, str]) -> str:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("BEGIN IMMEDIATE")
    try:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        if tables:
            if ("meta",) not in tables or conn.execute(
                "SELECT value FROM meta WHERE key = 'schema_version'"
            ).fetchone() != (SCHEMA_VERSION,):
                raise ValueError("Existing database is not schema v2; no migration was applied.")
        else:
            schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
            for stmt in schema.split(";"):
                if stmt.strip():
                    conn.execute(stmt)
            try:
                conn.execute(
                    "CREATE VIRTUAL TABLE pages_fts USING fts5(norm, doc_id UNINDEXED, "
                    "page UNINDEXED, tokenize='unicode61 remove_diacritics 2')"
                )
                fts = "1"
            except sqlite3.OperationalError as exc:
                if "no such module: fts5" not in str(exc).lower():
                    raise
                fts = "0"
            conn.executemany("INSERT INTO meta VALUES (?, ?)", sorted({
                **metadata, "schema_version": SCHEMA_VERSION, "fts5": fts,
            }.items()))
        checksum = content_hash(conn)
        conn.execute("INSERT OR REPLACE INTO meta VALUES ('content_hash', ?)", (checksum,))
        conn.commit()
        return checksum
    except BaseException:
        conn.rollback()
        raise
