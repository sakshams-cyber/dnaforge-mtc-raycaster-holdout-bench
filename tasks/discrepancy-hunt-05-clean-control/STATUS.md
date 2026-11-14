# Clean control

Same full documents and instructions as audit 04. Stage with `--clean`; the
workspace is unaltered. The reviewer approved the original recovery-count
discrepancy as the only credited item. Local sanity passed.

```sh
python scripts/stage_text.py --pack-root data/pack3 \
  --task tasks/discrepancy-hunt-05-clean-control --clean
```
