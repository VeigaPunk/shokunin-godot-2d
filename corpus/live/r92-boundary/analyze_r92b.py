#!/usr/bin/env python3
"""r92-boundary analyzer.

Byte-compares every r92-boundary receipt (13 scout arms x 7 conditions + the seat's
own poller arms) against the r92 scout's canonical/loadtest/tps120 receipts, and
reports field-level diffs where a row payload changed.

Usage: python3 analyze_r92b.py [root]   (root = the game-dev-2d-shokunin repo)
Writes runs/analyze_r92b.json and prints a table.
"""
import json
import os
import sys
import difflib

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
SCOUT = os.path.join(ROOT, "corpus", "live", "r92-scout")
RUNS = os.path.join(HERE, "runs")

ARMS = ["census", "atlas", "cells", "custom", "terrain", "pattern", "encoding",
        "fixinvalid", "srcids", "physics", "timing", "quadrant", "nav"]
MY_ARMS = ["sched", "phys", "nav"]

BATCHES = ["q60", "l60", "f30", "f60", "f120", "f120l", "t120",
           "q60b", "f10", "f20", "f600", "f30l", "l32"]
REPS = {"q60": 3, "l60": 3, "f30": 3, "f60": 3, "f120": 3, "f120l": 2, "t120": 3,
        "q60b": 2, "f10": 2, "f20": 2, "f600": 2, "f30l": 2, "l32": 2}
OWN_BATCHES = {"oq": 2, "ol": 2, "of30": 2, "of60": 2, "of120": 2, "of120l": 2, "ot120": 2,
               "oq60b": 2, "of10": 2, "of20": 2, "of600": 2, "of30l": 2, "ol32": 2}


def read_pass(path):
    try:
        with open(path, "r", errors="replace") as f:
            for line in f:
                if line.startswith("PASS "):
                    return line.rstrip("\n")
    except FileNotFoundError:
        return None
    return None


def read_all_pass(path):
    out = []
    try:
        with open(path, "r", errors="replace") as f:
            for line in f:
                if line.startswith("PASS "):
                    out.append(line.rstrip("\n"))
    except FileNotFoundError:
        pass
    return out


def read_sidecar(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def read_raw(path):
    try:
        with open(path, errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return None


def norm_err(text):
    """Normalise the two harness-local differences vs the scout receipts:
    this seat's probe copy is named scout_tilemap_lattice.gd, so engine backtraces
    print `res://scout_tilemap_lattice.gd:<line>` where the scout printed
    `res://tilemap_lattice.gd:<line>`. Engine source paths and line numbers are
    unchanged; this makes the stderr byte-comparison behavioural."""
    if text is None:
        return None
    return text.replace("res://scout_tilemap_lattice.gd", "res://tilemap_lattice.gd")


def tok_diff(a, b):
    ta, tb = a.split(" "), b.split(" ")
    sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
    parts = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        parts.append({"op": op, "canonical": ta[i1:i2], "mine": tb[j1:j2]})
    return parts


def canonical():
    """Canonical payload per arm: scout's 60 tps reps, loadtest, tps120."""
    canon = {}
    for arm in ARMS:
        cell = "r92_tm_%s" % arm
        reps = []
        errs = []
        for i in range(1, 7):
            p = read_pass(os.path.join(SCOUT, "runs", "%s.rep%d.out" % (cell, i)))
            if p:
                reps.append(p)
            e = read_raw(os.path.join(SCOUT, "runs", "%s.rep%d.err" % (cell, i)))
            if e is not None:
                errs.append(e)
        lt = read_pass(os.path.join(SCOUT, "runs", "loadtest", "%s.rep1.out" % cell))
        t120 = read_pass(os.path.join(SCOUT, "runs", "tps120", "%s.rep1.out" % cell))
        canon[arm] = {
            "reps": len(reps),
            "uniq": len(set(reps)),
            "pass": reps[0] if reps else None,
            "err": errs[0] if errs else None,
            "err_uniq": len(set(errs)),
            "loadtest": lt,
            "tps120": t120,
        }
    return canon


def mine():
    res = {}
    for b in BATCHES:
        res[b] = {}
        for arm in ARMS:
            passes, rcs, walls, errs = [], [], [], []
            for i in range(1, REPS[b] + 1):
                base = os.path.join(RUNS, "%s_%s.rep%d" % (b, arm, i))
                p = read_pass(base + ".out")
                passes.append(p)
                rcs.append(read_sidecar(base + ".rc"))
                walls.append(read_sidecar(base + ".wall"))
                errs.append(norm_err(read_raw(base + ".err")))
            res[b][arm] = {"passes": passes, "rcs": rcs, "walls": walls, "errs": errs,
                           "uniq": len(set(x for x in passes if x)),
                           "missing": sum(1 for x in passes if x is None)}
    own = {}
    for b, reps in OWN_BATCHES.items():
        own[b] = {}
        for arm in MY_ARMS:
            passes, rcs = [], []
            for i in range(1, reps + 1):
                base = os.path.join(RUNS, "%s_%s.rep%d" % (b, arm, i))
                passes.append(read_pass(base + ".out"))
                rcs.append(read_sidecar(base + ".rc"))
            own[b][arm] = {"passes": passes, "rcs": rcs}
    return res, own


def main():
    canon = canonical()
    res, own = mine()
    report = {"canonical": canon, "batches": res, "own": own, "verdicts": {}}

    print("== canonical (scout receipts) ==")
    for arm in ARMS:
        c = canon[arm]
        print("  %-11s reps=%d uniq=%d loadtest=%s tps120=%s" % (
            arm, c["reps"], c["uniq"],
            "same" if c["loadtest"] and c["loadtest"] == c["pass"] else ("none" if not c["loadtest"] else "DIFF"),
            "same" if c["tps120"] and c["tps120"] == c["pass"] else ("none" if not c["tps120"] else "DIFF")))

    print("\n== boundary runs vs canonical ==")
    verdicts = {}
    for arm in ARMS:
        row = []
        v = {"canonical_uniq": canon[arm]["uniq"], "canonical_loadtest_same": canon[arm]["loadtest"] == canon[arm]["pass"],
             "canonical_tps120_same": canon[arm]["tps120"] == canon[arm]["pass"], "batches": {}}
        for b in BATCHES:
            m = res[b][arm]
            passes = [p for p in m["passes"] if p]
            same = bool(passes) and all(p == canon[arm]["pass"] for p in passes)
            err_same = all(e == canon[arm]["err"] for e in m["errs"] if e is not None)
            v["batches"][b] = {
                "n": len(passes), "uniq": m["uniq"], "same_as_canonical": same,
                "stderr_same_as_canonical": err_same,
                "rcs": m["rcs"], "walls": m["walls"], "missing": m["missing"],
                "diffs": [] if same else [tok_diff(canon[arm]["pass"], p) for p in passes if p != canon[arm]["pass"]],
            }
            row.append("%s:%s" % (b, "OK" if same else ("n=%d" % len(passes) if not passes else "DIFF")))
            if not err_same:
                row.append("ERRDIFF")
        verdicts[arm] = v
        print("  %-11s %s" % (arm, " ".join("%-9s" % x for x in row)))

    print("\n== differing payloads (field-level) ==")
    for arm in ARMS:
        for b in BATCHES:
            v = verdicts[arm]["batches"][b]
            if v["same_as_canonical"] or not v["diffs"]:
                continue
            print("  %s / %s:" % (arm, b))
            for d in v["diffs"][:1]:
                for part in d:
                    print("     %-8s canonical=%s  mine=%s" % (part["op"], part["canonical"], part["mine"]))
            if len(v["diffs"]) > 1:
                print("     (+%d more rep diffs)" % (len(v["diffs"]) - 1))

    print("\n== own poller arms (mode-dependent by construction) ==")
    for arm in MY_ARMS:
        for b in OWN_BATCHES:
            for i, p in enumerate(own[b][arm]["passes"], 1):
                print("  %s/%s rep%d: %s" % (b, arm, i, p))

    report["verdicts"] = verdicts
    with open(os.path.join(RUNS, "analyze_r92b.json"), "w") as f:
        json.dump(report, f, indent=1)
    print("\nwrote runs/analyze_r92b.json")


if __name__ == "__main__":
    main()
