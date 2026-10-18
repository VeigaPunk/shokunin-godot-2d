#!/usr/bin/env python3
"""r102-D4: timeout-probe predicate auditor + repair patch emitter (analysis only, no edits).

Usage:
  python3 r102-D4-timeout-predicate.py --record <timeout-verdicts.json> [--record ...]
  python3 r102-D4-timeout-predicate.py --self-test
  python3 r102-D4-timeout-predicate.py --emit-patch > r102-D4-timeout-repair.diff

Recomputes run_battery.py probe_timeout's meta conjunction (lines 5375-5387) verbatim
and names the exact failing conjunct per record. Never runs run_battery.py.
"""
import argparse
import json
import sys

# Verbatim from corpus/fixtures/run_battery.py:5375-5387 (probe_timeout meta).
def predicates(results):
    old_positive, new_positive, hold_open = results[0], results[1], results[2]
    expected_exit = 0
    old_rejects = (old_positive["timed_out"] and old_positive["marker_observed"]
                   and old_positive["inner_classification"] is False
                   and old_positive["direct_child_alive_after_cleanup"] is False)
    new_accepts = (not new_positive["timed_out"] and new_positive["actual_exit"] == expected_exit
                   and new_positive["marker_observed"]
                   and new_positive["inner_classification"] is True)
    hold_rejects = (hold_open["timed_out"] and hold_open["marker_observed"]
                    and hold_open["inner_classification"] is False
                    and hold_open["direct_child_alive_after_cleanup"] is False)
    return {"old_rejects": old_rejects, "new_accepts": new_accepts, "hold_rejects": hold_rejects}


def failing_conjuncts(record, kind):
    """kind: 'old' | 'hold' (both share the rejection conjunction shape)."""
    want = {"timed_out": True, "marker_observed": True,
            "inner_classification": False, "direct_child_alive_after_cleanup": False}
    out = []
    for field, want_val in want.items():
        got = record.get(field)
        if got is not want_val and got != want_val:
            out.append(f"{field}: want {want_val!r} got {got!r}")
    return out


def audit(path):
    data = json.load(open(path))
    results = data["results"]
    pred = predicates(results)
    print(f"record: {path}")
    print(f"  verdict={data['verdict']} mode={data['mode']}")
    for r in results:
        print(f"  arm {r['case']}: timed_out={r['timed_out']} marker={r['marker_observed']} "
              f"class={r['inner_classification']} alive_after={r['direct_child_alive_after_cleanup']} "
              f"elapsed={r.get('elapsed_seconds')}")
        print(f"    raw_stdout={r.get('raw_stdout')!r}")
    print(f"  predicates: {pred}  meta_pass={all(pred.values())}")
    for name, kind in (("slow_clean_old_bound", "old"), ("hold_open_new_bound", "hold")):
        rec = next((r for r in results if r["case"] == name), None)
        if rec is None:
            continue
        bad = failing_conjuncts(rec, kind)
        print(f"  {name}: failing conjuncts = {bad if bad else 'none (arm green)'}")
    return 0


def self_test():
    green = {"timed_out": True, "marker_observed": True, "inner_classification": False,
             "direct_child_alive_after_cleanup": False}
    red_marker = dict(green, marker_observed=False)
    assert failing_conjuncts(green, "old") == []
    assert failing_conjuncts(red_marker, "old") == ["marker_observed: want True got False"]
    # Envelope clause (proposed): marker requirable only when the measured
    # startup floor (a no-arg clean run) finishes inside the old bound.
    def old_rejects_envelope(old, baseline_elapsed, old_bound):
        return (old["timed_out"] and old["inner_classification"] is False
                and old["direct_child_alive_after_cleanup"] is False
                and (old["marker_observed"] or baseline_elapsed >= old_bound))
    assert old_rejects_envelope(red_marker, 0.88, 0.75) is True     # slow host: marker not required
    assert old_rejects_envelope(red_marker, 0.40, 0.75) is False    # fast host: marker required
    assert old_rejects_envelope(green, 0.40, 0.75) is True
    print("self-test OK")
    return 0


PATCH = '''diff --git a/corpus/fixtures/run_battery.py b/corpus/fixtures/run_battery.py
--- a/corpus/fixtures/run_battery.py
+++ b/corpus/fixtures/run_battery.py
@@ -5369,18 +5369,31 @@
             return record
 
         old_positive = bounded_run("slow_clean_old_bound", ["--delay-clean"], old_timeout_seconds)
         new_positive = bounded_run("slow_clean_new_bound", ["--delay-clean"], timeout_seconds)
         hold_open = bounded_run("hold_open_new_bound", ["--hold-open"], timeout_seconds)
-        probe_results = [old_positive, new_positive, hold_open]
-        old_rejects = (old_positive["timed_out"] and old_positive["marker_observed"]
-                       and old_positive["inner_classification"] is False
-                       and old_positive["direct_child_alive_after_cleanup"] is False)
+        # r102-D4: the 0.75s bound and the marker print both sit inside the
+        # engine-startup latency band (measured 0.63-0.80s, loadavg 8-18;
+        # r101 runs at loadavg ~40 measured startup > bound). The marker
+        # clause is host-latency-conditional, so gate it on an in-run
+        # measurement of the startup floor instead of on a fixed constant.
+        clean_baseline = bounded_run("clean_baseline", [], timeout_seconds)
+        probe_results = [old_positive, new_positive, hold_open, clean_baseline]
+        marker_requirable = clean_baseline["elapsed_seconds"] < old_timeout_seconds
+        old_rejects = (old_positive["timed_out"]
+                       and old_positive["inner_classification"] is False
+                       and old_positive["direct_child_alive_after_cleanup"] is False
+                       and (old_positive["marker_observed"] or not marker_requirable))
         new_accepts = (not new_positive["timed_out"] and new_positive["actual_exit"] == expected_exit
                        and new_positive["marker_observed"]
                        and new_positive["inner_classification"] is True)
@@ -5388,6 +5401,9 @@
                          "constants": {"old_timeout_seconds": old_timeout_seconds,
                                        "measured_delay_seconds": measured_delay_seconds,
                                        "new_timeout_seconds": timeout_seconds,
                                        "cleanup_seconds": cleanup_seconds},
+                         "startup_floor_seconds": clean_baseline["elapsed_seconds"],
+                         "marker_requirable": marker_requirable,
+                         "old_marker_within_bound": old_positive["marker_observed"],
                          "bounded_claim": "controlled delayed clean startup is rejected by old bound and accepted by new bound; hold-open marker still times out; direct child cleanup only",
                          "verdict": "PASS" if meta_pass else "FAIL"}
'''

ALT_PATCH = '''# Alternative (cheapest, loses the started-script nuance on purpose):
-        old_rejects = (old_positive["timed_out"] and old_positive["marker_observed"]
+        old_rejects = (old_positive["timed_out"]
                        and old_positive["inner_classification"] is False
                        and old_positive["direct_child_alive_after_cleanup"] is False)
# `marker_observed` stays in the arm record, reported but not gated.

# Alternative C (recalibrate the pair; fragile under load spikes):
-        old_timeout_seconds = 0.75
+        old_timeout_seconds = 1.0
# measured startup band 0.63-0.88s leaves only ~120-370ms margin; rejected as
# less robust than the self-calibrating envelope above.
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="append", default=[])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--emit-patch", action="store_true")
    ap.add_argument("--emit-alt", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.emit_patch:
        sys.stdout.write(PATCH)
        return 0
    if args.emit_alt:
        sys.stdout.write(ALT_PATCH)
        return 0
    if not args.record:
        ap.print_help()
        return 2
    for path in args.record:
        audit(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
