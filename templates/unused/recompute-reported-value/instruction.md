# Recompute a reported value from raw wells

You are reviewing the reported concentration in cell C8 of
`source-data/elisa/026_summary.tsv`. Independently recompute that row's
concentration from the matching wells. Report the mean, sum and range
(maximum minus minimum), all in ng/mL. State the method used and whether the
mean agrees with the report within 2% relative tolerance.

Choose `raw_mean`, `blank_subtracted_mean` or `normalized_to_control`.
List the workspace-relative source path and sheet name for each input
table. Use an empty sheet name for a TSV or CSV file. Write
`/app/output/answer.json`.

Fictional example:

```json
{"values":{"mean_ng_ml":10,"sum_ng_ml":20,"range_ng_ml":4},"method":"raw_mean","inputs":[{"path":"example.tsv","sheet":""}],"matches_reported":true}
```
