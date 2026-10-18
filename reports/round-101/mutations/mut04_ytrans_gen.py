#!/usr/bin/env python3
"""MUT-4 (r101) — generate forgery mutants of the REAL C3 fixture corpus/fixtures/r101_ytrans.gd.

Read-only on the lane repo. Writes ONLY under /tmp/r101-mut04/proj2/.

Target fixture: corpus/fixtures/r101_ytrans.gd (E17-YTRANS, sha printed at generation).
Mutation edits are spliced inside `_arm_ytrans()` only (function-body scoped), so
ysep/ycop/census are byte-identical to the pristine fixture.

Mutants (forgery classes for the "omit / order-swap on the C3 Y measurement" seat):
  mut_noop_full      : echo-only forgery -- the flag reaches the PASS line as offy=1000.0000 but
                       the pile/query physics stay at y=0 (the r95 phantom, now with an echo);
                       every evidence key is still emitted, so the fixture self-reports the lie.
  mut_omitevid       : omit forgery (real physics) -- the four physics-bound evidence keys
                       dy_resid / t2_absy / t64_absy / n_at_0 are dropped from the PASS line;
                       the remaining keys are all Y-translation-invariant.
  mut_omitevid_noop  : omit forgery + echo-only physics -- same key set as mut_omitevid but the
                       translation never happens; expected byte-identical to mut_omitevid.
  mut_swapkeys       : order-swap forgery -- t2_vec and t2_relpos emission order swapped
                       (one axis: key order inside the PASS line).
"""
import hashlib
import json
import pathlib
import shutil

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIXTURE = REPO / "corpus/fixtures/r101_ytrans.gd"
R95B = REPO / "corpus/fixtures/r95b_order.gd"
PROJECT = REPO / "corpus/fixtures/project.godot"
OUT = pathlib.Path("/tmp/r101-mut04/proj2")

FUNC = "func _arm_ytrans() -> void:"
NEXT = "# --------------------------------------------------------------- ysep"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sub1(text: str, old: str, new: str, tag: str) -> str:
    n = text.count(old)
    assert n == 1, f"{tag}: {n} hits, expected exactly 1"
    return text.replace(old, new)


def splice_body(src: str, edits):
    head, rest = src.split(FUNC, 1)
    body, tail = rest.split(NEXT, 1)
    for old, new, tag in edits:
        body = sub1(body, old, new, tag)
    return head + FUNC + body + NEXT + tail


def main() -> None:
    src = FIXTURE.read_text()
    src_sha = sha(src)

    edits_noop = [
        ('_pile(["a", "b", "c", "d", "e"], 0.0, offy)', '_pile(["a", "b", "c", "d", "e"], 0.0, 0.0)', "noop pile"),
        ("_ladder(ticks, 0.0, offy)", "_ladder(ticks, 0.0, 0.0)", "noop ladder"),
        ("_pt(Vector2(16.0, offy))", "_pt(Vector2(16.0, 0.0))", "noop query"),
    ]
    edits_omitevid = [
        ('\t_it("dy_resid", _y_resid(made, offy))\n', "", "omit dy_resid"),
        ('\t_it("t2_absy", lad["first_absy"])\n', "", "omit t2_absy"),
        ('\t_it("t64_absy", lad["last_absy"])\n', "", "omit t64_absy"),
        ('\t_it("n_at_0", str(n_0))\n', "", "omit n_at_0"),
    ]
    edits_swap = [
        (
            '\t_it("t2_vec", lad["first_vec"])\n\t_it("t2_relpos", lad["first_relpos"])',
            '\t_it("t2_relpos", lad["first_relpos"])\n\t_it("t2_vec", lad["first_vec"])',
            "swap t2_vec/t2_relpos",
        )
    ]

    noop_full = splice_body(src, edits_noop)
    omit_evid = splice_body(src, edits_omitevid)
    omit_evid_noop = splice_body(omit_evid, edits_noop)
    swap_keys = splice_body(src, edits_swap)

    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "r101_ytrans.gd": src,  # pristine control, as read from the lane repo
        "ytrans_mut_noop_full.gd": noop_full,
        "ytrans_mut_omitevid.gd": omit_evid,
        "ytrans_mut_omitevid_noop.gd": omit_evid_noop,
        "ytrans_mut_swapkeys.gd": swap_keys,
    }
    manifest = {"source": {"path": str(FIXTURE), "sha256": src_sha,
                           "bytes": len(src.encode()), "generated_utc": None}}
    import datetime
    manifest["source"]["generated_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for name, text in outputs.items():
        (OUT / name).write_text(text)
        manifest[name] = {"sha256": sha(text), "bytes": len(text.encode())}
    shutil.copy2(PROJECT, OUT / "project.godot")
    shutil.copy2(R95B, OUT / "r95b_order.gd")  # census measures these exact bytes
    manifest["r95b_order.gd"] = {"sha256": sha((OUT / "r95b_order.gd").read_text()),
                                 "bytes": (OUT / "r95b_order.gd").stat().st_size}
    (OUT.parent / "manifest2.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
