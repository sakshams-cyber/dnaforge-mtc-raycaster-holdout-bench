import sqlite3

import pytest

from packindex.db import doc_id, initialize
from packindex.discovery import discover


def test_phase_zero_discovery_counts_without_document_text(tmp_path):
    (tmp_path / "README.txt").write_text("Layout: source-data. Fictional description remains local.")
    (tmp_path / "index.csv").write_text("path,description\nsource-data/values.csv,Fictional index row\n")
    source = tmp_path / "source-data"
    source.mkdir()
    (source / "values.csv").write_text("header\nFictional cell\n")
    (source / "._values.csv").write_text("Ignored metadata")
    (tmp_path / "linked").symlink_to(source, target_is_directory=True)
    report, summary = discover(tmp_path)
    assert summary == "Anchors found: source-data; index format: CSV; 3 files."
    assert "index.csv: CSV; columns: path, description" in report
    assert "| source-data | 1 |" in report
    assert "Fictional" not in report


def test_phase_zero_requires_extracted_pack(tmp_path):
    with pytest.raises(ValueError, match="README.txt is missing"):
        discover(tmp_path)


def test_v2_schema_reuses_rows_and_hashes_nfc_ids(tmp_path):
    with sqlite3.connect(tmp_path / "pack.sqlite") as conn:
        initial = initialize(conn, {"built_at": "first", "pack_root_name": "one"})
        assert initial == initialize(conn, {"built_at": "second", "pack_root_name": "two"})
        assert conn.execute("PRAGMA journal_mode").fetchone() == ("wal",)
        assert conn.execute("SELECT value FROM meta WHERE key = 'schema_version'").fetchone() == ("2",)
        conn.execute("INSERT INTO leads(lead_id, text, origin) VALUES ('L1', 'fictional', 'fixture')")
        conn.commit()
        assert initialize(conn, {}) != initial
        assert conn.execute("SELECT status FROM leads").fetchone() == ("unverified",)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE leads SET status = 'unknown'")
    assert doc_id("source-data/cafe\u0301.csv") == doc_id("source-data/café.csv")


def test_unknown_database_is_not_overwritten(tmp_path):
    with sqlite3.connect(tmp_path / "unknown.sqlite") as conn:
        conn.execute("CREATE TABLE keep_me (value TEXT)")
        with pytest.raises(ValueError, match="not schema v2"):
            initialize(conn, {})
        assert conn.execute("SELECT count(*) FROM keep_me").fetchone() == (0,)
