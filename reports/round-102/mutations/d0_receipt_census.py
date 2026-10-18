#!/usr/bin/env python3
"""r102-D0: census every tracked timeout-probe receipt, per arm, with its recorded constants.

Reproduces the C2 evidence table: the old-bound arm's marker_observed over the whole tracked
history, the bound-pinned old-arm elapsed, and the passing new arm's elapsed as the honest
host-cost thermometer.  Read-only.
"""
import datetime, glob, json, os


def main():
    rows = []
    for path in sorted(glob.glob("corpus/live/**/timeout-verdicts.json", recursive=True)):
        payload = json.load(open(path))
        by = {r.get("case"): r for r in payload.get("results", [])}
        old, new, hold = (by.get("slow_clean_old_bound"), by.get("slow_clean_new_bound"),
                          by.get("hold_open_new_bound"))
        rows.append({
            "run": os.path.basename(os.path.dirname(path)),
            "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M"),
            "verdict": payload.get("verdict"),
            "constants": payload.get("constants"),
            "old_marker": None if old is None else old.get("marker_observed"),
            "old_timed_out": None if old is None else old.get("timed_out"),
            "old_elapsed": None if old is None else old.get("elapsed_seconds"),
            "new_elapsed": None if new is None else new.get("elapsed_seconds"),
            "hold_marker": None if hold is None else hold.get("marker_observed"),
        })
    print(f"{'run':28s} {'mtime':16s} {'verdict':5s} old(mk/to/el)          new_el   constants")
    for r in rows:
        c = r["constants"] or {}
        print(f"{r['run']:28s} {r['mtime']:16s} {str(r['verdict']):5s} "
              f"{str(r['old_marker']):5s}/{str(r['old_timed_out']):5s}/{str(r['old_elapsed']):7s} "
              f"{str(r['new_elapsed']):8s} old={c.get('old_timeout_seconds')} new={c.get('new_timeout_seconds')}")
    with_arm = [r for r in rows if r["old_marker"] is not None]
    print(f"\nreceipts total={len(rows)} with-old-arm={len(with_arm)} "
          f"old_marker_TRUE={sum(1 for r in with_arm if r['old_marker'])} "
          f"old_marker_FALSE={sum(1 for r in with_arm if not r['old_marker'])}")
    print(f"old_elapsed distinct={sorted({r['old_elapsed'] for r in with_arm if r['old_elapsed'] is not None})}")
    print(f"new_elapsed range={min(r['new_elapsed'] for r in with_arm if r['new_elapsed'])}"
          f"..{max(r['new_elapsed'] for r in with_arm if r['new_elapsed'])}")
    consts = [(c.get("old_timeout_seconds"), c.get("new_timeout_seconds"))
              for c in ((r["constants"] or {}) for r in rows)]
    print(f"constants distinct={sorted({p for p in consts if None not in p})} "
          f"receipts_without_constants={sum(1 for p in consts if p == (None, None))}")


if __name__ == "__main__":
    main()
