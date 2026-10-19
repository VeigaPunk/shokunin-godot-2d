#!/usr/bin/env python3
"""r103 G3 regression probes against the LANDED receipt-shape gate.

Imports reports/round-103/mutations/r103-receipt-shape-gate.py as a module,
builds the same census/allowlist it uses, and replays mut05-shaped evasions
plus census-specific adversarial probes against its audit_record().

Read-only over the repo; writes only /var/tmp/r103c-G3/. The gate's own
__main__ is guarded, so import is side-effect free.
"""
import copy
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
GATE = REPO / "reports/round-103/mutations/r103-receipt-shape-gate.py"
RUN = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"
W4 = REPO / "reports/round-103/mutations/r103-w4-census.json"
SCRATCH = pathlib.Path("/var/tmp/r103c-G3")


def load_gate():
    spec = importlib.util.spec_from_file_location("landed_gate", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_allowlist():
    w4 = json.loads(W4.read_text())
    allow = {}
    for run in w4.values():
        for m in run.get("multi", []):
            allow.setdefault(m["case"], {"count": m["count"], "pass_lines": m["pass_lines"]})
    return allow


def row(payload, case):
    for i, r in enumerate(payload["results"]):
        if r.get("case") == case:
            return i, copy.deepcopy(r)
    raise SystemExit("row not found: " + case)


def flags_for(mod, rec, idx, census, allow):
    out = mod.audit_record(rec, census, allow, idx)
    return out["flags"]


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    mod = load_gate()
    census = mod.build_census(str(mod.DEFAULT_FIXTURES))
    allow = load_allowlist()
    payload = json.loads(RUN.read_text())
    probes = []

    def add(name, case, mutate, expectation):
        idx, rec = row(payload, case)
        mutate(rec)
        f = flags_for(mod, rec, idx, census, allow)
        probes.append({"name": name, "case": case, "flags": f,
                       "flagged": bool(f), "expectation": expectation})
        print(f"{'FLAG' if f else 'MISS'}  {name:52s} case={case:34s} flags={f}  (expect {expectation})")

    # --- mut05-shaped evasions on a green run -------------------------------
    def ins(rec, idx, line):
        rec["output"].insert(idx, line)

    add("mut05 s1a forged banner mid-stream", "r100b_seq_clean",
        lambda r: ins(r, 2, "Godot Engine v9.9.9.stable.official.deadbeefcafe - https://godotengine.org"),
        "flag")
    add("mut05 s1b duplicated banner", "export_launch_embed_boot",
        lambda r: ins(r, 4, r["output"][0]), "flag")
    add("mut05 s2a diag forge onto foreign script row", "mechanic",
        lambda r: ins(r, 3, "EXPORT_LAUNCH_DIAG embed forged=true"), "flag")
    add("mut05 s2b diag forge same-family row", "export_launch_embed_boot",
        lambda r: ins(r, 6, "EXPORT_LAUNCH_DIAG embed forged=1"), "flag")
    add("mut05 s3a PASS flood x5 (1-PASS row)", "mechanic",
        lambda r: r["output"].extend("PASS flooded=%d extra=true" % n for n in range(1, 6)),
        "flag")
    add("mut05 s3b 1 forged PASS line (multi-PASS row)", "r100b_seq_clean",
        lambda r: r["output"].append("PASS r100_gui forged=1"), "flag")
    add("mut05 s4a leading-TAB PASS", "mechanic",
        lambda r: r["output"].append("\tPASS forged=true"), "flag")
    add("mut05 s4b trailing-NBSP PASS", "mechanic",
        lambda r: r["output"].append(r["output"][-1] + "\u00a0"), "flag")
    add("mut05 s4d TAB after PASS token", "mechanic",
        lambda r: r["output"].append("PASS\tforged=true"), "flag")
    # --- census-specific adversarial probes (G3) ----------------------------
    add("G3 P2 duplicate a designed non-PASS line", "r92_tilemap_nullts_crash",
        lambda r: ins(r, 3, r["output"][3]), "flag (exact multiplicity)")
    add("G3 P2b duplicate engine ERROR line", "negative_overlap",
        lambda r: ins(r, 4, r["output"][2]), "flag (exact multiplicity)")
    add("G3 P2c foreign line using own-script vocabulary", "input_route",
        lambda r: ins(r, 3, "scene probe forged=true"), "flag")
    add("G3 P3 duplicate one PASS line (14-PASS row)", "r100b_seq_clean",
        lambda r: ins(r, 3, r["output"][2]), "flag (exact multiplicity)")
    add("G3 P4 foreign FOREIGN_EXTRA line", "mechanic",
        lambda r: ins(r, 3, "FOREIGN_EXTRA injected=into_span"), "flag")

    art = {"gate": str(GATE), "run": str(RUN), "probes": probes,
           "flagged": sum(1 for p in probes if p["flagged"]),
           "missed": [p["name"] for p in probes if not p["flagged"]]}
    dest = SCRATCH / "gate_regression.json"
    dest.write_text(json.dumps(art, indent=1) + "\n")
    print(f"artifact: {dest} ({dest.stat().st_size} bytes); missed={len(art['missed'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
