#!/usr/bin/env python3
"""Count Q-id mappings in the two round-105 Git blobs, not evidence grounding."""
import re
import subprocess
import sys


def count_mappings(quality_text, lesson_text):
    quality_rows = re.findall(r"^\| (Q[0-9]+) \|", quality_text, re.M)
    quality_ids = set(quality_rows)
    mistakes = []
    for line in lesson_text.splitlines():
        cells = re.split(r"(?<!\\)\|", line)
        if len(cells) >= 7 and re.fullmatch(r"M[0-9]+", cells[1].strip()):
            mistakes.append((cells[1].strip(), cells[4].strip()))

    syntactic = valid = 0
    unknown = {}
    for mistake, captured in mistakes:
        if not re.fullmatch(r"Q[0-9]+(?:,Q[0-9]+)*", captured):
            continue
        syntactic += 1
        missing = set(captured.split(",")) - quality_ids
        valid += not missing
        for criterion in missing:
            unknown.setdefault(criterion, set()).add(mistake)
    return {
        "quality_rows": len(quality_rows),
        "baseline_rows": sum(q in {"Q1", "Q2", "Q3"} for q in quality_rows),
        "lesson_derived_rows": sum(4 <= int(q[1:]) <= 23 for q in quality_rows),
        "mistake_rows": len(mistakes),
        "syntactic_rows": syntactic,
        "joined_valid_rows": valid,
        "unknown": unknown,
    }


def unknown_diagnostics(unknown):
    return "; ".join(
        f"{q} via {','.join(sorted(mistakes))}"
        for q, mistakes in sorted(unknown.items())
    ) or "none"


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <git-revision>", file=sys.stderr)
        return 2
    revision = subprocess.run(
        ["git", "rev-parse", "--verify", f"{sys.argv[1]}^{{commit}}"],
        capture_output=True, text=True,
    )
    if revision.returncode:
        print(f"invalid Git revision: {sys.argv[1]}", file=sys.stderr)
        return 2
    revision = revision.stdout.strip()
    texts, missing = [], []
    for path in ("corpus/QUALITY.md", "corpus/lessons/round-105.md"):
        blob = subprocess.run(
            ["git", "show", f"{revision}:{path}"], capture_output=True, text=True,
        )
        texts.append(blob.stdout)
        if blob.returncode:
            missing.append(path)
    result = count_mappings("", "") if missing else count_mappings(*texts)
    print(f"measured_revision: {revision}")
    for label, key in (
        ("QUALITY_criterion_rows", "quality_rows"),
        ("inherited_contract_baseline_rows_Q1-Q3", "baseline_rows"),
        ("lesson_derived_criteria_rows_Q4-Q23", "lesson_derived_rows"),
        ("lesson_mistake_rows", "mistake_rows"),
        ("syntactic_mapping_rows", "syntactic_rows"),
        ("joined_valid_mapping_rows", "joined_valid_rows"),
    ):
        print(f"{label}: {result[key]}")
    print(f"unknown_criterion_ids: {unknown_diagnostics(result['unknown'])}")
    print("mapping_scope: Q-id syntax and existence join only; no grounding claim")
    if missing:
        print(f"missing_inputs (all counts zero): {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
