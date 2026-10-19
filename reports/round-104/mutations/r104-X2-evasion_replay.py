#!/usr/bin/env python3
"""r104-X2 C3a — STORED in-battery gate-evasion replay probe (K>=8 shapes).

Replays K synthetic evasion shapes (each a tampered copy of a REAL green stored
row) against the AST-extracted landed gate `receipt_shape_flag`. Green only if
every shape's flag status equals its declared classification. run_battery.py is
never imported or executed; the gate module is a side-effect-free extraction.

Modes:
  --emit-only            build + write /var/tmp/r104-X2/evasions_r104.json
  --gate PATH            replay against PATH (default the r104-X2 extraction)
Exit code 0 iff every shape matches its declared expectation.
"""
import argparse, copy, hashlib, importlib.util, json, sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = Path("/var/tmp/r104-X2")
RUN = REPO / "corpus/live/runs/20261019T005558434174Z/verdicts.json"
DEFAULT_GATE = SCRATCH / "gate_extract.py"

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")

# (base_case, ops, declared)  declared in {"FLAG","HARMLESS"}
# HARMLESS = the shape-layer gate does not flag it, and the verdict layer does
# (proof in the companion C2b script); a HARMLESS shape that the gate DID flag
# is not a failure of the probe, it is an over-flag — reported as such.
SHAPES = [
    ("s1a_banner_forged_seq",   "r100b_seq_clean",
     [("insert", 2, FORGED_BANNER)], "HARMLESS"),
    ("s1b_banner_dup_launch",   "export_launch_embed_boot",
     [("insert", 4, BANNER)], "HARMLESS"),
    ("s2a_diag_other_family",   "input_route",
     [("insert", 3, "EXPORT_LAUNCH_DIAG embed forged=true")], "HARMLESS"),
    ("s2b_diag_forged_launch",  "export_launch_embed_boot",
     [("insert", 6, "EXPORT_LAUNCH_DIAG embed forged=1")], "HARMLESS"),
    ("s3a_flood5_simple",       "input_route",
     [("append", None, "PASS flooded=%d extra=true" % n) for n in range(1, 6)], "FLAG"),
    ("s3b_flood1_seq",          "r100b_seq_clean",
     [("append", None, "PASS r100_gui forged=1")], "FLAG"),
    ("s4a_tab_lead_simple",     "input_route",
     [("append", None, "\tPASS forged=true")], "HARMLESS"),
    ("s4b_trail_space_simple",  "input_route",
     [("append", None, None)], "FLAG"),          # None -> last line + " "
    ("s4c_trail_nbsp_simple",   "input_route",
     [("append", None, "PASS forged=true\u00a0")], "FLAG"),
    ("s4d_tab_after_pass",      "input_route",
     [("append", None, "PASS\tforged=true")], "HARMLESS"),
]


def find_row(rows, case):
    for r in rows:
        if r.get("case") == case:
            return r
    raise SystemExit("base row not found: %s" % case)


def build(rows):
    bases = {c: find_row(rows, c) for c in {s[1] for s in SHAPES}}
    out = []
    for name, base_case, ops, declared in SHAPES:
        row = copy.deepcopy(bases[base_case])
        lines = list(row["output"])
        for kind, idx, line in ops:
            if line is None:
                line = lines[-1] + " "
            if kind == "insert":
                lines.insert(idx, line)
            else:
                lines.append(line)
        row["output"] = lines
        out.append({"name": name, "base_case": base_case, "declared": declared,
                    "row": row, "added": [o[2] if o[2] is not None else "<last+space>"
                                          for o in ops]})
    return out


def load_gate(path):
    spec = importlib.util.spec_from_file_location("x2_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", default=str(DEFAULT_GATE))
    ap.add_argument("--emit-only", action="store_true")
    args = ap.parse_args()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    raw = RUN.read_bytes()
    rows = json.loads(raw)["results"]
    shapes = build(rows)
    payload = {"run": str(RUN), "run_sha256": hashlib.sha256(raw).hexdigest(),
               "gate": args.gate, "k": len(shapes),
               "shapes": [{"name": s["name"], "base_case": s["base_case"],
                           "declared": s["declared"], "added": s["added"]}
                          for s in shapes]}
    (SCRATCH / "evasions_r104.json").write_text(json.dumps(payload, indent=1) + "\n")
    print("WROTE %s K=%d" % (SCRATCH / "evasions_r104.json", len(shapes)))
    if args.emit_only:
        return 0
    mod = load_gate(args.gate)
    fn = mod.receipt_shape_flag
    print("GATE=%s sha256=%s" % (args.gate,
          hashlib.sha256(Path(args.gate).read_bytes()).hexdigest()[:16]))
    mismatch = 0
    for s in shapes:
        flags = fn(s["row"])
        observed = "FLAG" if flags else "HARMLESS"
        ok = (observed == s["declared"])
        if not ok:
            mismatch += 1
        whys = ",".join(sorted({f["why"] for f in flags}))
        print("%-24s declared=%-8s observed=%-8s %s  [%s]" %
              (s["name"], s["declared"], observed, "OK" if ok else "MISMATCH", whys))
    print("SHAPES=%d MISMATCH=%d" % (len(shapes), mismatch))
    return 0 if mismatch == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
