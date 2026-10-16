#!/usr/bin/env python3
"""r94 scribe — cross-run comparison of the two committed-byte battery runs.

Compares per-row verdicts and outputs between two `verdicts.json` files
(default: scribe battery-runs vs battery-committed), classifies each row as
identical / tail-only / head-diff / verdict-flip, and reports r94-row status.

Writes corpus/live/r94-scribe/audit/compare_runs.json.
"""
import json
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/game-dev-2d-shokunin")  # unused placeholder
REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r94-scribe/audit"


def load(p):
    return {r["case"]: r for r in json.loads(Path(p).read_text())["results"]}


def main(a, b):
    ra, rb = load(a), load(b)
    assert set(ra) == set(rb), (len(ra), len(rb))
    cls = {"identical": [], "tail_only": [], "head_diff": [], "verdict_flip": []}
    for case in sorted(ra):
        x, y = ra[case], rb[case]
        ox, oy = "\n".join(x.get("output") or []), "\n".join(y.get("output") or [])
        if x["verdict"] != y["verdict"]:
            cls["verdict_flip"].append({"case": case, "a": x["verdict"], "b": y["verdict"]})
        elif ox == oy:
            cls["identical"].append(case)
        else:
            sx, sy = ox.split(" | ", 1), oy.split(" | ", 1)
            if len(sx) == 2 and len(sy) == 2 and sx[0] == sy[0]:
                cls["tail_only"].append(case)
            else:
                cls["head_diff"].append(case)
    out = {k: (v if k != "identical" else len(v)) for k, v in cls.items()}
    out["n_rows"] = len(ra)
    out["r94_rows"] = {c: ("identical" if c in cls["identical"] else
                           "tail_only" if c in cls["tail_only"] else
                           "head_diff" if c in cls["head_diff"] else "verdict_flip")
                       for c in sorted(ra) if c.startswith("r94_")}
    (OUT / "compare_runs.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: (v if not isinstance(v, list) else v[:12]) for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else None
    b = sys.argv[2] if len(sys.argv) > 2 else None
    if not a:
        a = sorted((REPO / "corpus/live/r94-scribe/battery-runs").glob("*/verdicts.json"))[-1]
    if not b:
        b = sorted((REPO / "corpus/live/r94-scribe/battery-committed").glob("*/verdicts.json"))[-1]
    main(a, b)
