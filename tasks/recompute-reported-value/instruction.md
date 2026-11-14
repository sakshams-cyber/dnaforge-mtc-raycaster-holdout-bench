# Recompute a reported value from raw data

You are reviewing a reported result. Find the reported value, independently
recompute it from the supplied raw table, and decide whether the two agree
within the stated tolerance.

Review the result in `source-data/elisa/026_summary.tsv`, cell C8
(`ngml_av` in row 8, counting the header). Match its sample and standard curve
to the well table `source-data/elisa/026.tsv`, using the well table's `detail`
and `standard_curve` columns. Take the unweighted arithmetic mean of the
matching nonmissing `ngml_trunc` values. Use `mean` for the method and `ng/mL`
for the unit. Do not use the reported summary value as a calculation input.

**Draft: the comparison tolerance awaits human confirmation.**

Write `/app/output/answer.json` as `{"items": [...]}`. Each item includes `id`,
`reported`, `recomputed`, `unit`, `method`, `matches_reported`, and `inputs`.
Use `elisa-026-c8` as the item ID and workspace-relative file paths. List every
raw well value used in `inputs`. Spreadsheet references use the exact sheet
name, a 1-based row (including headers), and a column letter. Use an empty
sheet name for CSV/TSV. For example (fictional):

```json
{"items":[{"id":"value-example","reported":12,"recomputed":10,"unit":"ratio","method":"example_method","matches_reported":false,"inputs":[{"path":"raw.tsv","sheet":"","row":2,"col":"B","value":"10"}]}]}
```
