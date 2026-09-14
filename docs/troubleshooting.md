# GitHub Action troubleshooting

## `Resource not accessible by integration`

For a private repository, start with:

```yaml
permissions:
  actions: read
  contents: read
  security-events: write
```

The upload step needs permission to write code-scanning results. A read-only
token used for code checkout is not enough.

## SARIF file is not found

The action output and the upload input must match:

```yaml
      - uses: yuan1521913/code-audit-action@v0
        with:
          output: code-audit.sarif

      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: code-audit.sarif
```

If the output is inside a subdirectory, keep the same relative path in both
places.

## Results are missing after the scan fails

`fail-on: high` makes the scan step return a failure code. Later steps do not
run by default.

Use:

```yaml
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: code-audit.sarif
```

This keeps the evidence visible even when the workflow is blocked.

## Code Scanning is unavailable

Private repositories need GitHub Advanced Security for the Code Scanning UI.
Without it, save the report as an artifact:

```yaml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: code-audit-sarif
          path: code-audit.sarif
```

## Fork pull requests

Fork pull requests normally receive a lower-privilege token. SARIF upload may
be rejected.

Do not switch blindly to `pull_request_target` and then execute untrusted fork
code. Start with same-repository pull requests and pushes. Add a separate,
trusted workflow only when there is a clear security design.

## Every pull request turns red

A repository with existing findings should not enable a hard gate on day one.

Start with:

```yaml
fail-on: none
```

Review the initial results, remove false positives, fix urgent findings, and
introduce a baseline where available. Then change to:

```yaml
fail-on: high
```

## The action cannot be resolved

Use a released reference:

```yaml
uses: yuan1521913/code-audit-action@v0
```

Do not depend on `main` if reproducible workflow behavior matters.
