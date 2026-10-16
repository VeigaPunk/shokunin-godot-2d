#!/usr/bin/env python3
"""r93 verifier — independent re-derivation of the four encoded laws.

Sources: this seat's fresh arm receipts (arms/*.out) + every committed
scout/boundary/author receipt.  Nothing here trusts a pinned value: each law is
re-derived from the fixture source semantics and recomputed arithmetically.

  L1  crossfade weight law  w_i=(i-1)/(N-1), v_i = 100 + 400*w_i
  L2  runtime overshoot (BACK<start, SPRING>end) + no-clamp extrapolation,
      cross-checked against the pure-function grid of the same easing
  L3  N-1 await law (independent probe, probes/nminus1/) + pinned-clause
      stability vs mode tails in the committed frame receipts
  L4  DEFERRED flush routes (process + physics frame, two-advance queue,
      IMMEDIATE inside advance)
"""
import pathlib
import re
import sys
from collections import defaultdict

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r93-verifier"
OUT = []
TOL = 5e-4


def p(s=""):
    OUT.append(str(s))


def arrays(line, field):
    """[a,b,c] float list for `field=[` inside a PASS line."""
    m = re.search(re.escape(field) + r"=\[([^\]]*)\]", line)
    if not m:
        return None
    return [float(x) for x in m.group(1).split(",")]


def scalar(line, field):
    m = re.search(r"(?<![A-Za-z0-9_])" + re.escape(field) + r"=([-0-9.eE]+)", line)
    return float(m.group(1)) if m else None


def collect(pattern):
    """all PASS lines whose line matches `pattern` across the corpora."""
    hits = []
    for corpus in [V / "arms", REPO / "corpus/live/r93-scout/runs",
                   REPO / "corpus/live/r93-boundary/runs",
                   REPO / "corpus/live/r93-author/fresh-reps"]:
        for f in sorted(corpus.rglob("*.out")):
            if "proj" in f.parts:
                continue
            for ln in f.read_text(errors="replace").splitlines():
                if re.match(pattern, ln):
                    hits.append((f, ln))
    return hits


# ---------------------------------------------------------------- L1 crossfade
p("== L1 crossfade weight law  v_i = 100 + 400*(i-1)/(N-1) ==")
for stem in ("anim_lattice", "r93b_anim"):
    pass_lines = [ln for _, ln in collect(rf"^PASS {stem} (animblend|blend) ")]
    p(f"  {stem}: receipts={len(pass_lines)}")
    for N, field in [(10, "finished_010"), (20, "finished_005"), (5, "finished_020")]:
        bad = 0
        present = 0
        uniq = set()
        for ln in pass_lines:
            arr = arrays(ln, field)
            if arr is None:
                continue  # this arm does not print that lattice (r93b prints only 010/020)
            present += 1
            if len(arr) != N:
                bad += 1
                continue
            uniq.add(tuple(arr))
            for i, v in enumerate(arr):
                want = 100.0 + 400.0 * i / (N - 1)
                if abs(v - want) > TOL:
                    bad += 1
                    p(f"    !! {field}[{i}]={v} want {want}")
        p(f"    {field}: present={present} distinct_arrays={len(uniq)} formula_violations={bad}")
    # interleaved control (r93b only)
    if stem == "r93b_anim":
        eq = all(("interleaved_eq_plain=true" in ln) and
                 (arrays(ln, "interleaved") == arrays(ln, "finished_010"))
                 for ln in pass_lines)
        p(f"    interleaved==finished_010 elementwise in all receipts: {eq}")
    # granularity: the three lattices must not be interchangeable
    a10 = {tuple(arrays(ln, "finished_010")) for ln in pass_lines if arrays(ln, "finished_010")}
    a05 = {tuple(arrays(ln, "finished_005")) for ln in pass_lines if arrays(ln, "finished_005")}
    a20 = {tuple(arrays(ln, "finished_020")) for ln in pass_lines if arrays(ln, "finished_020")}
    p(f"    distinct lattices 010/005/020: {len(a10)}/{len(a05)}/{len(a20)}; "
      f"at t=0.6: 010[5]={sorted(a10)[0][5]:.6f} vs 020[2]={sorted(a20)[0][2]:.6f} (same 1s blend, different N)")

# ------------------------------------------------------------------ L2 overshoot
p("")
p("== L2 runtime overshoot + no-clamp (r93b purity) ==")
pur = [ln for _, ln in collect(r"^PASS r93b_anim purity ")]
p(f"  purity receipts={len(pur)}")
checks = {"back025_below_start": 0, "spr050_above_end": 0, "spr100_endpoint": 0,
          "ela025_inside": 0, "clamp_extrapolates": 0}
for ln in pur:
    back = scalar(ln, "back025")
    spr = scalar(ln, "spr050")
    spr100 = scalar(ln, "spr100")
    ela = scalar(ln, "ela025")
    cneg = scalar(ln, "neg")
    cover = scalar(ln, "over")
    if back is not None and back < 1.0:
        checks["back025_below_start"] += 1
    if spr is not None and spr > 10.0:
        checks["spr050_above_end"] += 1
    if spr100 == 10.0:
        checks["spr100_endpoint"] += 1
    if ela is not None and 0.0 < ela < 10.0:
        checks["ela025_inside"] += 1
    if cneg == -5.0 and cover == 15.0:
        checks["clamp_extrapolates"] += 1
p("  " + " ".join(f"{k}={v}/{len(pur)}" for k, v in checks.items()))

# cross-check runtime values against the pure-function grid of the same easing
grid = [ln for _, ln in collect(r"^PASS anim_lattice tweenval_grid ")]
bac_io_025 = spr_out_050 = ela_out_025 = None
FOUR = r"in=([-0-9.,eE]+) out=([-0-9.,eE]+) io=([-0-9.,eE]+) oi=([-0-9.,eE]+)"
for ln in grid:
    m = re.search(r"bac " + FOUR, ln)
    if m:
        bac_io_025 = float(m.group(3).split(",")[1])
    m = re.search(r"spr " + FOUR, ln)
    if m:
        spr_out_050 = float(m.group(2).split(",")[2])
    m = re.search(r"ela " + FOUR, ln)
    if m:
        ela_out_025 = float(m.group(2).split(",")[1])
p(f"  pure grid: bac_io(0.25)={bac_io_025} spr_out(0.5)={spr_out_050} ela_out(0.25)={ela_out_025}")
if pur and bac_io_025 is not None:
    back = scalar(pur[0], "back025")
    spr = scalar(pur[0], "spr050")
    ela = scalar(pur[0], "ela025")
    p(f"  runtime-normalized: back f={(back-1.0)/9.0:.15f} vs pure f={bac_io_025/10.0:.15f} "
      f"delta={abs((back-1.0)/9.0-bac_io_025/10.0):.2e}")
    p(f"  runtime-normalized: spr  f={spr/10.0:.15f} vs pure f={spr_out_050/10.0:.15f} "
      f"delta={abs(spr/10.0-spr_out_050/10.0):.2e}")
    p(f"  runtime-normalized: ela  f={ela/10.0:.15f} vs pure f={ela_out_025/10.0:.15f} "
      f"delta={abs(ela/10.0-ela_out_025/10.0):.2e}")

# ------------------------------------------------------------------- L3 N-1 law
p("")
p("== L3 N-1 await law ==")
fr = [ln for _, ln in collect(r"^PASS r93b_anim frame ")]
p(f"  frame receipts={len(fr)}")
x1 = defaultdict(int)
tail_uniq = defaultdict(set)
for ln in fr:
    m = re.search(r"idle=\[x1=([-0-9.eE]+),x2=([-0-9.eE]+),x3=([-0-9.eE]+),x5=([-0-9.eE]+),x10=([-0-9.eE]+)\]", ln)
    if m:
        x1[m.group(1)] += 1
        for k, v in zip(("x2", "x3", "x5", "x10"), m.group(2, 3, 4, 5)):
            tail_uniq[k].add(v)
p(f"  distinct x1 values: {dict(x1)}")
p(f"  distinct unpinned tails: " + " ".join(f"{k}={len(v)}" for k, v in tail_uniq.items()))
# independent probe (this seat)
for mode in ("default", "ff60"):
    rows = []
    for rep in (1, 2, 3):
        f = V / "probes" / "nminus1" / f"{mode}.rep{rep}.out"
        if f.is_file():
            for ln in f.read_text().splitlines():
                if ln.startswith("R93V nminus1"):
                    rows.append(ln)
    p(f"  independent probe {mode}: {len(rows)} reps")
    if rows:
        m = re.search(r"pos=\[([^\]]*)\] deltas=\[([^\]]*)\]", rows[0])
        pos = [float(x) for x in m.group(1).split(",")]
        dl = [float(x) for x in m.group(2).split(",")]
        pred = [0.0]
        for k in range(2, 7):
            pred.append(100.0 * sum(dl[1:k]))
        dev = max(abs(a - b) for a, b in zip(pos, pred))
        p(f"    pos={pos}")
        p(f"    predicted 100*sum(deltas[1..N-1])={pred}")
        p(f"    max deviation={dev:.2e}  (law: N awaits => N-1 applied steps)")

# ------------------------------------------------------------------- L4 deferred
p("")
p("== L4 DEFERRED flush routes ==")
dfr = [ln for _, ln in collect(r"^PASS r93b_anim deferred ")]
p(f"  deferred receipts={len(dfr)}")
pat = {
    "manual_def": r"manual_def=\[after_adv=\[\],next_proc=\[7,8\],second_proc=\[7,8\]\]",
    "manual_def_phys": r"manual_def_phys=\[after_adv=\[\],after_phys=\[7,8\]\]",
    "two_adv": r"two_adv=\[after=\[\],flush=\[7,8\]\]",
    "immediate": r"immediate=\[after_adv=\[7,8\],after_frame=\[7,8\]\]",
}
for name, rx in pat.items():
    n = sum(1 for ln in dfr if re.search(rx, ln))
    p(f"  {name}: {n}/{len(dfr)}")
for mode in ("default", "ff60"):
    f = V / "probes" / "nminus1" / f"{mode}.rep1.out"
    if f.is_file():
        for ln in f.read_text().splitlines():
            if ln.startswith("R93V deferred"):
                p(f"  independent probe {mode}: {ln}")

(V / "probes" / "laws.txt").write_text("\n".join(OUT) + "\n")
print("\n".join(OUT))
sys.exit(0)
