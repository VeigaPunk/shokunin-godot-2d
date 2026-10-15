#!/usr/bin/env python3
"""r93-scout author-row builder.

Extracts the pinned signatures from the canonical receipts and classifies every
candidate row with the PRODUCTION `classify_process` (AST-extracted from
corpus/fixtures/run_battery.py) against every canonical + loadtest receipt.
Writes author-rows.py.txt.
"""
import ast
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"

src = FIXTURE.read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src, "classify_process not found"
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()

ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

SCRIPT = "anim_lattice.gd"
ARM_TO_CELL = {
    "census": "census", "tweenval": "tweenval", "tweenval_grid": "tweenval_grid",
    "tweenstep": "tweenstep", "tweenchain": "tweenchain", "tweenproc": "tweenproc",
    "animseek": "animseek", "animmethod": "animmethod", "animtrack": "animtrack",
    "animblend": "animblend", "animproc": "animproc",
}


def pass_line(cell: str) -> str:
    out = (HERE / "runs" / f"r93_{cell}.rep1.out").read_text()
    for ln in out.splitlines():
        if ln.startswith(f"PASS anim_lattice {cell}"):
            return ln
    raise SystemExit(f"no PASS line for {cell}")


def sub(line: str, start: str, end: str = None) -> str:
    i = line.index(start)
    j = len(line) if end is None else line.index(end) + len(end)
    return line[i:j]


def grid_slice(tokens: list, first: int, last: int) -> str:
    """tokens are space-separated groups: name + 4 ease cells = 5 tokens per group."""
    return " ".join(tokens[first * 5: last * 5])


census = pass_line("census")
tweenval = pass_line("tweenval")
grid = pass_line("tweenval_grid")
animtrack = pass_line("animtrack")
tweenstep = pass_line("tweenstep")
tweenchain = pass_line("tweenchain")
tweenproc = pass_line("tweenproc")
animseek = pass_line("animseek")
animmethod = pass_line("animmethod")
animblend = pass_line("animblend")
animproc = pass_line("animproc")

grid_payload = grid.split(" ")[3:]  # drop "PASS anim_lattice tweenval_grid"

ROWS = [
    ("r93_tween_census", SCRIPT, ["--arm=census"], 0, census),
    ("r93_tween_interp_value", SCRIPT, ["--arm=tweenval"], 0, tweenval),
    ("r93_tween_interp_grid_a", SCRIPT, ["--arm=tweenval_grid"], 0, grid_slice(grid_payload, 0, 5)),
    ("r93_tween_interp_grid_b", SCRIPT, ["--arm=tweenval_grid"], 0, grid_slice(grid_payload, 5, 12)),
    ("r93_anim_track_interp", SCRIPT, ["--arm=animtrack"], 0, animtrack),
    ("r93_tween_manual_step", SCRIPT, ["--arm=tweenstep"], 0, tweenstep),
    ("r93_tween_chain", SCRIPT, ["--arm=tweenchain"], 0, tweenchain),
    ("r93_tween_process_stable", SCRIPT, ["--arm=tweenproc"], 0,
     sub(tweenproc, "stable=[auto_advanced")),
    ("r93_tween_phys_manual_step", SCRIPT, ["--arm=tweenproc"], 0,
     sub(tweenproc, "phys_manual=[", "after_step025=2.0]")),
    ("r93_anim_seek", SCRIPT, ["--arm=animseek"], 0, animseek),
    ("r93_anim_method_callback", SCRIPT, ["--arm=animmethod"], 0, animmethod),
    ("r93_anim_blend_finished", SCRIPT, ["--arm=animblend"], 0,
     sub(animblend, "finished_010=[", "finished_020=[100.0,200.0,300.0,400.0,500.0]")),
    ("r93_anim_blend_running", SCRIPT, ["--arm=animblend"], 0,
     sub(animblend, "running_from_50=[")),
    ("r93_anim_process_manual", SCRIPT, ["--arm=animproc"], 0,
     sub(animproc, "manual=[x=25.0", "inactive=[50.0,true]")),
    ("r93_anim_process_stable", SCRIPT, ["--arm=animproc"], 0,
     sub(animproc, "stable=[manual_frame_frozen")),
]

# informational: the full mode-cell lines (load-fragile counters included)
ROWS_FULL = [
    ("r93_tween_process_full", SCRIPT, ["--arm=tweenproc"], 0, tweenproc),
    ("r93_anim_process_full", SCRIPT, ["--arm=animproc"], 0, animproc),
]

EXPECTED_ERRORS = {}


def receipts():
    for out in sorted((HERE / "runs").glob("r93_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())
    for out in sorted((HERE / "runs" / "loadtest").glob("r93_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield "loadtest/" + out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())


def check(rows, label):
    rejected = []
    checked = 0
    for case, script, flags, expected_exit, sig in rows:
        arm = next(f.split("=", 1)[1] for f in flags if f.startswith("--arm="))
        cell = ARM_TO_CELL[arm]
        allowed = EXPECTED_ERRORS.get(case, ())
        for name, output, code in receipts():
            base = name.split("/")[-1]
            if not base.startswith(f"r93_{cell}."):
                continue
            ok = classify_process(code, None, output, expected_exit, sig, allowed)
            checked += 1
            if not ok:
                rejected.append((case, name))
    print(f"[{label}] rows={len(rows)} receipts_checked={checked} rejected={rejected}")
    return rejected


rejected = check(ROWS, "ROWS(recommended, GATING)")
rejected_full = check(ROWS_FULL, "ROWS_FULL(full-line, informational)")

lines = [
    "# r93-scout author rows — AnimationPlayer + Tween authorability lattice.",
    "# Generated by make_author_rows.py from canonical receipts; classified with the",
    f"# production classify_process (segment sha256 {seg_sha[:16]}).",
    f"# GATING set: rejected={rejected} over canonical+loadtest receipts.",
    f"# Informational full-line set: rejected={rejected_full} (load-fragile counters).",
    "",
    "ROWS = [",
]
for case, script, flags, expected_exit, sig in ROWS:
    lines.append(f"    ({case!r}, {script!r}, {flags!r}, {expected_exit!r},")
    lines.append(f"     {sig!r}),")
lines.append("]")
lines.append("")
lines.append("ROWS_FULL = [")
for case, script, flags, expected_exit, sig in ROWS_FULL:
    lines.append(f"    ({case!r}, {script!r}, {flags!r}, {expected_exit!r},")
    lines.append(f"     {sig!r}),")
lines.append("]")
lines.append("")
lines.append(f"EXPECTED_ERRORS = {EXPECTED_ERRORS!r}")
lines.append("")
(HERE / "author-rows.py.txt").write_text("\n".join(lines))
print(f"wrote author-rows.py.txt ({len(ROWS)} gating rows, {len(ROWS_FULL)} informational rows)")
print(f"classify_process segment sha256={seg_sha}")
sys.exit(1 if rejected else 0)
