#!/usr/bin/env python3
"""r103 mut08 (W7) — replay the mut09 attack JSON against the G1 receipt-shape predicate (import+call).

Inputs (pinned by sha256 in the output artifact):
  * reports/round-102/mutations/mut09_export_launch_span_attack.json  (attack bytes)
  * reports/round-103/mutations/r103-w4-census.json                   (multi-PASS allowlist fold)
  * /var/tmp/r103-g0/proto_gate.py — G0 prototype predicate, sha256
    416fe7975aef573e9c2faa08aae6c8917ac75ee3bffebf8620ec2bc6d41c2ccb (byte-identical to the G2
    re-seat copy /var/tmp/r103c-G2/G1_predicate.py). `gate_row(r, family_used)` is the imported callable.

Import hygiene: proto_gate.py runs a module-level driver sweep at import time which writes
/var/tmp/r103-g0/proto_report.json (a sibling seat's artifact). To import `gate_row` WITHOUT
clobbering that file, everything from the driver line `report={}` to EOF is spliced off before
exec; the spliced head is executed from a scratch copy and both hashes are recorded. The predicate
itself is NOT reimplemented.

Replay (in-process only; run_battery.py never executed; no Godot, no subprocess besides
date/uptime/git for the header):
  family L — mut09 launch captures (base/A1/A2/A3 stdout_text) with the marker+FRAME span pin;
  family B — landed-fixture receipts (pristine/attacked pass_lines) with mut09's truncated pin;
  family C — landed-fixture run-log span (pristine/attacked run_log_span) with the LAUNCH_S02 span pin;
  green sweep — gate_row over every row of r101 x2 + r102 x2 verdicts.json, raw and with the
  W4-census allowlist folded into the module's family-pin table (per-script union of the 19 cases).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRATCH = Path("/var/tmp/r103c-w7")
MUT09 = REPO / "reports" / "round-102" / "mutations" / "mut09_export_launch_span_attack.json"
CENSUS = REPO / "reports" / "round-103" / "mutations" / "r103-w4-census.json"
PRED_SRC = Path("/var/tmp/r103-g0/proto_gate.py")
PRED_SHA = "416fe7975aef573e9c2faa08aae6c8917ac75ee3bffebf8620ec2bc6d41c2ccb"
OUT_JSON = REPO / "reports" / "round-103" / "mutations" / "mut08_replay.json"
RUNS = {
    "r101-run1": "corpus/live/runs/20261018T200239625248Z/verdicts.json",
    "r101-run2": "corpus/live/runs/20261018T202131127599Z/verdicts.json",
    "r102-run1": "corpus/live/runs/20261018T212500022987Z/verdicts.json",
    "r102-run2": "corpus/live/runs/20261018T213443471189Z/verdicts.json",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_predicate():
    src = PRED_SRC.read_bytes()
    got = sha256(src)
    if got != PRED_SHA:
        raise SystemExit(f"predicate sha drift: {got} != {PRED_SHA}")
    text = src.decode()
    marker = "\nreport={}"
    if text.count(marker) != 1:
        raise SystemExit("splice marker not unique")
    head = text.split(marker)[0]
    SCRATCH.mkdir(parents=True, exist_ok=True)
    frozen = SCRATCH / "g1_predicate_frozen.py"
    frozen.write_text(head + "\n")
    spec = importlib.util.spec_from_file_location("g1_predicate_frozen", frozen)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not callable(getattr(mod, "gate_row", None)):
        raise SystemExit("gate_row missing from imported predicate")
    return mod, got, sha256((head + "\n").encode()), len((head + "\n").encode())


def pinned_receipt(line: str) -> str:
    """mut09-style truncated pin: through ' exit=0' (mut09 script §attack_landed_fixture)."""
    cut = line.find(" exit=")
    return line[:cut + len(" exit=0")] if cut >= 0 else line


def record(case, script, output, signature, verdict="PASS"):
    return {"case": case, "script": script, "verdict": verdict,
            "output": output, "signature": signature}


def main():
    os.chdir(REPO)
    t0 = time.monotonic()
    mod, src_sha, imported_sha, imported_bytes = load_predicate()
    gate_row = mod.gate_row

    meta = {
        "date_utc": subprocess.run(["date", "-u"], capture_output=True, text=True).stdout.strip(),
        "uptime": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
        "loadavg": Path("/proc/loadavg").read_text().strip(),
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                   text=True).stdout.strip(),
        "predicate": {
            "source_path": str(PRED_SRC),
            "source_sha256": src_sha,
            "splice_rule": "drop everything from the module-level driver line '\\nreport={}' to EOF; "
                           "append '\\n' and exec from scratch copy",
            "imported_sha256": imported_sha,
            "imported_bytes": imported_bytes,
            "callable": "gate_row(r, family_used)",
        },
        "inputs": {
            "mut09_json": {"path": str(MUT09.relative_to(REPO)),
                           "sha256": sha256(MUT09.read_bytes())},
            "w4_census_json": {"path": str(CENSUS.relative_to(REPO)),
                               "sha256": sha256(CENSUS.read_bytes())},
            "runs": RUNS,
        },
        "note": "no battery run; no Godot; records synthesized from stored bytes; no classifier change",
    }

    mut09 = json.loads(MUT09.read_text())
    q = mut09["quit_after"]
    span_L = "\n".join([mut09["marker"]] + [f"FRAME {i}" for i in range(1, q + 1)])
    span_F = "\n".join(["LAUNCH_S02_MARKER boot=true"] + [f"LAUNCH_S02_FRAME {i}" for i in range(1, q + 1)])

    famL = {}
    for name, v in mut09["variants"].items():
        r = record("export_launch_s02", "export_launch.gd", v["stdout_text"], span_L)
        famL[name] = {"flags": gate_row(r, set()), "stdout_sha256": v["stdout_sha256"],
                      "stdout_lines": len(v["stdout_text"])}

    fx = mut09["landed_fixture"]
    pin_B = pinned_receipt(fx["pristine"]["pass_lines"][0])
    famB = {}
    for name in ("pristine", "attacked"):
        r = record("export_launch_s02", "export_launch.gd", fx[name]["pass_lines"], pin_B)
        famB[name] = {"flags": gate_row(r, set()),
                      "receipt_line": fx[name]["pass_lines"][0] if fx[name]["pass_lines"] else None}

    famC = {}
    for name in ("pristine", "attacked"):
        r = record("export_launch_s02", "export_launch.gd", fx[name]["run_log_span"], span_F)
        famC[name] = {"flags": gate_row(r, set()),
                      "span_lines": len(fx[name]["run_log_span"]),
                      "foreign_in_run_log": fx[name]["foreign_in_run_log"]}

    sweep = {}
    for tag, rel in RUNS.items():
        d = json.loads((REPO / rel).read_text())
        rows = d["results"]
        flagged, no_output, zero_pass = {}, 0, 0
        for r in rows:
            out = r.get("output")
            if out is None:
                no_output += 1
            elif not any(isinstance(L, str) and L.startswith("PASS ") for L in out):
                zero_pass += 1
            f = gate_row(r, set())
            if f:
                flagged[r.get("case")] = f
        sweep[tag] = {"file": rel, "rows": len(rows), "verdict": d.get("verdict"),
                      "output_none_silently_exempt": no_output,
                      "zero_pass_with_output": zero_pass,
                      "flagged_raw": len(flagged), "flagged_cases_raw": flagged}

    census = json.loads(CENSUS.read_text())
    allow = {}
    for run in ("run1", "run2"):
        for m in census[run]["multi"]:
            allow.setdefault(m["script"], set()).update(m["pass_lines"])
    added = 0
    for script, lines in allow.items():
        have = {P for _, P in mod.SCRIPT_PASS_PINS.get(script, [])}
        for line in sorted(lines):
            if line in have:
                continue
            mod.SCRIPT_PASS_PINS[script].append(("w4-allowlist", line))
            added += 1

    def residual_class(r):
        """Byte-level class of a residual (post-allowlist) green flag; inspection only."""
        sig = r.get("signature")
        obs = [L for L in (r.get("output") or []) if isinstance(L, str) and L.startswith("PASS ")]
        pins = [sig] if isinstance(sig, str) else (
            list(sig) if isinstance(sig, (list, tuple)) else [])
        payloads = [pl for P in pins if isinstance(P, str)
                    for pl in P.splitlines() if pl.startswith("PASS ")]
        if not payloads:
            return "A_pin_has_no_pass_payload"
        if any(not any(P in L for L in obs) for P in payloads):
            return "B_list_pin_payload_variant_absent"
        return "C_observed_line_unaccounted"

    for tag, rel in RUNS.items():
        d = json.loads((REPO / rel).read_text())
        flagged = {}
        residual = {}
        for r in d["results"]:
            f = gate_row(r, set())
            if f:
                flagged[r.get("case")] = f
                residual.setdefault(residual_class(r), []).append(r.get("case"))
        sweep[tag]["flagged_equipped"] = len(flagged)
        sweep[tag]["flagged_cases_equipped"] = flagged
        sweep[tag]["equipped_residual_classes"] = {k: sorted(v)
                                                   for k, v in sorted(residual.items())}

    out = {
        "meta": meta,
        "replay": {
            "family_L_launch_capture_span_pin": {"span": span_L, "variants": famL},
            "family_B_fixture_receipt_pinned": {"pin": pin_B, "records": famB},
            "family_C_fixture_runlog_span_pin": {"span": span_F, "records": famC},
        },
        "green_sweep": sweep,
        "allowlist_folded": {"per_script_lines_added": added,
                             "scripts": {s: len(lines) for s, lines in allow.items()}},
        "elapsed_s": round(time.monotonic() - t0, 2),
    }
    payload = json.dumps(out, indent=1) + "\n"
    OUT_JSON.write_text(payload)
    (SCRATCH / "mut08_replay.json").write_text(payload)

    print("predicate source_sha256:", src_sha)
    print("predicate imported_sha256:", imported_sha, f"({imported_bytes} bytes)")
    for name in ("base", "A1", "A2", "A3"):
        v = famL[name]
        print(f"familyL {name:6s} lines={v['stdout_lines']} flags={v['flags']}")
    for name in ("pristine", "attacked"):
        print(f"familyB {name:8s} flags={famB[name]['flags']}")
        print(f"familyC {name:8s} span_lines={famC[name]['span_lines']} flags={famC[name]['flags']}")
    for tag, s in sweep.items():
        print(f"{tag}: rows={s['rows']} raw={s['flagged_raw']} equipped={s['flagged_equipped']} "
              f"outputNone={s['output_none_silently_exempt']} zeroPass={s['zero_pass_with_output']}")
        print("   residual classes:", {k: len(v) for k, v in s["equipped_residual_classes"].items()})
    print("allowlist lines added:", added)
    print("wrote", OUT_JSON)
    print("elapsed_s", out["elapsed_s"])


if __name__ == "__main__":
    main()
