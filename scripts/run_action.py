from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codeaudit_community import __version__, scanner  # noqa: E402


def _lines(name: str) -> list[str]:
    return [line.strip() for line in os.environ.get(name, "").splitlines() if line.strip()]


def _artifact_uri(path: str, root: Path) -> str:
    try:
        return Path(path).resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return Path(path).as_posix()


def render_sarif(findings: list[dict[str, Any]], root: Path) -> str:
    rule_ids = [rule["name"] for rule in scanner.RULES]
    results = []
    for finding in findings:
        results.append(
            {
                "ruleId": finding["pattern"],
                "level": "error" if finding["severity"] == "high" else "warning",
                "message": {"text": finding["reason"]},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": _artifact_uri(finding["file"], root)},
                            "region": {"startLine": finding["line"]},
                        }
                    }
                ],
                "properties": {"snippet": finding["snippet"]},
            }
        )
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "code-audit-community",
                        "version": __version__,
                        "rules": [{"id": rule_id, "name": rule_id} for rule_id in rule_ids],
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def main() -> int:
    target = Path(os.environ.get("INPUT_PATH", "."))
    if not target.exists():
        print(f"path not found: {target}", file=sys.stderr)
        return 2

    fmt = os.environ.get("INPUT_FORMAT", "sarif").lower()
    output = Path(os.environ.get("INPUT_OUTPUT", "code-audit-results.sarif"))
    fail_on = os.environ.get("INPUT_FAIL_ON", "high").lower()
    if fmt not in {"sarif", "json", "markdown"}:
        print(f"unsupported format: {fmt}", file=sys.stderr)
        return 2
    if fail_on not in {"high", "none"}:
        print(f"unsupported fail-on value: {fail_on}", file=sys.stderr)
        return 2

    findings = scanner.scan_path(
        target,
        ignore_patterns=_lines("INPUT_IGNORE"),
        skip_rules=set(_lines("INPUT_SKIP_RULE")),
    )
    if fmt == "sarif":
        report = render_sarif(findings, target if target.is_dir() else target.parent)
    elif fmt == "json":
        report = scanner.render_json(findings)
    else:
        report = scanner.render_markdown(findings)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    summary = scanner.summarize(findings)
    _write_output("total", str(summary["total"]))
    _write_output("high", str(summary["high"]))
    _write_output("medium", str(summary["medium"]))
    _write_output("low", str(summary["low"]))
    _write_output("report", output.as_posix())
    print(f"report={output.as_posix()}")
    print(f"summary={summary}")

    if fail_on == "high" and scanner.has_high(findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
