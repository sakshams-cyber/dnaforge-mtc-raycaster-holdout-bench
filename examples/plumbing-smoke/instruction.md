# Synthetic infrastructure test

Read response.txt and report the fictional request status. This is not a real filing task.
Write /app/output/answer.json. Paths are workspace-relative; pages are 1-based.

Schema:
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
        "required": [
          "id",
          "status",
          "path",
          "page",
          "quote"
        ],
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "status": {
            "type": "string",
            "enum": [
              "resolved",
              "partially_resolved",
              "unresolved"
            ]
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
          }
        }
      }
    }
  }
}
```

Use id `synthetic-1`. Quotes must be verbatim and at least 20 characters.
