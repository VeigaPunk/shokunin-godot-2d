#!/usr/bin/env python3
"""r102 CRIT-3 static coverage analyzer.

For each patch hunk: map changed BASE line numbers to the enclosing `func` in the
committed fixture, then check whether that func (or, for helpers, the arms that call
it) is exercised by any registered CASES row. Outputs the touched-func table and
flags touched funcs with no registered arm.

Reads only. Prints JSON to stdout.
"""
import ast, re, json
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BASE = Path("/var/tmp/r102-crit3/base")
MUT = REPO / "reports/round-101/mutations"

PATCHES = {
    "r101-simp1-r91-nav_lattice.patch": "nav_lattice.gd",
    "r101-simp1-r98-canvas_lattice.patch": "canvas_lattice.gd",
    "r101-simp1-r98-r98b_attack.patch": "r98b_attack.gd",
    "r101-simp1-r98-r98b_rksenum.patch": "r98b_rksenum.gd",
    "r101-simp1-r99-audio_lattice.patch": "audio_lattice.gd",
    "r101-simp2-stree_lattice.gd.diff": "stree_lattice.gd",
    "r101-simp2-scene_io_lattice.gd.diff": "scene_io_lattice.gd",
    "r101-simp3-particles-fold.patch": "particles_lattice.gd",
    "r101-simp3-r95-fold.patch": None,  # two files: dss_lattice.gd + r95b_order.gd
    "r101-simp1-r91-nav_lattice.patch": "nav_lattice.gd",
}


def get_assign(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return node.value
    raise SystemExit("no CASES")


src = (REPO / "corpus/fixtures/run_battery.py").read_text()
tree = ast.parse(src)
CASES = ast.literal_eval(get_assign(tree, "CASES"))


def func_of_lines(gd_path):
    """line -> enclosing func name map + func name -> (start, end)."""
    lines = gd_path.read_text().splitlines()
    funcs = []
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^func ([A-Za-z0-9_]+)\(", ln)
        if m:
            funcs.append([m.group(1), i])
    out = {}
    for idx, (name, start) in enumerate(funcs):
        end = funcs[idx + 1][1] - 1 if idx + 1 < len(funcs) else len(lines)
        for ln in range(start, end + 1):
            out[ln] = name
    return out


def hunk_changes(patch_path):
    """(file, base_line_number_of_each_changed_deleted_or_replaced_line)."""
    changes = []
    cur = None
    base = None
    for ln in patch_path.read_text().splitlines():
        m = re.match(r"^\+\+\+ b/(.+)$", ln)
        if m:
            cur = m.group(1)
        m = re.match(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@", ln)
        if m:
            base = int(m.group(1))
            continue
        if cur and base is not None:
            if ln.startswith("-") and not ln.startswith("---"):
                changes.append((cur, base))
                base += 1
            elif ln.startswith(" ") or ln.startswith("+"):
                if ln.startswith(" "):
                    base += 1
    return changes


def dispatch_map(gd_path):
    """arm string -> arm func, from the `match arm:` block (any enclosing func)."""
    lines = gd_path.read_text().splitlines()
    out = {}
    for i, ln in enumerate(lines):
        if ln.strip() == "match arm:":
            for ln2 in lines[i + 1:]:
                mm = re.match(r'\s+"([^"]+)":.*?(_arm_[A-Za-z0-9_]+)\(\)', ln2)
                if not mm:
                    break
                out[mm.group(1)] = mm.group(2)
            break
    return out


def rows_for(script):
    return [c for c in CASES if c[1] == script]


def registered_arms(script):
    arms = []
    for c in rows_for(script):
        for f in c[2]:
            if f.startswith("--arm="):
                arms.append(f[6:])
    return arms


report = {}
for pname, fname in PATCHES.items():
    patch = MUT / pname
    if patch.suffix == ".diff":
        patch = MUT / pname
    changes = hunk_changes(patch)
    by_file = {}
    for f, bl in changes:
        by_file.setdefault(f, []).append(bl)
    for f, lines in by_file.items():
        gd = BASE / Path(f).name
        if fname and Path(f).name != fname:
            continue
        line_map = func_of_lines(gd)
        touched = sorted({line_map.get(bl, "?") for bl in lines})
        disp = dispatch_map(gd)
        reg = registered_arms(Path(gd).name)
        # helper funcs: which arms call them
        txt = gd.read_text()
        entry = {"touched_funcs": {}, "arms_registered": sorted(set(reg)),
                 "arms_implemented": sorted(disp.keys()),
                 "rows": len(rows_for(Path(gd).name))}
        for fn in touched:
            callers = []
            if fn not in ("?",) and fn not in disp.values():
                for arm, af in disp.items():
                    body = re.search(rf"func {re.escape(af)}\(\) -> void:\n(.*?)(?=\nfunc |\Z)",
                                     txt, re.S)
                    if body and re.search(rf"\b{re.escape(fn)}\(", body.group(1)):
                        callers.append(arm)
            entry["touched_funcs"][fn] = {
                "is_arm": fn in disp.values(),
                "arm_names": [a for a, af in disp.items() if af == fn],
                "caller_arms": sorted(callers),
            }
        report[Path(f).name] = entry

print(json.dumps(report, indent=1))
