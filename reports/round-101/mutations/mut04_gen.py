#!/usr/bin/env python3
"""MUT-4 (r101) — generate the C3 Y-measurement model fixture and its forgery mutants.

Read-only on the lane repo. Writes ONLY under /tmp/r101-mut04/proj/.

Source of truth: corpus/fixtures/r95b_order.gd
  (sha256 4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490,
   the lane-frozen probe per run_battery.py:884-886)

Patch axis (models the projected C3 "real Y-translation measurement", i.e. what
E17's r101_ytrans.gd would have to do to make the y=+1000 cell measurable):
  * _ladder gains an optional oy (query at Vector2(16+ox, oy)); default 0.0 keeps
    every other arm byte-identical.
  * _arm_celloff reads --offy, translates the pile to y=offy, queries at y=offy,
    and prints an `offy=` key. _relpos leaves y raw, so the translation lands in
    the pinned bytes (y=1000.0000) -- that is the discriminating content.

Mutants (one axis each, all on top of the patched baseline ytrans_base.gd):
  m1_echo     : --offy never reaches pile/query; PASS line still echoes offy=1000.0000
  m2_omitkey  : measurement real; the `offy=` key is omitted from the PASS line
  m3_omity    : measurement real; relpos y normalized (-offy) so no 1000.0000 byte is emitted
  m4_swapkeys : measurement real; t64_relpos and t2_relpos keys swapped in emission order
  m5_noenv    : measurement real; the R95B env diagnostic line is omitted

Also copied: project.godot + the unpatched r95b_order.gd (phantom-state control).
"""
import hashlib
import json
import pathlib
import shutil

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SRC = REPO / "corpus/fixtures/r95b_order.gd"
PROJECT = REPO / "corpus/fixtures/project.godot"
OUT = pathlib.Path("/tmp/r101-mut04/proj")

SRC_SHA = "4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sub1(text: str, old: str, new: str, tag: str) -> str:
    n = text.count(old)
    assert n == 1, f"{tag}: {n} hits, expected exactly 1"
    return text.replace(old, new)


def main() -> None:
    src = SRC.read_text()
    assert sha(src) == SRC_SHA, "source drift: r95b_order.gd changed"

    p1_old = (
        "func _ladder(ticks: Array, ox: float) -> Dictionary:\n"
        "\tvar dss := _dss()\n"
        "\tvar q := Vector2(16.0 + ox, 0.0)"
    )
    p1_new = (
        "func _ladder(ticks: Array, ox: float, oy: float = 0.0) -> Dictionary:\n"
        "\tvar dss := _dss()\n"
        "\tvar q := Vector2(16.0 + ox, oy)"
    )
    celloff_old = (
        '\tvar off := _opt_float("off", 0.0)\n'
        '\tvar made := _pile(["a", "b", "c", "d", "e"], off, 0.0)\n'
        '\t_it("off", "%.4f" % off)\n'
        '\t_it("add_order", "[a,b,c,d,e]")\n'
        "\tvar ticks := [2, 3, 4, 6, 8, 16, 32, 64]\n"
        "\tvar lad := await _ladder(ticks, off)"
    )
    celloff_new = (
        '\tvar off := _opt_float("off", 0.0)\n'
        '\tvar offy := _opt_float("offy", 0.0)\n'
        '\tvar made := _pile(["a", "b", "c", "d", "e"], off, offy)\n'
        '\t_it("off", "%.4f" % off)\n'
        '\t_it("offy", "%.4f" % offy)\n'
        '\t_it("add_order", "[a,b,c,d,e]")\n'
        "\tvar ticks := [2, 3, 4, 6, 8, 16, 32, 64]\n"
        "\tvar lad := await _ladder(ticks, off, offy)"
    )
    base = sub1(sub1(src, p1_old, p1_new, "P1 ladder oy"), celloff_old, celloff_new, "P2 celloff")

    relpos_pair = (
        '\t_it("t2_relpos", lad["first_relpos"])\n'
        '\t_it("t64_relpos", lad["last_relpos"])'
    )

    m1 = sub1(base, '_pile(["a", "b", "c", "d", "e"], off, offy)', '_pile(["a", "b", "c", "d", "e"], off, 0.0)', "m1 pile")
    m1 = sub1(m1, "_ladder(ticks, off, offy)", "_ladder(ticks, off, 0.0)", "m1 ladder")

    m2 = sub1(base, '\t_it("offy", "%.4f" % offy)\n', "", "m2 omit offy key")

    norm_helper = (
        "func _relpos_norm(s: String, oy: float) -> String:\n"
        '\tvar out: PackedStringArray = []\n'
        '\tfor part in s.trim_prefix("[").trim_suffix("]").split("|"):\n'
        '\t\tvar xy := part.split(",")\n'
        '\t\tout.append("%.4f,%.4f" % [float(xy[0]), float(xy[1]) - oy])\n'
        '\treturn "[%s]" % "|".join(out)\n\n'
    )
    m3 = sub1(base, "func _arm_celloff() -> void:\n", norm_helper + "func _arm_celloff() -> void:\n", "m3 helper")
    m3 = sub1(
        m3,
        relpos_pair,
        '\t_it("t2_relpos", _relpos_norm(lad["first_relpos"], offy))\n'
        '\t_it("t64_relpos", _relpos_norm(lad["last_relpos"], offy))',
        "m3 normalize y",
    )

    m4 = sub1(
        base,
        relpos_pair,
        '\t_it("t64_relpos", lad["last_relpos"])\n'
        '\t_it("t2_relpos", lad["first_relpos"])',
        "m4 key swap",
    )

    m5 = sub1(base, '\t_it("t64_relpos", lad["last_relpos"])\n\t_diag("env", _envstr())',
              '\t_it("t64_relpos", lad["last_relpos"])', "m5 drop env diag")

    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "r95b_order.gd": src,
        "ytrans_base.gd": base,
        "ytrans_m1_echo.gd": m1,
        "ytrans_m2_omitkey.gd": m2,
        "ytrans_m3_omity.gd": m3,
        "ytrans_m4_swapkeys.gd": m4,
        "ytrans_m5_noenv.gd": m5,
    }
    manifest = {}
    for name, text in outputs.items():
        path = OUT / name
        path.write_text(text)
        manifest[name] = {"sha256": sha(text), "bytes": len(text.encode())}
    shutil.copy2(PROJECT, OUT / "project.godot")
    manifest["project.godot"] = {"sha256": sha((OUT / "project.godot").read_text()),
                                 "bytes": (OUT / "project.godot").stat().st_size}
    (OUT.parent / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
