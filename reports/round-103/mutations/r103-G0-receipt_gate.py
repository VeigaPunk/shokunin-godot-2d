#!/usr/bin/env python3
"""r103 G0-SPEC — receipt-shape META gate (executable spec prototype).

Scope (C2): audit STORED verdict records only. Never touches classify_process,
never mutates run_battery.py. Reads the r102 run verdicts.json files plus the
w4 census allowlist; emits flags per the SPEC in reports/round-103/r103-G0.md.

Flag taxonomy
  F0  fail-closed: missing/malformed required field, or PASS row whose stored
      pin is absent from stored stdout (evidence-absent). Probe meta rows
      (case starts with "probe_" and no `signature` key and output None) are
      the only documented exemption.
  F1  unaccounted PASS-line: a PASS_RE line in `output` that cannot be debited
      (exact multiplicity) against the row pin's PASS-lines + the per-case
      allowlist entry from r103-w4-census.json.
  F2  foreign content inside a pinned span: pin has >=2 lines; pin first/last
      lines both appear in `output` (last after first) but the contiguous
      span match fails. Interior lines that are neither the span's own member
      line (positional) nor SPAN_LEGAL (blank only) are listed.

Label: every count printed here is [obs] over the named JSON inputs.
"""
import difflib
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

PASS_RE = re.compile(r"^\s*PASS(\b|$|[:=])")

# SPAN_LEGAL: lines tolerated strictly inside a pinned span. Drawn from the
# empirical census: stored green spans contain ONLY their own member lines, so
# the span-legal set is blank-only. The wider DIAG_RE (below) is the
# output-level account (preamble/epilogue advisory), deliberately NOT applied
# inside spans so a banner/diag spoof injected mid-span still flags.
SPAN_LEGAL_RE = re.compile(r"^\s*$")

# DIAG_RE (final proposal for the diag-account): union of the non-PASS print
# families empirically observed in the two r102 run verdicts.json records
# (first-token census; counts identical in run1/run2). Each alternative is
# anchored; PASS-lines never reach this regex (checked first).
DIAG_RE = re.compile(
    r"^(?:"
    r"\s*$"                                            # blank
    r"|Godot Engine v\S+ .*"                           # engine banner
    r"|ERROR: .*"                                      # Godot error report
    r"|\s+at: .*"                                      #   ...trace frame
    r"|\s*GDScript backtrace.*"                        #   ...backtrace head
    r"|\s*\[\d+\] .*"                                  #   ...stack frame
    r"|WARNING: .*"                                    # engine warning
    r"|The .*"                                         # multi-instance line
    r"|\s*\"Linux/X11\""                               # video driver line
    r"|\s*\[\s*\d+% \].*"                              # editor progress line
    r"|\x1b\[\d+m.*"                                   # ANSI-colored editor line
    r"|OBSERVED .*"                                    # probe verb
    r"|HEALTH_GAUGE_NEGATIVE.*"                        # fixture verb
    r"|SPONTANEOUS_CRASH_PROBE: .*"                    # probe verb
    r"|DESCENDANT_PIPE(_FORGE|_PROBE)?:?.*"            # probe verb
    r"|\s*NavigationServer .*|Use .*"                  # godot server lines
    r"|NAV_LATTICE_TEARDOWN_CRASH.*"                   # fixture verb
    r"|double .*"                                      # godot server line
    r"|-> .*|-- .*|=====.*"                            # separator shapes
    r"|handle_crash: .*|Engine .*|Dumping .*|Load .*"  # crash handler
    r"|SEQ_BEGIN .*|SEQ_CENSUS .*|SEQ_END .*"          # span framing verbs
    r"|SEQ_DONE.*"
    r"|R\d{2}[A-Z]* .*"                                # r79..r101 diag verbs
    r"|R101Y .*"
    r"|EXPORT_PROD_DIAG .*|EXPORT_LAUNCH_DIAG .*"
    r"|arm=[A-Za-z0-9_]+.*|ei=-?\d+.*"                 # census arm verbs
    r"|BUTTON_[A-Z_]+.*|CHECKBOX[A-Z_]*.*|SLIDER_[A-Z_]+.*"
    r"|/usr/include/.*"                                # libstdc++ assert text
    r")$"
)


def pin_of(record):
    """('str', lines) | ('envelope', [payload_lines, ...]) | (None, None).

    Matching run_battery.py semantics: a str signature is a single pin
    (substring over merged output); a list signature is an any-payload
    envelope (PASS iff ANY payload matches)."""
    sig = record.get("signature")
    if isinstance(sig, str):
        return "str", sig.splitlines()
    if isinstance(sig, (list, tuple)):
        payloads = []
        for item in sig:
            if not isinstance(item, str):
                return None, None
            payloads.append(item.splitlines())
        return "envelope", payloads
    return None, None


def load_allowlist(path):
    """Per-case exact PASS-line allowlist from the w4 census (run1 multi list)."""
    census = json.load(open(path))
    return {row["case"]: row["pass_lines"] for row in census["run1"]["multi"]}


def default_allowlist():
    import os
    cands = [os.environ.get("R103_W4_CENSUS"),
             "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/"
             "reports/round-103/mutations/r103-w4-census.json",
             str(Path(__file__).resolve().parents[3] /
                 "reports/round-103/mutations/r103-w4-census.json")]
    for c in cands:
        if c and Path(c).is_file():
            return load_allowlist(c)
    return {}


def receipt_shape_gate(records):
    """Public gate entry point (mut05 interface): audit a list of records."""
    allow = default_allowlist()
    return [{"case": c, "flag": f, "detail": d, "advisory": adv}
            for f, c, d, adv in audit(records, allow)]


def audit_row(record, allowlist):
    """Return list of (flag, detail) for one stored verdict record."""
    case = record.get("case")
    flags = []
    if not isinstance(case, str) or not case:
        return [("F0", "missing/malformed case field")]
    if "verdict" not in record:
        return [("F0", f"{case}: missing verdict field")]
    out = record.get("output")
    if out is None:
        # documented exemption: meta-probe records carry their own field sets
        if case.startswith("probe_") and "signature" not in record:
            return []
        return [("F0", f"{case}: output field is None (not an exempt meta probe)")]
    if not isinstance(out, list) or not all(isinstance(x, str) for x in out):
        return [("F0", f"{case}: output is not a list[str]")]
    kind, pin = pin_of(record)
    if kind is None:
        if "signature" in record and record.get("signature") is not None:
            return [("F0", f"{case}: signature is not str/list[str]")]
        # no pin recorded: legal only when the row has no PASS-lines
        if any(PASS_RE.match(ln) for ln in out):
            return [("F0", f"{case}: PASS verdict with PASS-lines but no signature pin")]
        return []
    joined = "\n".join(out)
    harness_row = str(record.get("script", "")).startswith("__")
    if record.get("verdict") == "PASS" and not harness_row:
        if kind == "str":
            present = ("\n".join(pin) in joined) if pin else True
        else:
            present = any("\n".join(pl) in joined for pl in pin)
        if not present:
            flags.append(("F0", f"{case}: stored pin absent from stored stdout (evidence-absent)"))
    # ---- F1: PASS-line accounting, exact multiplicity -------------------
    # Account-source precedence: when the case has a w4 allowlist entry, that
    # entry (full lines, exact multiplicity) IS the account; otherwise the
    # pin's own PASS-lines account, with substring semantics and pin
    # multiplicity (mirrors the harness's `signature in output` predicate).
    if case in allowlist:
        allow = Counter(allowlist[case])
        for i, ln in enumerate(out):
            if PASS_RE.match(ln):
                if allow[ln] > 0:
                    allow[ln] -= 1
                else:
                    flags.append(("F1", f"{case}: unaccounted PASS-line at out[{i}]: {ln[:120]!r}"))
    else:
        if kind == "str":
            rem = Counter(ln for ln in pin if ln)
        else:
            # envelope: a line is accounted with multiplicity = max count of
            # that line within any single payload (GD-5: envelope with exact
            # multiplicity, not a presence substring).
            per_line = {}
            for pl in pin:
                for ln, c in Counter(pl).items():
                    per_line[ln] = max(per_line.get(ln, 0), c)
            rem = Counter({ln: c for ln, c in per_line.items() if ln})
        # Self-report credit: a row whose pin is a non-PASS assertion (e.g.
        # save_process_missing pins an ERROR: line) may present exactly ONE
        # PASS line as its fixture self-report, but only when the pin's own
        # match landed on non-PASS output lines. Fragment pins that match
        # inside the PASS line itself get credit 0, so an appended forged
        # PASS line on such rows still flags.
        loc = [i for i, l in enumerate(out) if any(p in l for p in rem)]
        credit = 1 if (loc and not any(PASS_RE.match(out[i]) for i in loc)) else 0
        for i, ln in enumerate(out):
            if not PASS_RE.match(ln):
                continue
            cands = [p for p in rem if rem[p] > 0 and p in ln]
            if cands:
                rem[max(cands, key=len)] -= 1
            elif credit > 0:
                credit -= 1
            else:
                flags.append(("F1", f"{case}: unaccounted PASS-line at out[{i}]: {ln[:120]!r}"))
    # ---- F2: foreign content inside a pinned span (str pins only) ------
    if kind == "str" and len(pin) >= 2:
        first, last = pin[0], pin[-1]
        idx = [i for i, ln in enumerate(out) if ln == first]
        jdx = [i for i, ln in enumerate(out) if ln == last]
        if idx and jdx and jdx[-1] > idx[0]:
            s, e = idx[0], jdx[-1]
            interior = out[s:e + 1]
            if interior != pin:
                sm = difflib.SequenceMatcher(a=pin, b=interior, autojunk=False)
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag == "equal":
                        continue
                    for off in range(j1, j2):
                        ln = interior[off]
                        if SPAN_LEGAL_RE.match(ln):
                            continue
                        flags.append(("F2", f"{case}: foreign line inside pinned span at out[{s + off}]: {ln[:120]!r}"))
    return flags


def audit(results, allowlist):
    """[(flag, case, detail, advisory)] — advisory=True for verdict!=PASS rows.

    Scoping rule: the gate audits receipt CLAIMS. A FAIL row's claim is already
    false, so its shape findings are advisory only; the round-level gate
    verdict counts non-advisory flags (rows whose record verdict is PASS)."""
    allflags = []
    for r in results:
        adv = r.get("verdict") != "PASS"
        for flag, detail in audit_row(r, allowlist):
            allflags.append((flag, r.get("case"), detail, adv))
    return allflags


# ---------------- synthetic adversaries (built from stored records) --------
def mkrow(results, case):
    return next(r for r in results if r["case"] == case)


def adversaries(results):
    """(name, mutated record, expected flag) tuples."""
    advs = []
    r = json.loads(json.dumps(mkrow(results, "r101_seqfull_clean")))
    r["output"] = r["output"][:6] + [r["output"][7]] + r["output"][6:]
    advs.append(("AD1 foreign line spliced inside seqfull span", r, "F2"))
    r = json.loads(json.dumps(mkrow(results, "r101_seqfull_clean")))
    r["output"] = r["output"][:6] + ["Godot Engine v9.9.9.spoof banner replay"] + r["output"][6:]
    advs.append(("AD2 banner spoof inside seqfull span", r, "F2"))
    r = json.loads(json.dumps(mkrow(results, "export_prod_base_pck")))
    r["output"] = r["output"] + ["PASS export_prod forged=1"]
    advs.append(("AD3 forged PASS line appended (export_prod)", r, "F1"))
    r = json.loads(json.dumps(mkrow(results, "r100b_seq_clean")))
    r["output"] = r["output"] + [r["output"][7]]
    advs.append(("AD4 pin PASS-line duplicated (r100b)", r, "F1"))
    r = json.loads(json.dumps(mkrow(results, "r101_seqfull_clean")))
    r["output"] = r["output"][:6] + ["PASS r100_gui forged_cell=1"] + r["output"][6:]
    advs.append(("AD5 forged PASS inside seqfull span", r, "F1"))
    r = json.loads(json.dumps(mkrow(results, "r101_seqfull_clean")))
    del r["signature"]
    advs.append(("AD6 pinned PASS row with signature stripped", r, "F0"))
    r = json.loads(json.dumps(mkrow(results, "export_prod_base_pck")))
    r["output"] = None
    advs.append(("AD7 non-probe row with output=None", r, "F0"))
    r = json.loads(json.dumps(mkrow(results, "r101_seqfull_clean")))
    # drop SEQ_END: boundary present? first line yes, last line (SEQ_END) gone
    r["output"] = [ln for ln in r["output"] if not ln.startswith("SEQ_END")]
    advs.append(("AD8 SEQ_END removed (evidence-absent)", r, "F0"))
    r = json.loads(json.dumps(mkrow(results, "save_process_missing")))
    dup = next(ln for ln in r["output"] if PASS_RE.match(ln))
    r["output"] = r["output"] + [dup]
    advs.append(("AD9 self-report PASS-line duplicated (negative-assertion row)", r, "F1"))
    r = json.loads(json.dumps(mkrow(results, "export_readiness")))
    r["output"] = r["output"] + ["PASS export_readiness forged=1"]
    advs.append(("AD10 forged PASS on harness-verdict row", r, "F1"))
    r = json.loads(json.dumps(mkrow(results, "r93_tween_interp_grid_a")))
    r["output"] = r["output"] + ["PASS anim_lattice forged=1"]
    advs.append(("AD11 forged PASS appended to fragment-pin row", r, "F1"))
    return advs


def diag_census(results):
    counts = Counter()
    examples = {}
    for r in results:
        out = r.get("output") or []
        for ln in out:
            if PASS_RE.match(ln):
                continue
            tok = ln.split(None, 1)[0] if ln.strip() else "<blank>"
            counts[tok] += 1
            examples.setdefault(tok, ln)
    return counts, examples


def main():
    if "--all-runs" in sys.argv:
        allow = default_allowlist()
        for path in sorted(glob.glob("corpus/live/runs/*/verdicts.json")):
            rows = json.load(open(path))["results"]
            flags = audit(rows, allow)
            eff = [x for x in flags if not x[3]]
            by = Counter(f for f, _, _, _ in eff)
            adv = Counter(f for f, _, _, a in flags if a)
            print(f"[obs] {path}: rows={len(rows)} effective_flags={len(eff)} "
                  f"by_kind={dict(by)} advisory={dict(adv)}")
            for f, c, d, a in eff[:6]:
                print(f"      {f} {d}")
        return
    run1 = json.load(open("corpus/live/runs/20261018T212500022987Z/verdicts.json"))
    run2 = json.load(open("corpus/live/runs/20261018T213443471189Z/verdicts.json"))
    allowlist = load_allowlist("reports/round-103/mutations/r103-w4-census.json")
    print(f"[obs] allowlist cases: {len(allowlist)}")
    for tag, data in (("run1", run1), ("run2", run2)):
        flags = audit(data["results"], allowlist)
        adv = [x for x in flags if x[3]]
        print(f"[obs] {tag} green audit: effective_flags={len(flags) - len(adv)} "
              f"by_kind={dict(Counter(f for f, _, _, a in flags if not a))} "
              f"advisory_flags={len(adv)}")
        for f, c, d, a in flags[:10]:
            print(f"      {f}{' [advisory]' if a else ''} {d}")
    advs = adversaries(run1["results"])
    for name, row, want in advs:
        got = [f for f, _, _, _ in audit([row], allowlist)]
        ok = "OK" if want in got else "MISS"
        print(f"[obs] adversary {name}: expected {want} got={got or ['<none>']} -> {ok}")
    counts, examples = diag_census(run1["results"])
    fam = [t for t in counts if not PASS_RE.match(t)]
    print(f"[obs] non-PASS first-token families (run1): {len(fam)} tokens, "
          f"{sum(counts.values())} lines")
    # DIAG_RE coverage over the census lines
    covered, uncovered = 0, 0
    for r in run1["results"]:
        for ln in (r.get("output") or []):
            if PASS_RE.match(ln):
                continue
            if DIAG_RE.match(ln):
                covered += 1
            else:
                uncovered += 1
    print(f"[obs] DIAG_RE coverage of stored non-PASS lines: covered={covered} uncovered={uncovered}")


if __name__ == "__main__":
    main()
