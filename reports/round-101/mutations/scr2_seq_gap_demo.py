#!/usr/bin/env python3
"""r101 SCR-2 — r100b_seq seq-gap closure demonstration (read-only; no battery).

Evaluates the landed one-line `r100b_seq_*` pins and candidate full-transcript
pins against real captured replay bytes, under the production `classify_process`
semantics copied from corpus/fixtures/run_battery.py:1725-1742. The battery's
merged output shape for ordinary rows is `output = proc_stdout + proc_stderr`
(run_battery.py:1870-1871); the transcript files used here were captured with
the same launch shape the battery uses (run_battery.py:1862):

    godot --headless --path <scratch> --script res://r100b_seq.gd -- --clean=<0|1>

Evidence transcripts (this host, 4.7.2.stable):
  /var/tmp/r101-scr2/seq1.{stdout,stderr}   variant --clean=1
  /var/tmp/r101-scr2/seq0.{stdout,stderr}   variant --clean=0

Never runs run_battery.py; reads only. Usage:
  python3 reports/round-101/mutations/scr2_seq_gap_demo.py | tee /var/tmp/r101-scr2/demo.log
"""
import ast
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
SCRATCH = pathlib.Path("/var/tmp/r101-scr2")
ARMS = ["census", "routing", "hover", "motion", "localpos", "cursor", "clip",
        "drag", "touch", "subvp", "warp", "focus", "render", "osmeta"]
ALLOW_T_NULL = ('ERROR: Parameter "t" is null.',)  # run_battery.py:2225-2230


def landed_cases():
    tree = ast.parse((REPO / "corpus/fixtures/run_battery.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "CASES" for t in node.targets):
            rows = {}
            for elt in node.value.elts:
                vals = [ast.literal_eval(e) for e in elt.elts]
                rows[vals[0]] = vals
            return rows
    raise SystemExit("CASES not found in run_battery.py")


def classify_process(output, signature, allowed_errors=()):
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped
                    and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, a) for a in allowed_errors)]
    # exit code 0 / error None verified separately for these captures (rc=0).
    return (signature in output and not unrelated_errors
            and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def load(variant):
    stdout = (SCRATCH / f"seq{variant}.stdout").read_text()
    stderr = (SCRATCH / f"seq{variant}.stderr").read_text()
    return stdout, stderr, stdout + stderr


def cells_of(stdout):
    cells = [line for line in stdout.splitlines()
             if line.startswith("PASS r100_gui ") and line.split()[2] in ARMS]
    assert len(cells) == 14, f"expected 14 cell lines, got {len(cells)}"
    assert [c.split()[2] for c in cells] == ARMS
    return cells


def first_diff(x, y):
    for i, (cx, cy) in enumerate(zip(x, y)):
        if cx != cy:
            return i
    return min(len(x), len(y))


def verdicts(output, pins):
    return {k: classify_process(output, s, ALLOW_T_NULL) for k, s in pins.items()}


def main():
    cases = landed_cases()
    old = {"old_clean": cases["r100b_seq_clean"][4],
           "old_noclean": cases["r100b_seq_noclean"][4]}
    fresh = {a: cases[f"r100_gui_{a}"][4] for a in ARMS}
    for variant, tag in (("1", "clean=1"), ("0", "noclean=0")):
        stdout, stderr, merged = load(variant)
        cells = cells_of(stdout)
        seq_done = next(l for l in stdout.splitlines() if l.startswith("SEQ_DONE"))
        pins = dict(old)
        pins["P14_cells"] = "\n".join(cells)
        pins["P15_cells+done"] = pins["P14_cells"] + "\n" + seq_done
        pins["PALL_stdout"] = "\n".join(stdout.splitlines())
        print(f"\n=== variant {tag} ===")
        base = verdicts(merged, pins)
        print("baseline: " + " ".join(f"{k}={v}" for k, v in base.items()))
        eq = [(a, cells[i] == fresh[a]) for i, a in enumerate(ARMS)]
        print(f"replay-vs-fresh: equal={sum(1 for _, ok in eq if ok)}/14  "
              + " ".join(f"{a}:{'==' if ok else '!='}" for a, ok in eq))
        for i, a in enumerate(ARMS):
            if cells[i] != fresh[a]:
                d = first_diff(cells[i], fresh[a])
                print(f"  divergent {a}: replay[...{cells[i][max(0,d-30):d+40]!r}] "
                      f"fresh[...{fresh[a][max(0,d-30):d+40]!r}]")
        print("forged-extra-line seams (insert FORGED_EXTRA_CELL_OUTPUT):")
        for i in range(-1, 14):
            pos = "head" if i == -1 else f"after:{ARMS[i]}"
            if i == -1:
                forged = merged.replace(cells[0], "FORGED_EXTRA_CELL_OUTPUT\n" + cells[0], 1)
            else:
                forged = merged.replace(cells[i], cells[i] + "\nFORGED_EXTRA_CELL_OUTPUT", 1)
            v = verdicts(forged, pins)
            print(f"  {pos:<16} " + " ".join(f"{k}={v[k]}" for k in pins))
        print("replay cell line -> fresh cell line:")
        for i, a in enumerate(ARMS):
            if cells[i] == fresh[a]:
                continue
            mut = merged.replace(cells[i], fresh[a], 1)
            v = verdicts(mut, pins)
            print(f"  {a:<10} " + " ".join(f"{k}={v[k]}" for k in pins))


if __name__ == "__main__":
    main()
