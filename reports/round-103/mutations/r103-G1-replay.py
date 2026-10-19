#!/usr/bin/env python3
"""r103 G1 (C2 depth): replay the patched receipt-shape meta-gate over a
STORED verdicts.json — plus discrimination probes on mutated copies of the
green records. Imports the predicate from the patched run_battery.py copy so
the harness exercises the patch's own code path, not a reimplementation.

Usage: python3 r103-G1-replay.py [patched_run_battery.py] [verdicts.json]
"""
import importlib.util
import json
import sys
from pathlib import Path

PATCHED = Path(sys.argv[1] if len(sys.argv) > 1 else "/var/tmp/r103c-G1/run_battery_g1.py")
VERDICTS = Path(sys.argv[2] if len(sys.argv) > 2 else
               "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/runs/20261018T213443471189Z/verdicts.json")
OUT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/reports/round-103/mutations/r103-G1-replay.json")


def load_module(path):
    spec = importlib.util.spec_from_file_location("patched_run_battery", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scan(module, records):
    pins = module.receipt_pin_corpus(records)
    checked = [r for r in records if "signature" in r]
    flags = {}
    for record in checked:
        labels = module.receipt_shape_violations(record, pins)
        if labels:
            flags[record["case"]] = labels
    return pins, checked, flags


def probe(module, records, name, mutate, expect_label_substr):
    pins = module.receipt_pin_corpus(records)
    victim = mutate(json.loads(json.dumps(records)))
    labels = module.receipt_shape_violations(victim, pins)
    caught = any(expect_label_substr in label for label in labels)
    return {"probe": name, "expect_label_contains": expect_label_substr,
            "labels": labels, "caught": caught}


def main():
    module = load_module(PATCHED)
    payload = json.loads(VERDICTS.read_text())
    records = payload["results"]
    pins, checked, flags = scan(module, records)
    print(f"records={len(records)} checked(signature-bearing)={len(checked)} "
          f"pin_corpus={len(pins)} flags={len(flags)}")
    for case, labels in flags.items():
        print(f"  FLAG {case}: {labels}")

    by_case = {r["case"]: r for r in records}
    seq = by_case["r101_seqfull_clean"]

    def span_splice(recs):
        out = list(seq["output"])
        width = seq["signature"].count("\n") + 1
        for i in range(len(out) - width + 1):
            if "\n".join(out[i:i + width]) == seq["signature"]:
                out.insert(i + 5, "FOREIGN_EXTRA injected=into_span")
                break
        recs[0].update(seq)
        recs[0]["output"] = out
        return recs[0]

    def post_span_pass(recs):
        out = list(seq["output"]) + ["PASS cargo_cult=true forged=post_span"]
        recs[0].update(seq)
        recs[0]["output"] = out
        return recs[0]

    def pre_span_pass(recs):
        out = ["PASS cargo_cult=true forged=pre_span"] + list(seq["output"])
        recs[0].update(seq)
        recs[0]["output"] = out
        return recs[0]

    def drop_output(recs):
        recs[0].update(seq)
        recs[0].pop("output")
        return recs[0]

    def flip_verdict(recs):
        recs[0].update(seq)
        recs[0]["verdict"] = "FAIL"
        return recs[0]

    def export_pin_mismatch(recs):
        recs[0].update(by_case["export_readiness"])
        recs[0]["export_artifact"] = dict(by_case["export_readiness"]["export_artifact"],
                                          artifact_bytes=73703801)
        return recs[0]

    def export_bad_digest(recs):
        recs[0].update(by_case["export_readiness"])
        recs[0]["export_artifact"] = dict(by_case["export_readiness"]["export_artifact"],
                                          artifact_sha256="NOPE")
        return recs[0]

    def allowlist_forgery(recs):
        recs[0].update(by_case["save_process_missing"])
        recs[0]["output"] = list(recs[0]["output"]) + [
            "PASS save_process missing=true pid=999 path=/tmp/forged"]
        return recs[0]

    probes = [
        probe(module, records, "A1 span splice (multi-line pin)",
              span_splice, "span:"),
        probe(module, records, "A2 PASS-shaped line post-span",
              post_span_pass, "pass_line:"),
        probe(module, records, "A3 PASS-shaped line pre-span",
              pre_span_pass, "pass_line:"),
        probe(module, records, "shape: output field dropped",
              drop_output, "shape:output"),
        probe(module, records, "replay: verdict flipped off the classifier",
              flip_verdict, "replay"),
        probe(module, records, "artifact: pin bytes != artifact bytes",
              export_pin_mismatch, "artifact:pin_mismatch"),
        probe(module, records, "artifact: malformed sha256",
              export_bad_digest, "artifact:record"),
        probe(module, records, "declared ceiling: line matching allowlist",
              allowlist_forgery, "PASS save_process"),
    ]
    for p in probes:
        print(f"probe={p['probe']!r} caught={p['caught']} labels={p['labels']}")
    artifact = {
        "patched_module": str(PATCHED), "verdicts": str(VERDICTS),
        "records": len(records), "checked": len(checked), "pin_corpus": sorted(pins),
        "flags": flags, "probes": probes,
    }
    OUT.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"artifact: {OUT}")
    return 0 if not flags else 1


if __name__ == "__main__":
    sys.exit(main())
