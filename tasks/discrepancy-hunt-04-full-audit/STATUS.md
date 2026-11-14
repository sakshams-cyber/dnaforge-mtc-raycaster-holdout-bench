# Draft audit

The full-text manifest includes the complete reports and four additional IND
documents. The answer schema allows up to six findings. Reviewer confirmation
of the four proposed entries and baseline evidence is pending. No gold or
oracle answer has been created for this task.

Local staging requires Poppler for consistent page text and the ignored
mutation plan derived from the three existing tasks:

```sh
python scripts/stage_text.py --pack-root data/pack3 \
  --task tasks/discrepancy-hunt-04-full-audit \
  --plan data/gold_notes/audit-04-local-plant.json
```
