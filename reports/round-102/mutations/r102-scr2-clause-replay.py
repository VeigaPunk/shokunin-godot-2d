#!/usr/bin/env python3
"""Seat R2 (r102): mechanically replay the timeout probe's meta_pass clauses
against stored timeout-verdicts.json artifacts, using the EXACT clause code
from corpus/fixtures/run_battery.py:5375-5387 (r101 commit ac4eb8d4).

Usage: python3 r102-scr2-clause-replay.py <timeout-verdicts.json> [...]
"""
import json
import sys


def clauses(d):
    by = {r["case"]: r for r in d["results"]}
    old, new, hold = by["slow_clean_old_bound"], by["slow_clean_new_bound"], by["hold_open_new_bound"]
    old_rejects = (old["timed_out"] and old["marker_observed"]
                   and old["inner_classification"] is False
                   and old["direct_child_alive_after_cleanup"] is False)
    new_accepts = (not new["timed_out"] and new["actual_exit"] == 0
                   and new["marker_observed"]
                   and new["inner_classification"] is True)
    hold_rejects = (hold["timed_out"] and hold["marker_observed"]
                    and hold["inner_classification"] is False
                    and hold["direct_child_alive_after_cleanup"] is False)
    same_script = all(r["command"][r["command"].index("--script") + 1] == "res://timeout_probe.gd"
                      for r in d["results"])
    same_expected_exit = all(r["expected_exit"] == 0 for r in d["results"])
    meta_pass = old_rejects and new_accepts and hold_rejects and same_script and same_expected_exit
    return {"old_rejects": old_rejects, "new_accepts": new_accepts, "hold_rejects": hold_rejects,
            "same_script": same_script, "same_expected_exit": same_expected_exit,
            "meta_pass": meta_pass}


def main(paths):
    for p in paths:
        d = json.load(open(p))
        c = clauses(d)
        failing = [k for k, v in c.items() if not v]
        verdict_delta = d["verdict"] != ("PASS" if c["meta_pass"] else "FAIL")
        sub = {k: {"timed_out": r["timed_out"], "marker_observed": r["marker_observed"],
                   "inner_classification": r["inner_classification"],
                   "direct_child_alive_after_cleanup": r["direct_child_alive_after_cleanup"],
                   "elapsed_seconds": r.get("elapsed_seconds")}
               for k, r in ((r["case"], r) for r in d["results"])}
        print(json.dumps({"artifact": p, "recorded_verdict": d["verdict"],
                          "replayed_meta_pass": c["meta_pass"], "failing_clauses": failing,
                          "verdict_replay_consistent": not verdict_delta, "arms": sub}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
