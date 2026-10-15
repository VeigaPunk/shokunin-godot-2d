#!/usr/bin/env python3
"""r91-critic: two-directional check of the nav_lattice_teardown_crash
required_stderr + stdout-anchor clauses, on the real captured crash receipt
(byte-level synthetic variants of the captured streams; no new process).

Mirrors run_battery.py's execute() required_stderr block:
    passed = classify_process(...) and all(fragment in proc_stderr ...)
             and any(sig in proc_stdout ...)
"""
import ast
import hashlib
import json
import pathlib
import sys

SEAT = pathlib.Path(__file__).resolve().parent.parent
FROZEN = SEAT / "run_battery.committed-77d2f7e.py"
RUNS = SEAT / "runs"
FRAG = ("double free or corruption",)
SIG = "NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=true"


def extract(fname):
    src = FROZEN.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == fname:
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def " + fname + seg.split("def " + fname, 1)[1], ns)
            return ns[fname], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit(fname + " not found")


def main():
    cls, sha = extract("classify_process")
    out = (RUNS / "fresh.teardown_crash.rep1.out").read_text()
    err = (RUNS / "fresh.teardown_crash.rep1.err").read_text()
    rc = int((RUNS / "fresh.teardown_crash.rep1.rc").read_text().strip())
    code = -(rc - 128) if rc > 128 else rc

    def verdict(stdout, stderr, expected_exit=code, sig=SIG, frag=FRAG,
                use_frag=True, anchor=True):
        v = cls(code, None, stdout + stderr, expected_exit, sig, ())
        if use_frag:
            v = v and all(f in stderr for f in frag)
        if anchor:
            v = v and sig in stdout
        return v

    cases = {
        "committed_capture": (out, err, True, True, True),
        "no_required_stderr_clause": (out, err, True, False, True),
        "fragment_moved_to_stdout": (out + "\n" + "\n".join(FRAG), err.replace("double free or corruption", "X"), True, True, True),
        "marker_moved_to_stderr": (out.replace(SIG, "X"), err, True, True, True),
        "wrong_exit_only": (out, err, True, True, True),
    }
    report = {"classifier_sha256": sha, "captured_rc": rc, "code": code,
              "fragment": list(FRAG), "signature": SIG, "results": {}}
    for name, (o, e, use_frag, anchor, _x) in cases.items():
        expected_exit = code
        if name == "wrong_exit_only":
            expected_exit = 0
        v = verdict(o, e, expected_exit=expected_exit, use_frag=use_frag, anchor=anchor)
        report["results"][name] = {"verdict": "PASS" if v else "FAIL",
                                   "stdout_has_sig": SIG in o,
                                   "stderr_has_frag": all(f in e for f in FRAG)}
    (SEAT / "required_stderr_check.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, r in report["results"].items():
        print(f"{name:28s} {r['verdict']:4s} stdout_sig={r['stdout_has_sig']} "
              f"stderr_frag={r['stderr_has_frag']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
