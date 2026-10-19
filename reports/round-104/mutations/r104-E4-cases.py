#!/usr/bin/env python3
"""r104-E4 mutation: register the res_uid_s04 arms in corpus/fixtures/run_battery.py.

Applied by the ORCHESTRATOR (seat E4 never edits shared files). The three rows
below are the exact PASS lines measured on godot 4.7.2.stable.arch_linux.ed1daf0bf
in reports/round-104/r104-E4.md; each is pinned through its FIRST field only
(`PASS res_uid s04 arm=<arm> ...`) because every field after it is either fixed
by the fixture or is a derived boolean, and the uid tokens are run-random and
therefore kept out of the pinned text entirely (RES_UID_DIAG only).

Anchor discipline: the CASES list closes at the first line that is exactly `]`
after `CASES = [`; the rows are inserted immediately before it so the
`export_div_*` block above stays byte-identical (r103-V11 load-bearing
adjacency). The script refuses to write unless that anchor is unique.

Usage:
  python3 r104-E4-cases.py            # print the unified diff, write nothing
  python3 r104-E4-cases.py --apply    # rewrite run_battery.py in place
"""

import argparse
import difflib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"

ROWS = [
    ('res_uid_s04_persist', 'res_uid_s04.gd', '["--arm=persist"]', 0,
     'PASS res_uid s04 arm=persist cache_records=1 cache_declared=1 cache_consistent=true '
     'cache_id_match=true roundtrip=true reader_has=true reader_path=res://alpha.gd '
     'nocache_has=false uidfile_only_authority=false'),
    ('res_uid_s04_classes', 'res_uid_s04.gd', '["--arm=classes"]', 0,
     'PASS res_uid s04 arm=classes create_distinct=true create_positive=true text_roundtrip=true '
     'invalid_text=-1 empty_text=-1 uidroot_text=0 invalid_id_text=uid://<invalid> path_echo=true '
     'cidf_deterministic=true cidf_pure=true same_path_two_ids=true dup_add_keeps_first=true '
     'dup_add_err=true set_unknown_err=true remove_unknown_err=true ghost_has=false'),
    ('res_uid_s04_collision', 'res_uid_s04.gd', '["--arm=collision"]', 0,
     'PASS res_uid s04 arm=collision dup_warn=true pair=res://alpha.gd,res://beta.gd records=1 '
     'dup_records=1 dup_text_roundtrip=true winner_in_pair=true reader_matches_winner=true'),
]

BLOCK = """
    # r104 C1 (seat E4): ResourceUID add/remove/persistence lattice. The runtime
    # uid:// authority is the binary .godot/uid_cache.bin written by an editor
    # scan; the text .gd.uid sidecar alone resolves nothing in a --script
    # process (arm=persist). Misuse classes are engine ERRORs, not no-ops, and
    # their diagnostics are confined to nested logs (arm=classes). Duplicate
    # sidecars warn and collapse to one cache record (arm=collision).
"""


def build_block() -> str:
    lines = [BLOCK]
    for name, script, flags, exit_code, sig in ROWS:
        lines.append(f"    ({name!r}, {script!r}, {flags}, {exit_code},\n     {sig!r}),\n")
    return "".join(lines)


def find_anchor(text: str) -> int:
    start = text.index("CASES = [")
    close = text.index("\n]\n", start)
    # `close` points at the newline before the closing bracket.
    return close + 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    text = BATTERY.read_text()
    if "res_uid_s04_persist" in text:
        print("already applied; nothing to do")
        return 0

    anchor = find_anchor(text)
    if text.count("\n]\n", text.index("CASES = [")) < 1:
        print("anchor not found", file=sys.stderr)
        return 2
    if not text[anchor - 1] == "\n" or text[anchor] != "]":
        print("anchor shape unexpected", file=sys.stderr)
        return 2

    patched = text[:anchor] + build_block() + text[anchor:]

    diff = difflib.unified_diff(
        text.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile="a/corpus/fixtures/run_battery.py",
        tofile="b/corpus/fixtures/run_battery.py",
        n=3,
    )
    sys.stdout.writelines(diff)

    if args.apply:
        BATTERY.write_text(patched)
        print("\n[applied]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
