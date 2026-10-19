#!/usr/bin/env python3
"""r103 seat V3 — s02 second-root receipt cross-check (read-only).

Compares the s02 verdict lines of the first root (seat E0, revision
50b56438 of export_div_s02.gd) with this seat's second root
(/var/tmp/r103c-V3) on both fixture revisions:
  50b56438 = pre-fix _wipe_dir (static *_at getters, dot-entries skipped)
  c08792c1 = E2's include_hidden fix (landed 20:57:06 while V3 was running)

Only the documented unpinned trailing `proj=` field is masked; every other
byte of the verdict line must match for a cross-check to pass. Prints raw
sha256 per receipt so the shard can pin bytes without re-running.

Usage: python3 r103-ver3-crosscheck.py
"""
import hashlib
import pathlib
import re
import sys

E0 = pathlib.Path("/var/tmp/r103c-E0/logs")
V3 = pathlib.Path("/var/tmp/r103c-V3/logs")

ROWS = {
    "E0/iso   rev1": E0 / "s02_iso.out",
    "E0/xdg   rev1": E0 / "s02_xdg.out",
    "V3/iso   rev1": V3 / "iso_pass1.out",
    "V3/xdg   rev1 standalone": V3 / "xdg_standalone.out",
    "V3/xdg   rev1 reuse-dirty": V3 / "xdg_reuse.out",
    "V3/iso   rev2": V3 / "new_iso.out",
    "V3/xdg   rev2 #1": V3 / "new_xdg1.out",
    "V3/xdg   rev2 #2 reuse": V3 / "new_xdg2.out",
}

# (a, b) -> expected relation: "same" or a short reason for a KNOWN diff.
PAIRS = [
    (("E0/iso   rev1", "V3/iso   rev1"), "same"),
    (("E0/iso   rev1", "V3/iso   rev2"), "same"),
    (("V3/iso   rev1", "V3/iso   rev2"), "same"),
    (("E0/xdg   rev1", "V3/xdg   rev2 #1"), "same"),
    (("V3/xdg   rev2 #1", "V3/xdg   rev2 #2 reuse"), "same"),
    # standalone xdg arm ran in a root with no prior iso row, so the
    # informational xdg_a_store field is [<missing>] instead of [run1,run2];
    # the field is in no bad-condition, both receipts PASS.
    (("E0/xdg   rev1", "V3/xdg   rev1 standalone"), "known-diff:standalone xdg_a_store"),
    # rev1 defect on a reused root: homeC/.local survives _wipe_dir (probed
    # mechanism, shard V3.2); rev2 fixes it (V3/xdg rev2 #2 = same).
    (("E0/xdg   rev1", "V3/xdg   rev1 reuse-dirty"), "known-diff:rev1 wipe defect"),
]


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verdict(path: pathlib.Path) -> str:
    for line in path.read_text().splitlines():
        if line.startswith(("PASS export_div", "FAIL export_div")):
            return line
    return "<no export_div verdict line>"


def masked(line: str) -> str:
    return re.sub(r"(?:^| )proj=\S*", " proj=<masked>", line).strip()


def main() -> int:
    lines = {}
    print("== receipts (raw bytes) ==")
    for name, path in ROWS.items():
        if not path.is_file():
            print(f"{name:28s} MISSING {path}")
            return 2
        text = verdict(path)
        lines[name] = masked(text)
        kind = text.split(" ", 1)[0]
        print(f"{name:28s} {kind:4s} {path.stat().st_size:5d} B  "
              f"sha256={sha(path)}")

    print("\n== masked verdict lines ==")
    for name, text in lines.items():
        print(f"{name:28s} {text}")

    print("\n== cross-root masked comparisons ==")
    failures = 0
    for (a, b), expect in PAIRS:
        same = lines[a] == lines[b]
        want = expect == "same"
        ok = same == want
        failures += 0 if ok else 1
        verdict_text = "SAME" if same else "DIFF"
        print(f"{'ok  ' if ok else 'BAD '}{verdict_text:5s} {a} vs {b}  [{expect}]")
        if not same:
            sa, sb = set(lines[a].split()), set(lines[b].split())
            print(f"      only-{a}: {sorted(sa - sb)}")
            print(f"      only-{b}: {sorted(sb - sa)}")
    print(f"\n{len(PAIRS) - failures}/{len(PAIRS)} pairs match expectation")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
