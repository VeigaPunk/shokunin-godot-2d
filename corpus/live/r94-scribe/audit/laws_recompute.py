#!/usr/bin/env python3
"""r94 scribe law re-derivation from raw receipts.

Every value below is parsed out of receipt text on disk (scout canonical+loadtest,
boundary matrix, author battery rows, scribe fresh arms + battery runs) — nothing is
copied from a dossier. Checks the encoded laws and the fixture's own `_okb` windows
against the measured values.

Writes corpus/live/r94-scribe/audit/laws.json.
"""
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r94-scribe/audit"

# ---- collect PASS lines per arm per source --------------------------------
lines = defaultdict(list)  # arm -> [(source, line)]


def feed(text, source):
    for m in re.finditer(r"^PASS particles_lattice (\w+) .*$", text, re.M):
        arm = m.group(1)
        lines[arm].append((source, m.group(0)))


scout = REPO / "corpus/live/r94-scout"
for f in sorted((scout / "runs").glob("r94_particles_*.out")):
    feed(f.read_text(), "scout-canonical")
for f in sorted((scout / "runs/loadtest").glob("r94_particles_*.out")):
    feed(f.read_text(), "scout-loadtest")
bnd = REPO / "corpus/live/r94-boundary"
for batch in ("quiet", "load", "ff30", "ff60", "ff120", "ff120load", "ab", "reprobe"):
    for f in sorted((bnd / "runs" / batch).glob("*.out")):
        feed(f.read_text(), f"boundary-{batch}")
for stamp in ("20261016T055703426158Z", "20261016T060430025246Z"):
    p = REPO / f"corpus/live/runs/{stamp}/verdicts.json"
    if p.is_file():
        d = json.loads(p.read_text())
        for r in d["results"]:
            if r["case"].startswith("r94_"):
                feed("\n".join(r.get("output") or []), "author-battery")
for mode in ("fresh", "fresh-ff30", "fresh-ff60"):
    for f in sorted((REPO / f"corpus/live/r94-scribe/{mode}").glob("*.out")) if (REPO / f"corpus/live/r94-scribe/{mode}").is_dir() else []:
        feed(f.read_text(), f"scribe-{mode}")
for d in sorted((REPO / "corpus/live/r94-scribe").glob("battery-*/*/verdicts.json")):
    dd = json.loads(d.read_text())
    for r in dd["results"]:
        if r["case"].startswith("r94_"):
            feed("\n".join(r.get("output") or []), f"scribe-battery-{d.parent.name}")

# ---- parse fields ---------------------------------------------------------
NUM = r"-?\d+(?:\.\d+)?"


def tail(line):
    return line.split(" | ", 1)[1] if " | " in line else ""


def field(line, key, bracket=None):
    """first `key=<num>` (optionally inside `[bracket]`)"""
    seg = line
    if bracket is not None:
        m = re.search(re.escape(bracket) + r"\[([^\]]*)\]", line)
        seg = m.group(1) if m else ""
    m = re.search(re.escape(key) + r"=(" + NUM + r")", seg)
    return float(m.group(1)) if m else None


def ints(line, key, bracket=None):
    seg = line
    if bracket is not None:
        m = re.search(re.escape(bracket) + r"\[([^\]]*)\]", line)
        seg = m.group(1) if m else ""
    return [int(float(x)) for x in re.findall(re.escape(key) + r"=(" + NUM + r")", seg)]


def distinct(arm, kind):
    vals = defaultdict(set)
    for src, line in lines[arm]:
        if kind == "full":
            vals["full"].add(line)
        else:
            vals["prefix"].add(line.split(" | ")[0])
    return {k: sorted(v) for k, v in vals.items()}


laws = {}

# 1. lifetime ladder ---------------------------------------------------------
lad = {"l01": [], "l025": [], "l05": [], "l1": []}
for src, line in lines["cpu_lifetime"]:
    for k in lad:
        lad[k] += ints(line, "delta", k)
laws["ladder"] = {
    "measured": {k: sorted(set(v)) for k, v in lad.items()},
    "counts": {k: len(v) for k, v in lad.items()},
    "round_L60": {"l01": round(0.1 * 60), "l025": round(0.25 * 60),
                  "l05": round(0.5 * 60), "l1": round(1.0 * 60)},
    "prefixes": distinct("cpu_lifetime", "prefix"),
}

# 2. expl formula -----------------------------------------------------------
expl = {"e1": [], "e05": [], "e0": []}
for src, line in lines["cpu_expl"]:
    for k in expl:
        expl[k] += ints(line, "delta", k)
laws["expl"] = {
    "measured": {k: sorted(set(v)) for k, v in expl.items()},
    "model_ticks": {"e1": 0.5 * 60,
                    "e05": (0.5 + 0.5 * (1 - 0.5) * 7 / 8) * 60,
                    "e0": (0.5 + 0.5 * 1.0 * 7 / 8) * 60},
}

# 3. speed/preprocess/ff ----------------------------------------------------
sp = {"ss2": [], "ss05": [], "pre25": [], "ff30": []}
for src, line in lines["cpu_speed_pre"]:
    for k in sp:
        sp[k] += ints(line, "delta", k)
laws["speed_pre"] = {"measured": {k: sorted(set(v)) for k, v in sp.items()}}

# 4. request lattice --------------------------------------------------------
req = {"step010": [], "step005": []}
for src, line in lines["cpu_request"]:
    req["step010"] += ints(line, "fin_call1", "step0.10")
    req["step005"] += ints(line, "fin_call1", "step0.05")
laws["request"] = {
    "measured": {k: sorted(set(v)) for k, v in req.items()},
    "floor_L_over_step_plus1": {"step010": int(0.5 / 0.10) + 1,
                                "step005": int(0.5 / 0.05) + 1},
}

# 5. pause windows ----------------------------------------------------------
pause = defaultdict(list)
for src, line in lines["cpu_pause"]:
    pause["vis"].append((src, field(line, "fin_after_show", "vis")))
    pause["vis_parent"].append((src, field(line, "fin_after_show", "vis_parent")))
    pause["pm_disabled"].append((src, field(line, "fin_after_enable", "pm_disabled")))
    pause["ts0"].append((src, field(line, "fin_after_restore", "ts0")))
laws["pause"] = {
    k: {"values": sorted({v for _, v in pairs if v is not None}),
        "by_source": {s: sorted({v for src2, v in pairs if src2 == s and v is not None})
                      for s in sorted({src2 for src2, _ in pairs})}}
    for k, pairs in pause.items()}
laws["pause"]["prefixes"] = distinct("cpu_pause", "prefix")

# 6. contam / never ---------------------------------------------------------
laws["never"] = {
    "n_fin": sorted({field(l, "n_fin") for _, l in lines["cpu_never"]}),
    "fin_delta": sorted({field(l, "fin_delta") for _, l in lines["cpu_never"]}),
    "n_never": sorted({field(l, "n_never") for _, l in lines["cpu_contam"]}),
    "never_fin_delta": sorted({int(x) for _, l in lines["cpu_contam"]
                               for x in re.findall(r"never\d+\[fin_delta=(" + NUM + r")", l)}),
}

# 7. restart / retrigger ----------------------------------------------------
laws["restart"] = {
    "first_delta": sorted({int(x) for _, l in lines["cpu_restart"]
                           for x in re.findall(r"first_delta=(" + NUM + r")", l)}),
    "second_after": sorted({int(x) for _, l in lines["cpu_restart"]
                            for x in re.findall(r"second_after=(" + NUM + r")", l)}),
    "n_fin": sorted({field(l, "n_fin") for _, l in lines["cpu_restart"]}),
}
laws["retrigger"] = {
    "n_fin": sorted({field(l, "n_fin") for _, l in lines["cpu_retrigger"]}),
    "second_after": sorted({int(x) for _, l in lines["cpu_retrigger"]
                            for x in re.findall(r"second_after=(" + NUM + r")", l)}),
}

# 8. mid-flight params ------------------------------------------------------
laws["lt_mid"] = {"fin_after_set": sorted({field(l, "fin_after_set") for _, l in lines["cpu_lt_mid"]})}
laws["speed_mid"] = {"fin_after_set": sorted({field(l, "fin_after_set") for _, l in lines["cpu_speed_mid"]})}
laws["amount_mid"] = {
    "fin_after_set": sorted({field(l, "fin_after_set") for _, l in lines["cpu_amount_mid"]}),
    "em_fin": sorted({m for _, l in lines["cpu_amount_mid"] for m in re.findall(r"em_fin=(\w+)", l)}),
    "em_at_end": sorted({m for _, l in lines["cpu_amount_mid"] for m in re.findall(r"em_at_end=(\w+)", l)}),
}

# 9. stop / oneshot ---------------------------------------------------------
laws["stop"] = {
    "stop10": sorted({int(x) for _, l in lines["cpu_stop"]
                      for x in re.findall(r"stop10\[fin_after=(" + NUM + r")", l)}),
    "stop40": sorted({int(x) for _, l in lines["cpu_stop"]
                      for x in re.findall(r"stop40\[fin_after=(" + NUM + r")", l)}),
}
laws["oneshot_off"] = {
    "fin_after_off": sorted({field(l, "fin_after_off") for _, l in lines["cpu_oneshot_off"]}),
    "n_fin": sorted({field(l, "n_fin") for _, l in lines["cpu_oneshot_off"]}),
}
laws["oneshot_flag"] = {
    "fin_after_flag": sorted({field(l, "fin_after_flag") for _, l in lines["cpu_oneshot_flag"]}),
    "n_fin": sorted({field(l, "n_fin") for _, l in lines["cpu_oneshot_flag"]}),
}

# 10. GPU headless ----------------------------------------------------------
flips = set()
for _, l in lines["gpu_headless"]:
    flips |= {int(x) for x in re.findall(r"flip_after=(" + NUM + r")", l)}
laws["gpu"] = {
    "flip_after_values": sorted(flips),
    "flip_after_in_1_7": all(1 <= x <= 7 for x in flips if x >= 0),
    "os_fin_delta": sorted({int(x) for _, l in lines["gpu_headless"]
                            for x in re.findall(r"os\[fin_delta=(" + NUM + r")", l)}),
    "capture_zero": all("capture[rect=(0.0000,0.0000,0.0000,0.0000)" in l
                        for _, l in lines["gpu_headless"]),
}

# 11. byte-stable cells: 1 distinct full line per arm across landed receipts -
stable_cells = ["census", "ppm", "convert", "cpu_never", "cpu_contam",
                "cpu_oneshot_off", "cpu_oneshot_flag", "cpu_retrigger",
                "cpu_lt_mid", "cpu_speed_mid", "cpu_amount_mid", "cpu_request"]
laws["byte_stable"] = {}
for arm in stable_cells:
    landed = [l for s, l in lines[arm] if s.startswith(("scribe-", "author-"))]
    allsrc = [l for _, l in lines[arm]]
    laws["byte_stable"][arm] = {
        "landed_receipts": len(landed),
        "landed_distinct_full_lines": len(set(landed)),
        "all_receipts": len(allsrc),
        "all_distinct_full_lines": len(set(allsrc)),
    }

# 12. fixture _okb windows (landed bytes) vs measured values -----------------
fix = (REPO / "corpus/fixtures/particles_lattice.gd").read_text()
windows = {}
for m in re.finditer(r"_okb\([^,]+,\s*(\d+),\s*(\d+)\)", fix):
    windows.setdefault((int(m.group(1)), int(m.group(2))), 0)
    windows[(int(m.group(1)), int(m.group(2)))] += 1
laws["fixture_okb_windows"] = {f"{a}-{b}": n for (a, b), n in sorted(windows.items())}

# 13. the 19 prefixes are byte-stable across landed receipts ----------------
laws["landed_prefix_stability"] = {}
for arm in lines:
    landed = [l.split(" | ")[0] for s, l in lines[arm] if s.startswith(("scribe-", "author-"))]
    if landed:
        laws["landed_prefix_stability"][arm] = {"receipts": len(landed),
                                                "distinct_prefixes": len(set(landed))}

(OUT / "laws.json").write_text(json.dumps(laws, indent=2, default=str) + "\n")
print(json.dumps(laws, indent=1, default=str)[:5500])
