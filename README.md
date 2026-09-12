# Code Audit Community Action

Run a local-first heuristic code safety scan in GitHub Actions and export
SARIF, JSON, or Markdown.

This action is free and uses the community rule set. It does not upload source
code to a service.

## Quick start

```yaml
name: code-audit

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: yuan1521913/code-audit-action@v1
        with:
          path: .
          format: sarif
          output: code-audit.sarif
          fail-on: high
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: code-audit.sarif
```

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `path` | `.` | File or directory to scan |
| `format` | `sarif` | `sarif`, `json`, or `markdown` |
| `output` | `code-audit-results.sarif` | Output path |
| `fail-on` | `high` | `high` or `none` |
| `ignore` | empty | Newline-separated fnmatch patterns |
| `skip-rule` | empty | Newline-separated rule names |

## Outputs

| Output | Meaning |
| --- | --- |
| `total` | Total findings |
| `high` | High-severity findings |
| `medium` | Medium-severity findings |
| `low` | Low-severity findings |
| `report` | Report path |

## Rule boundary

The community action checks:

- `sql-concat`
- `pickle-loads`
- `eval-exec-subprocess`
- `js-command-exec`
- `raw-html-reflect`

Findings are review candidates, not proof that an exploit exists. A clean scan
does not prove that the repository is safe.

## Development

```bash
python -m unittest discover -s tests -v
```

## License

MIT. See `LICENSE`.
