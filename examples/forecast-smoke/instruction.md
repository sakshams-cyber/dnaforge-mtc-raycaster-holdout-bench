# Predict the next stability results for a fictional lot

The workspace holds three successive stability reports for one lot of an invented compound, ZX-000. Each report repeats the earlier time points and adds the newest one. This is a fictional fixture that only exercises the grader.

The workspace holds every version of these documents filed up to submission
**0003**. A later submission, which is not in the workspace, reports the
values below. Predict each one from the data you have.

| id | What to predict | Unit | Full credit | Half credit |
| --- | --- | --- | --- | --- |
| `assay-18m` | Assay of lot F-001 at 18 months, long-term condition | % label claim | ±0.3 % label claim | ±0.6 % label claim |
| `impurities-18m` | Total impurities of lot F-001 at 18 months, long-term condition | % | ±0.03 % | ±0.06 % |
| `water-18m` | Water content of lot F-001 at 18 months, long-term condition | % | ±0.1 % | ±0.2 % |

There is no file that contains these values, and no network access is needed or
allowed. Each prediction earns full credit inside the "full" range around the
value later reported, half credit inside the "half" range, and nothing outside it.
Give your best estimate for every target; a missing target scores zero.

## Reading the files

Read only files under `/app/workspace/`. Text files are split into pages by lines of the form `===== PAGE 7 =====`; page numbers match the original PDF.
`python3 /app/source_tool.py list`, `search --query "..."` and
`page --path <file> --page <n>` are available, or read the files directly.

## Output

Write `/app/output/answer.json` with one item per target: `id` exactly as listed
above and `value` as a JSON number in the unit shown (no unit text, no ranges).

Example of the shape only (invented ids and values):

```json
{"items": [{"id": "example-a", "value": 12.3}, {"id": "example-b", "value": 0.45}]}
```
