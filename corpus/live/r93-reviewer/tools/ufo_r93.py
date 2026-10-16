#!/usr/bin/env python3
"""r93-reviewer shared helpers.

Loads the PINNED committed harness (corpus/live/r93-reviewer/pinned/run_battery.py
= git show 4b75151:corpus/fixtures/run_battery.py) and extracts, without
re-implementation:
  - classify_process() source VERBATIM via AST (segment sha256 recorded),
  - CASES as a dict name -> (script, flags, expected_exit, signature),
  - expected_errors / required_stderr entries (r93_ keys only, and full dicts),
  - the CASES order list (for insertion diffs).
"""
import ast
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PIN = HERE.parent / "pinned" / "run_battery.py"


def _fn_src(tree, src, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    return None


def load(pin: pathlib.Path = PIN):
    src = pin.read_text()
    tree = ast.parse(src)
    fn_src = _fn_src(tree, src, "classify_process")
    assert fn_src, "classify_process not found"
    seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()
    ns = {}
    exec("import re\n" + fn_src, ns)
    cases = {}
    order = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": list(t[2]),
                               "expected_exit": t[3], "signature": t[4]}
                order.append(t[0])
    def _lit(v):
        try:
            return ast.literal_eval(v)
        except Exception:
            return None

    exp_err, req_err = {}, {}
    exp_err_all, req_err_all = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            vals = [_lit(v) for v in node.values]
            if any(k.startswith("r93_") for k in keys):
                for k, v in zip(keys, vals):
                    if k.startswith("r93_") and k in cases:
                        exp_err[k] = v
                    if k in cases:
                        exp_err_all.setdefault(k, v)
    # required_stderr lives in its own dict literal; locate it by its known
    # neighbours (the spontaneous-crash row + the descendant control) and take
    # any r93 keys.
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "crash_spontaneous_sigabrt" in keys and "descendant_pipe_detached_control" in keys:
                for k, v in zip(keys, [_lit(x) for x in node.values]):
                    req_err_all[k] = v
                    if k.startswith("r93_"):
                        req_err[k] = v
    return {"src_sha": hashlib.sha256(src.encode()).hexdigest(),
            "classify": ns["classify_process"], "seg_sha": seg_sha,
            "cases": cases, "order": order,
            "exp_err": exp_err, "req_err": req_err,
            "exp_err_all": exp_err_all, "req_err_all": req_err_all,
            "src": src, "tree": tree}


def sigs_of(row):
    s = row["signature"]
    return tuple(s) if isinstance(s, (tuple, list)) else (s,)


def classify_row(C, case, out, err, rc, *, override_ee=None, override_sig=None,
                 drop_fragment=False, sig_to_stderr=False, extra_error=None,
                 override_exit=None):
    """Mirror the battery's execute() classification for one row.

    Stream-anchored exactly like the production path: signature must appear in
    stdout (the battery merges stdout+stderr for the clause scan but the r93
    rows' signatures are stdout-anchored by construction), required_stderr
    fragments must appear in stderr.
    """
    row = C["cases"][case]
    sig_list = override_sig if override_sig is not None else sigs_of(row)
    if not isinstance(sig_list, (tuple, list)):
        sig_list = (sig_list,)
    ee = override_ee if override_ee is not None else C["exp_err"].get(case, ())
    expected_exit = row["expected_exit"] if override_exit is None else override_exit
    merged = out + err
    if extra_error:
        merged = merged + extra_error
    passed = any(C["classify"](rc, None, merged, expected_exit, s, ee) for s in sig_list)
    rs = C["req_err"].get(case, ())
    if rs and not drop_fragment:
        passed = passed and all(f in err for f in rs)
    # signature must be on stdout in every case (r93 rows are stdout-anchored)
    passed = passed and any(s in out for s in sig_list)
    if sig_to_stderr:
        passed = passed and False
    return bool(passed)


def load_rows(pin: pathlib.Path = PIN):
    C = load(pin)
    return C, {k: v for k, v in C["cases"].items() if k.startswith("r93_")}


if __name__ == "__main__":
    C, rows = load_rows()
    print(json.dumps({"src_sha": C["src_sha"], "seg_sha": C["seg_sha"],
                      "cases": len(C["cases"]), "r93_rows": len(rows),
                      "r93_expected_errors": C["exp_err"],
                      "r93_required_stderr": C["req_err"]}, indent=1))
