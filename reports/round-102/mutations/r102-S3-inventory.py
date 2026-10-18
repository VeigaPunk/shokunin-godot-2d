#!/usr/bin/env python3
"""r102-S3 hunk inventory: enumerate every hunk of the r101 simplifier queue
(unique patch files), split each into a one-hunk patch (with its OWN file
header), and `git apply --check` it individually at HEAD. Read-only (temp
patches under /var/tmp/r102-S3/inventory). Emits markdown.
"""
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
MUT = REPO / "reports/round-101/mutations"
# unique change sets in r101-simp shard order; duplicates / combined supersets excluded
PATCHES = [
    "r101-simp1-r91-nav_lattice.patch",
    "r101-simp1-r98-canvas_lattice.patch",
    "r101-simp1-r98-r98b_attack.patch",
    "r101-simp1-r98-r98b_rksenum.patch",
    "r101-simp1-r99-audio_lattice.patch",
    "r101-simp2-stree_lattice.gd.diff",
    "r101-simp2-scene_io_lattice.gd.diff",
    "r101-simp3-particles-fold.patch",
    "r101-simp3-r95-fold.patch",
    "r101-simp3-r95-harness-comment.patch",
]
R101_FIXTURES = {"export_prod.gd", "r101_seqfull.gd", "r101_ytrans.gd"}


def sections(text):
    """[(file_header_text, hunk_text)] for a unified diff with >=1 file."""
    lines = text.splitlines(keepends=True)
    out = []
    header, i = [], 0
    while i < len(lines) and not lines[i].startswith("@@"):
        header.append(lines[i]); i += 1
    assert header and header[-1].startswith("+++ "), header
    cur = None
    for line in lines[i:]:
        if line.startswith("@@"):
            if cur:
                out.append(("".join(header), "".join(cur)))
            cur = [line]
        else:
            if line.startswith("--- ") and line.rstrip().endswith(".gd") or \
               line.startswith("--- ") and line.rstrip().endswith(".py"):
                # new file header begins (our patches: headers end in .gd/.py)
                if cur:
                    out.append(("".join(header), "".join(cur)))
                    cur = None
                header = [line]
            elif line.startswith("+++ "):
                header.append(line)
            elif cur is not None:
                cur.append(line)
    if cur:
        out.append(("".join(header), "".join(cur)))
    return out


def main():
    rows = []
    idx = 0
    for pname in PATCHES:
        text = (MUT / pname).read_text()
        n_files = sum(1 for l in text.splitlines() if l.startswith("--- "))
        secs = sections(text)
        assert n_files == len({h.splitlines()[0] for h, _ in secs}), (pname, n_files, len(secs))
        for head, hunk in secs:
            m = re.search(r"^\+\+\+ b/(\S+)", head, re.M)
            assert m, head
            target = m.group(1)
            tmp = pathlib.Path(f"/var/tmp/r102-S3/inventory/{pname}.{idx+1}.patch")
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(head + hunk)
            r = subprocess.run(["git", "apply", "--check", str(tmp)], cwd=REPO,
                               capture_output=True, text=True)
            check = f"rc={r.returncode}" + (f" ({r.stderr.strip().splitlines()[0]})" if r.stderr.strip() else "")
            base = pathlib.Path(target).name
            cls = ("SHARED-FILE" if base == "run_battery.py" else
                   "R101-FIXTURE" if base in R101_FIXTURES else "fixture")
            idx += 1
            rows.append((idx, pname, target, hunk.splitlines()[0].split("@@")[1].strip(), check, cls))
    print("| # | patch | target | hunk | per-hunk `git apply --check` | class |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        print("| {idx} | {p} | {f} | `@@{h}@@` | {c} | {cls} |".format(
            idx=r[0], p=r[1].replace("r101-simp", "s"), f=r[2], h=r[3], c=r[4], cls=r[5]))
    print(f"\ntotal hunks: {idx}")
    n_shared = sum(1 for r in rows if r[5] == "SHARED-FILE")
    n_r101 = sum(1 for r in rows if r[5] == "R101-FIXTURE")
    n_bad = sum(1 for r in rows if not r[4].startswith("rc=0"))
    print(f"shared-file hunks: {n_shared}; r101-fixture hunks: {n_r101}; per-hunk check failures: {n_bad}")


if __name__ == "__main__":
    main()
