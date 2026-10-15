#!/usr/bin/env python3
"""r91-scribe: verify the landed nav pins against FRESH receipts from this seat.

For every nav_lattice_* CASES row:
  * the pinned literal must be a PREFIX of the arm's emitted line (pinned block
    first, diagnostic tail last);
  * no scheduler/race tail token may appear inside the pinned prefix;
  * exactly one PASS line (or the one teardown marker) per arm;
  * report the tail tokens that actually follow the pin (fold evidence).
"""
import ast, json, re, sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FRESH = ROOT / "corpus/live/r91-scribe/fresh"
TAIL = ["settle", "iter", "ladder", "first_reach", "first_reach_sync",
        "walk_steps", "reached_at", "first_reachable", "iter_b", "link_iter",
        "gate", "chg_iter_same", "chg_iter_settled", "dis_same",
        "fwd_disabled_same", "seq_a", "seq_b", "vel_a", "vel_b", "sum_max",
        "settle_a", "settle_b"]
TAIL_RE = {t: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(t) + "=") for t in TAIL}

bat = ast.parse((ROOT / "corpus/fixtures/run_battery.py").read_text())
cases = next(n for n in bat.body if isinstance(n, ast.Assign)
             and any(getattr(t, "id", "") == "CASES" for t in n.targets)).value.elts
nav = [(e.elts[0].value, ast.literal_eval(e.elts[3]), e.elts[4].value)
       for e in cases if e.elts[0].value.startswith("nav_lattice_")]

rows = []
for name, rc, sig in nav:
    arm = name[len("nav_lattice_"):]
    out = (FRESH / f"{arm}.out").read_text()
    err = (FRESH / f"{arm}.err").read_text()
    real_rc = int((FRESH / f"{arm}.rc").read_text().strip())
    lines = [l for l in out.splitlines() if l.strip()]
    pass_lines = [l for l in lines if l.startswith("PASS ")]
    hit = [l for l in lines if l.startswith(sig)]
    tail_tokens_in_pin = sorted(t for t, rx in TAIL_RE.items() if rx.search(sig))
    tail_tokens_after = sorted(t for t, rx in TAIL_RE.items()
                               if hit and rx.search(hit[0][len(sig):]))
    rows.append({
        "case": name, "arm": arm, "expected_rc": rc,
        "shell_rc": real_rc, "expected_shell_rc": 128 + (-rc) if rc < 0 else rc,
        "pin_is_prefix_of_emitted": bool(hit),
        "emitted_line_len": len(hit[0]) if hit else None,
        "pin_len": len(sig), "tail_len": (len(hit[0]) - len(sig)) if hit else None,
        "tail_tokens_inside_pin": tail_tokens_in_pin,
        "tail_tokens_after_pin": tail_tokens_after,
        "pass_lines": len(pass_lines), "stale_lines": len([l for l in lines if l.startswith("STALE ")]),
        "stderr_bytes": len(err),
    })
print(json.dumps(rows, indent=1))
(ROOT / "corpus/live/r91-scribe/audit/fold_check.json").write_text(json.dumps(rows, indent=1))
bad = [r for r in rows if not r["pin_is_prefix_of_emitted"]
       or r["tail_tokens_inside_pin"]
       or r["shell_rc"] != r["expected_shell_rc"]
       or (r["case"] != "nav_lattice_teardown_crash" and r["pass_lines"] != 1)]
print("\nVIOLATIONS:", len(bad))
for r in bad:
    print(" ", r["case"], "prefix", r["pin_is_prefix_of_emitted"], "inside", r["tail_tokens_inside_pin"],
          "rc", r["shell_rc"], "vs", r["expected_shell_rc"], "pass_lines", r["pass_lines"])
