# Nonclinical review of an IND: check every claim against the data under it

You are the pharmacology/toxicology reviewer for an Investigational New Drug (IND)
application. The workspace holds text conversions of five documents from one IND:

- `summaries/investigator-brochure.txt`
- `summaries/general-investigational-plan.txt`
- `study-reports/A-703-01-report.txt` (rat toxicology study, report body)
- `study-reports/A-703-02-report.txt` (dog toxicology study, complete report with all appendices, about 1,000 pages)
- `study-reports/A-703-03-summary-report.txt` (dog maximum tolerated dose study, report body)

Find statements or table values that are wrong. Each layer of the filing must agree with
the layer under it, and the lower layer is the source of truth:

1. individual animal data, bioanalytical results, protocol and certificates in a study report's appendices
2. the study report's own text and summary tables
3. the summary documents written from the study reports

An error can sit in a summary document or in a study report's text or tables. Check
numbers, units, counts, classifications of findings, and anything derived by arithmetic
(doses, concentrations, means, margins). Apply the conventions the report itself states,
for example in table footnotes.

Report at most **eight** findings, most confident first. Report nothing you cannot support
with a verbatim source passage. If you find nothing, write `{"items": []}`.

## Reading the files

Read only files under `/app/workspace/`. Each file is split into pages by lines of the
form `===== PAGE 7 =====`; page numbers are those markers and match the original PDF.
The dog report is large, so search it rather than reading it end to end:
`python3 /app/source_tool.py search --query "..."`, `page --path <file> --page <n>` and
`list` are available, as are ordinary shell tools.

## Output

Write `/app/output/answer.json` matching this schema exactly:

```json
{
  "type": "object",
  "required": [
    "items"
  ],
  "additionalProperties": false,
  "properties": {
    "items": {
      "type": "array",
      "maxItems": 8,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id",
          "path",
          "page",
          "quote",
          "corrected_value",
          "source_path",
          "source_page",
          "source_quote"
        ],
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "path": {
            "type": "string",
            "minLength": 1
          },
          "page": {
            "type": "integer",
            "minimum": 1
          },
          "quote": {
            "type": "string",
            "minLength": 20
          },
          "corrected_value": {
            "type": "string",
            "minLength": 1
          },
          "source_path": {
            "type": "string",
            "minLength": 1
          },
          "source_page": {
            "type": "integer",
            "minimum": 1
          },
          "source_quote": {
            "type": "string",
            "minLength": 20
          }
        }
      }
    }
  }
}
```

For each finding:

- `id`: any label unique within your answer, such as `f1`.
- `path`, `page`, `quote`: where the wrong statement or value is. `quote` is copied
  verbatim from that page, at least 20 characters, and must include the wrong value or
  wording itself. For a table cell, quote the row.
- `corrected_value`: what it should say, as the value alone. For a quantity give number
  and unit (`45 mg`, `310.5 ng/mL`); for a ratio give the number (`12`); for wording give
  the correct term or the finding that should be stated (`reversible`, `hepatocellular hypertrophy`).
- `source_path`, `source_page`, `source_quote`: the passage or data row from the lower
  layer that establishes the correct value, copied verbatim, at least 20 characters. For
  a recomputed value, quote one of the data rows it is computed from.

Paths are workspace-relative. Report each wrong statement once.

Example of the shape only (invented values, not from this filing):

```json
{"items": [{"id": "f1", "path": "study-reports/A-703-01-report.txt", "page": 9,
  "quote": "Male 310.5 44.2 5", "corrected_value": "301.5 ng/mL",
  "source_path": "study-reports/A-703-01-report.txt", "source_page": 20,
  "source_quote": "1001 2 Male Day 2 298.7"}]}
```
