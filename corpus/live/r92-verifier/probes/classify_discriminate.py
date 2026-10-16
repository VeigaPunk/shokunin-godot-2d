#!/usr/bin/env python3
"""r92 verifier — production-classifier discrimination on the r92 rows.

Uses the AST-extracted `classify_process` (verbatim from the committed harness)
and mirrors execute()'s envelope / required_stderr / stdout-anchor path.

Shapes exercised:
  * 9 allowlist-bearing rows: real receipt admitted WITH the committed
    expected_errors and REJECTED bare (the entry is load-bearing).
  * nullts: real receipt admitted; four forged shapes rejected
    (fragments-on-stdout, signature-on-stderr-only, rc flipped, fragment
    removed).
  * nav: both payloads admitted; a one-field mutation rejected.
"""
import ast
import hashlib
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r92-verifier"
FIX = V / "tree" / "corpus" / "fixtures" / "run_battery.py"
ARMS = V / "arms"

src = FIX.read_text()
tree = ast.parse(src)
ns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        print(f"classify_process segment sha256={hashlib.sha256(seg.encode()).hexdigest()}")
        exec("import re\n" + seg, ns)
classify = ns["classify_process"]

cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
rows = {}
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0].startswith("r92_"):
        rows[t[0]] = {"exit": t[3], "sig": t[4]}
exp_errors, req_stderr = {}, {}
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if "r92_tilemap_atlas" in keys and "nav_lattice_bake" in keys:
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant):
                    exp_errors[k.value] = ast.literal_eval(v)
        if "r92_tilemap_nullts_crash" in keys and "nav_lattice_teardown_crash" in keys:
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant):
                    req_stderr[k.value] = ast.literal_eval(v)

def row_verdict(case, rc, out, err):
    """Mirror of execute() for one receipt: envelope + required_stderr."""
    row = rows[case]
    sigs = row["sig"] if isinstance(row["sig"], (tuple, list)) else (row["sig"],)
    ee = exp_errors.get(case, ())
    rs = req_stderr.get(case, ())
    merged = out + err
    passed = any(classify(rc, None, merged, row["exit"], s, ee) for s in sigs)
    if rs:
        passed = passed and all(f in err for f in rs) and any(s in out for s in sigs)
    return passed

def bare_verdict(case, rc, out, err):
    row = rows[case]
    sigs = row["sig"] if isinstance(row["sig"], (tuple, list)) else (row["sig"],)
    merged = out + err
    return any(classify(rc, None, merged, row["exit"], s, ()) for s in sigs)

results = []
def check(name, cond):
    results.append((name, bool(cond)))

ALLOW = ["r92_tilemap_atlas", "r92_tilemap_cells", "r92_tilemap_custom",
         "r92_tilemap_terrain", "r92_tilemap_pattern", "r92_tilemap_encoding",
         "r92_tilemap_fixinvalid", "r92_tilemap_srcids", "r92_tilemap_physics"]

print("\n--- allowlist load-bearing (real fresh receipts) ---")
for case in ALLOW:
    arm = case.removeprefix("r92_tilemap_")
    out = (ARMS / f"{arm}.rep1.out").read_text()
    err = (ARMS / f"{arm}.rep1.err").read_text()
    rc = int((ARMS / f"{arm}.rep1.rc").read_text().strip())
    with_ = row_verdict(case, rc, out, err)
    without = bare_verdict(case, rc, out, err)
    n_err = sum(1 for l in (out + err).splitlines() if "ERROR:" in l)
    print(f"  {case:28s} with_allowlist={with_!s:5s} bare={without!s:5s} ERROR_lines={n_err}")
    check(f"{case}: admitted with allowlist", with_)
    check(f"{case}: rejected without allowlist (load-bearing)", not without)

print("\n--- nullts crash row: real + forged shapes ---")
# rep1 of the second sweep hit the 8 s wall bound (a TIMEOUT, not a
# classification event); rep2 is a clean rc=-6 receipt.
out = (ARMS / "nullts.rep2.out").read_text()
err = (ARMS / "nullts.rep2.err").read_text()
rc = int((ARMS / "nullts.rep2.rc").read_text().strip())
sig = rows["r92_tilemap_nullts_crash"]["sig"]
frags = req_stderr["r92_tilemap_nullts_crash"]
shapes = {
    "real receipt (rc=-6, sig on stdout, fragments on stderr)": (rc, out, err, True),
    "fragments moved to stdout, stderr empty": (rc, out + "\n".join(frags) + "\n", "", False),
    "signature on stderr only": (rc, "", err + sig + "\n", False),
    "signature absent everywhere": (rc, out.replace(sig, "R92 nullts other=1"), err, False),
    "rc flipped to 0": (0, out, err, False),
    "one fragment removed from stderr": (rc, out, err.replace(frags[1], ""), False),
    "foreign SIGSEGV class (stderr has no pinned fragments)":
        (rc, out, "handle_crash: Program crashed with signal 11\n", False),
}
for name, (c, o, e, want) in shapes.items():
    got = row_verdict("r92_tilemap_nullts_crash", c, o, e)
    print(f"  {'OK  ' if got == want else 'FAIL'} {name}: verdict={got} want={want}")
    check(f"nullts shape: {name}", got == want)

print("\n--- nav envelope: both payloads admitted, mutations rejected ---")
nav = rows["r92_tilemap_nav"]["sig"]
p0, p1 = nav
nav_receipt = (ARMS / "nav.rep1.out").read_text()
nav_err = (ARMS / "nav.rep1.err").read_text()
nav_rc = int((ARMS / "nav.rep1.rc").read_text().strip())
print(f"  live nav receipt rc={nav_rc} payload[0] present={p0 in nav_receipt} "
      f"payload[1] present={p1 in nav_receipt}")
check("nav live receipt admitted", row_verdict("r92_tilemap_nav", nav_rc, nav_receipt, nav_err))
check("nav live receipt is payload[0] (production scheduler)", p0 in nav_receipt)
# synthetic payload[1] receipt (the --fixed-fps regime), built from the real one
synth_p1 = nav_receipt.replace("regions_f1=1", "regions_f1=0")
check("nav synthetic payload[1] admitted", row_verdict("r92_tilemap_nav", nav_rc, synth_p1, nav_err))
# mutations (applied to the PASS line only: the arm also prints per-field
# `R92 nav <key>=<value>` diagnostics, and mutating the first occurrence in the
# file would leave the pinned PASS line untouched)
nav_pass = next(l for l in nav_receipt.splitlines() if l.startswith("PASS tilemap_lattice nav "))
for field, bad in (("regions_f1", "regions_f1=7"), ("regions_f2", "regions_f2=0"),
                   ("regions_reenabled", "regions_reenabled=0"),
                   ("nav_map_valid", "nav_map_valid=0")):
    assert f"{field}=1" in nav_pass, field
    mutated = nav_receipt.replace(nav_pass, nav_pass.replace(f"{field}=1", bad, 1), 1)
    got = row_verdict("r92_tilemap_nav", nav_rc, mutated, nav_err)
    print(f"  {'OK  ' if not got else 'FAIL'} nav mutation {field} -> {bad}: verdict={got} want=False")
    check(f"nav mutation {field} rejected", not got)

n_fail = sum(1 for _, ok in results if not ok)
print(f"\nchecks={len(results)} fails={n_fail}")
sys.exit(1 if n_fail else 0)
