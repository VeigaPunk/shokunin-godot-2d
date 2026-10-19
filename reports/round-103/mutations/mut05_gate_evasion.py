#!/usr/bin/env python3
"""r103-mut5 — gate evasion battery for the C2 receipt-shape meta-gate.

4 evasion shapes (each a tampered copy of a REAL green r102 stored record;
record verdict stays PASS; the landed gate must FLAG each):
  s1 banner-foreign     — a foreign line shaped like the engine banner
  s2 diag-prefixed      — a foreign line carrying a designed-verb prefix
  s3 PASS-flood         — extra PASS lines beyond pin / multi-PASS allowlist
  s4 whitespace-pass    — PASS-shaped lines whose whitespace evades naive scans

Modes:
  --emit-only        build + write /var/tmp/r103-mut5/evasions.json, no gate needed
  --gate PATH        import the gate function from a scratch copy of PATH
                     (/var/tmp/r103-mut5/gate.py) and replay every evasion +
                     green controls; writes evasion-results.json
Read-only over the repo; run_battery.py is never executed.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRATCH = Path("/var/tmp/r103-mut5")
# Green r102 run (554 rows, all PASS) — stored per-row stdout records.
RUN = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"
RUN_SHA = "d4d4e4b6e3f4c3a2"  # informational; recomputed below

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")

BASES = {
    "launch": "export_launch_embed_boot",   # 11 lines, 3 PASS, DIAG family
    "prod": "export_prod_base_pck",         # 9 lines, 3 PASS, DIAG family
    "seq": "r100b_seq_clean",               # 23 lines, 14 PASS, expected-error tail
    "simple": "input_route",                # 3 lines, 1 PASS, no DIAG
}


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def load_run():
    raw = RUN.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def find_row(rows, case):
    for i, r in enumerate(rows):
        if r.get("case") == case:
            return i, r
    raise SystemExit("base row not found: %s" % case)


def mutate(row, ops, label):
    """ops: list of ("insert", idx, line) / ("append", None, line)."""
    out = copy.deepcopy(row)
    lines = list(out["output"])
    for kind, idx, line in ops:
        if kind == "insert":
            lines.insert(idx, line)
        else:
            lines.append(line)
    out["output"] = lines
    out["_mut_note"] = label
    return out


def build_evasions(rows):
    ev = []
    cases = {}

    def base(name):
        if name not in cases:
            cases[name] = find_row(rows, BASES[name])[1]
        return cases[name]

    for k in BASES:  # resolve every base so green controls always exist
        base(k)

    # s1 banner-foreign: forged banner-shaped line mid-stream.
    ev.append(("s1a_banner_forged_seq", mutate(
        base("seq"), [("insert", 2, FORGED_BANNER)],
        "forged banner at idx2 of r100b_seq_clean")))
    ev.append(("s1b_banner_dup_launch", mutate(
        base("launch"), [("insert", 4, BANNER)],
        "exact banner duplicate at idx4 of export_launch_embed_boot")))

    # s2 diag-prefixed foreign: designed-verb prefix, unaccounted payload.
    ev.append(("s2a_diag_other_family_simple", mutate(
        base("simple"), [("insert", 3, "EXPORT_LAUNCH_DIAG embed forged=true")],
        "foreign DIAG line into input_route (no DIAG in its account)")))
    ev.append(("s2b_diag_forged_launch", mutate(
        base("launch"), [("insert", 6, "EXPORT_LAUNCH_DIAG embed forged=1")],
        "forged same-family DIAG line inside export_launch account")))

    # s3 PASS-flood: extra PASS lines beyond the account.
    flood5 = ["PASS flooded=%d extra=true" % n for n in range(1, 6)]
    ev.append(("s3a_flood5_simple", mutate(
        base("simple"), [("append", None, ln) for ln in flood5],
        "5 forged PASS lines appended to 1-PASS row")))
    ev.append(("s3b_flood1_seq", mutate(
        base("seq"), [("append", None, "PASS r100_gui forged=1")],
        "1 forged PASS line appended to 14-PASS allowlisted row")))

    # s4 whitespace-pass: PASS-shaped lines evading naive whitespace scans.
    wl = base("simple")["output"][-1]
    ev.append(("s4a_tab_lead_simple", mutate(
        base("simple"), [("append", None, "\tPASS forged=true")],
        "leading-tab forged PASS line")))
    ev.append(("s4b_trail_space_simple", mutate(
        base("simple"), [("append", None, wl + " ")],
        "trailing-space duplicate of the legit PASS line")))
    ev.append(("s4c_trail_nbsp_simple", mutate(
        base("simple"), [("append", None, "PASS forged=true\u00a0")],
        "trailing NBSP (U+00A0) forged PASS line")))
    ev.append(("s4d_tab_after_pass_simple", mutate(
        base("simple"), [("append", None, "PASS\tforged=true")],
        "TAB after PASS token instead of space")))
    return ev, cases


def emit(gate_path=None):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    data, run_sha = load_run()
    rows = data["results"]
    ev, cases = build_evasions(rows)
    payload = {
        "run": str(RUN), "run_sha256": run_sha, "n_rows": len(rows),
        "bases": {k: {"case": BASES[k], "row_index": find_row(rows, BASES[k])[0]}
                  for k in BASES},
        "evasions": [{"name": n, "note": r.pop("_mut_note", ""), "row": r}
                     for n, r in ev],
        "green_controls": [{"name": "green_%s" % k, "row": cases[k]}
                           for k in BASES],
    }
    dest = SCRATCH / "evasions.json"
    dest.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    print("WROTE %s (%d bytes)" % (dest, dest.stat().st_size))
    print("run=%s sha256=%s rows=%d" % (RUN, run_sha, len(rows)))
    for name, row in ev:
        note = row.get("_mut_note", "")
        ins = [l for l in row["output"]
               if l in (FORGED_BANNER, BANNER, "EXPORT_LAUNCH_DIAG embed forged=true",
                        "EXPORT_LAUNCH_DIAG embed forged=1", "PASS r100_gui forged=1",
                        "\tPASS forged=true", "PASS forged=true\u00a0",
                        "PASS\tforged=true") or l.startswith("PASS flooded=")]
        print("%-26s n_out=%2d inserted=%d sha(inserted)=%s" %
              (name, len(row["output"]), len(ins),
               ",".join(sha256_text(x)[:12] for x in ins)))
        for x in ins:
            print("      + %r" % x)
    return payload


def load_gate(path):
    SCRATCH.mkdir(parents=True, exist_ok=True)
    copy = SCRATCH / "gate.py"
    shutil.copyfile(path, copy)
    src = copy.read_bytes()
    spec = importlib.util.spec_from_file_location("r103_mut5_gate", copy)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("GATE_COPY=%s sha256=%s bytes=%d" %
          (copy, hashlib.sha256(src).hexdigest(), len(src)))
    names = [n for n in dir(mod) if not n.startswith("_")]
    print("GATE_MODULE_FUNCS=%s" % names)
    for want in ("receipt_shape_gate", "receipt_gate", "meta_gate",
                 "gate_receipts", "gate_records", "gate", "scan_receipts",
                 "check_receipts", "receipts_gate"):
        if hasattr(mod, want) and callable(getattr(mod, want)):
            print("GATE_FUNC=%s" % want)
            return getattr(mod, want)
    raise SystemExit("no callable gate function found in %s" % path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate")
    ap.add_argument("--emit-only", action="store_true")
    args = ap.parse_args()
    payload = emit()
    if args.emit_only or not args.gate:
        return 0
    fn = load_gate(Path(args.gate))
    # Call style is finalized against the landed prototype; the landing seat
    # ships either a per-record predicate or a per-list scan. Try list first.
    rows = [e["row"] for e in payload["evasions"]]
    try:
        res = fn(rows)
    except TypeError:
        res = [fn(r) for r in rows]
    print("GATE_RESULT_TYPE=%s" % type(res).__name__)
    print(json.dumps(res, indent=1, default=str)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
