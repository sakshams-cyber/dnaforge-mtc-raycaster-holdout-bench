# Check an IND's summary documents against its study reports

You are reviewing an Investigational New Drug (IND) application before it goes to FDA.
The workspace holds text conversions of five documents from one IND:

- `summaries/investigator-brochure.txt`
- `summaries/general-investigational-plan.txt`
- `study-reports/A-703-01-report.txt` (rat toxicology study)
- `study-reports/A-703-02-report.txt` (dog toxicology study)
- `study-reports/A-703-03-summary-report.txt` (dog maximum tolerated dose study)

The two summary documents were written from the study reports. Find statements in the
**summary documents** that are wrong: a nonclinical result, classification, dose, or
derived figure that disagrees with the study reports, or with the figures in the same
summary document that it is calculated from. The study reports are the source of truth.

Report at most **three** findings, most confident first. Report nothing you cannot
support with a verbatim source passage. If you find nothing, write `{"items": []}`.

## Reading the files

Read only files under `/app/workspace/`. Each file is split into pages by lines of the
form `===== PAGE 7 =====`; page numbers are those markers and match the original PDF.
`python3 /app/source_tool.py list`, `search --query "..."` and
`page --path <file> --page <n>` are available, or read the files directly.

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
      "maxItems": 3,
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
- `path`, `page`, `quote`: where the wrong statement is. `quote` is copied verbatim from
  that page, at least 20 characters, and must include the wrong value or wording itself.
- `corrected_value`: what the statement should say, as the value alone. For a quantity
  give number and unit (`45 mg`); for a ratio give the number (`12`); for a
  classification give the correct term (`reversible`).
- `source_path`, `source_page`, `source_quote`: the passage that establishes the correct
  value, copied verbatim, at least 20 characters. Cite the study report where the result
  is reported. For a derived figure, cite the passage it is calculated from.

Paths are workspace-relative. Report each wrong statement once.

Example of the shape only (invented values, not from this filing):

```json
{"items": [{"id": "f1", "path": "summaries/investigator-brochure.txt", "page": 2,
  "quote": "the half-life in monkeys was 45 hours", "corrected_value": "4.5 hours",
  "source_path": "study-reports/A-703-01-report.txt", "source_page": 9,
  "source_quote": "terminal half-life of 4.5 hours was observed"}]}
```
