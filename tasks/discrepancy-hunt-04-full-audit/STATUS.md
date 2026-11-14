# Draft audit

The full-text manifest includes the complete reports and four additional IND
documents. The answer schema allows up to six findings. The reviewer approved
the four-item list. The original baseline correction and evidence are pending;
they are required before writing the final key or starting real runs.

Local staging requires Poppler. The checked staging plan stores offsets and
synthetic replacements only; it reconstructs all three existing edits.

```sh
python scripts/stage_text.py --pack-root data/pack3 \
  --task tasks/discrepancy-hunt-04-full-audit
```
