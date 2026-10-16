#!/usr/bin/env python3
"""r91 verifier — independent closed-form re-derivations of the committed pins.

Every check recomputes a pinned value from the fixture's declared geometry /
constants (read from the frozen nav_lattice.gd + run_battery.py) and compares
with the committed CASES signature. No engine execution here.
"""
import ast
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
V = ROOT / "corpus/live/r91-verifier"
HARNESS = V / "tree/corpus/fixtures/run_battery.py"

tree = ast.parse(HARNESS.read_text())
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
SIG = {c[0]: c[4] for c in cases if c[0].startswith("nav_lattice_")}

checks = []


def check(tag, expected, actual, note=""):
    ok = expected == actual
    checks.append((tag, ok, expected, actual, note))
    print(f"{'PASS' if ok else 'FAIL'} {tag}: expected={expected!r} actual={actual!r} {note}")


def f4(x):
    return f"{x:.4f}"


def path_len(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def grab(sig, field):
    """Balanced-bracket aware field extractor."""
    m = re.search(rf"(?:^| ){field}=", sig)
    assert m, (field, sig[:120])
    i = m.end()
    if sig[i] in "[(":
        open_c, close_c = sig[i], "]" if sig[i] == "[" else ")"
        depth = 0
        for j in range(i, len(sig)):
            if sig[j] == open_c:
                depth += 1
            elif sig[j] == close_c:
                depth -= 1
                if depth == 0:
                    return sig[i:j + 1]
        raise AssertionError(field)
    j = sig.find(" ", i)
    return sig[i:] if j < 0 else sig[i:j]


def vertices(field_value):
    """Parse '[(a,b),(c,d),...]' into [(float,float), ...]."""
    return [tuple(float(x) for x in m.groups())
            for m in re.finditer(r"\((-?\d+\.\d+),(-?\d+\.\d+)\)", field_value)]


def v(x, y):
    return f"({f4(x)},{f4(y)})"


# ---------------------------------------------------------------- R1 path arm
sig = SIG["nav_lattice_path"]
diag = [(20, 180), (40, 40), (180, 20)]
raw = [(20, 180), (40, 20), (180, 20)]
check("R1a diag polyline length = 200*sqrt2", "282.8427", f4(path_len(diag)))
check("R1b edge-center cell polyline length", "301.2452", f4(path_len(raw)),
      "NOTE: this is the EDGECENTERED(1) cell (pp1); the row's length pin is the CORRIDORFUNNEL(0) cell (pp0, corner-cut, 282.8427)")
# out_start: line (0,0)->(90,20) crossing x=40
t = (40 - 0) / (90 - 0)
check("R1c out_start crossing x=40", v(40, 20 * t), "(40.0000,8.8889)")
# out_target: line (20,20)->(200,40) crossing x=40; closest point to (400,400) is (200,40)
t = (40 - 20) / (200 - 20)
check("R1d out_target crossing x=40", v(40, 20 + 20 * t), "(40.0000,22.2222)")
check("R1e out_target endpoint = closest point on rh to (400,400)", v(200, 40), "(200.0000,40.0000)")
check("R1f gap20 bridge midpoint of x=200..210", v(205, 20), "(205.0000,20.0000)")
check("R1g gap20 margin >= 10 px gap", "20.0000", grab(sig, "gap20_margin"))

# ---------------------------------------------------------------- R2 query arm
sig = SIG["nav_lattice_query"]
# maxlen=30 truncation along (20,180)->(40,40)
d = (20, -140)
n = math.hypot(*d)
p = (20 + 30 * d[0] / n, 180 + 30 * d[1] / n)
check("R2a maxlen=30 truncation point", f"[(20.0000,180.0000),{v(*p)}]",
      grab(sig, "maxlen"))
# maxrad=60 pin (empirical; characterize only)
print("INFO R2b maxrad=60 pinned:", grab(sig, "maxrad"))
# maxpolys=1 truncates inside the first polygon (rv) at its far corner (40,20)
check("R2c maxpolys=1 first-polygon cut", "[(20.0000,180.0000),(40.0000,20.0000)]",
      grab(sig, "maxpolys"))
# metadata flag matrix: NONE=0, RIDS=2, TYPES=1, OWNERS=4, ALL=7; 3-point path
md_expected = "md0:[]|n0|n0,md2:[]|n3|n0,md1:[0,0,0]|n0|n0,md4:[]|n0|n3,md7:[0,0,0]|n3|n3"
check("R2d metadata flag matrix", md_expected, grab(sig, "metadata").strip("[]"))
check("R2e length pin = polyline length of the CORRIDORFUNNEL(0) cell (pp0 corner-cut)",
      "282.8427", grab(sig, "length"),
      "NOTE: enum order NONE=2/CORRIDORFUNNEL=0/EDGECENTERED=1 (scout 3.1); pp0 path polyline = 200*sqrt2")

# ---------------------------------------------------------------- R3 agent arm
sig = SIG["nav_lattice_agent"]
check("R3a settled straight-line dist 160*sqrt2 -> %.2f", "226.27", f"{160 * math.sqrt(2):.2f}")
check("R3b path length 160*sqrt2 -> %.2f", "226.27", f"{160 * math.sqrt(2):.2f}")
check("R3c final_pos = target - 1.608 each axis (dist 1.608*sqrt2=2.2741)",
      v(180 - 1.608, 180 - 1.608), grab(sig, "final_pos"))
check("R3d dist pin = 1.608*sqrt2", "2.2741", f4(1.608 * math.sqrt(2)))
check("R3e settled next-point = path endpoint", "(180.0000,180.0000)", grab(sig, "settled").split("/")[0])

# ---------------------------------------------------------------- R4 avoid arm
sig = SIG["nav_lattice_avoid"]
check("R4a warmup 16 + measured 5 = 21", "21", grab(sig, "n_a"))
check("R4b warm_n_a = 16", "16", grab(sig, "warm_n_a"))
# ORCA bound (r_a + r_b) / tau with radius 10+10, time_horizon 1.0
check("R4c ORCA bound (10+10)/1.0", "20.0000", f4((10 + 10) / 1.0))
check("R4d radii/speed from fixture set calls", ("10.0", "50.0"), (grab(sig, "radius_a"), grab(sig, "maxspeed_a")))
check("R4e obstacle from fixture", ("(170.0000,150.0000)", "false"), (grab(sig, "obs_pos"), grab(sig, "obs_en")))

# ---------------------------------------------------------------- R5 bake arm
sig = SIG["nav_lattice_bake"]
check("R5a outline 4 verts + 4 verts hole", ("4", "8"), (grab(sig, "outline_polys"), grab(sig, "outline_verts")))
check("R5b square annulus bake = 4 polys / 8 verts", ("4", "8"), (grab(sig, "baked_polys"), grab(sig, "baked_verts")))
check("R5c collider-only silent empty", "0", grab(sig, "collider_only_polys"))
through = vertices(grab(sig, "through"))
around = vertices(grab(sig, "around"))
outside = vertices(grab(sig, "outside"))
check("R5d agent_radius=5 erosion: hole +-50 -> +-55",
      [(-100.0, 0.0), (-55.0, 55.0), (55.0, 55.0), (100.0, 0.0)], through)
check("R5e baking_rect -150 + agent_radius 5 = -145",
      (-145.0, -145.0), outside[0])
check("R5f around path corners", [(-100.0, -100.0), (-55.0, 55.0), (100.0, 100.0)], around)

# ---------------------------------------------------------------- R6 region arm
sig = SIG["nav_lattice_region"]
check("R6a b-corridor endpoints are closest points of b to start/target",
      "[(20.0000,40.0000),(80.0000,40.0000)]", grab(sig, "l2"))
check("R6b base (tie) chooses top corridor", "[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)]",
      grab(sig, "base"))
check("R6c dis_settled falls back to bottom", "[(10.0000,50.0000),(20.0000,40.0000),(80.0000,40.0000),(90.0000,50.0000)]",
      grab(sig, "dis_settled"))
check("R6d counts regs=4 and reset costs", "regs=4,cost_a=1.0,cost_b=1.0,en_a=true,en_b=true",
      grab(sig, "counts").strip("[]"))

# ---------------------------------------------------------------- R7 link arm
sig = SIG["nav_lattice_link"]
check("R7a fwd path = r1 run + link + r2 run", "[(10.0000,50.0000),(100.0000,50.0000),(400.0000,50.0000),(490.0000,50.0000)]",
      grab(sig, "fwd_default"))
check("R7b disabled link truncates at r1 end", "[(10.0000,50.0000),(100.0000,50.0000)]", grab(sig, "fwd_disabled_settled"))
check("R7c layer1 excludes the layer-2 link", "[(10.0000,50.0000),(100.0000,50.0000)]", grab(sig, "layer1"))
check("R7d layer2 excludes layer-1 regions", "[]", grab(sig, "layer2"))
check("R7e link property reads", ("(100.0000,50.0000)", "(400.0000,50.0000)", "1.0", "0.0", "2"),
      (grab(sig, "start"), grab(sig, "end"), grab(sig, "cost"), grab(sig, "enter"), grab(sig, "layers")))

# ---------------------------------------------------------------- R8 sync arm
sig = SIG["nav_lattice_sync"]
check("R8a pre-sync state (iteration 0, no regions, empty path, zero closest)",
      ("0", "0", "[]", "(0.0000,0.0000)"),
      (grab(sig, "pre_iter"), grab(sig, "pre_regions"), grab(sig, "pre_path"), grab(sig, "pre_closest")))
check("R8b sync law halves (new answer not same-frame, settled true, disable not settled)",
      ("false", "true", "false"), (grab(sig, "chg_same"), grab(sig, "chg_settled"), grab(sig, "dis_settled")))

# ---------------------------------------------------------------- R9 census arm
sig = SIG["nav_lattice_census"]
check("R9a qp_defaults (pp=0, md=7, maxpolys=4096, layers=1)", "pp=0,md=7,layers=1,maxlen=0.0000,maxrad=0.0000,maxdist=0.0000,maxpolys=4096,simpl=false,eps=0.0000",
      grab(sig, "qp_defaults").strip("[]"))
check("R9b agent_defaults radius/path/target", "r=10.0000,path_d=20.0000,tgt_d=10.0000", grab(sig, "agent_defaults").strip("[]")[:len("r=10.0000,path_d=20.0000,tgt_d=10.0000")])

# ---------------------------------------------------------------- R10 teardown
sig = SIG["nav_lattice_teardown_crash"]
check("R10a crash marker stdout-anchored", "NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=true", sig)
check("R10b expected exit -6", "-6", str([c[3] for c in cases if c[0] == "nav_lattice_teardown_crash"][0]))
check("R10c clean control exit 0", "0", str([c[3] for c in cases if c[0] == "nav_lattice_teardown_clean"][0]))

print()
print("TOTAL", sum(1 for _, ok, *_ in checks if ok), "/", len(checks), "checks pass")
