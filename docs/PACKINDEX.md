# Local pack index

This component prepares a deterministic index for authorized Holdout-Bench pack
holders. **Phase 0 only:** it inventories the folder tree and root index and
creates the SQLite v2 schema. Document extraction and gold commands are pending.

```bash
python -m packindex build --phase 0 --pack data/pack3
```

The extracted pack must have `README.txt` at its root. The command writes
`data/index/DISCOVERY.md` and `data/index/pack.sqlite` locally. Use `--db` to set
a different index path under `data/`. Keep the pack and index output local.

| Convention | Value |
| --- | --- |
| Paths | Pack relative; keep the on-disk spelling, compare in Unicode NFC. |
| Document IDs | `D` plus 10 hex digits of SHA-256 over the NFC path. |
| Pages and quotes | 1-based physical pages and shared grader normalization. |
| Cells | Exact sheet and A1 reference; CSV/TSV header is row 1. |
| Gold | Humans choose, verify and sign it. |
