# Fictional arithmetic plumbing check

The fictional report states a mean of 12 mg. Recompute the arithmetic mean from
raw.csv, rows 2 and 3, and report whether it matches. Rows include the header.
Use id synthetic-mean. This is synthetic infrastructure validation, not a biological task.
The numeric tolerance is 0.1% relative error; reported value is exact.
Write /app/output/answer.json using the schema below. Cite original cell text.

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
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id",
          "reported",
          "recomputed",
          "unit",
          "method",
          "inputs",
          "matches_reported"
        ],
        "properties": {
          "id": {
            "type": "string"
          },
          "reported": {
            "type": "number"
          },
          "recomputed": {
            "type": "number"
          },
          "unit": {
            "type": "string"
          },
          "method": {
            "type": "string",
            "enum": [
              "mean",
              "median"
            ]
          },
          "inputs": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "path",
                "sheet",
                "row",
                "col",
                "value"
              ],
              "properties": {
                "path": {
                  "type": "string"
                },
                "sheet": {
                  "type": "string"
                },
                "row": {
                  "type": "integer",
                  "minimum": 1
                },
                "col": {
                  "type": "string"
                },
                "value": {
                  "type": "string"
                }
              }
            }
          },
          "matches_reported": {
            "type": "boolean"
          }
        }
      }
    }
  }
}
```
