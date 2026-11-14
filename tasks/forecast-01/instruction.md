# Predict the final drug substance stability results at 25 °C

The workspace holds three successive versions of the drug substance stability data section (3.2.S.7.3) for ALLN-177 (oxalate decarboxylase), filed in submissions 0034, 0039 and 0053. Each version repeats the earlier time points and adds the newest ones. Two lots were still on stability at submission 0053: RX501601.01 (written RX501601.001 in the earlier versions), with data through 24 months, and RX501601.005, with data through 18 months. Both lots are stored at -20 °C, 5 °C, 25 °C / 60% RH and 40 °C / 75% RH. The targets are the next scheduled time point for each lot at 25 °C / 60% RH.

The workspace holds every version of these documents filed up to submission
**0053**. A later submission, which is not in the workspace, reports the
values below. Predict each one from the data you have.

| id | What to predict | Unit | Full credit | Half credit |
| --- | --- | --- | --- | --- |
| `lot01-rphplc-25c-36m` | Purity by RP-HPLC (main peak), lot RX501601.01, 25 °C / 60% RH, 36 months | % | ±1 % | ±2 % |
| `lot005-rphplc-25c-24m` | Purity by RP-HPLC (main peak), lot RX501601.005, 25 °C / 60% RH, 24 months | % | ±1 % | ±2 % |
| `lot005-potency-25c-24m` | Potency, lot RX501601.005, 25 °C / 60% RH, 24 months | u/mg | ±1 u/mg | ±2 u/mg |

No file in the workspace contains these values. Do not use the network or any
source outside the workspace. Each prediction earns full credit inside the "full" range around the
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
