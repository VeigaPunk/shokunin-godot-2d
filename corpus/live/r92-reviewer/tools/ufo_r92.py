"""r92-reviewer shared helpers: production classify_process extracted VERBATIM
(AST) from the PINNED committed harness, plus CASES/EXPECTED_ERRORS/REQUIRED_STDERR
read from the same pinned bytes. No hand-reimplementation."""
import ast, hashlib, json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
PIN = HERE.parent / "pinned" / "run_battery.py"

def load():
    src = PIN.read_text()
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
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": list(t[2]),
                               "expected_exit": t[3], "signature": t[4]}
    exp_err, req_err = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "r92_tilemap_atlas" in keys:
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_"):
                        exp_err[k.value] = ast.literal_eval(v)
            if "r92_tilemap_nullts_crash" in keys and "nav_lattice_teardown_crash" in keys:
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value == "r92_tilemap_nullts_crash":
                        req_err[k.value] = ast.literal_eval(v)
    return {"src_sha": hashlib.sha256(src.encode()).hexdigest(),
            "classify": ns["classify_process"], "seg_sha": seg_sha,
            "cases": cases, "exp_err": exp_err, "req_err": req_err,
            "tree": tree, "src": src}

def classify_row(C, case, out, err, rc, override_ee=None, override_sig=None,
                 drop_fragment=False, sig_to_stderr=False, extra_error=None):
    """Replicates execute()'s classification path for a row (stream-anchored)."""
    row = C["cases"][case]
    sigs = override_sig if override_sig is not None else row["signature"]
    if not isinstance(sigs, (tuple, list)):
        sigs = (sigs,)
    ee = override_ee if override_ee is not None else C["exp_err"].get(case, ())
    merged = out + err
    if extra_error:
        merged = merged + extra_error
    passed = any(C["classify"](rc, None, merged, row["expected_exit"], s, ee) for s in sigs)
    rs = C["req_err"].get(case, ())
    if rs and not drop_fragment:
        passed = (passed and all(f in err for f in rs)
                  and any(s in out for s in sigs))
    elif rs and drop_fragment:
        passed = (passed and any(s in out for s in sigs))
    if sig_to_stderr:
        # signature moved to stderr only: merged still has it, but the
        # stdout anchor must fail
        passed = passed and any(s in out for s in sigs)
    return bool(passed)
