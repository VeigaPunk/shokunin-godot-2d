#!/usr/bin/env python3
"""r101 SIMP-1 scratch harness: stage trees, apply candidate folds, run targeted rows.

Never touches the lane repo except by reading; every write lands under /var/tmp/r101-simp1
(/tmp is usrquota-exhausted for this user — the same condition r98/r99/r100 sims recorded).
"""
from __future__ import annotations

import ast
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus" / "fixtures"
WORK = Path("/var/tmp/r101-simp1")
GODOT = "/usr/bin/godot"


def fold_canvas():
    return {
        "canvas_lattice.gd": [
            (
                "func _notif_keys(d: Dictionary) -> String:\n"
                "\tvar keys: Array = []\n"
                "\tfor k in d.keys():\n"
                "\t\tif int(d[k]) != 0:\n"
                "\t\t\tkeys.append(int(k))\n"
                "\tkeys.sort()\n"
                '\treturn "[%s]" % ",".join(keys)\n'
                "\n",
                "",
            ),
            ("\tvar methods: Array = []\n", ""),
            ("\t\tmethods.append(nm)\n", ""),
        ]
    }


def fold_attack():
    return {
        "r98b_attack.gd": [
            ("\tvar owner_ref\n", ""),
            ("\tt.owner_ref = self\n", ""),
            ("\tvar pfs: Array = []\n", ""),
            ("\t\tpfs.append(Engine.get_process_frames())\n", ""),
        ]
    }


def fold_rksenum():
    return {
        "r98b_rksenum.gd": [
            ("var _items: PackedStringArray = []\n\n", ""),
            ('\t_items.append("%s=%s" % [key, value])\n', ""),
        ]
    }


def fold_audio():
    return {
        "audio_lattice.gd": [
            ("\tvar prev_t := Time.get_ticks_usec()\n", ""),
            ("\t\tprev_t = now\n", ""),
        ]
    }


def fold_nav():
    dst = "".join([
        "\tNavigationServer2D.agent_set_map(a, map)\n",
        "\tNavigationServer2D.agent_set_avoidance_enabled(a, true)\n",
        "\tNavigationServer2D.agent_set_avoidance_callback(a, func(_v: Vector2) -> void:\n",
        "\t\tpass)\n",
    ])
    crash_src = "".join([
        "\tvar hits: Array[Vector2] = []\n",
        "\tNavigationServer2D.agent_set_map(a, map)\n",
        "\tNavigationServer2D.agent_set_avoidance_enabled(a, true)\n",
        "\tNavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:\n",
        "\t\thits.append(v))\n",
        '\tawait _await_frames(3)\n\tprint("NAV_LATTICE_TEARDOWN_CRASH',
    ])
    clean_src = "".join([
        "\tvar hits: Array[Vector2] = []\n",
        "\tNavigationServer2D.agent_set_map(a, map)\n",
        "\tNavigationServer2D.agent_set_avoidance_enabled(a, true)\n",
        "\tNavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:\n",
        "\t\thits.append(v))\n",
        "\tawait _await_frames(3)\n\tNavigationServer2D.agent_set_avoidance_callback(a, Callable())",
    ])
    return {
        "nav_lattice.gd": [
            ("const SETTLE := 10\n", ""),
            (crash_src, dst + '\tawait _await_frames(3)\n\tprint("NAV_LATTICE_TEARDOWN_CRASH'),
            (clean_src, dst + "\tawait _await_frames(3)\n\tNavigationServer2D.agent_set_avoidance_callback(a, Callable())"),
        ]
    }


TREES = {
    "base": {},
    "f_nav": fold_nav(),
    "f_canvas": fold_canvas(),
    "f_attack": fold_attack(),
    "f_rksenum": fold_rksenum(),
    "f_audio": fold_audio(),
    "f_r98all": {**fold_canvas(), **fold_attack(), **fold_rksenum()},
    "f_all": {**fold_canvas(), **fold_attack(), **fold_rksenum(), **fold_nav(), **fold_audio()},
}

FIXTURE_TREES = {
    "nav_lattice.gd": ["base", "f_nav", "f_all"],
    "canvas_lattice.gd": ["base", "f_canvas", "f_r98all", "f_all"],
    "r98b_attack.gd": ["base", "f_attack", "f_r98all", "f_all"],
    "r98b_rksenum.gd": ["base", "f_rksenum", "f_r98all", "f_all"],
    "audio_lattice.gd": ["base", "f_audio", "f_all"],
}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stage(name: str, edits: dict) -> Path:
    dest = WORK / "trees" / name
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in sorted(FIX.iterdir()):
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    pf = dest / "project.godot"
    t = pf.read_text()
    t = t.replace('config/name="MechanicOneShotTest"',
                  'config/name="MechanicOneShotTest-r101simp1-%s"' % name, 1)
    pf.write_text(t)
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in text
    chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    for fname, pairs in edits.items():
        p = dest / fname
        txt = p.read_text()
        for old, new in pairs:
            n = txt.count(old)
            assert n == 1, "edit for %s fired %d times: %r" % (fname, n, old[:60])
            txt = txt.replace(old, new, 1)
        p.write_text(txt)
    return dest


def extract():
    src = (FIX / "run_battery.py").read_text()
    tree = ast.parse(src)
    cases = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "CASES" for t in node.targets):
            cases = ast.literal_eval(node.value)
    assert cases is not None and len(cases) > 400, len(cases or [])
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            fn = node
    cp_src = ast.get_source_segment(src, fn)
    ns = {}
    exec(cp_src, ns)
    return cases, ns["classify_process"]


def extract_dict(name):
    src = (FIX / "run_battery.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                and any(getattr(t, "id", None) == name for t in node.targets)):
            out = {}
            for k, v in zip(node.value.keys, node.value.values):
                key = ast.literal_eval(k)
                try:
                    out[key] = ast.literal_eval(v)
                except Exception:
                    out[key] = None
            return out
    return {}


def run_row(scratch: Path, script: str, flags, timeout=8):
    cmd = [GODOT, "--headless", "--path", str(scratch), "--script", "res://" + script, "--", *flags]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.stdout, p.stderr, p.returncode, None
    except subprocess.TimeoutExpired:
        return None, None, None, "TIMEOUT after %s seconds" % timeout


def classify(classify_process, row, stdout, stderr, rc, err, expected_errors, required_stderr):
    name, expected_exit, evidence = row[0], row[3], row[4]
    if stdout is None:
        return False
    output = stdout + stderr
    sigs = evidence if isinstance(evidence, (tuple, list)) else (evidence,)
    allowed = expected_errors.get(name, ())
    if allowed is None:
        allowed = ()
    passed = any(classify_process(rc, err, output, expected_exit, s, allowed) for s in sigs)
    rs = required_stderr.get(name) or ()
    if rs:
        passed = passed and all(f in stderr for f in rs) and any(s in stdout for s in sigs)
    if "SCRIPT ERROR:" in output or "Parse Error:" in output:
        passed = False
    return passed


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    cases, classify_process = extract()
    expected_errors = extract_dict("expected_errors")
    required_stderr = extract_dict("required_stderr")
    rows = [c for c in cases if c[1] in FIXTURE_TREES]
    print("rows selected:", len(rows), flush=True)
    for name in FIXTURE_TREES:
        print("  ", name, sum(1 for r in rows if r[1] == name), flush=True)
    (WORK / "rows.json").write_text(json.dumps(
        [{"name": r[0], "script": r[1], "flags": r[2], "expected_exit": r[3],
          "signature": r[4] if isinstance(r[4], str) else list(r[4])} for r in rows], indent=1))
    for tname, edits in TREES.items():
        d = stage(tname, edits)
        print("staged", tname, d, flush=True)
    print("fixture shas per tree:")
    for f in FIXTURE_TREES:
        print("  ", f, " ".join("%s=%s" % (t, sha256(WORK / "trees" / t / f)[:12]) for t in FIXTURE_TREES[f]), flush=True)


if __name__ == "__main__":
    main()
