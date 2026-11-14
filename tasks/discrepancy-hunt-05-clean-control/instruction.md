# Audit the filing

You are reviewing an investigational new drug filing. Identify material
discrepancies that can be verified using the documents in `/app/workspace/`.
Use the evidence to decide which statement needs correction. For every
finding, give the corrected value or label and cite the passage that supports
your correction. Report each discrepancy once and include at most six findings.

Use workspace-relative paths and physical page numbers from the page markers.
Both quotes must be verbatim and at least 20 characters. Give each finding
a unique ID. Use the same units as the source for numeric corrections. Write
`/app/output/answer.json` in this format (fictional example):

```json
{"items":[{"id":"finding-1","path":"example.txt","page":2,"quote":"The fictional filing recorded a count of nine.","corrected_value":"12","source_path":"another-example.txt","source_page":8,"source_quote":"The verified fictional count was twelve."}]}
```
