CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);



CREATE TABLE documents (
  doc_id TEXT PRIMARY KEY, rel_path TEXT NOT NULL UNIQUE, rel_path_nfc TEXT NOT NULL UNIQUE,
  folder TEXT NOT NULL, anchor TEXT,
  ext TEXT NOT NULL, kind TEXT NOT NULL,
  bytes INTEGER NOT NULL, sha256 TEXT NOT NULL,
  n_pages INTEGER, encrypted INTEGER NOT NULL DEFAULT 0,
  text_chars INTEGER, pages_need_ocr INTEGER NOT NULL DEFAULT 0,
  title_guess TEXT, date_guess TEXT,
  index_note TEXT,
  is_code INTEGER NOT NULL DEFAULT 0,
  error TEXT
);

CREATE TABLE pages (
  doc_id TEXT NOT NULL REFERENCES documents(doc_id), page INTEGER NOT NULL,
  printed_label TEXT, text TEXT NOT NULL, norm TEXT NOT NULL, chars INTEGER NOT NULL,
  redaction_marks INTEGER NOT NULL DEFAULT 0, ocr INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (doc_id, page)
);


CREATE TABLE sheets (doc_id TEXT NOT NULL, sheet TEXT NOT NULL, n_rows INTEGER, n_cols INTEGER,
  header_row_json TEXT, merged_ranges TEXT, PRIMARY KEY (doc_id, sheet));
CREATE TABLE cells (doc_id TEXT NOT NULL, sheet TEXT NOT NULL, ref TEXT NOT NULL,
  row INTEGER NOT NULL, col INTEGER NOT NULL, display TEXT, num REAL, qualifier TEXT, unit TEXT, formula TEXT,
  PRIMARY KEY (doc_id, sheet, ref));
CREATE INDEX cells_num ON cells(num);

CREATE TABLE sequences (seq_id INTEGER PRIMARY KEY, doc_id TEXT NOT NULL, locator TEXT NOT NULL,
  label TEXT, raw TEXT NOT NULL, letters TEXT NOT NULL, length INTEGER NOT NULL, nonstandard_chars TEXT);

CREATE TABLE mentions (id INTEGER PRIMARY KEY, doc_id TEXT NOT NULL, page INTEGER, kind TEXT NOT NULL,
  raw TEXT NOT NULL, value REAL, unit TEXT, char_start INTEGER, char_end INTEGER);


CREATE TABLE version_families (family_id TEXT NOT NULL, doc_id TEXT NOT NULL, stem TEXT NOT NULL,
  date_token TEXT, version_token TEXT, rank INTEGER, identical_to TEXT, flags TEXT,
  PRIMARY KEY (family_id, doc_id));


CREATE TABLE leads (lead_id TEXT PRIMARY KEY, text TEXT NOT NULL, origin TEXT NOT NULL,
  task_hint TEXT, status TEXT NOT NULL DEFAULT 'unverified', cites_json TEXT, checked_by TEXT,
  checked_at TEXT, notes TEXT,
  CHECK (status IN ('unverified','confirmed','not_in_pack','contradicted')));

CREATE TABLE gold_items (task_id TEXT NOT NULL, item_id TEXT NOT NULL, kind TEXT NOT NULL,
  expected_json TEXT NOT NULL, accept_json TEXT NOT NULL, oracle_json TEXT,
  planted INTEGER NOT NULL DEFAULT 0, lead_id TEXT, method TEXT,
  verified_by TEXT, verified_at TEXT, notes TEXT,
  PRIMARY KEY (task_id, item_id));

CREATE TABLE runs (run_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, version TEXT NOT NULL,
  agent TEXT NOT NULL, model TEXT NOT NULL, attempt INTEGER NOT NULL, reward REAL,
  criteria_met INTEGER, criteria_total INTEGER, passed INTEGER,
  refused INTEGER NOT NULL DEFAULT 0, started_at TEXT, ended_at TEXT, n_steps INTEGER,
  cost_usd REAL, run_path TEXT NOT NULL);
CREATE TABLE run_criteria (run_id TEXT NOT NULL, criterion_id TEXT NOT NULL, item_id TEXT,
  passed INTEGER NOT NULL, detail_json TEXT, PRIMARY KEY (run_id, criterion_id));
CREATE TABLE failure_tags (run_id TEXT NOT NULL, tag TEXT NOT NULL, criterion_id TEXT NOT NULL DEFAULT '',
  note TEXT, tagged_by TEXT NOT NULL, PRIMARY KEY (run_id, tag, criterion_id),
  CHECK (tag IN ('domain_knowledge','search_process','copied_not_computed','grounding','format',
                 'gaming_or_eval_awareness','gave_up_or_timeout','trusted_wrong_source','refused_or_flagged')));
