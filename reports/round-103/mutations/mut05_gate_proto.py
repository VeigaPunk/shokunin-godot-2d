#!/usr/bin/env python3
"""r103-M5 — receipt-shape meta-gate prototype + pin builder (scratch harness).

Serves the C2 receipt-shape meta-gate evidence need for the M5 seat (mut05 gate
evasion battery): no gate implementation had landed when mut05 was run, so this
file derives the account empirically from the two green r102 runs and generates
`mut05_gate.py` (self-contained, pin embedded) for mut05's `--gate PATH` mode.

Account model (per case, over STORED stdout records; never a classifier change):
  * key(line) = ('verb', valnorm(t0), valnorm(t1), t2-key) when t0 is a
                designed-verb token (uppercase family observed in the green
                census, or *_DIAG);
              = ('raw', valnorm(t0)) otherwise; ('blank',) for empty-after-strip.
    valnorm collapses digit runs to '#' so run-varying pids/floats/permutation
    seeds stay inside the shape key (measured: needed for green stability).
  * per-case key multiset is pinned with a count RANGE [n1, n2] from the two
    green r102 runs; n1 == n2 means the count is an exact receipt invariant,
    otherwise the key is volatile and only the observed range is enforced.
  * the engine banner must occur exactly once and at index 0.
  * a line that is not column-0 clean but whose stripped form starts with a
    designed verb is flagged as hidden_shape (whitespace-masked receipt line).
  * fail-closed: pinned case with missing/None output, record without a
    case/verdict field, or unknown case is flagged.

Calibration: the pin's counts come from the two green r102 runs; silence is
audited out-of-sample on every other run on disk (holdout), so the silence
claim is not self-fulfilling. Read-only over the repo; run_battery.py is never
executed.
"""
import argparse
import glob
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PIN_REF = REPO / "corpus/live/runs/20261018T212500022987Z/verdicts.json"
PIN_REF2 = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"
RUNRE = re.compile(r"MechanicOneShotTest-\d{8}T\d+Z")
DIGITS = re.compile(r"\d+")
VERB_T0 = re.compile(r"^[A-Z][A-Z0-9_]{2,24}$")
PIN = None  # set by main(); the generated mut05_gate.py embeds it as a literal
# Measured on 4 runs: the `[ N% ] <import-step>` progress family is
# environment-dependent (export_readiness 259 in both r102 greens vs 271 in both
# r101-era runs; export_preset_missing 85 vs 89). Presence-only, not count-pinned.
VOLATILE_KEYS = {"raw/["}


def norm(line):
    return RUNRE.sub("<RUN>", line)


def valnorm(tok):
    return DIGITS.sub("#", tok)


def tokens(line):
    return norm(line).strip().split()


def design_universe(rows):
    """Empirical designed-verb census over the green reference."""
    uni = Counter()
    for r in rows:
        for l in (r.get("output") or []):
            t = tokens(l)
            if t and VERB_T0.match(t[0]):
                uni[t[0]] += 1
    return uni


def line_key(line, verbs):
    t = tokens(line)
    if not t:
        return ("blank",)
    t0 = t[0]
    if t0 in verbs or t0.endswith("_DIAG"):
        t1 = valnorm(t[1]) if len(t) > 1 else ""
        t2 = t[2].split("=")[0] if len(t) > 2 else ""
        return ("verb", t0, t1, t2)
    return ("raw", valnorm(t0))


def case_keys(rows, verbs):
    out = {}
    for r in rows:
        e = out.setdefault(r.get("case"), {"keys": Counter(),
                                           "has_output": r.get("output") is not None})
        for l in (r.get("output") or []):
            e["keys"][line_key(l, verbs)] += 1
    return out


def build_pin(path_a, path_b):
    rows_a = json.loads(Path(path_a).read_bytes())["results"]
    rows_b = json.loads(Path(path_b).read_bytes())["results"]
    verbs = dict(design_universe(rows_a))
    ka, kb = case_keys(rows_a, verbs), case_keys(rows_b, verbs)
    pin = {"verbs": sorted(verbs), "cases": {}}
    for case in sorted(set(ka) | set(kb)):
        ea = ka.get(case, {"keys": Counter(), "has_output": False})
        eb = kb.get(case, {"keys": Counter(), "has_output": False})
        keys = {}
        for k in sorted(set(ea["keys"]) | set(eb["keys"]), key=str):
            n1, n2 = ea["keys"][k], eb["keys"][k]
            keys["/".join(k)] = [n1, n2]
        pin["cases"][case] = {
            "keys": keys,
            "has_output": ea["has_output"] and eb["has_output"],
            "has_output_any": ea["has_output"] or eb["has_output"],
        }
    return pin, len(rows_a)


def receipt_shape_gate(records, pin=None):
    """META predicate over stored verdict records. List -> summary; dict -> single."""
    if pin is None:
        pin = PIN
    single = isinstance(records, dict)
    recs = [records] if single else list(records)
    verbs = set(pin["verbs"])
    flags = []
    for r in recs:
        reasons = []
        case = r.get("case")
        out = r.get("output")
        if case is None or r.get("verdict") is None:
            reasons.append("record_field_missing case=%r verdict=%r"
                           % (case, r.get("verdict")))
        pe = pin["cases"].get(case)
        if pe is None:
            reasons.append("unpinned_case case=%r" % (case,))
        else:
            if out is None:
                if pe["has_output_any"]:
                    reasons.append("output_missing_for_pinned_case")
            else:
                obs = Counter("/".join(line_key(l, verbs)) for l in out)
                for k in sorted(set(pe["keys"]) | set(obs)):
                    lo, hi = pe["keys"].get(k, [0, 0])
                    lo, hi = min(lo, hi), max(lo, hi)
                    n = obs[k]
                    if k in VOLATILE_KEYS:
                        if max(lo, hi) > 0 and n == 0:
                            reasons.append("volatile_key_absent %s obs=0" % k)
                        continue
                    if not (lo <= n <= hi) or (lo == hi and n != lo):
                        reasons.append("key_count_mismatch %s exp=[%d,%d] obs=%d"
                                       % (k, lo, hi, n))
                nban = sum(1 for l in out if tokens(l)[:1] == ["Godot"])
                if nban != 1:
                    reasons.append("banner_count n=%d" % nban)
                elif tokens(out[0])[:1] != ["Godot"]:
                    reasons.append("banner_misplaced idx=%s"
                                   % ",".join(str(i) for i, l in enumerate(out)
                                              if tokens(l)[:1] == ["Godot"]))
                for i, l in enumerate(out):
                    t = tokens(l)
                    if not t:
                        continue
                    if l != l.strip() and (t[0] in verbs or t[0].endswith("_DIAG")):
                        reasons.append("hidden_shape idx=%d t0=%s raw=%r"
                                       % (i, t[0], l[:70]))
        if reasons:
            flags.append({"case": case, "reasons": reasons})
    if single:
        return flags[0] if flags else {"case": recs[0].get("case"), "reasons": []}
    return {"n_records": len(recs), "n_flagged": len(flags), "flags": flags}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-gate", metavar="PATH")
    ap.add_argument("--replay", metavar="EVASIONS_JSON")
    ap.add_argument("--negctl", metavar="EVASIONS_JSON")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()
    pin, n_rows = build_pin(PIN_REF, PIN_REF2)
    stable = sum(1 for c in pin["cases"].values() for v in c["keys"].values()
                 if v[0] == v[1])
    vol = sum(1 for c in pin["cases"].values() for v in c["keys"].values()
              if v[0] != v[1])
    print("PIN_REF=%s + %s rows=%d sha256=%s" % (PIN_REF.name, PIN_REF2.name,
          n_rows, hashlib.sha256(PIN_REF.read_bytes()).hexdigest()))
    print("DESIGNED_VERBS=%d cases=%d keys=%d (count-stable=%d volatile=%d)"
          % (len(pin["verbs"]), len(pin["cases"]), stable + vol, stable, vol))
    if args.audit:
        pin_r1, _ = build_pin(PIN_REF, PIN_REF)
        for f in sorted(glob.glob(str(REPO / "corpus/live/runs/*/verdicts.json"))):
            rows = json.loads(Path(f).read_bytes())["results"]
            res = receipt_shape_gate(rows, pin)
            res_r1 = receipt_shape_gate(rows, pin_r1)
            unpinned = sum(1 for r in rows if r.get("case") not in pin["cases"])
            print("AUDIT %s rows=%d unpinned_cases=%d two_ref_flagged=%d "
                  "run1only_pin_flagged=%d"
                  % (Path(f).parent.name, len(rows), unpinned,
                     res["n_flagged"], res_r1["n_flagged"]))
            for fl in res["flags"][:8]:
                print("   FLAG %s :: %s" % (fl["case"], "; ".join(fl["reasons"])[:220]))
    if args.replay:
        payload = json.loads(Path(args.replay).read_bytes())
        bad = 0
        for e in payload["evasions"]:
            res = receipt_shape_gate(e["row"], pin)
            flagged = bool(res["reasons"])
            bad += 0 if flagged else 1
            print("EVASION %-27s flagged=%-5s :: %s"
                  % (e["name"], flagged, "; ".join(res["reasons"])[:170]))
        for g in payload["green_controls"]:
            res = receipt_shape_gate(g["row"], pin)
            silent = not res["reasons"]
            bad += 0 if silent else 1
            print("CONTROL %-27s silent=%-5s :: %s"
                  % (g["name"], silent, "; ".join(res["reasons"])[:170]))
        print("REPLAY_SUMMARY evasions=%d controls=%d unexpected=%d"
              % (len(payload["evasions"]), len(payload["green_controls"]), bad))
    if args.negctl:
        payload = json.loads(Path(args.negctl).read_bytes())
        base = next(g for g in payload["green_controls"] if g["name"] == "green_simple")
        import copy as _copy
        probes = []
        n1 = _copy.deepcopy(base["row"]); n1["output"] = None
        probes.append(("n1_output_none_on_pinned_case", n1, True))
        n2 = _copy.deepcopy(base["row"])
        n2["output"] = [l.replace("receipt_count=1", "receipt_count=9")
                        for l in n2["output"]]
        probes.append(("n2_digit_flip_inside_pinned_key_value", n2, False))
        n3 = _copy.deepcopy(base["row"]); n3["case"] = "input_route_ghost"
        probes.append(("n3_unpinned_case_name", n3, True))
        n4 = _copy.deepcopy(base["row"])
        n4["output"] = [l for l in n4["output"] if not l.startswith("Godot Engine")]
        probes.append(("n4_banner_removed", n4, True))
        n5 = _copy.deepcopy(base["row"]); n5["verdict"] = None
        probes.append(("n5_verdict_field_dropped", n5, True))
        for name, row, expect_flag in probes:
            res = receipt_shape_gate(row, pin)
            got = bool(res["reasons"])
            print("NEGCTL %-34s expect_flag=%-5s flagged=%-5s %s :: %s"
                  % (name, expect_flag, got, "OK" if got == expect_flag else "MISMATCH",
                     "; ".join(res["reasons"])[:150]))
    if args.emit_gate:
        src = Path(__file__).read_text()
        body = src.split("def line_key", 1)[1].split("\ndef main(", 1)[0]
        body = "def line_key" + body
        gate = ('#!/usr/bin/env python3\n'
                '"""r103-M5 generated receipt-shape meta-gate (pin embedded).\n'
                'Generated by reports/round-103/mutations/mut05_gate_proto.py from\n'
                '%s + %s (%d rows). Scratch evidence harness for mut05.\n"""\n'
                'import json\nimport re\nfrom collections import Counter\n\n'
                'PIN = json.loads(%r)\n\n'
                'RUNRE = re.compile(r"MechanicOneShotTest-\\d{8}T\\d+Z")\n'
                'DIGITS = re.compile(r"\\d+")\n'
                'VERB_T0 = re.compile(r"^[A-Z][A-Z0-9_]{2,24}$")\n'
                '# Progress-family keys measured as environment-dependent across runs\n'
                '# (259 vs 271, 85 vs 89) -> presence-only, not count-pinned.\n'
                'VOLATILE_KEYS = {"raw/["}\n\n'
                'def norm(line):\n    return RUNRE.sub("<RUN>", line)\n\n\n'
                'def valnorm(tok):\n    return DIGITS.sub("#", tok)\n\n\n'
                'def tokens(line):\n    return norm(line).strip().split()\n\n\n'
                '%s\n'
                ) % (PIN_REF.name, PIN_REF2.name, n_rows,
                     json.dumps(pin, sort_keys=True), body)
        dst = Path(args.emit_gate)
        dst.write_text(gate)
        print("WROTE %s bytes=%d sha256=%s"
              % (dst, dst.stat().st_size,
                 hashlib.sha256(dst.read_bytes()).hexdigest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
