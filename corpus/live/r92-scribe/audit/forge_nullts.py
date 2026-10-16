#!/usr/bin/env python3
"""r92-scribe: nullts row binding falsification (production classifier).

Extracts classify_process + the r92 required_stderr pair from HEAD's harness
(AST) and applies the row's FULL pass condition to real receipt streams,
mutating one half at a time. A row that still passes with a half removed is
not bound to this null-deref.

Row pass condition (harness, lines 1249-1266):
    any(classify_process(code, None, merged, -6, sig) for sig in payloads)
    and all(frag in stderr for frag in required_stderr)
    and any(sig in stdout for sig in payloads)
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LIVE = REPO / "corpus" / "live"
src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
                     capture_output=True, check=True).stdout.decode()
tree = ast.parse(src)

fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        fn_src = "    " + seg.replace("\n", "\n    ")
        break
ns = {}
exec("def _wrap():\n" + fn_src + "\n    return classify_process\n", ns)
classify_process = ns["_wrap"]()
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()

cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
row = next(c for c in cases if c[0] == "r92_tilemap_nullts_crash")
expected_exit, signature = row[3], row[4]

rs = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "required_stderr" for t in node.targets):
        for sub in ast.walk(node.value):
            if isinstance(sub, ast.Dict):
                d = ast.literal_eval(sub)
                if "r92_tilemap_nullts_crash" in d:
                    rs = tuple(d["r92_tilemap_nullts_crash"])
assert rs, "required_stderr pair not found"


def row_passes(code, stdout, stderr, sig=signature, frags=rs,
               merge_for_classifier=True):
    merged = stdout + stderr if merge_for_classifier else stdout
    return (classify_process(code, None, merged, expected_exit, sig)
            and all(f in stderr for f in frags)
            and sig in stdout)


receipts = []
for tag, base in [("author-fresh", LIVE / "r92-author" / "fresh-reps"),
                  ("scribe-fresh", LIVE / "r92-scribe" / "fresh"),
                  ("scout-hazard", LIVE / "r92-scout" / "runs")]:
    if not base.exists():
        continue
    for out in sorted(base.glob("*nullts*.out")) + sorted(base.glob("*setcell_td*.out")):
        err, rcfile = out.with_suffix(".err"), out.with_suffix(".rc")
        if not err.exists():
            continue
        code = int(rcfile.read_text().strip()) if rcfile.exists() else 134
        receipts.append({"tag": tag, "name": out.name, "code": code,
                         "stdout": out.read_text(errors="replace"),
                         "stderr": err.read_text(errors="replace")})

variants = {}
for r in receipts:
    st, se, code = r["stdout"], r["stderr"], r["code"]
    frags = rs
    v = {
        # genuine receipt as recorded on disk (scout receipts: bash-timeout 134)
        "A_genuine_as_recorded": row_passes(code, st, se),
        # same streams, rc normalised to the Python-subprocess encoding
        "A2_rc_normalised_minus6": row_passes(-6, st, se),
        # 134 (128+6, shell wrapper) must NOT satisfy the -6 pin
        "A3_rc_134_shell_encoding": row_passes(134, st, se),
        # stderr stream stripped: fragments missing -> fail
        "B_stderr_stripped": row_passes(code, st, ""),
        # stdout stream stripped: stdout anchor missing -> fail
        "C_stdout_stripped": row_passes(code, "", se),
        # fragments moved onto stdout (merged blob still contains them):
        # the stderr-stream anchor must reject
        "D_stream_anchor_moved_to_stdout": row_passes(code, st + "\n" + "\n".join(rs), ""),
        # rc=0 with the same streams -> fail
        "E_rc0": row_passes(0, st, se),
        # a sibling hazard's anchor must not satisfy this row
        "F_other_hazard_signature": row_passes(code, st, se, sig="R92 nullts2 about_to_call"),
        # wrong crash site in the stderr fragment -> fail
        "G_wrong_site_fragment": row_passes(
            code, st, se, frags=(frags[0], "_nullts (res://tilemap_lattice.gd:928)")),
        # wrong handler header -> fail
        "H_wrong_handler_fragment": row_passes(
            code, st, se, frags=("handle_crash: Program crashed with signal 6", frags[1])),
    }
    variants[f"{r['tag']}/{r['name']}"] = v

# ---- cross-receipt: foreign SIGABRT/SIGSEGV crashes must not satisfy the row ----
cross = {}
foreign = {
    "r91-teardown-crash": LIVE / "r91-scribe" / "fresh" / "teardown_crash",
    "r92-author-nullts-rep1": LIVE / "r92-author" / "fresh-reps" / "nullts.rep1",
    "scribe-nullts-rep1": LIVE / "r92-scribe" / "fresh" / "nullts.rep1",
}
for label, stem in foreign.items():
    o, e, c = stem.with_suffix(".out"), stem.with_suffix(".err"), stem.with_suffix(".rc")
    if not (o.exists() and e.exists()):
        continue
    code = int(c.read_text().strip()) if c.exists() else None
    cross[label] = {"rc": code, "row_passes": row_passes(code, o.read_text(errors="replace"),
                                                         e.read_text(errors="replace"))}
# synthetic foreign SIGABRT: a different -6 crash with no nullts streams at all
cross["synthetic-foreign-sigabrt"] = {
    "rc": -6,
    "row_passes": row_passes(-6, "GDScript backtrace: some other abort\n",
                             "handle_crash: Program crashed with signal 11\n"
                             "double free or corruption (!prev)\n")}

out = {"classify_process_segment_sha256": seg_sha, "expected_exit": expected_exit,
       "signature": signature, "required_stderr": list(rs), "receipts": len(receipts),
       "variants": variants, "cross_receipt": cross}
print(json.dumps(out, indent=1))
(Path(__file__).parent / "forge_nullts.json").write_text(json.dumps(out, indent=1))
