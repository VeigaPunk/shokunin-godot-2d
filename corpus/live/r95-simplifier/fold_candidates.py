#!/usr/bin/env python3
"""r95-simplifier YAGNI fold candidates: the 18 dead stores in the two landed
fixtures (value never observed; the side-effecting call is retained).

Sites (committed line numbers, from deadstore_scan.py):
  dss_lattice.gd
    357/359  _arm_point_cap   append-only `pile` sink  -> bare _mk_body call
    370      _arm_point_edge  `var box := _mk_body(...)` (unread binding)
    499/500  _arm_order_core  `made2` out-param        -> `[]`
    506/507  _arm_order_core  `made3` out-param        -> `[]`
    514      _arm_order_core  `var fresh := _mk_body(...)`
    571      _arm_layer_forms `var cast := _sh(...)`
    585      _arm_cast_rest   `var ar := _mk_body(...)`
    629      _arm_cast_rest   `var b2 := _mk_body(...)`
  r95b_order.gd
    415      _arm_free        `var dss := _dss()` (pure getter, whole line)
    455      _arm_readd       `var dss := _dss()` (pure getter, whole line)
    530      _arm_layers      `var made := _pile(...)`
    567      _arm_celloff     `var made := _pile(...)`
    609      _arm_procwait    `var made := _pile(...)`
    745/750  _arm_twopiles    `var a/b := _pile(...)`

Builds the folded fixture bytes (asserting every original line), the exact
unified diff (including the two harness sha256 comment updates), two scratch
projects (committed vs folded), then launches all 52 r95 rows x N reps on both
and compares: rc, stderr, masked stdout (instance-id/env diagnostics masked,
exactly as the fixture documents them as non-signature), and the PASS line.
Also verifies every row's committed signature on both trees.

Usage: python3 fold_candidates.py [--reps 3]
Outputs: fold-proposal.diff, fold-candidates/**, fold-candidates-verification.json
"""
import argparse
import ast
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CF = HERE / "committed-fixtures"
HARNESS = CF / "run_battery.py"
REPO = HERE.parents[2]
FIXTURES = REPO / "corpus" / "fixtures"
GODOT = "godot"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

# (file, line number, expected exact line, replacement or None to delete)
EDITS = [
    ("dss_lattice.gd", 357, "\tvar pile: Array = []", None),
    ("dss_lattice.gd", 359,
     '\t\tpile.append(_mk_body("p%d" % i, Vector2(1000 + i * 2, 0), Vector2(200, 40)))',
     '\t\t_mk_body("p%d" % i, Vector2(1000 + i * 2, 0), Vector2(200, 40))'),
    ("dss_lattice.gd", 370,
     '\tvar box := _mk_body("box", Vector2(100, 0), Vector2(40, 40))',
     '\t_mk_body("box", Vector2(100, 0), Vector2(40, 40))'),
    ("dss_lattice.gd", 499, "\tvar made2: Array = []", None),
    ("dss_lattice.gd", 500,
     '\t_pile(["a2", "b2", "c2", "d2", "e2"], 0.0, 1000.0, made2)',
     '\t_pile(["a2", "b2", "c2", "d2", "e2"], 0.0, 1000.0, [])'),
    ("dss_lattice.gd", 506, "\tvar made3: Array = []", None),
    ("dss_lattice.gd", 507,
     '\t_pile(["e3", "d3", "c3", "b3", "a3"], 0.0, 2000.0, made3)',
     '\t_pile(["e3", "d3", "c3", "b3", "a3"], 0.0, 2000.0, [])'),
    ("dss_lattice.gd", 514,
     '\tvar fresh := _mk_body("f", Vector2(16, 0), Vector2(40, 40))',
     '\t_mk_body("f", Vector2(16, 0), Vector2(40, 40))'),
    ("dss_lattice.gd", 571,
     "\tvar cast := _sh(_circle(20), Transform2D(0, Vector2(700, 0)), Vector2(400, 0))",
     "\t_sh(_circle(20), Transform2D(0, Vector2(700, 0)), Vector2(400, 0))"),
    ("dss_lattice.gd", 585,
     '\tvar ar := _mk_body("ar", Vector2(200, 0), Vector2(4, 400), "area")',
     '\t_mk_body("ar", Vector2(200, 0), Vector2(4, 400), "area")'),
    ("dss_lattice.gd", 629,
     '\tvar b2 := _mk_body("b2", Vector2(112, 0), Vector2(4, 400))',
     '\t_mk_body("b2", Vector2(112, 0), Vector2(4, 400))'),
    ("r95b_order.gd", 415, "\tvar dss := _dss()", None),
    ("r95b_order.gd", 455, "\tvar dss := _dss()", None),
    ("r95b_order.gd", 530,
     '\tvar made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)',
     '\t_pile(["a", "b", "c", "d", "e"], 0.0, 0.0)'),
    ("r95b_order.gd", 567,
     '\tvar made := _pile(["a", "b", "c", "d", "e"], off, 0.0)',
     '\t_pile(["a", "b", "c", "d", "e"], off, 0.0)'),
    ("r95b_order.gd", 609,
     '\tvar made := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)',
     '\t_pile(["a", "b", "c", "d", "e"], 0.0, 0.0)'),
    ("r95b_order.gd", 745,
     '\tvar a := _pile(["a", "b", "c", "d", "e"], 0.0, 0.0)',
     '\t_pile(["a", "b", "c", "d", "e"], 0.0, 0.0)'),
    ("r95b_order.gd", 750,
     '\tvar b := _pile(["a2", "b2", "c2", "d2", "e2"], 0.0, 1000.0)',
     '\t_pile(["a2", "b2", "c2", "d2", "e2"], 0.0, 1000.0)'),
]

MASK_KEYS = ("ids", "env", "fresh_id")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mask_diag(stdout: str) -> str:
    lines = []
    for l in stdout.splitlines():
        m = re.match(r"^R95B \S+ (\w+)=", l)
        if m and (m.group(1) in MASK_KEYS or re.fullmatch(r"t\d+_bodypos", m.group(1))):
            lines.append("MASKED %s" % m.group(1))
        else:
            lines.append(l)
    return "\n".join(lines)


def extract_rows_and_classifier():
    src = HARNESS.read_text()
    tree = ast.parse(src)
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": list(t[2]),
                               "expected_exit": t[3], "signature": t[4]}
    r95 = {k: v for k, v in cases.items()
           if k.startswith("dss_lattice_") or k.startswith("r95b_order_")}
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
    ns = {}
    exec("import re\n" + ast.get_source_segment(src, fn), ns)
    return r95, ns["classify_process"]


def apply_edits(name: str, text: str) -> str:
    lines = text.splitlines(keepends=True)
    by_file = [e for e in EDITS if e[0] == name]
    # apply from the bottom so indices stay valid
    for _, ln, expect, repl in sorted(by_file, key=lambda e: -e[1]):
        actual = lines[ln - 1].rstrip("\n")
        assert actual == expect, "line %d of %s drifted:\n  want %r\n  got  %r" % (ln, name, expect, actual)
        if repl is None:
            del lines[ln - 1]
        else:
            lines[ln - 1] = repl + "\n"
    return "".join(lines)


def stage(dest: Path, fixture_bytes: dict) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    for item in FIXTURES.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    for name, data in fixture_bytes.items():
        (dest / name).write_text(data)
    pf = dest / "project.godot"
    pf.write_text(pf.read_text().replace(
        'config/name="MechanicOneShotTest"',
        'config/name="MechanicOneShotTest-%s"' % dest.name, 1))
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    t = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    chain.write_text(t.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    return dest


def launch(scratch: Path, script: str, flags: list, timeout=8):
    cmd = [GODOT, "--headless", "--path", str(scratch),
           "--script", "res://" + script, "--", *flags]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return out, err, None, "TIMEOUT"
    except OSError as exc:
        return "", str(exc), None, "OSError"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    args = ap.parse_args()

    committed = {name: (CF / name).read_text() for name in ("dss_lattice.gd", "r95b_order.gd")}
    folded = {name: apply_edits(name, text) for name, text in committed.items()}
    print("== fold candidate build ==")
    for name in committed:
        print("  %-16s committed=%s folded=%s  -%d lines"
              % (name, sha256(CF / name), hashlib.sha256(folded[name].encode()).hexdigest(),
                 len(committed[name].splitlines()) - len(folded[name].splitlines())))

    # unified diff of the two fixtures
    diff = []
    for name in ("dss_lattice.gd", "r95b_order.gd"):
        diff += list(difflib.unified_diff(
            committed[name].splitlines(keepends=True), folded[name].splitlines(keepends=True),
            fromfile="a/corpus/fixtures/%s" % name, tofile="b/corpus/fixtures/%s" % name))
    # harness sha comment updates
    h = HARNESS.read_text().splitlines(keepends=True)
    for name in ("dss_lattice.gd", "r95b_order.gd"):
        old = sha256(CF / name)
        new = hashlib.sha256(folded[name].encode()).hexdigest()
        replaced = 0
        for i, l in enumerate(h):
            if old in l:
                h[i] = l.replace(old, new)
                replaced += 1
        assert replaced == 1, "sha comment anchor for %s matched %d lines" % (name, replaced)
    harness_folded = "".join(h)
    diff += list(difflib.unified_diff(
        HARNESS.read_text().splitlines(keepends=True), harness_folded.splitlines(keepends=True),
        fromfile="a/corpus/fixtures/run_battery.py", tofile="b/corpus/fixtures/run_battery.py"))
    (HERE / "fold-proposal.diff").write_text("".join(diff))
    print("  fold-proposal.diff: %d lines" % len("".join(diff).splitlines()))

    # folded fixture dir + harness copy for a full-battery run
    if (HERE / "fold-candidates").exists():
        shutil.rmtree(HERE / "fold-candidates")
    (HERE / "fold-candidates").mkdir(parents=True)
    for name in ("dss_lattice.gd", "r95b_order.gd"):
        (HERE / "fold-candidates" / name).write_text(folded[name])
    (HERE / "fold-candidates" / "run_battery.py").write_text(harness_folded)

    # full launch project for the folded-tree battery (all fixtures, folded bytes)
    if (HERE / "fold-battery-project").exists():
        shutil.rmtree(HERE / "fold-battery-project")
    shutil.copytree(FIXTURES, HERE / "fold-battery-project")
    for name in ("dss_lattice.gd", "r95b_order.gd"):
        (HERE / "fold-battery-project" / name).write_text(folded[name])
    (HERE / "fold-battery-project" / "run_battery.py").write_text(harness_folded)

    r95, classify = extract_rows_and_classifier()
    run_dir = HERE / "fold-runs" / STAMP
    sc = stage(run_dir / "scratch-committed", committed)
    sf = stage(run_dir / "scratch-folded", folded)
    print("  scratch: %s | %s" % (sc, sf))

    per_row = {}
    t0 = time.time()
    for i, (row, spec) in enumerate(sorted(r95.items()), 1):
        rows = []
        for rep in range(1, args.reps + 1):
            oc, ec, rcc, terrc = launch(sc, spec["script"], spec["flags"])
            of, ef, rcf, terrf = launch(sf, spec["script"], spec["flags"])
            pc = classify(rcc, terrc, oc + ec, spec["expected_exit"], spec["signature"], ())
            pf = classify(rcf, terrf, of + ef, spec["expected_exit"], spec["signature"], ())
            pl_c = next((l for l in oc.splitlines() if l.startswith("PASS ")), "")
            pl_f = next((l for l in of.splitlines() if l.startswith("PASS ")), "")
            rows.append({
                "rep": rep,
                "committed": {"rc": rcc, "error": terrc, "passed": pc,
                              "pass_line_eq_sig": pl_c == spec["signature"],
                              "prefix": pl_c.startswith(spec["signature"]),
                              "masked_sha": hashlib.sha256(mask_diag(oc).encode()).hexdigest(),
                              "stderr": ec},
                "folded": {"rc": rcf, "error": terrf, "passed": pf,
                           "pass_line_eq_sig": pl_f == spec["signature"],
                           "prefix": pl_f.startswith(spec["signature"]),
                           "masked_sha": hashlib.sha256(mask_diag(of).encode()).hexdigest(),
                           "stderr": ef},
            })
        per_row[row] = rows
        cross_masked = sum(1 for r in rows if r["committed"]["masked_sha"] != r["folded"]["masked_sha"])
        cross_pass = sum(1 for r in rows if r["committed"]["pass_line_eq_sig"] != r["folded"]["pass_line_eq_sig"])
        print("%3d/%d %-34s masked_cross_diff=%d  passline_cross_diff=%d  pass c=%d/%d f=%d/%d"
              % (i, len(r95), row, cross_masked, cross_pass,
                 sum(1 for r in rows if r["committed"]["passed"]),
                 len(rows), sum(1 for r in rows if r["folded"]["passed"]), len(rows)))
        sys.stdout.flush()
    print("launch phase: %.1fs" % (time.time() - t0))

    summary = {
        "stamp": STAMP,
        "reps": args.reps,
        "committed_sha256": {n: sha256(CF / n) for n in committed},
        "folded_sha256": {n: hashlib.sha256(folded[n].encode()).hexdigest() for n in committed},
        "lines_removed": {n: len(committed[n].splitlines()) - len(folded[n].splitlines())
                          for n in committed},
        "sites": len(EDITS),
        "per_row": per_row,
        "cross_masked_diffs": sum(1 for rows in per_row.values() for r in rows
                                  if r["committed"]["masked_sha"] != r["folded"]["masked_sha"]),
        "cross_passline_diffs": sum(1 for rows in per_row.values() for r in rows
                                    if r["committed"]["pass_line_eq_sig"] != r["folded"]["pass_line_eq_sig"]),
        "all_pass_committed": all(r["committed"]["passed"] for rows in per_row.values() for r in rows),
        "all_pass_folded": all(r["folded"]["passed"] for rows in per_row.values() for r in rows),
    }
    (HERE / "fold-candidates-verification.json").write_text(json.dumps(summary, indent=1))
    print()
    print("cross masked diffs: %d   cross pass-line diffs: %d   all pass c=%s f=%s"
          % (summary["cross_masked_diffs"], summary["cross_passline_diffs"],
             summary["all_pass_committed"], summary["all_pass_folded"]))
    ok = (summary["cross_masked_diffs"] == 0 and summary["cross_passline_diffs"] == 0
          and summary["all_pass_committed"] and summary["all_pass_folded"])
    print("FOLD BYTE-NEUTRAL: %s" % ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
