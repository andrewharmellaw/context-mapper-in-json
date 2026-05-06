# JSON Schemas

These JSON Schema (Draft 7) files define the structure of the JSON input accepted
by the Context Mapper JSON Converter. They can be used independently of the Python
package — for example, to validate input files in your editor, CI pipeline, or any
other JSON Schema-aware tool.

## Files

| File | Validates |
|------|-----------|
| [`context-map.json`](context-map.json) | The top-level `contextMap` object |
| [`bounded-context.json`](bounded-context.json) | Each entry in `boundedContexts` |
| [`subdomain.json`](subdomain.json) | Each entry in `subdomains` |

## Usage

### Editor validation (VS Code)

Add a `$schema` reference to your JSON file:

```json
{
  "$schema": "https://raw.githubusercontent.com/ContextMapper/context-mapper-json-converter/main/schemas/context-map.json",
  "contextMap": { ... },
  "boundedContexts": [ ... ]
}
```

### CLI validation with `ajv`

```bash
npm install -g ajv-cli
ajv validate -s schemas/bounded-context.json -d my-bounded-context.json
```

### Python

```python
import json
import jsonschema
from pathlib import Path

schema = json.loads(Path("schemas/bounded-context.json").read_text())
jsonschema.validate(my_data, schema)
```

## Structure

A complete input document combines all three schemas:

```json
{
  "contextMap": {          // validated by context-map.json
    "type": "SYSTEM_LANDSCAPE",
    "contains": ["OrderService", "PaymentService"]
  },
  "boundedContexts": [     // each item validated by bounded-context.json
    { "name": "OrderService", "type": "FEATURE" },
    { "name": "PaymentService", "type": "FEATURE" }
  ],
  "subdomains": [          // each item validated by subdomain.json (optional)
    { "name": "Ordering", "type": "CORE_DOMAIN" }
  ]
}
```
