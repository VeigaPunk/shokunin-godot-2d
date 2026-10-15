#!/usr/bin/env python3
"""r91-scribe: re-derive the author's fresh-arm claims from
corpus/live/r91-author/fresh-reps (3 reps x 11 arms)."""
import ast, json, re
from pathlib import Path
ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FR = ROOT / "corpus/live/r91-author/fresh-reps"
TAIL = ["settle", "iter", "ladder", "first_reach", "first_reach_sync", "walk_steps",
        "reached_at", "first_reachable", "iter_b", "link_iter", "gate",
        "chg_iter_same", "chg_iter_settled", "dis_same", "fwd_disabled_same",
        "seq_a", "seq_b", "vel_a", "vel_b", "sum_max", "settle_a", "settle_b"]
RX = {t: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(t) + "=") for t in TAIL}
bat = ast.parse((ROOT / "corpus/fixtures/run_battery.py").read_text())
cases = next(n for n in bat.body if isinstance(n, ast.Assign)
             and any(getattr(t, "id", "") == "CASES" for t in n.targets)).value.elts
pins = {e.elts[0].value[len("nav_lattice_"):]: e.elts[4].value
        for e in cases if e.elts[0].value.startswith("nav_lattice_")}

out = {}
for arm, pin in pins.items():
    reps = sorted(FR.glob(f"{arm}.rep*.out"))
    rec = {"reps": len(reps), "sig_in_all": None, "rep_out_uniq": None,
           "err_bytes": [], "rc": [], "diff_region_all_tail": None,
           "tail_only": None, "tail_fields_seen": sorted(
               {t for r in reps for t, rx in RX.items() if rx.search(r.read_text())})}
    texts = [r.read_text() for r in reps]
    rec["rep_out_uniq"] = len(set(texts))
    lines = [[l for l in t.splitlines() if l.strip()] for t in texts]
    rec["sig_in_all"] = all(any(l.startswith(pin) for l in ls) for ls in lines)
    rec["rc"] = [ (FR / f"{arm}.rep{i+2}.rc").read_text().strip() for i in range(len(reps)) ]
    rec["err_bytes"] = [ len((FR / f"{arm}.rep{i+2}.err").read_text()) for i in range(len(reps)) ]
    # rep-to-rep diff: is every difference strictly after the pin?
    all_tail = True
    for a in range(len(texts)):
        for b in range(a + 1, len(texts)):
            la = [l for l in lines[a] if l.startswith(pin)]
            lb = [l for l in lines[b] if l.startswith(pin)]
            if not la or not lb:
                all_tail = False
                continue
            ta, tb = la[0][len(pin):], lb[0][len(pin):]
            if ta != tb and not (ta.strip() or tb.strip()):
                all_tail = False
    rec["diff_region_all_tail"] = all_tail
    rec["pin_len"] = len(pin)
    rec["emitted_lens"] = [len([l for l in ls if l.startswith(pin)][0]) if any(l.startswith(pin) for l in ls) else None for ls in lines]
    out[arm] = rec

print(json.dumps(out, indent=1))
print("\nSUMMARY: sig_in_all =", all(v["sig_in_all"] for v in out.values()),
      "| all diffs tail-only =", all(v["diff_region_all_tail"] for v in out.values()),
      "| avoid out_uniq =", out["avoid"]["rep_out_uniq"])
(ROOT / "corpus/live/r91-scribe/audit/author_fresh.json").write_text(json.dumps(out, indent=1))
