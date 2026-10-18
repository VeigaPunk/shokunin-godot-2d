#!/usr/bin/env python3
"""MUT-4 (r101) — apply ver8's staged variant-C C3 landing to scratch and grow its forgeries.

Inputs (read-only lane repo):
  reports/round-101/mutations/r101-ver8-offy-C.patch      (fixture: _arm_celloff consumes --offy; _relpos x-only)
  reports/round-101/mutations/r101-ver8-offy-C-cases.patch (harness: new 439 B expected line)
Outputs: /tmp/r101-mut04/proj3/  (patched fixture + project.godot + 3 one-axis mutants)

Cross-seat provenance checks (assert):
  * patched fixture sha256 == ver8's stated 9ed7ba47...25544 B
  * extracted expected line == 439 B, md5 fb57ea8b1d0f13e64e57703b8d30b5a3
If either fails, this script stops and the shard must not claim the cross-check.
"""
import hashlib
import json
import pathlib
import shutil
import subprocess

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus/fixtures/r95b_order.gd"
PROJ = REPO / "corpus/fixtures/project.godot"
PATCH = REPO / "reports/round-101/mutations/r101-ver8-offy-C.patch"
CPATCH = REPO / "reports/round-101/mutations/r101-ver8-offy-C-cases.patch"
OUT = pathlib.Path("/tmp/r101-mut04/proj3")

FUNC = "func _arm_celloff() -> void:"
NEXT = "# --------------------------------------------------------------- rigid"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sub1(text: str, old: str, new: str, tag: str) -> str:
    n = text.count(old)
    assert n == 1, f"{tag}: {n} hits, expected exactly 1"
    return text.replace(old, new)


def splice(src: str, edits):
    head, rest = src.split(FUNC, 1)
    body, tail = rest.split(NEXT, 1)
    for old, new, tag in edits:
        body = sub1(body, old, new, tag)
    return head + FUNC + body + NEXT + tail


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIX, OUT / "r95b_order.gd")
    shutil.copy2(PROJ, OUT / "project.godot")
    r = subprocess.run(["patch", "-p3", "-i", str(PATCH)], cwd=OUT,
                       capture_output=True, text=True)
    assert r.returncode == 0, f"patch failed: {r.stdout}{r.stderr}"
    patched = (OUT / "r95b_order.gd").read_text()
    patched_sha = sha(patched)
    assert patched_sha == "9ed7ba4795b1aa53dd734304af218c6f9c44c61234f0a8e3333d0827052816d9", \
        f"patched sha {patched_sha} != ver8 stated 9ed7ba47..."
    assert len(patched.encode()) == 25544

    cp = CPATCH.read_text()
    cand = [l for l in cp.splitlines() if l.startswith("+") and "'PASS r95b_order celloff" in l]
    assert len(cand) == 1, f"{len(cand)} candidate expected lines"
    sig = cand[0][1:].split("'")[1]
    sig_md5 = hashlib.md5(sig.encode()).hexdigest()
    assert len(sig.encode()) == 439, f"expected line {len(sig.encode())} B"
    assert sig_md5 == "fb57ea8b1d0f13e64e57703b8d30b5a3", f"expected line md5 {sig_md5}"
    (OUT / "c_expected.txt").write_text(sig)

    relpos_pair = ('\t_it("t2_relpos", lad["first_relpos"])\n'
                   '\t_it("t64_relpos", lad["last_relpos"])')
    norm_helper = (
        "func _relpos_norm(s: String, oy: float) -> String:\n"
        '\tvar out: PackedStringArray = []\n'
        '\tfor part in s.trim_prefix("[").trim_suffix("]").split("|"):\n'
        '\t\tvar xy := part.split(",")\n'
        '\t\tout.append("%.4f,%.4f" % [float(xy[0]), float(xy[1]) - oy])\n'
        '\treturn "[%s]" % "|".join(out)\n\n'
    )
    # splice() splits on FUNC, so the helper must be injected at the function start.
    head, rest = patched.split(FUNC, 1)
    body, tail = rest.split(NEXT, 1)
    body_omit = sub1(body, relpos_pair,
                     '\t_it("t2_relpos", _relpos_norm(lad["first_relpos"], offy))\n'
                     '\t_it("t64_relpos", _relpos_norm(lad["last_relpos"], offy))', "omit y")
    omit_y = head + norm_helper + FUNC + body_omit + NEXT + tail
    swap = splice(patched, [(relpos_pair,
                             '\t_it("t64_relpos", lad["last_relpos"])\n'
                             '\t_it("t2_relpos", lad["first_relpos"])', "swap keys")])
    dropt64 = splice(patched, [(relpos_pair, '\t_it("t2_relpos", lad["first_relpos"])', "drop t64")])

    manifest = {
        "source_fixture": {"sha256": sha(FIX.read_text()), "bytes": FIX.stat().st_size},
        "patch_applied": {"file": str(PATCH), "patched_sha256": patched_sha,
                          "patched_bytes": len(patched.encode())},
        "expected_line": {"sha_md5": sig_md5, "bytes": len(sig.encode()),
                          "from": str(CPATCH)},
        "r95b_order.gd": {"sha256": patched_sha, "bytes": len(patched.encode())},
        "c_mut_omit_y.gd": {"sha256": sha(omit_y), "bytes": len(omit_y.encode())},
        "c_mut_swapkeys.gd": {"sha256": sha(swap), "bytes": len(swap.encode())},
        "c_mut_dropt64.gd": {"sha256": sha(dropt64), "bytes": len(dropt64.encode())},
    }
    for name, text in {"r95b_order.gd": patched, "c_mut_omit_y.gd": omit_y,
                       "c_mut_swapkeys.gd": swap, "c_mut_dropt64.gd": dropt64}.items():
        (OUT / name).write_text(text)
    (OUT.parent / "manifest3.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
