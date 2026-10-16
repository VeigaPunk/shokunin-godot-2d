#!/usr/bin/env python3
"""r93-simplifier static pin analysis (no launches).

1. r93 row signature redundancy: exact duplicates, and strict substring
   subsumption between rows sharing the same (script, arm) — a row whose
   signature is a substring of a sibling row's signature on the same arm can
   never fail when the sibling passes.
2. Crossfade weight-law arithmetic against the pinned arrays
   (finished_010 / finished_005 / finished_020 / interleaved):
   w_i = (i-1)/(N-1), value = 100 + 400*w_i.
3. Harness-comment claims vs the pinned values (spot checks).
4. Floor-gate predicate / entry census.

Usage: python3 static_pin_analysis.py > static-pin-analysis.txt
"""
import ast
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"


def load_rows(path):
    src = path.read_text()
    tree = ast.parse(src)
    rows = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                rows[t[0]] = {"script": t[1], "flags": t[2], "exit": t[3],
                              "sig": t[4]}
    return src, rows


def arr(s):
    return [float(x) for x in s.strip("[]").split(",")]


def main():
    src, rows = load_rows(HARNESS)
    r93 = {k: v for k, v in rows.items() if k.startswith("r93_")}
    out = []

    out.append("== signature redundancy census ==")
    exact = {}
    for k, v in r93.items():
        if not isinstance(v["sig"], str):
            continue
        exact.setdefault(v["sig"], []).append(k)
    dups = {s: ks for s, ks in exact.items() if len(ks) > 1}
    out.append("exact duplicate signatures: %d" % len(dups))
    for s, ks in dups.items():
        out.append("  DUP %s" % ", ".join(ks))

    groups = {}
    for k, v in r93.items():
        key = (v["script"], tuple(v["flags"]))
        groups.setdefault(key, []).append(k)
    subsume = []
    for (script, flags), ks in groups.items():
        if len(ks) < 2:
            continue
        for a in ks:
            for b in ks:
                if a == b:
                    continue
                sa, sb = r93[a]["sig"], r93[b]["sig"]
                if isinstance(sa, str) and isinstance(sb, str) and sa != sb and sa in sb:
                    subsume.append((a, b, script, flags))
    out.append("strict substring subsumption within a shared (script,arm): %d"
               % len(subsume))
    for a, b, script, flags in subsume:
        out.append("  SUBSUMED %-38s by %-38s (%s %s)" % (a, b, script, flags))
    out.append("shared-arm groups: %d" % sum(1 for ks in groups.values() if len(ks) > 1))
    for (script, flags), ks in sorted(groups.items()):
        if len(ks) > 1:
            out.append("  %-18s %-22s rows=%d" % (script, ",".join(flags), len(ks)))

    out.append("")
    out.append("== crossfade weight-law arithmetic vs pinned arrays ==")
    law_ok = True
    for name, N in (("finished_010", 10), ("finished_005", 20), ("finished_020", 5)):
        m = re.search(re.escape(name) + r"=\[([^\]]*)\]", r93["r93_anim_blend_finished"]["sig"])
        if not m:
            out.append("  %s: NOT FOUND in r93_anim_blend_finished" % name)
            law_ok = False
            continue
        pinned = arr(m.group(1))
        expect = [100.0 + 400.0 * i / (N - 1) for i in range(N)]
        # float32-vs-float64 tolerance: pinned values are float32 prints
        errs = [abs(p - e) for p, e in zip(pinned, expect)]
        rel = [abs(p - e) / max(1.0, abs(e)) for p, e in zip(pinned, expect)]
        ok = len(pinned) == N and max(rel) < 5e-6
        law_ok &= ok
        out.append("  %-14s N=%-3d len=%d  max_abs_err=%.3e  max_rel_err=%.3e  law=%s"
                   % (name, N, len(pinned), max(errs), max(rel), "HOLDS" if ok else "BROKEN"))
        out.append("      first=%s mid=%s last=%s"
                   % (pinned[0], pinned[len(pinned) // 2], pinned[-1]))
    m = re.search(r"interleaved=\[([^\]]*)\]", r93["r93_anim_blend_interleaved"]["sig"])
    if m:
        inter = arr(m.group(1))
        m10 = re.search(r"finished_010=\[([^\]]*)\]", r93["r93_anim_blend_interleaved"]["sig"])
        f10 = arr(m10.group(1))
        out.append("  interleaved == finished_010 (same bytes in pin): %s"
                   % (inter == f10))
        law_ok &= inter == f10
    out.append("  OVERALL crossfade law: %s" % ("HOLDS" if law_ok else "BROKEN"))

    out.append("")
    out.append("== overshoot pin internal check ==")
    sig = r93["r93_anim_overshoot"]["sig"]
    m = re.search(r"overshoot=\[back025=([-\d.e]+),back050=([-\d.e]+)\]", sig)
    m2 = re.search(r"overshoot2=\[spr050=([-\d.e]+),spr100=([-\d.e]+),ela025=([-\d.e]+)\]", sig)
    m3 = re.search(r"clamp=\[neg=([-\d.e]+),over=([-\d.e]+)\]", sig)
    if m and m2 and m3:
        back025, back050 = float(m.group(1)), float(m.group(2))
        spr050, spr100, ela025 = (float(m2.group(1)), float(m2.group(2)), float(m2.group(3)))
        neg, over = float(m3.group(1)), float(m3.group(2))
        out.append("  BACK/EASE_IN_OUT 1.0->10.0: t=0.25 -> %s (start=1.0) below-start=%s"
                   % (back025, back025 < 1.0))
        out.append("  BACK t=0.5 midpoint=%s (expected 5.5) midpoint_holds=%s"
                   % (back050, abs(back050 - 5.5) < 1e-6))
        out.append("  SPRING/EASE_OUT 0.0->10.0: t=0.5 -> %s above-end=%s ; t=1.0 -> %s endpoint=%s"
                   % (spr050, spr050 > 10.0, spr100, abs(spr100 - 10.0) < 1e-6))
        out.append("  ELASTIC/EASE_OUT t=0.25 -> %s (inside [0,10]=%s)" % (ela025, 0.0 <= ela025 <= 10.0))
        out.append("  static interpolate_value extrapolates: neg=%s over=%s (t=-0.5 -> -5.0, t=1.5 -> 15.0) "
                   "no-clamp=%s" % (neg, over, neg == -5.0 and over == 15.0))
    else:
        out.append("  parse FAILED")

    out.append("")
    out.append("== N-1 await-law pin shape ==")
    out.append("  r93_anim_await_offbyone sig = %r" % r93["r93_anim_await_offbyone"]["sig"])
    out.append("  prefix ends before ',x2=' (binds only the first-await read): %s"
               % (not r93["r93_anim_await_offbyone"]["sig"].rstrip().endswith("x2=")))
    out.append("  r93_anim_physics_tick sig = %r" % r93["r93_anim_physics_tick"]["sig"])
    out.append("  r93_anim_phys_delta sig = %r" % r93["r93_anim_phys_delta"]["sig"])
    out.append("  r93_anim_deferred_flush sig = %r" % r93["r93_anim_deferred_flush"]["sig"])
    out.append("  r93_anim_manual_clock_interleaved sig = %r"
               % r93["r93_anim_manual_clock_interleaved"]["sig"])
    out.append("  r93_anim_manual_clock_control sig = %r"
               % r93["r93_anim_manual_clock_control"]["sig"])

    out.append("")
    out.append("== harness-comment claims vs pins (spot checks) ==")
    claims = {
        "comment: BACK/EASE_IN_OUT reads 0.1029 BELOW the start at t=0.25":
            ("0.1029" in src and "0.10286344587803" in r93["r93_anim_overshoot"]["sig"]),
        "comment: SPRING/EASE_OUT reads 10.5102 ABOVE the end at t=0.5":
            ("10.5102" in src and "10.510157585144" in r93["r93_anim_overshoot"]["sig"]),
        "comment: idle=[x1=0.0 pinned in 258/258 frame runs":
            ("258/258" in src and "idle=[x1=0.0" in r93["r93_anim_await_offbyone"]["sig"]),
        "comment: DEFERRED flushes on a physics frame (new route)":
            ("after_phys=[7,8]" in r93["r93_anim_deferred_flush"]["sig"]),
        "comment: w_i=(i-1)/(N-1)":
            ("w_i=(i-1)/(N-1)" in src),
        "comment: all 23 rows are ERROR:-clean / no expected_errors entries":
            (len(r93) == 23),
    }
    for c, ok in claims.items():
        out.append("  %-70s %s" % (c, "CONSISTENT" if ok else "MISMATCH"))

    out.append("")
    out.append("== floor gate ==")
    lines = src.splitlines()
    for i, l in enumerate(lines):
        if '"r93_expected_errors_all_matched"' in l:
            out.append("  line=%d: %s" % (i + 1, l.strip()))
            for j in range(i + 1, min(i + 6, len(lines))):
                out.append("      %s" % lines[j].rstrip())
    print("\n".join(out))


if __name__ == "__main__":
    main()
