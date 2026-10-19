#!/usr/bin/env python3
"""r103-W2 — diag-account prototype + FROZEN regex proposal for the C2
receipt-shape META gate (seat W2 deliverable, round 103).

What this is: a per-record line account over STORED verdict records ONLY
(verdicts.json `results[*]`), implementing the final diag-prefix rules that
account for every non-PASS, non-engine line a green battery record may carry,
while flagging foreign content. It never touches the classifier and never runs
run_battery.py; it reads the two r102 green runs (554 rows each) and mut05's
evasion corpus.

Account classes, per output line (order matters):
  1. BLANK            ^\\s*$
  2. BANNER index 0   ^Godot Engine v\\d+\\.\\d+\\.\\d+   (index 0 only; any other
                      banner-shaped line -> BANNER_POS; catches mut05 s1a/s1b)
  3. PASS             strict ^PASS  (single space, no leading whitespace); a
                      PASS line must (a) carry a per-case tag seen green, and
                      (b) not exceed the per-case PASS count cap (-> PASS_TAG /
                      PASS_COUNT; catches mut05 s3a/s3b/s4b/s4c; tab-led and
                      `PASS\\t` forms fall through to FOREIGN; s4a/s4d)
  4. ENGINE block     `ERROR: `/`WARNING: ` start a block; block continuation
                      lines (at:, GDScript backtrace, [N] frames, tab-led,
                      "The following presets", 8-space quoted, "Use ") are
                      accounted; crash blocks (handle_crash:, ====, double free
                      or corruption, /usr/include/) likewise. Per-case counts of
                      block starts must not exceed the green-census cap
                      (ENGINE_ERR_UNEXPECTED / ENGINE_CRASH_UNEXPECTED).
  5. DIAG             FAMILY_RE (the frozen diag-prefix regex below) names the
                      line's family token; the token must be bound to the row's
                      script (DIAG_UNBOUND) and, for families with key=value
                      payloads, every bare-word key must be in that family's
                      r102 key vocabulary (DIAG_KEY; catches mut05 s2a/s2b).
  6. TOOL/PROBE       ANSI / `[`-prefixed lines for the export-tool
                      pseudo-scripts __godot_export__ / __godot_export_missing__.
  7. FOREIGN          anything else -> flag.

PIN: `signature in output` is a substring test (run_battery.py:1808); the
account mirrors it (list signatures: any element). Rows carrying an
`export_artifact` receipt (export meta rows) are exempt from the pin test.

Usage (repo root):
  python3 reports/round-103/mutations/r103-w2-account.py \\
    --ref corpus/live/runs/20261018T212500022987Z/verdicts.json \\
          corpus/live/runs/20261018T213443471189Z/verdicts.json \\
    --check <same or later runs...> [--evasions evasions.json] [--detail]
    [--dump-tables reports/round-103/mutations/r103-w2-famtables.json]

Evidence (2026-10-18, seat W2): green r102 runs -> 0 flags each; mut05's 10
evasions -> all flagged (codes in shard r103-w2.md); 4 green controls -> silent.
Hard rules honoured: run_battery.py never executed; no shared file edited; the
frozen tables are a separate JSON artifact for G1; scratch used /var/tmp only.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

BANNER_RE = re.compile(r"^Godot Engine v[0-9]+\.[0-9]+\.[0-9]+")
PASS_RE = re.compile(r"^PASS ")
BLANK_RE = re.compile(r"^\s*$")
ANSI_RE = re.compile(r"^\x1b\[[0-9;]*m")
BRACKET_RE = re.compile(r"^\[")
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
EXPORT_TOOL_SCRIPTS = {"__godot_export__", "__godot_export_missing__"}

# ---- THE FROZEN DIAG-PREFIX REGEX (W2 final proposal) -----------------------
# Family token = first token of a designed diagnostic line. Complete against
# the r102 stored-stdout census (85 distinct tokens over 2079 diag lines/run;
# every token also has an emission site in its script's source, except the
# helper-built R-families, whose literal prefix is present once per script).
FAMILY_RE = re.compile(
    r"^(?:R\d+[A-Z]*"
    r"|SEQ_(?:BEGIN|CENSUS|DONE|END)"
    r"|EXPORT_[A-Z0-9_]+_DIAG"
    r"|S03_DIAG"
    r"|(?:BUTTON|CHECKBOX|SLIDER|HEALTH_GAUGE)(?:_[A-Z0-9_]+)*"
    r"|OBSERVED|STALE|NAV_LATTICE_TEARDOWN_CRASH"
    r"|DESCENDANT_PIPE(?:_[A-Z]+)*"
    r"|SPONTANEOUS_CRASH_PROBE:"
    r"|FEATVEC|TEXPROBE|E6_S06_[A-Z]+"
    r"|DIV_S02_[A-Z]+|S03_MARKER|LAUNCH_S02_[A-Z]+"
    r"|EXPORT_(?:PROD|LAUNCH)_(?:MAIN|FRAME)"
    r"|arm=[a-z_]+|g_low|g_up|ei=-?\d+)(?=[\s=:]|$)")

ERR_START = re.compile(r"^(?:ERROR: |WARNING: )")
ERR_CONT = re.compile(r"^(?: {0,12}at: | {0,12}GDScript backtrace \(most recent call first\):"
                      r"| {0,12}\[\d+\] |\t|The following presets| {8}\"|Use )")
CRASH_START = re.compile(r"^(?:handle_crash:|====|double free or corruption|/usr/include/)")
CRASH_CONT = re.compile(r"^(?:handle_crash:|Engine |Dumping|Load |====|--|\[\d+\] "
                        r"|    \[\d+\] |GDScript backtrace \(most recent call first\):"
                        r"|-- END OF [A-Z+ ]+ BACKTRACE --|double free or corruption|/usr/include/|\t)")


def load_rows(p):
    return json.load(open(p))["results"]


def tag_of(line):
    toks = line.split(" ")
    if len(toks) >= 2 and IDENT_RE.match(toks[1]):
        return toks[0] + " " + toks[1]
    return toks[0]


def build_tables(runs):
    fams = collections.defaultdict(set)
    vocab = collections.defaultdict(set)
    caseinfo = {}
    for rows in runs:
        for r in rows:
            ci = caseinfo.setdefault(r["case"], {"tags": set(), "maxpass": 0,
                                                 "maxerr": 0, "maxcrash": 0})
            o = r.get("output")
            if o is None:
                continue
            npass = nerr = ncrash = 0
            for ln in o:
                if BLANK_RE.match(ln) or BANNER_RE.match(ln):
                    continue
                if PASS_RE.match(ln):
                    npass += 1
                    ci["tags"].add(tag_of(ln))
                    continue
                if ANSI_RE.match(ln):
                    continue
                if ERR_START.match(ln):
                    nerr += 1
                    continue
                if CRASH_START.match(ln):
                    ncrash += 1
                    continue
                m = FAMILY_RE.match(ln)
                if not m:
                    continue
                tok = m.group(0)
                fams[r.get("script")].add(tok)
                for w in ln[len(tok):].split(" "):
                    if KEY_RE.match(w):
                        vocab[tok].add(w.split("=")[0])
            ci["maxpass"] = max(ci["maxpass"], npass)
            ci["maxerr"] = max(ci["maxerr"], nerr)
            ci["maxcrash"] = max(ci["maxcrash"], ncrash)
    return fams, vocab, caseinfo


def account_record(r, fams, vocab, caseinfo, multi_allow):
    flags = []
    o = r.get("output")
    if o is None:
        return flags  # 16 meta rows: fail-closed clause is G0's spec decision
    sc = r.get("script")
    ci = caseinfo.get(r["case"], {"tags": set(), "maxpass": 0, "maxerr": 0, "maxcrash": 0})
    allowed = set(multi_allow.get(r["case"], []))
    npass = nerr = ncrash = 0
    state = None
    for i, ln in enumerate(o):
        if BLANK_RE.match(ln):
            continue
        if i == 0 and BANNER_RE.match(ln):
            continue
        if BANNER_RE.match(ln):
            flags.append(("BANNER_POS", i, ln))
            continue
        if PASS_RE.match(ln):
            npass += 1
            if ln not in allowed and tag_of(ln) not in ci["tags"]:
                flags.append(("PASS_TAG", i, ln))
            if npass > ci["maxpass"]:
                flags.append(("PASS_COUNT", i, ln))
            continue
        if state == "err" and ERR_CONT.match(ln):
            continue
        if state == "crash" and CRASH_CONT.match(ln):
            continue
        state = None
        if ERR_START.match(ln):
            state = "err"
            nerr += 1
            continue
        if CRASH_START.match(ln):
            state = "crash"
            ncrash += 1
            continue
        if sc in EXPORT_TOOL_SCRIPTS and (ANSI_RE.match(ln) or BRACKET_RE.match(ln)):
            continue
        m = FAMILY_RE.match(ln)
        if m:
            tok = m.group(0)
            if tok not in fams.get(sc, set()):
                flags.append(("DIAG_UNBOUND", i, ln))
                continue
            for w in ln[len(tok):].split(" "):
                if KEY_RE.match(w) and w.split("=")[0] not in vocab.get(tok, set()):
                    flags.append(("DIAG_KEY", i, ln))
                    break
            continue
        flags.append(("FOREIGN", i, ln))
    if nerr > ci["maxerr"]:
        flags.append(("ENGINE_ERR_UNEXPECTED", -1, "n=%d cap=%d" % (nerr, ci["maxerr"])))
    if ncrash > ci["maxcrash"]:
        flags.append(("ENGINE_CRASH_UNEXPECTED", -1, "n=%d cap=%d" % (ncrash, ci["maxcrash"])))
    sig = r.get("signature")
    if sig and not r.get("export_artifact"):
        out_text = "\n".join(o)
        ok = any(s in out_text for s in sig) if isinstance(sig, list) else (sig in out_text)
        if not ok:
            flags.append(("PIN_SUBSTRING_MISSING", -1,
                          (sig if isinstance(sig, str) else repr(sig))[:80]))
    return flags


def dump_tables(fams, vocab, caseinfo, path):
    payload = {
        "generated_by": "reports/round-103/mutations/r103-w2-account.py",
        "generated_at": "2026-10-18",
        "scripts": {k: sorted(v) for k, v in fams.items()},
        "key_vocab": {k: sorted(v) for k, v in vocab.items()},
        "cases": {k: {"tags": sorted(v["tags"]), "maxpass": v["maxpass"],
                      "maxerr": v["maxerr"], "maxcrash": v["maxcrash"]}
                  for k, v in caseinfo.items()},
    }
    Path(path).write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    print("TABLES_DUMPED %s (%d bytes)" % (path, Path(path).stat().st_size))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", nargs="+", required=True, help="green runs the tables are frozen from")
    ap.add_argument("--check", nargs="+", required=True, help="runs to account against the tables")
    ap.add_argument("--census", default=str(Path(__file__).resolve().parents[3]
                    / "reports/round-103/mutations/r103-w4-census.json"))
    ap.add_argument("--evasions")
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--dump-tables")
    a = ap.parse_args()
    fams, vocab, caseinfo = build_tables([load_rows(p) for p in a.ref])
    cen = json.load(open(a.census))
    multi_allow = {e["case"]: e["pass_lines"] for k in ("run1", "run2") for e in cen[k]["multi"]}
    print("TABLES: family-tokens=%d vocab-families=%d cases=%d multi-cases=%d"
          % (sum(len(v) for v in fams.values()), len(vocab), len(caseinfo), len(multi_allow)))
    if a.dump_tables:
        dump_tables(fams, vocab, caseinfo, a.dump_tables)
    for p in a.check:
        tot = collections.Counter()
        ex = {}
        for r in load_rows(p):
            for code, i, ln in account_record(r, fams, vocab, caseinfo, multi_allow):
                tot[code] += 1
                ex.setdefault(code, (r["case"], i, ln[:120]))
        print("CHECK %s -> flags=%d %s" % (p, sum(tot.values()), dict(tot)))
        for c, (case, i, ln) in ex.items():
            print("   %-22s %s idx=%s %r" % (c, case, i, ln))
    if a.evasions:
        ev = json.load(open(a.evasions))
        print("\nEVASIONS (gate must FLAG each):")
        for e in ev["evasions"]:
            fl = account_record(e["row"], fams, vocab, caseinfo, multi_allow)
            print("  %-28s flags=%-2d %s" % (e["name"], len(fl), sorted(set(c for c, _, _ in fl))))
            if a.detail:
                for c, i, ln in fl[:8]:
                    print("       %-14s idx=%-3d %r" % (c, i, ln[:110]))
        print("GREEN CONTROLS (gate must be silent):")
        for e in ev["green_controls"]:
            fl = account_record(e["row"], fams, vocab, caseinfo, multi_allow)
            print("  %-28s flags=%d %s" % (e["name"], len(fl), sorted(set(c for c, _, _ in fl))))


if __name__ == "__main__":
    sys.exit(main())
