#!/usr/bin/env python3
"""r104-G0 — shape x gate matrix: which evasions each candidate rule closes,
plus the residual classes neither closes.

Candidate rules (each a minimal, verbatim patch of the landed source):
  L : landed            `line.startswith("PASS ")`                        x1 site
  T1: census widened    `line.strip().startswith("PASS")`                 x1 site
  T2: all four sites    the three span/diag-window sites widened too      x4 sites

Shapes: the 10 r103 evasions + the whitespace-shifted-pin class (V1-V6) that
the whitespace-pin-hole probe identified.

Read-only; run_battery.py is imported, never executed.
"""
import copy
import json
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RB = REPO / "corpus" / "fixtures" / "run_battery.py"
RUNS = REPO / "corpus" / "live" / "runs"
BASE = RUNS / "20261018T213443471189Z" / "verdicts.json"

SITES = [
    'pass_lines = [line for line in output if line.startswith("PASS ")]',
    'if not (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)):',
    'if (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)',
    'if (line.startswith("PASS ") or RECEIPT_BANNER_RE.match(line)',
]
WIDE = [
    'pass_lines = [line for line in output if line.strip().startswith("PASS")]',
    'if not (line.strip().startswith("PASS") or RECEIPT_SEQ_RE.match(line)):',
    'if (line.strip().startswith("PASS") or RECEIPT_SEQ_RE.match(line)',
    'if (line.strip().startswith("PASS") or RECEIPT_BANNER_RE.match(line)',
]

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")
BASES = {"launch": "export_launch_embed_boot", "prod": "export_prod_base_pck",
         "seq": "r100b_seq_clean", "simple": "input_route"}


def build(rows):
    by = {}
    for r in rows:
        by.setdefault(r.get("case"), r)
    base = {k: by[c] for k, c in BASES.items()}
    pin = base["simple"]["output"][-1]
    ev = []
    ev.append(("s1a_banner_foreign", "seq", FORGED_BANNER, "append"))
    ev.append(("s1b_banner_dup", "launch", BANNER, "append"))
    ev.append(("s2a_diag_foreign", "simple", "EXPORT_LAUNCH_DIAG embed forged=true", "append"))
    ev.append(("s2b_diag_same_family", "launch", "EXPORT_LAUNCH_DIAG embed forged=1", "append"))
    ev.append(("s3a_pass_flood5", "simple", "PASS flooded=1 extra=true", "append"))
    ev.append(("s3b_pass_flood1_seq", "seq", "PASS r100_gui forged=1", "append"))
    ev.append(("s4a_tab_lead", "simple", "\tPASS forged=true", "append"))
    ev.append(("s4b_trail_space", "simple", pin + " ", "append"))
    ev.append(("s4c_trail_nbsp", "simple", "PASS forged=true\u00a0", "append"))
    ev.append(("s4d_tab_after_pass", "simple", "PASS\tforged=true", "append"))
    ev.append(("V1_shift_tab", "simple", "\t" + pin, "replace"))
    ev.append(("V2_shift_spaces", "simple", "    " + pin, "replace"))
    ev.append(("V3_shift_nbsp", "simple", "\u00a0" + pin, "replace"))
    ev.append(("V4_prefix_noise", "simple", "x\t" + pin, "replace"))
    # Composite: the shape that makes the whitespace bypass MATTER. Injecting a
    # forged PASS line and then hiding the row's own pinned line behind leading
    # whitespace leaves exactly one column-0 PASS line (the forgery), so the
    # landed pass-accounting branch sees a well-formed single-PASS row.
    ev.append(("C1_hidepin_forge", "simple", "PASS forged=true", "hidepin"))
    ev.append(("C2_hidepin_flood3", "simple", "PASS flooded=1 extra=true", "hidepin"))
    # C3/C4: the decisive pair. The forged line CARRIES the row's pinned prefix
    # (so the landed anchor-content check is satisfied) while the row's real
    # pinned line is hidden behind a leading tab. The landed census then sees
    # exactly one column-0 PASS line and stays silent; the widened census sees
    # two and flags.
    ev.append(("C3_hidepin_forge_pinned", "simple", pin + " forged=evil", "hidepin"))
    ev.append(("C4_hidepin_forge_pinned2", "simple", pin + " forged=evil2", "hidepin"))
    return base, ev


def load(src, name):
    mod = types.ModuleType(name)
    mod.__dict__["__file__"] = str(RB)
    exec(compile(src, str(RB), "exec"), mod.__dict__)
    return mod


def apply_shape(base, line, key, kind):
    r = copy.deepcopy(base[key])
    out = list(r["output"])
    if kind == "append":
        out.append(line)
    else:
        i = next(i for i, l in enumerate(out) if "route=parse_input_event" in l)
        if kind == "replace":
            out[i] = line
        elif kind == "hidepin":
            # the row's own pinned line loses column-0 anchoring; the forged
            # line is appended as the only column-0 PASS line.
            out[i] = "\t" + out[i]
            out.append(line)
    r["output"] = out
    return r


def main():
    src = RB.read_text()
    for s in SITES:
        assert s in src, "site not found verbatim: %r" % s
    t1 = src.replace(SITES[0], WIDE[0])
    t2 = src
    for a, b in zip(SITES, WIDE):
        t2 = t2.replace(a, b)
    mods = {"L_landed": load(src, "gL"), "T1_census": load(t1, "gT1"),
            "T2_all4": load(t2, "gT2")}
    print("SITE_OCCURRENCES: " + ", ".join("%s=%d" % (s.split("(")[0][:28], src.count(s))
                                           for s in SITES))

    rows = json.loads(BASE.read_bytes())["results"]
    base, ev = build(rows)
    print("\n%-24s %-8s %-8s %-8s" % ("shape", "L", "T1", "T2"))
    counts = {k: 0 for k in mods}
    for name, key, line, kind in ev:
        row = apply_shape(base, line, key, kind)
        cells = []
        for k, m in mods.items():
            fl = m.receipt_shape_flag(row)
            if fl:
                counts[k] += 1
            cells.append("FLAG" if fl else "-")
        print("%-24s %-8s %-8s %-8s" % (name, *cells))
    print("CAUGHT: " + ", ".join("%s=%d/%d" % (k, v, len(ev)) for k, v in counts.items()))

    # false positives: same three modules over every stored run
    print("\n=== FP sweep over all stored runs ===")
    for k, m in mods.items():
        tot = fl = 0
        for p in sorted(RUNS.glob("*/verdicts.json")):
            a = m.receipt_shape_audit(json.loads(p.read_bytes()).get("results", []))
            tot += a["audited"]
            fl += len(a["flags"])
        print("%-10s audited=%d flags=%d" % (k, tot, fl))
    return 0


if __name__ == "__main__":
    sys.exit(main())
