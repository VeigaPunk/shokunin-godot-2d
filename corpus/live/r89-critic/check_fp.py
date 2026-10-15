#!/usr/bin/env python3
"""Feed the false-positive probes through the production classify_process."""
import ast, hashlib, pathlib

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BATTERY = REPO / "corpus/fixtures/run_battery.py"
RUNS = pathlib.Path(__file__).parent / "runs"

def extract_classifier():
    src = BATTERY.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def classify_process" + seg.split("def classify_process", 1)[1], ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()

cls, sha = extract_classifier()
print(f"classifier sha={sha[:12]} (author claims 749fa060…)")
# committed row: ('geo2d_lattice_lineempty', 'geo2d_lattice.gd', ['--arm=lineempty'], -6,
#   'R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)')
SIG = 'R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)'

for probe in ("fp_wrongcause", "fp_stderr_sig"):
    out = (RUNS / f"{probe}.out").read_text()
    err = (RUNS / f"{probe}.err").read_text()
    rc = int((RUNS / f"{probe}.rc").read_text().strip())
    code = -(rc - 128) if rc > 128 else rc   # shell 134 -> python -6
    merged = out + err                        # exactly what run_process returns
    verdict = cls(code, None, merged, -6, SIG, ())
    print(f"{probe}: shell_rc={rc} python_rc={code} sig_on={'stderr' if SIG in err and SIG not in out else 'stdout' if SIG in out else 'none'} -> classify_process = {'PASS' if verdict else 'FAIL'}")

# also: real lineempty receipt for contrast
out = (RUNS / "geo2d_lattice.gd.lineempty.load.rep1.out").read_text()
err = (RUNS / "geo2d_lattice.gd.lineempty.load.rep1.err").read_text()
# battery doesn't wrap in `timeout`; strip the timeout binary's line for parity
err_battery = "\n".join(l for l in err.splitlines() if not l.startswith("timeout:")) + "\n"
code = -6
print("real lineempty (timeout-line stripped):", cls(code, None, out + err_battery, -6, SIG, ()))
