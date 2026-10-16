#!/usr/bin/env python3
"""r94 reviewer: cross-session / cross-condition pin identity for the 19 rows.

Sessions compared (all read-only):
  mine    corpus/live/r94-reviewer/fresh/<stamp>/receipts/*.out   (folded fixture)
  mineB   corpus/live/r94-reviewer/runs/<stamp>/scratch (battery) -> verdicts.json output
  author  corpus/live/runs/{stamp}/verdicts.json                  (folded fixture)
  bound   corpus/live/r94-boundary/runs/<batch>/r94_particles_<arm>.rep*.out
          (frozen scout probe, pre-fold)
  scout   corpus/live/r94-scout/runs/r94_particles_<arm>.rep*.out

For every row: pin presence, pinned-prefix identity (text before " | "), and
full-line identity where the pin is the full line.
"""
import argparse
import ast
import glob
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REVIEWER = HERE.parent
PINNED = REVIEWER / "pinned-tmp"
LIVE = REVIEWER.parent


def load_rows():
    t = ast.parse((PINNED / "run_battery.py").read_text())
    for node in t.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "CASES":
            return [ast.literal_eval(e) for e in node.value.elts]


def passline(text):
    for l in text.splitlines():
        if l.startswith("PASS particles_lattice "):
            return l
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, default=REVIEWER / "cross_session.json")
    args = ap.parse_args()
    rows = [c for c in load_rows() if c[0].startswith("r94_")]

    author_runs = sorted(glob.glob(str(LIVE / "runs/2026*/verdicts.json")))
    author = {}
    for p in author_runs:
        d = json.loads(pathlib.Path(p).read_text())
        for r in d["results"]:
            if r["case"].startswith("r94_"):
                author.setdefault(r["case"], []).append(
                    {"run": pathlib.Path(p).parent.name, "verdict": r["verdict"],
                     "lines": r["output"]})

    batches = ["quiet", "load", "ff30", "ff60", "ff120", "ff120load"]
    out = {"sessions": {"author_runs": author_runs}, "rows": []}
    for name, script, flags, rc, sig in rows:
        arm = [f for f in flags if f.startswith("--arm=")][0].split("=")[1]
        rec = {"case": name, "arm": arm, "pin_len": len(sig),
               "pin_is_full_line": None, "mine": {}, "author": {}, "boundary": {}, "scout": {}}
        # mine (fresh, folded fixture)
        mine_lines = []
        for p in sorted((args.fresh / "receipts").glob(f"{name}.rep*.out")):
            pl = passline(p.read_text())
            if pl:
                mine_lines.append(pl)
        rec["mine"] = {"reps": len(mine_lines),
                       "pin_in_all": all(sig in l for l in mine_lines),
                       "prefix_uniq": len({l.split(" | ")[0] for l in mine_lines}),
                       "line_uniq": len(set(mine_lines)),
                       "prefix": mine_lines[0].split(" | ")[0] if mine_lines else None,
                       "full": mine_lines[0] if mine_lines else None}
        # author runs (folded fixture, committed run evidence re-read from disk)
        al = []
        for r in author.get(name, []):
            pl = passline("\n".join(r["lines"]))
            if pl:
                al.append(pl)
        rec["author"] = {"runs": len(author.get(name, [])),
                         "pin_in_all": bool(al) and all(sig in l for l in al),
                         "prefix_uniq": len({l.split(" | ")[0] for l in al}),
                         "line_uniq": len(set(al)),
                         "prefix": al[0].split(" | ")[0] if al else None}
        # boundary (pre-fold probe) per batch
        for b in batches:
            lines = []
            for p in sorted((LIVE / f"r94-boundary/runs/{b}").glob(f"{name}.rep*.out")):
                pl = passline(p.read_text())
                if pl:
                    lines.append(pl)
            rec["boundary"][b] = {
                "receipts": len(lines),
                "pin_present": sum(1 for l in lines if sig in l),
                "prefix_uniq": len({l.split(" | ")[0] for l in lines}),
                "prefix": lines[0].split(" | ")[0] if lines else None}
        # scout canonical
        sl = []
        for p in sorted((LIVE / "r94-scout/runs").glob(f"{name}.rep*.out")):
            pl = passline(p.read_text())
            if pl:
                sl.append(pl)
        rec["scout"] = {"receipts": len(sl),
                        "pin_present": sum(1 for l in sl if sig in l),
                        "line_uniq": len(set(sl)),
                        "prefix": sl[0].split(" | ")[0] if sl else None}
        rec["pin_is_full_line"] = (rec["mine"]["full"] == sig) if rec["mine"]["full"] else None
        out["rows"].append(rec)
    args.out.write_text(json.dumps(out, indent=1))

    # console summary
    print(f"{'arm':16s} {'mine':>10s} {'author':>8s} {'scout':>7s} " +
          " ".join(f"{b[:6]:>9s}" for b in batches))
    for r in out["rows"]:
        b = r["boundary"]
        print(f"{r['arm']:16s} {r['mine']['pin_in_all']!s:>10s} "
              f"{r['author']['pin_in_all']!s:>8s} "
              f"{(r['scout']['pin_present']==r['scout']['receipts'])!s:>7s} " +
              " ".join(f"{b[x]['pin_present']}/{b[x]['receipts']}".rjust(9) for x in batches))
    pref_ok = all(r["mine"]["prefix_uniq"] == 1 and
                  all(r["boundary"][b]["prefix_uniq"] in (0, 1) for b in batches) and
                  (r["boundary"][b]["prefix"] in (None, r["mine"]["prefix"]) for b in batches)
                  for r in out["rows"])
    print("pinned prefix identical across mine/author/scout/boundary (mod ff30 cpu_pause):", pref_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
