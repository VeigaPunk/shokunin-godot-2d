#!/usr/bin/env python3
"""r95 critic: build fixture/harness mutants from the frozen committed tree.

Every mutant is a byte-copy of corpus/live/r95-critic/frozen/corpus/fixtures with
ONE declared textual substitution, recorded in mutants/<name>/mutation.json.
"""
import json
import shutil
import sys
from pathlib import Path

SEAT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r95-critic")
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
MUT = SEAT / "mutants"


def copy_tree(dest: Path):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(FROZEN, dest)


def patch(dest: Path, rel: str, old: str, new: str, count=1):
    p = dest / rel
    text = p.read_text()
    assert text.count(old) == count, f"{rel}: expected {count} occurrence(s), got {text.count(old)}"
    p.write_text(text.replace(old, new, count))


def arm_order_core_nomeasure(dest: Path):
    old = '''	var first := _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP))
	_it("rep1", first)'''
    new = '''	_pass()
	var first := _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP))
	_it("rep1", first)'''
    patch(dest, "dss_lattice.gd", old, new)


def arm_order_core_mirror(dest: Path):
    old = "	_pile(order, 0.0, 0.0, made)"
    new = "	var mir: Array = order.duplicate()\n	mir.reverse()\n	_pile(mir, 0.0, 0.0, made)"
    patch(dest, "dss_lattice.gd", old, new)


def arm_point_cap_cap0_full(dest: Path):
    old = '_it("cap0", _ord(dss.intersect_point(_pt(Vector2(16, 0)), 0)))'
    new = '_it("cap0", _ord(dss.intersect_point(_pt(Vector2(16, 0)), CAP)))'
    patch(dest, "dss_lattice.gd", old, new)


def arm_canon_extra_collider(dest: Path):
    old = '''	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	_it("add_order", "[a,b,c,d,e]")
	_it("map", "[a@0,b@8,c@16,d@24,e@32]")
	var dss := _dss()'''
    new = '''	var made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)
	_mk_body("z", Vector2(16.0, 0.0), Vector2(40, 40))
	_it("add_order", "[a,b,c,d,e]")
	_it("map", "[a@0,b@8,c@16,d@24,e@32]")
	var dss := _dss()'''
    patch(dest, "r95b_order.gd", old, new)


def arm_periodx_extended_window(dest: Path):
    # extend the observation window to 2*k*(k-1)+3 ticks and search p up to 2*k*(k-1);
    # the pinned `n_ticks=` token will differ -> this arm is read out of band (the
    # emitted cycle_len is compared against the same law over the longer window).
    old = "	var nticks := k * (k - 1) + 3"
    new = "	var nticks := 2 * k * (k - 1) + 3"
    patch(dest, "r95b_order.gd", old, new)
    old2 = "	for p in range(1, k * (k - 1) + 1):"
    new2 = "	for p in range(1, 2 * k * (k - 1) + 1):"
    patch(dest, "r95b_order.gd", old2, new2)


MUTANTS = {
    "m1a_ordercore_nomeasure": (arm_order_core_nomeasure, "order_core/_rev: all queries removed after the add_order echo"),
    "m1b_ordercore_mirror": (arm_order_core_mirror, "order_core/_rev: real creation order mirrored, add_order echo unchanged"),
    "m2_pointcap_cap0_full": (arm_point_cap_cap0_full, "point_cap: cap0 operand prints the full set instead of the cap-0 set"),
    "m3_canon_extra_collider": (arm_canon_extra_collider, "canon: a 6th overlapping collider added to the pile"),
    "m5_periodx_ext_window": (arm_periodx_extended_window, "periodx: observation window doubled (out-of-band readout)"),
}


def main():
    for name, (fn, note) in MUTANTS.items():
        dest = MUT / name / "fixtures"
        copy_tree(dest)
        fn(dest)
        (MUT / name / "mutation.json").write_text(json.dumps({"name": name, "note": note}, indent=1))
        print(f"built {name}: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
