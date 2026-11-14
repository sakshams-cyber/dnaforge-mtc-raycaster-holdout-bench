# Full audit

The full-text manifest includes the complete reports and four additional IND
documents. The answer schema allows up to six findings. The reviewer approved
three existing planted findings and one real recovery-count discrepancy.
The key and oracle contain only values and locations. Local sanity and the
Harbor oracle scored 1.0. The four model attempts and citation diagnostics
are in [the run summary](../../runs/SUMMARY.md).

Local staging requires Poppler. The checked staging plan stores offsets and
synthetic replacements only; it reconstructs all three existing edits.

```sh
python scripts/stage_text.py --pack-root data/pack3 \
  --task tasks/discrepancy-hunt-04-full-audit
```
