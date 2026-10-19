#!/usr/bin/env python3
"""r103c-C2: reference receipt-shape META gate v2 (scratch prototype).

Operates on stored per-row verdict records ONLY; never touches the classifier.

Rule set (v2; each rule backed by an all-green census over r101 x2 + r102 x2):
  R0 scope: content rules audit verdict=PASS rows only. A FAIL record is not a
     green receipt. Unknown verdict values flag.
  R1 schema fail-closed: output list[str] or None; output None allowed only for
     the frozen opaque set (probe_* meta rows).
  R2 banner: exactly one banner line, at index 0, engine version pinned.
  R3 PASS shape: PASS-shaped lines (lstrip starts with PASS) must be canonical
     (raw `PASS ` prefix, no trailing whitespace) -- catches tab-lead, trailing
     space/NBSP, tab-after-PASS forgeries.
  R4 PASS account: canonical PASS lines must be byte-equal to a frozen
     case/script allow-list line or start with the row's own signature payload;
     exact duplicates inside one record flag.
  R5 non-PASS account: blank/banner ok; ERROR-bearing lines accounted by the
     row's expected_errors (classifier-mirror) OR by the row's own signature
     being contained in the line (mutant/export rows whose pin IS an ERROR);
     remaining lines token-known to the row's script (frozen per-script verb
     registry), with foreign `key=` atoms flagged against the frozen key-set.
  R6 signature presence: for PASS rows with a signature, a str pin must appear in
     the output text; a list pin requires at least one listed payload present
     (the r87 any-listed-payload whitelist precedent, 8 cases/run); exceptions
     only via the frozen sig_offline set AND a non-empty export_artifact field
     (substance clause).
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
DEFAULT_REGISTRY = Path(__file__).with_name("r103-crit2-registry.json")
FALLBACK_REGISTRY = Path("/var/tmp/r103c-C2/registry.json")
KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
DEFAULT_RUNS = [
    "corpus/live/runs/20261018T200239625248Z/verdicts.json",
    "corpus/live/runs/20261018T202131127599Z/verdicts.json",
    "corpus/live/runs/20261018T212500022987Z/verdicts.json",
    "corpus/live/runs/20261018T213443471189Z/verdicts.json",
]


def token_of(line):
    if line != line.lstrip():
        stripped = line.lstrip()
        return "<ind> " + stripped.split(" ")[0].split("\t")[0]
    return line.split(" ")[0].split("\t")[0]


def load_registry(path=None):
    p = Path(path) if path else (DEFAULT_REGISTRY if DEFAULT_REGISTRY.exists()
                                else FALLBACK_REGISTRY)
    return json.loads(p.read_text())


def exp_allowed(stripped, exp):
    for e in exp:
        if stripped == e:
            return True
        if e.endswith(",") and stripped.startswith(e) and stripped.count("ERROR:") == 1:
            return True
        if e == "ERROR: chain incomplete":
            if (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped
                    and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1):
                return True
    return False


def receipt_gate(r, reg):
    """Return list of flag strings for one stored record."""
    flags = []
    case = r.get("case")
    script = r.get("script")
    out = r.get("output")
    sig = r.get("signature")
    verdict = r.get("verdict")
    if verdict not in ("PASS", "FAIL"):
        flags.append("malformed_verdict=%r" % (verdict,))
        return flags
    if verdict != "PASS":
        return flags  # R0: FAIL receipts are not green evidence
    if out is None:
        if case not in set(reg["opaque_cases"]):
            flags.append("missing_output")
        return flags
    if not (isinstance(out, list) and all(isinstance(x, str) for x in out)):
        flags.append("malformed_output")
        return flags

    # R2 banner layout + version pin
    bi = [i for i, l in enumerate(out) if l.startswith("Godot Engine v")]
    if bi != [0]:
        flags.append("banner_layout=%s" % bi)
    for i in bi:
        if not any(out[i].startswith(p) for p in reg["engine_pins"]):
            flags.append("banner_version@%d" % i)

    # R3 PASS shape
    for i, l in enumerate(out):
        if l.lstrip().startswith("PASS"):
            if not l.startswith("PASS ") or l != l.rstrip():
                flags.append("pass_shape@%d=%r" % (i, l[:70]))

    # R4 PASS account
    pins = []
    if isinstance(sig, str):
        pins = [p for p in sig.split("\n") if p.startswith("PASS")]
    elif isinstance(sig, (list, tuple)):
        pins = [p for p in sig if isinstance(p, str) and p.startswith("PASS")]
    allow = set(reg["pass_lines_by_case"].get(case, []))
    allow_script = set(reg["pass_lines_by_script"].get(script, []))
    seen = collections.Counter()
    for i, l in enumerate(out):
        if not l.startswith("PASS "):
            continue
        seen[l] += 1
        if l in allow or l in allow_script:
            continue
        if any(l == p or l.startswith(p) for p in pins):
            continue
        flags.append("pass_unaccounted@%d=%r" % (i, l[:110]))
    for l, n in seen.items():
        if n > 1:
            flags.append("pass_dup=%r" % l[:70])

    # R5 non-PASS account
    exp = r.get("expected_errors") or []
    regscript = reg["scripts"].get(script, {})
    for i, l in enumerate(out):
        s = l.strip()
        if not s or l.startswith("Godot Engine v") or l.startswith("PASS "):
            continue
        if "ERROR:" in l:
            if exp_allowed(s, exp):
                continue
            if isinstance(sig, str) and sig and sig in l:
                continue
            flags.append("unaccounted_error@%d=%r" % (i, l[:90]))
            continue
        tok = token_of(l)
        info = regscript.get(tok)
        if info is None:
            flags.append("unaccounted_line@%d tok=%r" % (i, tok[:60]))
            continue
        keys = set(KEY_RE.findall(l))
        extra = keys - set(info["keys"])
        if extra:
            flags.append("diag_key@%d tok=%r extra=%s" % (i, tok[:40], sorted(extra)))

    # R6 signature presence: str pin must appear; list pin = any listed payload
    text = "\n".join(out)
    sig_missing = False
    if isinstance(sig, str) and sig:
        sig_missing = sig not in text
    elif isinstance(sig, (list, tuple)):
        members = [s for s in sig if isinstance(s, str) and s]
        sig_missing = bool(members) and not any(s in text for s in members)
    if sig_missing:
        offline = set(reg.get("sig_offline_cases", []))
        if case in offline and r.get("export_artifact"):
            pass
        else:
            flags.append("sig_absent")
    return flags


def receipt_shape_gate(records, reg=None):
    """Records -> list of {case, flags} for flagged rows (empty = all clean)."""
    reg = reg or load_registry()
    flagged = []
    for r in records:
        f = receipt_gate(r, reg)
        if f:
            flagged.append({"case": r.get("case"), "flags": f})
    return flagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--registry")
    ap.add_argument("--json-out")
    args = ap.parse_args()
    reg = load_registry(args.registry)
    runs = args.run or DEFAULT_RUNS
    report = {}
    for rel in runs:
        d = json.loads((REPO / rel).read_bytes())
        rows = d["results"]
        flagged = receipt_shape_gate(rows, reg)
        run_consistent = not (d.get("verdict") == "PASS"
                              and any(r.get("verdict") != "PASS" for r in rows))
        report[rel] = {"rows": len(rows), "flagged": len(flagged),
                       "run_verdict": d.get("verdict"),
                       "run_verdict_consistent": run_consistent,
                       "cases": flagged[:80]}
        print("%-66s rows=%d flagged=%d run_verdict=%s consistent=%s" % (
            rel, len(rows), len(flagged), d.get("verdict"), run_consistent))
        for f in flagged[:40]:
            print("   %-38s %s" % (f["case"], f["flags"][:4]))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
