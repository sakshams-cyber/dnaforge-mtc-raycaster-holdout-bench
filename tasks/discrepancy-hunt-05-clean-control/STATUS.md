# Clean control

Same full documents and instructions as audit 04. Stage with `--clean`; the
workspace is unaltered. The reviewer approved the original recovery-count
discrepancy as the only credited item. Local sanity and the Harbor oracle
scored 1.0. The four model attempts and citation diagnostics are in
[the run summary](../../runs/SUMMARY.md).

```sh
python scripts/stage_text.py --pack-root data/pack3 \
  --task tasks/discrepancy-hunt-05-clean-control --clean
```
