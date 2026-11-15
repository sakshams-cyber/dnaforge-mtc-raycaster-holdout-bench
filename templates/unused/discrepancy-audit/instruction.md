# Check reported values against records

You are a CMC and nonclinical reviewer. Audit the listed filing claims against
the source of record in `/app/workspace/`. Recompute when needed. Use the current
governing record where there are multiple versions.

Use `consistent` when a numeric claim agrees within 2% relative tolerance or
when a text value agrees exactly after normalizing case and whitespace. Use
`inconsistent` otherwise. Give the correct value and the record you used for
each claim. For an agreeing claim, report the value supported by that record.
Cite a workspace-relative path and a 1-based PDF page, or a spreadsheet sheet
name and A1 cell. Use an empty sheet name for CSV or TSV. Write the answer to
`/app/output/answer.json`.

The reviewer will supply the audited claim IDs and locations.

Fictional example:

```json
{"items":[{"id":"aud-1","verdict":"consistent","correct_value":7,"source":{"path":"fictional.tsv","sheet":"","cell":"C14"}}]}
```
