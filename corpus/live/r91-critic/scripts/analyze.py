#!/usr/bin/env python3
"""r91-critic analyzer: production-classifier replay of the r91 nav rows.

Extracts `classify_process` from the frozen committed battery blob (AST,
byte-segment sha recorded) and classifies fresh receipts captured in the
battery's exact launch shape. Also:
  - byte-prefix check: the row signature must be a leading prefix of the
    printed PASS line (the committed pin is the leading block);
  - tail-token check: no declared scheduler/race field token may appear
    inside the pin prefix;
  - rep-to-rep diff summary (which tokens move).
"""
import ast
import hashlib
import json
import pathlib
import re
import sys

SEAT = pathlib.Path(__file__).resolve().parent.parent
REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FROZEN = SEAT / "run_battery.committed-77d2f7e.py"
RUNS = SEAT / "runs"

TAIL_FIELDS = [
    "settle=", "iter=", "ladder=", "first_reach=", "first_reach_sync=",
    "walk_steps=", "reached_at=", "first_reachable=", "iter_b=",
    "link_iter=", "gate=", "chg_iter_same=", "chg_iter_settled=",
    "dis_same=", "fwd_disabled_same=", "settle_a=", "settle_b=",
]

ALLOW = {
    "nav_lattice_sync": (
        "ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.",),
    "nav_lattice_bake": ("ERROR: The root node needs to be inside the SceneTree.",),
}
REQUIRED_STDERR = {
    "nav_lattice_teardown_crash": ("double free or corruption",),
}


def load_cases():
    src = FROZEN.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CASES not found")


def extract_classifier():
    src = FROZEN.read_text()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(src, node)
            ns = {}
            exec("def classify_process" + seg.split("def classify_process", 1)[1], ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("classify_process not found")


def rc_to_code(rc):
    return -(rc - 128) if rc > 128 else rc


def classify_case(cls, case, out, err, rc, use_allow=True):
    name, script, flags, exit_, sig = case
    code = rc_to_code(rc)
    merged = out + err
    entries = ALLOW.get(name, ()) if use_allow else ()
    ok = cls(code, None, merged, exit_, sig, entries)
    if name in REQUIRED_STDERR:
        sigs = sig if isinstance(sig, (tuple, list)) else (sig,)
        ok = (ok and all(f in err for f in REQUIRED_STDERR[name])
              and any(s in out for s in sigs))
    return ok, code


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "fresh"
    cases = load_cases()
    cls, sha = extract_classifier()
    nav = [c for c in cases if c[0].startswith("nav_lattice_")]
    report = {"tag": tag, "classifier_sha256": sha, "rows": {}, "findings": []}
    for case in nav:
        name, script, flags, exit_, sig = case
        arm = flags[0].split("=")[1]
        reps = sorted(RUNS.glob(f"{tag}.{arm}.rep*.out"))
        if not reps:
            report["rows"][name] = {"arm": arm, "reps": [], "verdicts": [],
                                    "skipped": True}
            continue
        row = {"arm": arm, "expected_exit": exit_, "reps": [], "verdicts": [],
               "out_uniq": 0, "err_uniq": 0, "prefix_ok": True,
               "tail_in_pin": [], "line_uniq": 0, "rep_lines": []}
        outs, errs = set(), set()
        lines = []
        for o in reps:
            k = o.name.rsplit(".rep", 1)[1].split(".")[0]
            base = RUNS / f"{tag}.{arm}.rep{k}"
            out = o.read_text()
            err = (RUNS / f"{base}.err").read_text()
            rc = int((RUNS / f"{base}.rc").read_text().strip())
            ok, code = classify_case(cls, case, out, err, rc)
            bare_ok, _ = classify_case(cls, case, out, err, rc, use_allow=False)
            pass_line = next((ln for ln in out.splitlines()
                              if ln.startswith("PASS nav_lattice ")), "")
            lines.append(pass_line)
            prefix = pass_line.startswith(sig)
            if not prefix and pass_line:
                row["prefix_ok"] = False
                pin_toks = sig.split()
                got_toks = pass_line.split()
                for i, (a, b) in enumerate(zip(pin_toks, got_toks)):
                    if a != b:
                        row["first_mismatch"] = {"tok": i, "pin": a, "got": b}
                        break
                else:
                    row["first_mismatch"] = {"tok": len(pin_toks),
                                             "pin": f"<{len(pin_toks)} toks>",
                                             "got": f"<{len(got_toks)} toks>"}
            pin_toks = sig.split()
            got_toks = pass_line.split()
            for t in got_toks[:len(pin_toks)]:
                for f in TAIL_FIELDS:
                    if t.startswith(f):
                        row["tail_in_pin"].append(t)
            row.setdefault("tail_tokens", sorted({
                t.split("=", 1)[0] for t in got_toks[len(pin_toks):] if "=" in t}))
            outs.add(out)
            errs.add(err)
            lines.append(pass_line)
            row["rep_lines"].append(pass_line)
            row["reps"].append({"rep": k, "rc": rc, "code": code,
                                "verdict": "PASS" if ok else "FAIL",
                                "bare": "PASS" if bare_ok else "FAIL",
                                "err_bytes": len(err),
                                "stdout_lines": len(out.splitlines())})
            row["verdicts"].append(ok)
        row["out_uniq"] = len(outs)
        row["err_uniq"] = len(errs)
        row["line_uniq"] = len(set(lines))
        # diff confinement: any token that differs between reps must sit at a
        # tail index (>= len(pin)) — i.e. rep-to-rep variance never touches
        # the pinned block.
        base_toks = row["rep_lines"][0].split() if row["rep_lines"] else []
        pin_len = len(sig.split())
        row["rep_diff_indices"] = sorted({
            i for ln in row["rep_lines"][1:]
            for i, (a, b) in enumerate(zip(base_toks, ln.split())) if a != b})
        row["diff_confined_to_tail"] = all(i >= pin_len for i in row["rep_diff_indices"])
        row["all_pass"] = all(row["verdicts"]) and bool(reps)
        report["rows"][name] = row
        if not row["all_pass"]:
            report["findings"].append(f"{name}: not all reps PASS")
        if not row["prefix_ok"]:
            report["findings"].append(f"{name}: signature is not a line prefix")
        if row["tail_in_pin"]:
            report["findings"].append(f"{name}: tail tokens inside pin")
        if not row["diff_confined_to_tail"]:
            report["findings"].append(f"{name}: rep variance not confined to tail")
    (SEAT / f"analyze.{tag}.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, row in report["rows"].items():
        if row.get("skipped"):
            continue
        print(f"{name:28s} arm={row['arm']:14s} reps={len(row['reps'])} "
              f"all_pass={row['all_pass']} out_uniq={row['out_uniq']} "
              f"err_uniq={row['err_uniq']} line_uniq={row['line_uniq']} "
              f"prefix_ok={row['prefix_ok']} tail_in_pin={row['tail_in_pin']}")
    print("findings:", report["findings"])
    return 0 if not report["findings"] else 1


if __name__ == "__main__":
    sys.exit(main())
