#!/usr/bin/env python3
"""r103-G2 / mut09_replay.py — adversary replay harness against the G1 receipt-shape predicate.

Seat KEY=G2-ADVERSARY, round 103, lane game-dev-2d-shokunin.

WHAT "REPLAY-IMPORT" MEANS HERE
  G1 (the C2 gate seat) never landed an implementation: reports/round-103/r103-G1.md is
  plan-only and reports/round-103/mutations/ contains no gate file.  The only existing
  implementation of the receipt-shape predicate is the G0 prototype
  /var/tmp/r103-g0/proto_gate.py (sha256 pinned below).  This harness therefore
  *replays* stored verdict records through that predicate, *importing* its gate_row()
  verbatim (source is read, its driver tail -- the part from `report={` onward, which
  re-reads the corpus on import -- is cut, everything above it is exec'd).

  It never re-implements gate_row.  It adds, on top, the two clauses this seat's
  adversaries prove are missing (documented in the shard as ADV-1/ADV-2), plus the W4
  multi-PASS allowlist calibration, and reports RAW (prototype) and ARMED (prototype +
  calibration + ADV clauses) verdicts side by side.  No repo file is written; the
  battery is never executed; device-census tokens are never pinned.

USAGE
  python3 mut09_replay.py --check          # 5 attacks must ARMED-FLAG, 20 clean must be silent
  python3 mut09_replay.py --corpus-scan    # ARMED false-positive census over the 554-row run
  python3 mut09_replay.py --json-out F     # full result JSON
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import sys

PRED = "/var/tmp/r103c-G2/G1_predicate.py"
PRED_SHA = "416fe7975aef573e9c2faa08aae6c8917ac75ee3bffebf8620ec2bc6d41c2ccb"
CUT_AT = "\nreport={}"

MUT09_REL = "reports/round-102/mutations/mut09_export_launch_span_attack.json"
CENSUS_REL = "reports/round-103/mutations/r103-w4-census.json"
RUN_REL = "corpus/live/runs/20261018T213443471189Z/verdicts.json"

# Two real banner shapes exist: editor runs print `v<ver> (<build date>) - https://…`,
# exported/debug binaries print `v<ver> - https://…` (mut09 capture, r102).  Both are legitimate.
BANNER_RE = re.compile(r"^Godot Engine v(\S+)( \(.*\))? - https://godotengine\.org$")
ENGINE_GRAMMAR = re.compile(
    r"^(\s*Godot Engine v|$|ERROR: |\s+at: |\s+GDScript backtrace|\s+\[[0-9]+\] |WARNING: |"
    r"SCRIPT ERROR:|Parse Error:|UserWarning|\s+res://|\s+user://|"
    r".*ObjectDB instances were leaked)")
PRINT_RE = re.compile(r"""print(?:_rich|_err)?\(\s*(?:'([^']*)'|"([^"]*)")""")


def repo_root():
    return pathlib.Path(__file__).resolve().parents[3]


def import_predicate(path=PRED, allow_drift=False):
    """Exec proto_gate.py up to (not including) its corpus-reading driver."""
    src = pathlib.Path(path).read_text()
    sha = hashlib.sha256(src.encode()).hexdigest()
    if sha != PRED_SHA and not allow_drift:
        raise SystemExit(f"predicate sha256={sha} != pinned {PRED_SHA}; refusing (use --allow-drift)")
    head, sep, _tail = src.partition(CUT_AT)
    if not sep:
        raise SystemExit("predicate driver marker not found; refusing to guess")
    ns = {"__name__": "g1_predicate_replay"}
    exec(compile(head, path, "exec"), ns)
    for fn in ("gate_row", "SCRIPT_PASS_PINS"):
        if fn not in ns:
            raise SystemExit(f"predicate lacks {fn!r} after import; refusing")
    return ns, sha, len(head.encode())


def load_json(p):
    with open(p) as fh:
        return json.load(fh)


def allowlist_from_census(census, tag="run2"):
    out = {}
    for m in census[tag]["multi"]:
        out[m["case"]] = set(m["pass_lines"])
    return out


def fixture_literals(script, fixdir):
    """Exact literals + leading literal fragments from print-family calls in the fixture."""
    if not script:
        return set(), set()
    p = pathlib.Path(fixdir) / script
    if not p.exists():
        return set(), set()
    exact, prefix = set(), set()
    for m in PRINT_RE.finditer(p.read_text(encoding="utf-8", errors="replace")):
        lit = (m.group(1) if m.group(1) is not None else m.group(2))
        lit = lit.encode().decode("unicode_escape")
        if not lit:
            continue
        for part in lit.split("\n"):
            if part:
                exact.add(part)
        cut = len(lit)
        for hook in ("%", "{", "\\"):
            i = lit.find(hook)
            if i >= 0:
                cut = min(cut, i)
        if lit[:cut]:
            prefix.add(lit[:cut])
    return exact, prefix


def pins_of(rec):
    sig = rec.get("signature")
    if isinstance(sig, str):
        return [sig]
    if isinstance(sig, list) and sig and all(isinstance(x, str) for x in sig):
        return list(sig)
    return None


def armed_verdict(rec, ns, allow, fixdir, verbose=False):
    """RAW = prototype gate_row(); ARMED = RAW minus allowlist-calibrated false positives,
    plus ADV-1 (banner shape) and ADV-2 (foreign-line account)."""
    raw = list(ns["gate_row"](rec, set()))
    flags = list(raw)
    notes = []
    out = rec.get("output")
    pins = pins_of(rec)
    case = rec.get("case")

    # ---- calibration: exact-match PASS accounting with the W4 multi-PASS allowlist
    if isinstance(out, list) and pins is not None:
        allowed = allow.get(case, set())
        pred = ns["SCRIPT_PASS_PINS"]
        exp = []
        for P in pins:
            for pl in P.split("\n"):
                if pl.startswith("PASS "):
                    exp.append(pl)
        for name, P in pred.get(rec.get("script"), []):
            if name == case or "\n" in P:
                continue
            exp.append(P)
        avail = list(exp) + sorted(allowed)
        unmatched_obs = []
        for line in [x for x in out if x.startswith("PASS ")]:
            hit = next((i for i, P in enumerate(avail) if P in line), None)
            if hit is None:
                unmatched_obs.append(line)
            else:
                avail.pop(hit)
        if not unmatched_obs and "pass_line_unaccounted" in flags:
            flags.remove("pass_line_unaccounted")
            notes.append("calibrated:pass_line_unaccounted(allowlist)")
        untouched_own = []
        for P in pins:
            for pl in P.split("\n"):
                if pl.startswith("PASS ") and not any(pl in x for x in out):
                    untouched_own.append(pl)
        if untouched_own and case in allow and "own_pin_pass_line_absent" in flags:
            flags.remove("own_pin_pass_line_absent")
            notes.append(f"calibrated:own_pin_pass_line_absent(derived-receipt pin,{len(untouched_own)} line(s))")

    # ---- ADV-1: engine banner shape (exactly one banner, exact engine identity line)
    if isinstance(out, list):
        banners = [x for x in out if x.startswith("Godot Engine v")]
        if len(banners) != 1 or not BANNER_RE.match(banners[0]):
            flags.append(f"adv1:banner_shape(n={len(banners)})")

    # ---- ADV-2: foreign-line account over the captured stream
    if isinstance(out, list) and pins is not None:
        pin_lines = set()
        for P in pins:
            for pl in P.split("\n"):
                if pl:
                    pin_lines.add(pl)
        exact, prefix = fixture_literals(rec.get("script"), fixdir)
        accounted_pass = set()
        for P in pins:
            for pl in P.split("\n"):
                if pl.startswith("PASS "):
                    accounted_pass.add(pl)
        for P in allow.get(case, set()):
            accounted_pass.add(P)
        for name, P in ns["SCRIPT_PASS_PINS"].get(rec.get("script"), []):
            accounted_pass.add(P)
        foreign = []
        for line in out:
            if not line.strip() or ENGINE_GRAMMAR.match(line):
                continue
            if line in pin_lines or line in exact:
                continue
            if any(line.startswith(p) for p in prefix if p):
                continue
            if line.startswith("PASS "):
                matched = any(P in line for P in accounted_pass) or any(
                    P in line for P in allow.get(case, set()))
                if matched:
                    continue
                foreign.append(line)
                continue
            if line.split(" ", 1)[0].endswith("_DIAG") or line.startswith("SEQ_BEGIN"):
                continue
            foreign.append(line)
        if foreign:
            flags.append(f"adv2:foreign_line_unaccounted(n={len(foreign)},first={foreign[0][:60]!r})")

    return raw, sorted(set(flags)), notes


def mut09_base_record(mut09, variant):
    """Replay-import: a record whose stdout is the real captured bytes of that variant."""
    v = mut09["variants"][variant]
    base = mut09["variants"]["base"]
    pin = "\n".join(base["stdout_text"][2:])          # marker + FRAME 1..5
    rec = {
        "case": f"export_launch_span_{variant}",
        "script": "export_launch.gd",
        "verdict": "PASS",
        "expected_exit": 0,
        "expected_errors": [],
        "output": list(v["stdout_text"]),
        "signature": pin,
        "actual_exit": v.get("launch_exit", 0),
    }
    return rec, v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--predicate", default=PRED)
    ap.add_argument("--allow-drift", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--corpus-scan", action="store_true")
    ap.add_argument("--json-out")
    args = ap.parse_args()

    root = repo_root()
    ns, pred_sha, pred_bytes = import_predicate(args.predicate, args.allow_drift)
    mut09 = load_json(root / MUT09_REL)
    census = load_json(root / CENSUS_REL)
    allow = allowlist_from_census(census)
    corpus = load_json(root / RUN_REL)["results"]
    fixdir = root / "corpus/fixtures"
    by_case = {r["case"]: r for r in corpus}
    print(f"[predicate] {args.predicate} sha256={pred_sha} exec_bytes={pred_bytes} (driver tail cut at {CUT_AT!r})")
    print(f"[corpus]    {RUN_REL} rows={len(corpus)} allowlist_cases={len(allow)}")

    attacks = []

    def add(name, rec, expect, note):
        raw, armed, cal = armed_verdict(rec, ns, allow, fixdir)
        attacks.append({"attack": name, "case": rec.get("case"), "raw_flags": raw,
                        "armed_flags": armed, "calibration_notes": cal,
                        "expected": expect, "ok": bool(armed), "note": note,
                        "stdout_lines": len(rec.get("output") or [])})

    # ATT1 / ATT2 — mut09's two real captured span attacks (into-span, post-span)
    for variant, expect, note in (("A1", "adv2|adv1|multiline", "foreign line INSIDE the pinned marker->FRAME5 span"),
                                  ("A2", "adv2", "foreign line AFTER the pinned span")):
        rec, v = mut09_base_record(mut09, variant)
        add(f"mut09-{variant}", rec, expect, note)

    # ATT3 — PASS-flood: real row, extra PASS lines not covered by pin or allowlist
    flood = dict(by_case["export_launch_embed_boot"])
    flood["output"] = list(flood["output"]) + [
        "PASS export_launch embed_boot boot=true frames=[1,2,3] extra=false exit=0 cwd=isolated",
        "PASS r100_gui census dv=headless vpsize=(1.0, 1.0) final=FORGED",
        "PASS export_launch stock_census artifacts=99 pck_exists=true pck_magic=47445043 pck_bytes=1 bin_bytes=1",
    ]
    add("PASS-flood", flood, "pass_line_duplicate|pass_line_unaccounted|adv2",
        "3 forged PASS lines appended to a single-PASS row (1 pin-duplicate, 2 unaccounted)")

    # ATT4 — foreign line inside an existing seqfull multi-line pin span
    seq = dict(by_case["r101_seqfull_clean"])
    o = list(seq["output"])
    i = next(k for k, line in enumerate(o) if line.startswith("PASS ") and k > 2)
    o.insert(i, "FOREIGN_EXTRA injected=into_seqfull_span")
    seq["output"] = o
    add("foreign-in-seqfull-span", seq, "adv2|multiline",
        f"foreign line spliced at output[{i}] inside the r101_seqfull_clean pinned PASS sequence")

    # ATT5 — banner spoof (extra + rewritten banner line)
    spoof = dict(by_case["export_launch_stock_boot"])
    os_ = list(spoof["output"])
    os_[0] = "Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org"
    os_.insert(0, os_[0].replace("4.7.2.stable", "4.7.1.stable"))
    spoof["output"] = os_
    add("banner-spoof", spoof, "adv1", "engine identity line rewritten + duplicated banner")

    # ---- 20 clean records: the 19 W4 multi-PASS allowlist cases + 1 zero-PASS row
    clean = []
    for case in list(allow):
        rec = by_case.get(case)
        if rec is None:
            clean.append({"case": case, "missing": True})
            continue
        raw, armed, cal = armed_verdict(rec, ns, allow, fixdir)
        clean.append({"case": case, "raw_flags": raw, "armed_flags": armed,
                      "silent": not armed, "notes": cal})
    zero_pass = [r for r in corpus if r.get("output") and not any(
        x.startswith("PASS ") for x in r["output"])]
    for rec in zero_pass:
        raw, armed, cal = armed_verdict(rec, ns, allow, fixdir)
        if not armed:
            clean.append({"case": rec["case"], "raw_flags": raw, "armed_flags": [],
                          "silent": True, "notes": cal + ["zero-PASS designed-verb row"]})
            break

    n_flagged_attacks = sum(1 for a in attacks if a["ok"])
    n_silent_clean = sum(1 for c in clean if c.get("silent"))
    print(f"\n[attacks]   {n_flagged_attacks}/{len(attacks)} ARMED-flag")
    for a in attacks:
        print(f"  {'FLAG' if a['ok'] else 'MISS':4s} {a['attack']:24s} case={a['case']:34s} "
              f"lines={a['stdout_lines']:3d} armed={a['armed_flags']} raw={a['raw_flags']}")
    print(f"\n[clean]     {n_silent_clean}/{len(clean)} silent under ARMED")
    for c in clean:
        if not c.get("silent"):
            print(f"  NOISE {c['case']:34s} armed={c.get('armed_flags')} raw={c.get('raw_flags')}")

    result = {"predicate": {"path": args.predicate, "sha256": pred_sha, "exec_bytes": pred_bytes},
              "attacks": attacks, "clean": clean,
              "n_attacks_flagged": n_flagged_attacks, "n_clean_silent": n_silent_clean}

    if args.corpus_scan:
        noisy = []
        for rec in corpus:
            raw, armed, cal = armed_verdict(rec, ns, allow, fixdir)
            if armed:
                noisy.append({"case": rec["case"], "armed_flags": armed, "raw_flags": raw})
        result["corpus_scan"] = {"rows": len(corpus), "armed_noisy": len(noisy), "cases": noisy[:60]}
        print(f"\n[corpus-scan] ARMED flags {len(noisy)}/{len(corpus)} rows")
        for n in noisy[:25]:
            print(f"  {n['case']:34s} {n['armed_flags']}")

    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(result, fh, indent=1)
        print(f"\n[json] wrote {args.json_out}")

    if args.check:
        ok = n_flagged_attacks == len(attacks) and n_silent_clean == len(clean) and len(clean) == 20
        print(f"\n[check] attacks 5/5 and clean 20/20 silent -> {'OK' if ok else 'FAIL'}")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
