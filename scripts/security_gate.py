#!/usr/bin/env python3
"""Security Quality Gate for SAST (semgrep) findings.

Reads a semgrep --json report and decides whether the finding set should
block the pipeline or merely warn. The decision uses semgrep's own
rule-assigned `extra.severity` field (ERROR / WARNING / INFO) -- that
field exists specifically for downstream tools to make this call, as
opposed to `extra.metadata.impact/confidence/likelihood`, which are a
separate, human-review-oriented risk assessment and do not agree with
`severity` on every finding.

Policy:
  ERROR            -> blocking     (exit 1, red GitHub Actions error annotations)
  WARNING / INFO    -> advisory     (exit 0, yellow annotations + $GITHUB_STEP_SUMMARY)

SCA (pip-audit) is out of scope for this gate; it is graded separately.
"""
import json
import os
import sys

# 這就是投影片「SECURITY QUALITY GATE」講的那個規則：擋不擋部署，只看這一個 set。
BLOCKING_SEVERITIES = {"ERROR"}

RESET = "\033[0m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"


def load_findings(report_path):
    with open(report_path) as f:
        report = json.load(f)
    return report.get("results", [])


def classify(findings):
    # 投影片「SECURITY QUALITY GATE」的核心邏輯：每個 finding 只依 severity 二分，
    # 落在 BLOCKING_SEVERITIES 裡的擋部署，其餘全部只當警告放行。
    blocking, advisory = [], []
    for finding in findings:
        severity = finding.get("extra", {}).get("severity", "WARNING")
        if severity in BLOCKING_SEVERITIES:
            blocking.append(finding)
        else:
            advisory.append(finding)
    return blocking, advisory


def describe(finding):
    path = finding.get("path", "?")
    line = finding.get("start", {}).get("line", "?")
    rule = finding.get("check_id", "?")
    message = finding.get("extra", {}).get("message", "").strip().splitlines()[0]
    return path, line, rule, message


def emit_gh_annotation(level, finding):
    path, line, rule, message = describe(finding)
    print(f"::{level} file={path},line={line}::[{rule}] {message}")


def print_console(color, label, finding):
    path, line, rule, message = describe(finding)
    print(f"{color}[{label}] {path}:{line} ({rule}){RESET}")
    print(f"  {message}")


def write_step_summary(blocking, advisory):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a") as f:
        f.write("# Security Quality Gate: SAST\n\n")
        if blocking:
            f.write(f"## 🔴 Blocking findings ({len(blocking)})\n\n")
            f.write("| Rule | File | Line |\n|---|---|---|\n")
            for finding in blocking:
                path, line, rule, _ = describe(finding)
                f.write(f"| {rule} | {path} | {line} |\n")
            f.write("\n")
        if advisory:
            f.write(f"## 🟡 Advisory findings ({len(advisory)}, not blocking)\n\n")
            f.write("| Rule | File | Line |\n|---|---|---|\n")
            for finding in advisory:
                path, line, rule, _ = describe(finding)
                f.write(f"| {rule} | {path} | {line} |\n")
            f.write("\n")
        if not blocking and not advisory:
            f.write("No SAST findings.\n")


def main():
    if len(sys.argv) != 2:
        print("usage: security_gate.py <semgrep-json-report>", file=sys.stderr)
        return 2

    findings = load_findings(sys.argv[1])
    blocking, advisory = classify(findings)

    print(
        f"Security Quality Gate: {len(findings)} SAST finding(s) "
        f"-- {len(blocking)} blocking (ERROR), {len(advisory)} advisory (WARNING/INFO)\n"
    )

    for finding in blocking:
        emit_gh_annotation("error", finding)
        print_console(RED, "BLOCKING", finding)

    for finding in advisory:
        emit_gh_annotation("warning", finding)
        print_console(YELLOW, "ADVISORY", finding)

    write_step_summary(blocking, advisory)

    if blocking:
        print(f"\n{RED}Gate FAILED: {len(blocking)} blocking (ERROR-severity) finding(s).{RESET}")
        return 1

    if advisory:
        print(
            f"\n{YELLOW}Gate PASSED with {len(advisory)} advisory (WARNING/INFO-severity) "
            f"finding(s) -- see step summary.{RESET}"
        )
        return 0

    print(f"{GREEN}Gate PASSED: no SAST findings.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
