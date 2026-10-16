#!/usr/bin/env python3
"""r93-reviewer claim verification from receipts (production classifier).

usage: claim_checks.py --mine <dir> --reps 5 --author <dir> --json out.json

Verifies, from receipt bytes only (no fixture re-derivation):
  C1  overshoot: runtime BACK<start and SPRING>end, no clamp on the static path
  C2  N-1 await law: x1=0.0; frame lattice + physics lattice pinned tokens
  C3  crossfade w_i=(i-1)/(N-1) at 3 step granularities (numeric re-derivation)
  C4  DEFERRED flush: process-frame + physics-frame routes, two-advance queue, IMMEDIATE
  C5  manual clock invariance + non-vacuity control
  C6  negative controls present in the pinned rows
  C7  production classify PASS for every row in every rep (mine + author)
  C8  rep-level byte stability: full-line arms out_uniq=1; clause arms clause-stable
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ufo_r93


def parse_kv(line, key):
    """Extract `key=[...]` (bracket-balanced) or `key=token` from a PASS line."""
    i = line.find(key + "=")
    if i < 0:
        return None
    j = i + len(key) + 1
    if j < len(line) and line[j] == "[":
        depth = 0
        for k in range(j, len(line)):
            if line[k] == "[":
                depth += 1
            elif line[k] == "]":
                depth -= 1
                if depth == 0:
                    return line[j:k + 1]
    k = j
    while k < len(line) and line[k] not in ", ":
        k += 1
    return line[j:k]


def floats(bracket):
    return [float(x) for x in bracket.strip("[]").split(",") if x.strip()]


def kv_floats(bracket):
    """`[a=1.0,b=2.0]` -> {"a": 1.0, "b": 2.0}; `[]` -> {}."""
    out = {}
    for tok in bracket.strip("[]").split(","):
        tok = tok.strip()
        if not tok:
            continue
        k, _, v = tok.partition("=")
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mine", type=pathlib.Path, required=True)
    ap.add_argument("--author", type=pathlib.Path, default=None)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--json", type=pathlib.Path, default=None)
    args = ap.parse_args()
    C, rows = ufo_r93.load_rows()
    arm_case = {}
    for case, row in rows.items():
        arm = [f.removeprefix("--arm=") for f in row["flags"] if f.startswith("--arm=")][0]
        arm_case[arm] = case

    res = {"classify": {}, "stability": {}, "laws": {}}

    # ---------- C7 classify all receipts (mine + author)
    for label, d, reps in (("mine", args.mine, args.reps),
                           ("author", args.author, 3)):
        if not d:
            continue
        verdicts = {}
        for case, row in sorted(rows.items()):
            arm = [f.removeprefix("--arm=") for f in row["flags"] if f.startswith("--arm=")][0]
            vs = []
            for rep in range(1, reps + 1):
                f = d / f"{arm}.rep{rep}.out"
                if not f.is_file():
                    continue
                out = f.read_text()
                err = (d / f"{arm}.rep{rep}.err").read_text()
                rc = int((d / f"{arm}.rep{rep}.rc").read_text().strip())
                vs.append(ufo_r93.classify_row(C, case, out, err, rc))
            verdicts[case] = vs
        res["classify"][label] = verdicts

    # ---------- C8 stability (mine) — per ROW (arms are shared by several rows)
    stab = {}
    for case, row in sorted(rows.items()):
        arm = [f.removeprefix("--arm=") for f in row["flags"] if f.startswith("--arm=")][0]
        outs, errs, rcs = [], [], []
        for rep in range(1, args.reps + 1):
            f = args.mine / f"{arm}.rep{rep}.out"
            if f.is_file():
                outs.append(f.read_text())
                errs.append((args.mine / f"{arm}.rep{rep}.err").read_text())
                rcs.append((args.mine / f"{arm}.rep{rep}.rc").read_text())
        sigs = ufo_r93.sigs_of(rows[case])
        clause_uniq = len(set(tuple(s in o for s in sigs) for o in outs))
        stab[case] = {"arm": arm, "out_uniq": len(set(outs)), "err_uniq": len(set(errs)),
                      "rc_uniq": len(set(rcs)), "clause_sig_uniq": clause_uniq}
    res["stability"]["mine"] = stab

    # ---------- claim parsing from mine rep1 (values) + all reps (stability)
    def line_of(arm, rep=1):
        return (args.mine / f"{arm}.rep{rep}.out").read_text()

    laws = {}

    # C1 overshoot
    ov = {}
    for rep in range(1, args.reps + 1):
        line = line_of("purity", rep)
        ov[rep] = {"overshoot": parse_kv(line, "overshoot"),
                   "overshoot2": parse_kv(line, "overshoot2"),
                   "clamp": parse_kv(line, "clamp")}
    b025 = parse_kv(line_of("purity"), "overshoot")
    o1 = kv_floats(parse_kv(line_of("purity"), "overshoot"))
    o2 = kv_floats(parse_kv(line_of("purity"), "overshoot2"))
    laws["C1_overshoot"] = {
        "pinned_tokens": sorted({v for r in ov.values() for v in r.values()}),
        "back025": o1["back025"], "back050": o1["back050"],
        "spr050": o2["spr050"], "spr100": o2["spr100"], "ela025": o2["ela025"],
        "back025_below_start_1.0": o1["back025"] < 1.0,
        "spr050_above_end_10.0": o2["spr050"] > 10.0,
        "spr100_exact_end": o2["spr100"] == 10.0,
        "ela025_below_end": o2["ela025"] < 10.0,
        "clamp_no_clamp": parse_kv(line_of("purity"), "clamp"),
        "token_stable_all_reps": len({tuple(sorted(r.values())) for r in ov.values()}) == 1,
    }

    # C2 N-1 await law + frame lattice
    fr = {}
    for rep in range(1, args.reps + 1):
        line = line_of("frame", rep)
        fr[rep] = {"idle": parse_kv(line, "idle"), "mixer": parse_kv(line, "mixer_applied_10"),
                   "phys": parse_kv(line, "phys"), "pos10": parse_kv(line, "pos10"),
                   "phys_delta": parse_kv(line, "phys_delta")}
    laws["C2_await"] = {
        "x1_zero_all_reps": all(kv_floats(fr[r]["idle"])["x1"] == 0.0 for r in fr),
        "idle_pin_substring_stable": all("idle=[x1=0.0" in line_of("frame", r) for r in fr),
        "mixer10_stable": len({fr[r]["mixer"] for r in fr}) == 1,
        "phys_lattice_stable": len({fr[r]["phys"] for r in fr}) == 1,
        "phys_delta_stable": len({fr[r]["phys_delta"] for r in fr}) == 1,
        "rep1": fr[1],
    }

    # C3 crossfade weight law at 3 granularities
    def law_ok(vals, N):
        """Finished-source lattice: value_i = 100 + 400*w_i, w_i = (i-1)/(N-1)."""
        if len(vals) != N:
            return False, f"len={len(vals)}"
        for i, v in enumerate(vals, start=1):
            w = min(1.0, (i - 1) / (N - 1))
            exp = 100.0 + 400.0 * w
            if abs(v - exp) > 1e-3:
                return False, f"i={i} got={v} exp={exp}"
        return True, "ok"

    def running_ok(vals, N):
        """Running-source lattice: value_i = w_i*500 + (1-w_i)*a(t_i), a(t)=100t,
        t_i = 0.5 + i*(1/N)."""
        if len(vals) != N:
            return False, f"len={len(vals)}"
        for i, v in enumerate(vals, start=1):
            w = min(1.0, (i - 1) / (N - 1))
            t = 0.5 + i * (1.0 / N)
            a = 100.0 * min(t, 1.0)  # source animation holds its last pose past its end
            exp = w * 500.0 + (1.0 - w) * a
            if abs(v - exp) > 1e-3:
                return False, f"i={i} got={v} exp={exp}"
        return True, "ok"
    bl = {}
    for rep in range(1, args.reps + 1):
        line = line_of("animblend", rep)
        bl[rep] = {k: floats(parse_kv(line, k)) for k in
                   ("finished_010", "finished_005", "finished_020", "running_from_50")}
    c3 = {}
    for rep, d in bl.items():
        c3[rep] = {k: (law_ok(v, 10) if k == "finished_010" else
                       law_ok(v, 20) if k == "finished_005" else
                       law_ok(v, 5) if k == "finished_020" else
                       running_ok(v, 10))
                   for k, v in d.items()}
    laws["C3_crossfade"] = {"per_rep": c3,
                            "all_ok": all(ok for d in c3.values() for ok, _ in d.values()),
                            "mid_060_010": bl[1]["finished_010"][5],
                            "mid_060_020": bl[1]["finished_020"][2],
                            "mid_060_005": bl[1]["finished_005"][11],
                            "granularity_distinct": len({bl[1]["finished_010"][5],
                                                         bl[1]["finished_020"][2],
                                                         bl[1]["finished_005"][11]}) == 3}

    # C4 DEFERRED routes
    df = {}
    for rep in range(1, args.reps + 1):
        line = line_of("deferred", rep)
        df[rep] = {k: parse_kv(line, k) for k in
                   ("manual_def", "manual_def_phys", "two_adv", "immediate")}
    laws["C4_deferred"] = {
        "token_stable": len({tuple(sorted(r.values())) for r in df.values()}) == 1,
        "rep1": df[1],
        "routes": {
            "manual_no_call_in_advance": "after_adv=[]" in df[1]["manual_def"],
            "process_frame_flush": "next_proc=[7,8]" in df[1]["manual_def"],
            "physics_frame_flush": "after_phys=[7,8]" in df[1]["manual_def_phys"],
            "two_adv_queue": "after=[]" in df[1]["two_adv"] and "flush=[7,8]" in df[1]["two_adv"],
            "immediate_in_advance": "after_adv=[7,8]" in df[1]["immediate"],
        },
    }

    # C5 manual clock
    mc = {}
    for rep in range(1, args.reps + 1):
        line = line_of("manual_inv", rep)
        mc[rep] = {k: parse_kv(line, k) for k in ("paused", "manual", "inv", "step_exact", "unpaused_moved")}
    laws["C5_manual"] = {
        "token_stable": len({tuple(sorted(r.values())) for r in mc.values()}) == 1,
        "rep1": mc[1],
        "inv_all_true": mc[1]["inv"] == "[paused_proc=true,paused_phys=true,manual_proc=true,manual_phys=true]",
        "step_exact_all_true": mc[1]["step_exact"] == "[paused025=true,paused_done=true,manual025=true,manual_done=true]",
        "unpaused_moved": mc[1]["unpaused_moved"] == "true",
    }

    # C6 negative controls present in pinned rows
    ctrl = {}
    for rep in range(1, args.reps + 1):
        an = line_of("animmethod", rep)
        aw = line_of("animseek", rep)
        ch = line_of("tweenchain", rep)
        tp = line_of("tweenproc", rep)
        ctrl[rep] = {
            "deferred_adv_empty": parse_kv(an, "deferred_adv") == "[]",
            "disabled_track_empty": parse_kv(an, "disabled_track") == "[]",
            "manual_frames_zero": parse_kv(aw, "manual_frames") == "[0.0,0.0]",
            "at_play_pre_pose": parse_kv(aw, "at_play").startswith("[7.0,true,0.0"),
            "kill_immediate": "kill=[before=[true,false],after=[false,false]]" in ch,
            "node_free_lazy": "after_frame=[false,true]" in ch,
            "phys_manual_step": parse_kv(tp, "phys_manual") == "[before=1.0,after_step025=2.0]",
            "deltas_tokens": parse_kv(line_of("purity", rep), "deltas"),
            "accum1000": parse_kv(line_of("purity", rep), "accum1000"),
        }
    laws["C6_controls"] = {
        "all_present_all_reps": all(all(v for k, v in c.items()
                                        if k not in ("deltas_tokens", "accum1000"))
                                    for c in ctrl.values()),
        "rep1": ctrl[1],
    }

    res["laws"] = laws

    # ---------- C9 cross-session identity: my reps vs the committed author reps
    cross = {}
    for case, row in sorted(rows.items()):
        arm = [f.removeprefix("--arm=") for f in row["flags"] if f.startswith("--arm=")][0]
        sigs = ufo_r93.sigs_of(row)
        mine, auth = [], []
        for rep in range(1, args.reps + 1):
            f = args.mine / f"{arm}.rep{rep}.out"
            if f.is_file():
                mine.append(f.read_text())
        for rep in range(1, 4):
            stem = row['script'][:-3] if row['script'].endswith('.gd') else row['script']
            for cand in ((args.author / f"{stem}.{arm}.rep{rep}.out"),
                         (args.author / f"{arm}.rep{rep}.out")):
                if args.author and cand.is_file():
                    auth.append(cand.read_text())
                    break
        same_pins = all(any(s in o for s in sigs) for o in mine + auth)
        line_mine = sorted({l for o in mine for l in o.splitlines() if l.startswith("PASS ")})
        line_auth = sorted({l for o in auth for l in o.splitlines() if l.startswith("PASS ")})
        # a pin is a FULL-LINE pin iff it covers the emitted PASS line exactly
        # (tail length 0 in every receipt); otherwise it is a prefix/substring pin.
        tails = []
        for o in mine + auth:
            pl = next((l for l in o.splitlines() if l.startswith("PASS ")), None)
            if pl is None:
                tails.append(None); continue
            hit = next((s for s in sigs if s in o), None)
            tails.append(None if hit is None else len(pl) - len(hit))
        full_line = bool(tails) and all(t == 0 for t in tails)
        cross[case] = {"arm": arm, "full_line_pin": full_line, "tails": sorted(set(tails)),
                       "pins_present_in_all_mine_and_author": same_pins,
                       "pass_lines_identical_across_sessions": line_mine == line_auth if full_line else None,
                       "mine_line_uniq": len(line_mine), "author_line_uniq": len(line_auth)}
    res["cross_session"] = cross

    # ---------- C10 static vs runtime (claim probe receipts)
    stat = pathlib.Path(__file__).resolve().parent.parent / "claim/static2.out"
    c10 = {"static_file": str(stat), "exists": stat.exists()}
    if stat.exists():
        sline = [l for l in stat.read_text().splitlines() if l.startswith("PASS r93r_static ")][0]
        raw = {}
        for tok in sline[len("PASS r93r_static "):].split(","):
            k, _, v = tok.partition("=")
            raw[k] = v
        runtime = {"back025": "0.10286344587803", "back050": "5.5",
                   "spr050": "10.510157585144", "spr100": "10.0",
                   "ela025": "9.11611652374268"}
        c10["static"] = raw
        c10["runtime"] = runtime
        c10["runtime_vs_static"] = {
            "back025_exact": raw.get("back_io_025_1to10") == runtime["back025"],
            "back050_exact": raw.get("back_io_050_1to10") == runtime["back050"],
            "spr100_exact": raw.get("spr_out_100_0to10") == runtime["spr100"],
            "spr050_absdiff": abs(float(raw["spr_out_050_0to10"]) - float(runtime["spr050"])),
            "ela025_absdiff": abs(float(raw["ela_out_025_0to10"]) - float(runtime["ela025"])),
            "clamp_static": [raw.get("lin_neg_050"), raw.get("lin_over_150")],
        }
    res["static_vs_runtime"] = c10
    print(json.dumps(res, indent=1, default=str))
    if args.json:
        args.json.write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
