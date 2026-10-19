#!/usr/bin/env python3
"""r103 receipt-shape META gate — offline auditor over STORED verdict records ONLY.

Never imported by, nor invoked from, corpus/fixtures/run_battery.py; it makes
no change to the classifier. Input: one or more verdicts.json payloads
(written by run_battery.py at <runs>/<UTCstamp>/verdicts.json). Output: one
JSON audit report per input file + a console summary.

Flags (fail-closed where stated):
  schema:<field>          missing/ill-typed record field
  output_unreplayable     output is None although the record is process-bearing
  exit_or_error_state     verdict PASS but exit!=expected or error non-null
  signature_absent        signature string not contained in the merged output
  banner_shape            engine banner not exactly once / not at line 0
  foreign_line            output line matched by neither the row script's
                          print-literal census nor the engine-diagnostic regex
  unaccounted_pass_line   PASS-shaped line not covered by the pinned signature
                          nor the multi-PASS allowlist for that case
  pass_multiplicity       #PASS lines disagrees with signature/allowlist count

Usage:
  r103-receipt-shape-gate.py [--fixtures DIR] [--allowlist FILE] [-o OUTFILE] verdicts.json ...
  r103-receipt-shape-gate.py --census [--fixtures DIR] verdicts.json ...
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_FIXTURES = os.path.join(REPO, "corpus", "fixtures")

# ---------------------------------------------------------------- diag regex
# W2/G3 account: engine-authored line shapes observed in stored green runs
# (corpus/live/runs/20261018T21*). Anchored, no fixture vocabulary inside.
DIAG_RE = [
    r"^Godot Engine v[0-9]",                                   # banner (pos 0)
    r"^\s*$",                                                  # blank
    r"^\s*at: ",                                               # C++ backtrace frame
    r"^\s*GDScript backtrace \(most recent call first\):$",
    r"^\s*\[[0-9]+\] ",                                        # script backtrace frame
    r"^-- END OF (C\+\+|GDSCRIPT) BACKTRACE --$",
    r"^handle_crash: Program crashed with signal [0-9]+$",
    r"^Dumping the backtrace\. Please include this when reporting the bug on: ",
    r"^Load address: [0-9a-f]+$",
    r"^Engine version: Godot Engine v[0-9]",
    r"^(ERROR|WARNING|SCRIPT ERROR|USER ERROR|USER WARNING|Parse Error): ",
    r"^\tNavigationServer ",
    r"^Use NavigationServer2D\.parse_source_geometry_data\(\) and ",
    r"^\x1b\[0m$",
    r"^\x1b\[92m\[ DONE \]\x1b\[39m \x1b\[1m",                 # editor import done
    r"^\[ *[0-9]+% \] ",                                       # editor import progress
    r"^={16,}$",                                               # crash-handler rule
    r"^\[[0-9]+\] [0-9a-f]{6,} \(",                             # crash-handler C frame
    r"^double free or corruption \(!prev\)$",                  # glibc abort tail
    r"^/usr/include/c\+\+/",                                   # libstdc++ assert
    r"^The following presets were detected in this project's `export_presets\.cfg`:$",
    r'^ {8}"[^"`]{1,64}"$',                                    # export preset listing
]
DIAG_RE = [re.compile(p) for p in DIAG_RE]

BANNER = re.compile(r"^Godot Engine v[0-9]")

# ------------------------------------------------- per-script literal census
PRINT_CALL = re.compile(r"\b(?:print|print_rich|push_error|push_warning|printerr)\s*\(\s*\"((?:[^\"\\]|\\.)*)\"")
# rich-text tags the engine strips from print_rich before capture
RICH_STRIP = re.compile(r"\[/?[a-z][a-z0-9_=#]*\]")


def script_account(path):
    """Literal prefixes a script can print.

    T1a: first literal of every print-family call (authoritative grammar).
    T1b: any other source string literal >= 6 chars (probe/echo vocabulary that
    reaches stdout through consts, spliced prints and spawned shell echoes).
    """
    try:
        src = open(path, "r", encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    out = []
    for lit in PRINT_CALL.findall(src):
        lit = RICH_STRIP.sub("", lit)
        if "%" in lit:
            lit = lit.split("%")[0]                 # "FRAME %d" -> "FRAME "
        out.append(lit)
    for lit in re.findall(r"\"((?:[^\"\\]|\\.)*)\"", src):
        lit = RICH_STRIP.sub("", lit)
        if "%" in lit:
            lit = lit.split("%")[0]
        if len(lit) >= 6:
            out.append(lit)
    return list(dict.fromkeys(out))


def build_census(fixtures_dir):
    acc = {}
    for name in sorted(os.listdir(fixtures_dir)):
        if name.endswith(".gd") and name != "run_battery.py":
            acc[name] = script_account(os.path.join(fixtures_dir, name))
    # controls/ fixtures stage to scratch root; include them under their own name
    ctl = os.path.join(fixtures_dir, "controls")
    if os.path.isdir(ctl):
        for name in sorted(os.listdir(ctl)):
            if name.endswith(".gd"):
                acc["controls/" + name] = script_account(os.path.join(ctl, name))
    return acc


def line_accounted(line, script, census):
    """True iff line is a legit engine diag or starts with a literal the script prints."""
    for rx in DIAG_RE:
        if rx.match(line):
            return True
    for prefix in census.get(script, []):
        if prefix and line.startswith(prefix):
            return True
    return False


def pass_lines_of(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip().startswith("PASS")]


def print_site_prefixes(script, census):
    """Print-family literal prefixes only (T1a grammar), for PASS-family accounting."""
    return [p for p in census.get(script, []) if p.startswith("PASS") or p.startswith("EXPORT PASS")]


# row sentinels whose real script lives under a fixture filename
SENTINELS = {
    "__save_process_missing__": "save_process.gd",
    "__save_process_writer__": "save_process.gd",
    "__save_process_reader__": "save_process.gd",
}


def script_key(script):
    return SENTINELS.get(script, script)


def audit_record(rec, census, allowlist, idx):
    flags = []
    if not isinstance(rec, dict):
        return {"row": idx, "case": None, "flags": ["schema:record"]}
    case = rec.get("case")
    command = rec.get("command")
    process_bearing = command is not None
    if process_bearing:
        for f in ("case", "script", "verdict"):
            if not isinstance(rec.get(f), str) or not rec.get(f):
                flags.append(f"schema:{f}")
    else:
        if not isinstance(case, str) or not case:
            flags.append("schema:case")
    if "output" not in rec and process_bearing:
        flags.append("schema:output")
    out = rec.get("output")
    out_ok = isinstance(out, list) and all(isinstance(l, str) for l in out)
    if out is not None and not out_ok:
        flags.append("schema:output")
    expected_exit = rec.get("expected_exit")
    actual_exit = rec.get("actual_exit")
    verdict = rec.get("verdict")
    err = rec.get("error")
    signature = rec.get("signature")

    if verdict == "PASS":
        if actual_exit != expected_exit or err is not None:
            flags.append("exit_or_error_state")

    if not out_ok:
        # fail-closed: process-bearing record (has a command) must carry output
        if command is not None:
            flags.append("output_unreplayable")
        return {"row": idx, "case": case, "flags": flags}

    # signature may be a single string or a list of alternative signatures
    # (bimodal rows); each alternative counts as satisfied if contained.
    sig_ok = isinstance(signature, str) or (isinstance(signature, (list, tuple)) and all(isinstance(s, str) for s in signature))
    if process_bearing and not sig_ok:
        flags.append("schema:signature")
    if sig_ok:
        alts = [signature] if isinstance(signature, str) else list(signature)
    else:
        alts = []
    merged = "\n".join(out)
    contained = [a for a in alts if a and a in merged]
    if process_bearing:
        synthetic_export = alts and all(a.startswith("EXPORT PASS") for a in alts)
        if alts and not contained and not synthetic_export:
            flags.append("signature_absent")
    # export rows: signature is synthetic evidence; bind it to the artifact instead
    for a in alts:
        m = re.search(r"executable_bytes=(\d+)", a or "")
        art = rec.get("export_artifact")
        if m and isinstance(art, dict) and art.get("artifact_bytes") is not None:
            if int(m.group(1)) != art["artifact_bytes"]:
                flags.append("artifact_binding")

    # banner: exactly one, at line 0, when the record ran the engine
    bidx = [i for i, l in enumerate(out) if BANNER.match(l)]
    if len(bidx) > 1 or (bidx and bidx != [0]):
        flags.append("banner_shape")

    # line accounting (PASS lines are handled by the PASS-accounting block)
    for l in out:
        if l.strip().startswith("PASS"):
            continue
        if not line_accounted(l, script_key(rec.get("script")), census):
            flags.append("foreign_line")
            break

    # PASS-line accounting: the matched signature pins prefix-substrings of PASS
    # lines (classifier: `signature in "\n".join(output)`); the case allowlist
    # (multi-PASS rows) and the row script's own PASS print sites cover the rest.
    sig_pass = pass_lines_of(max(contained, key=len)) if contained else (pass_lines_of(alts[0]) if alts and not process_bearing else [])
    al = allowlist.get(case) if isinstance(case, str) else None
    al_lines = [l.strip() for l in al["pass_lines"]] if al else []
    out_pass = [l.strip() for l in out if l.strip().startswith("PASS")]
    sites = print_site_prefixes(script_key(rec.get("script")), census)

    def accounted(l):
        if any(l.startswith(s) for s in sig_pass):
            return True
        if any(l == a or l.startswith(a) for a in al_lines):
            return True
        if any(l.startswith(p) for p in sites):
            return True
        return False

    if any(not accounted(l) for l in out_pass):
        flags.append("unaccounted_pass_line")
    bound = max(len(sig_pass), al.get("count", 0) if al else 0, len(sites))
    if len(out_pass) > bound:
        flags.append("pass_multiplicity")
    return {"row": idx, "case": case, "flags": flags}


def audit(payload, census, allowlist):
    return [audit_record(r, census, allowlist, i) for i, r in enumerate(payload.get("results", []))]


def census_report(payload, census):
    total = passl = diag = fx = foreign = 0
    per_script_foreign = {}
    for rec in payload.get("results", []):
        out = rec.get("output")
        if not isinstance(out, list):
            continue
        for l in out:
            total += 1
            if l.strip().startswith("PASS"):
                passl += 1
                continue
            if any(rx.match(l) for rx in DIAG_RE):
                diag += 1
            elif any(p and l.startswith(p) for p in census.get(rec.get("script"), [])):
                fx += 1
            else:
                foreign += 1
                per_script_foreign.setdefault(rec.get("script"), []).append(l)
    return {"lines": total, "pass": passl, "engine_diag": diag, "script_literal": fx,
            "unaccounted": foreign, "unaccounted_samples": {k: v[:3] for k, v in list(per_script_foreign.items())[:8]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verdicts", nargs="+")
    ap.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    ap.add_argument("--allowlist", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "r103-w4-census.json"))
    ap.add_argument("--census", action="store_true")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    census = build_census(args.fixtures)
    allowlist = {}
    if args.allowlist and os.path.exists(args.allowlist):
        w4 = json.load(open(args.allowlist))
        for run in w4.values():
            for m in run.get("multi", []):
                allowlist.setdefault(m["case"], {"count": m["count"], "pass_lines": m["pass_lines"]})
    report = {"fixtures": args.fixtures, "fixture_scripts": len(census), "allowlist_cases": len(allowlist), "files": {}}
    for path in args.verdicts:
        payload = json.load(open(path))
        if args.census:
            report["files"][path] = census_report(payload, census)
        else:
            recs = audit(payload, census, allowlist)
            flagged = [r for r in recs if r["flags"]]
            report["files"][path] = {"rows": len(recs), "flagged": len(flagged), "flags": flagged[:40]}
    text = json.dumps(report, indent=1, sort_keys=True)
    if args.out:
        open(args.out, "w").write(text + "\n")
    print(text[:4000])
    bad = sum(v.get("flagged", 0) for v in report["files"].values()) if not args.census else 0
    if args.census:
        for p, c in report["files"].items():
            print(f"CENSUS {p}: lines={c['lines']} pass={c['pass']} diag={c['engine_diag']} script={c['script_literal']} unaccounted={c['unaccounted']}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
