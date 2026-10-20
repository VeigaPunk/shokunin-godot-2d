#!/usr/bin/env python3
"""Count round-105 lesson mappings against QUALITY at an explicit Git revision.

The metadata-backed count establishes only a resolvable why -> M-row -> evidence
pointer chain. It does not assess whether that evidence substantively grounds a
criterion.
"""

import argparse
import re
import subprocess
import sys

QUALITY_PATH = "corpus/QUALITY.md"
LESSON_PATH = "corpus/lessons/round-105.md"
CAPTURED_IDS = re.compile(r"Q[0-9]+(?:,Q[0-9]+)*\Z")
FILE_REFERENCE = re.compile(
    r"(?P<path>(?:corpus|reports)/[A-Za-z0-9_./-]+|"
    r"[A-Za-z0-9_./-]+\.(?:md|gd|py|json|txt))"
    r"(?::(?P<first>[0-9]+)(?:-(?P<last>[0-9]+))?)?"
)

BARE_PATHS = {
    "CORPUS.md": "CORPUS.md",
    "LOG.md": "LOG.md",
    "PROTOCOL.md": "PROTOCOL.md",
    "SCORECARD.md": "SCORECARD.md",
    "seed.md": "corpus/knowledge/seed.md",
    "run_battery.py": "corpus/fixtures/run_battery.py",
}


def git_text(revision, path, cache):
    key = (revision, path)
    if key not in cache:
        result = subprocess.run(
            ["git", "show", "{}:{}".format(revision, path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        cache[key] = (
            result.stdout.decode("utf-8", errors="replace")
            if result.returncode == 0
            else None
        )
    return cache[key]


def valid_revision(revision):
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "{}^{{commit}}".format(revision)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("not a resolvable Git commit: {}".format(revision))
    return result.stdout.decode("ascii", errors="replace").strip()


def markdown_cells(line):
    if not line.startswith("|"):
        return None
    # A literal table-cell pipe is escaped as \| in QUALITY's command examples.
    cells = re.split(r"(?<!\\)\|", line)
    if len(cells) < 3:
        return None
    return [cell.strip().replace(r"\|", "|") for cell in cells[1:-1]]


def parse_quality(text):
    rows = []
    for line in text.splitlines():
        cells = markdown_cells(line)
        if cells and len(cells) >= 3 and re.fullmatch(r"Q[0-9]+", cells[0]):
            rows.append({"id": cells[0], "why": cells[2]})
    return rows


def parse_mistakes(text):
    rows = []
    for line in text.splitlines():
        cells = markdown_cells(line)
        if cells and len(cells) >= 4 and re.fullmatch(r"M[0-9]+", cells[0]):
            rows.append(
                {
                    "id": cells[0],
                    "evidence": cells[2],
                    "captured_by": cells[3],
                }
            )
    return rows


def evidence_paths(pointer):
    refs = []
    for match in FILE_REFERENCE.finditer(pointer):
        path = match.group("path")
        path = BARE_PATHS.get(path, path)
        first = int(match.group("first")) if match.group("first") else None
        last = int(match.group("last")) if match.group("last") else first
        refs.append((path, first, last))
    return refs


def pointer_resolves(revision, pointer, cache):
    for path, first, last in evidence_paths(pointer):
        text = git_text(revision, path, cache)
        if text is None:
            continue
        if first is None:
            return True
        line_count = len(text.splitlines())
        if first >= 1 and last >= first and last <= line_count:
            return True
    return False


def criterion_has_resolvable_lesson_pointer(why, mistakes_by_id, revision, cache):
    for number in re.findall(r"(?<![A-Za-z0-9])M([0-9]+)(?![0-9])", why):
        for mistake in mistakes_by_id.get("M" + number, []):
            if pointer_resolves(revision, mistake["evidence"], cache):
                return True
    return False


def analyze_texts(quality_text, lesson_text, revision, cache, invalid_id=None):
    quality_rows = parse_quality(quality_text)
    mistake_rows = parse_mistakes(lesson_text)
    quality_ids = {row["id"] for row in quality_rows}
    mistakes_by_id = {}
    for row in mistake_rows:
        mistakes_by_id.setdefault(row["id"], []).append(row)

    criterion_metadata = {}
    for row in quality_rows:
        criterion_metadata[row["id"]] = criterion_metadata.get(row["id"], False) or (
            criterion_has_resolvable_lesson_pointer(
                row["why"], mistakes_by_id, revision, cache
            )
        )

    mapped_rows = []
    malformed_rows = []
    for row in mistake_rows:
        captured = row["captured_by"]
        if CAPTURED_IDS.fullmatch(captured):
            ids = captured.split(",")
            mapped_rows.append({"mistake": row["id"], "ids": ids})
        elif captured not in ("", "—", "none-before-r105"):
            malformed_rows.append((row["id"], captured))

    if invalid_id is not None:
        if invalid_id in quality_ids:
            raise ValueError("self-test id already exists in QUALITY: {}".format(invalid_id))
        if not mapped_rows:
            raise ValueError("no syntactic mapping row available for mutation")
        # Mutate only the parsed in-memory record, never the lesson file or worktree.
        mapped_rows[0]["ids"].append(invalid_id)

    joined_valid = []
    unresolved = {}
    for row in mapped_rows:
        missing = [criterion_id for criterion_id in row["ids"] if criterion_id not in quality_ids]
        if missing:
            for criterion_id in missing:
                unresolved.setdefault(criterion_id, set()).add(row["mistake"])
        else:
            joined_valid.append(row)

    metadata_backed = []
    metadata_unbacked = []
    for row in joined_valid:
        if all(criterion_metadata.get(criterion_id, False) for criterion_id in row["ids"]):
            metadata_backed.append(row)
        else:
            metadata_unbacked.append(row)

    metadata_unbacked_ids = sorted(
        {
            criterion_id
            for row in metadata_unbacked
            for criterion_id in row["ids"]
            if not criterion_metadata.get(criterion_id, False)
        },
        key=lambda item: int(item[1:]),
    )

    baseline_ids = {"Q1", "Q2", "Q3"}
    lesson_ids = {"Q" + str(number) for number in range(4, 24)}
    return {
        "quality_rows": len(quality_rows),
        "baseline_rows": sum(1 for row in quality_rows if row["id"] in baseline_ids),
        "lesson_derived_rows": sum(1 for row in quality_rows if row["id"] in lesson_ids),
        "syntactic_rows": len(mapped_rows),
        "joined_valid_rows": len(joined_valid),
        "metadata_backed_rows": len(metadata_backed),
        "metadata_unbacked_rows": len(metadata_unbacked),
        "metadata_unbacked_ids": metadata_unbacked_ids,
        "unresolved": unresolved,
        "malformed": malformed_rows,
        "mutated_row": mapped_rows[0]["mistake"] if invalid_id is not None and mapped_rows else None,
    }


def analyze_revision(revision, cache, invalid_id=None):
    quality_text = git_text(revision, QUALITY_PATH, cache)
    lesson_text = git_text(revision, LESSON_PATH, cache)
    missing = []
    if quality_text is None:
        missing.append(QUALITY_PATH)
    if lesson_text is None:
        missing.append(LESSON_PATH)
    if missing:
        return {
            "quality_rows": 0,
            "baseline_rows": 0,
            "lesson_derived_rows": 0,
            "syntactic_rows": 0,
            "joined_valid_rows": 0,
            "metadata_backed_rows": 0,
            "metadata_unbacked_rows": 0,
            "metadata_unbacked_ids": [],
            "unresolved": {},
            "malformed": [],
            "missing": missing,
        }
    result = analyze_texts(
        quality_text, lesson_text, revision, cache, invalid_id=invalid_id
    )
    result["missing"] = []
    return result


def print_measurement(result):
    print("QUALITY_criterion_rows: {}".format(result["quality_rows"]))
    print("inherited_contract_baseline_rows_Q1-Q3: {}".format(result["baseline_rows"]))
    print("lesson_derived_criteria_rows_Q4-Q23: {}".format(result["lesson_derived_rows"]))
    print("syntactic_mapping_rows: {}".format(result["syntactic_rows"]))
    print("joined_valid_mapping_rows: {}".format(result["joined_valid_rows"]))
    print("metadata_lesson_backed_mapping_rows: {}".format(result["metadata_backed_rows"]))
    print("metadata_unbacked_mapping_rows: {}".format(result["metadata_unbacked_rows"]))
    if result["metadata_unbacked_ids"]:
        print("metadata_unbacked_criterion_ids: {}".format(",".join(result["metadata_unbacked_ids"])))
    else:
        print("metadata_unbacked_criterion_ids: none")
    print(
        "metadata_scope: criterion why -> matching lesson M-row -> resolvable evidence path/line; not substantive grounding"
    )
    if result.get("missing"):
        print("missing_inputs (all C2 measurements zero): {}".format(", ".join(result["missing"])))
    if result["unresolved"]:
        diagnostics = []
        for criterion_id in sorted(result["unresolved"]):
            classes = ",".join(sorted(result["unresolved"][criterion_id], key=lambda item: int(item[1:])))
            diagnostics.append("{} via {}".format(criterion_id, classes))
        print("unresolved_criterion_ids: {}".format("; ".join(diagnostics)))
    else:
        print("unresolved_criterion_ids: none")
    if result["malformed"]:
        print(
            "malformed_capture_rows: {}".format(
                "; ".join("{}={!r}".format(row, value) for row, value in result["malformed"])
            )
        )
    else:
        print("malformed_capture_rows: none")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revision", help="Git revision whose corpus is measured")
    parser.add_argument(
        "--self-test-invalid",
        metavar="QID",
        help="also append an absent criterion ID to an in-memory mapping row and check the join",
    )
    args = parser.parse_args()

    try:
        revision = valid_revision(args.revision)
        cache = {}
        result = analyze_revision(revision, cache)
        print("measured_revision: {}".format(revision))
        print_measurement(result)

        if args.self_test_invalid:
            before_quality = git_text(revision, QUALITY_PATH, cache)
            before_lesson = git_text(revision, LESSON_PATH, cache)
            if before_quality is None or before_lesson is None:
                raise ValueError("self-test requires both measured corpus files")
            mutated = analyze_texts(
                before_quality,
                before_lesson,
                revision,
                cache,
                invalid_id=args.self_test_invalid,
            )
            expected_valid = result["joined_valid_rows"] - 1
            if (
                mutated["syntactic_rows"] != result["syntactic_rows"]
                or mutated["joined_valid_rows"] != expected_valid
                or args.self_test_invalid not in mutated["unresolved"]
            ):
                raise ValueError("invalid-criterion self-test did not produce the expected one-row join loss")
            classes = ",".join(sorted(mutated["unresolved"][args.self_test_invalid]))
            print("-- in-memory invalid-criterion mutation (no corpus write)")
            print("mutation: append {} to captured-by on {}".format(args.self_test_invalid, mutated["mutated_row"]))
            print(
                "syntactic_mapping_rows: {} -> {}".format(
                    result["syntactic_rows"], mutated["syntactic_rows"]
                )
            )
            print(
                "joined_valid_mapping_rows: {} -> {}".format(
                    result["joined_valid_rows"], mutated["joined_valid_rows"]
                )
            )
            print("diagnostic: {} via {}".format(args.self_test_invalid, classes))
            print("repository_corpus_mutated: no")
    except (OSError, ValueError) as error:
        print("r105-mapped-criteria: {}".format(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
