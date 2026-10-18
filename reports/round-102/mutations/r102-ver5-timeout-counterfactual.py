#!/usr/bin/env python3
"""V5 envelope counterfactual: slow_clean_old_bound arm at raised bounds (1.0 / 1.5), x5 each,
using the EXACT driver flow from replica.bounded_run. Proves the minimal repair direction."""
import json, sys
sys.path.insert(0, "/var/tmp/r102-ver5")
from replica import bounded_run

def main():
    out = {"runs": []}
    for bound in (1.0, 1.5):
        hits = 0
        for rep in range(1, 6):
            r = bounded_run("slow_clean_old_bound_%s" % bound, ["--delay-clean"], bound)
            r["rep"] = rep
            r["loadavg_after"] = open("/proc/loadavg").read().split()[0:3]
            out["runs"].append(r)
            hits += 1 if r["marker_observed"] else 0
            print("bound=%s rep%d timed_out=%s marker=%s inner=%s rc=%s elapsed=%s" %
                  (bound, rep, r["timed_out"], r["marker_observed"], r["inner_classification"],
                   r["actual_exit"], r["elapsed_seconds"]))
        out["hit_rate_%s" % bound] = "%d/5" % hits
        # driver-shaped old_rejects for this bound
        rejects = all(r["timed_out"] and r["marker_observed"] and r["inner_classification"] is False
                      and r["direct_child_alive_after_cleanup"] is False for r in out["runs"][-5:])
        out["old_rejects_%s" % bound] = rejects
        print("bound=%s old_rejects_all5=%s" % (bound, rejects))
    out["loadavg_end"] = open("/proc/loadavg").read().split()[0:3]
    with open("/var/tmp/r102-ver5/logs/counterfactual.json", "w") as f:
        json.dump(out, f, indent=2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
