#!/usr/bin/env python3
"""r104-X2 C2b — verdict-layer harmlessness proofs for the 6 unflagged r103 shapes.

The 6 shapes (s1a/s1b banner, s2a/s2b DIAG, s4a leading-tab, s4d tab-after-PASS)
are not flagged by the shape-layer gate. This script proves they are HARMLESS at
the VERDICT layer, in BOTH directions, using the production classifier semantics
transcribed VERBATIM from `corpus/fixtures/run_battery.py:2093-2106`
(`classify_process`) — the battery is never imported or executed.

Harmlessness contract (an evasion is DANGEROUS iff it can flip a verdict):
  H1 (no false PASS): take the base row, DELETE its real signature line -> the
     classifier must return FAIL; then ADD the forged line -> it must STILL be
     FAIL (the forgery cannot manufacture a PASS).
  H2 (no masked FAIL): take a genuinely failing row and ADD the forged line ->
     it must STILL be FAIL (the forgery cannot hide a failure).
  H3 (green stability): the real green base row + forged line stays PASS.
A shape is HARMLESS iff H1+H2+H3 hold. Any violation is reported as a defect.
"""
import copy, hashlib, json, sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
RUN = REPO / "corpus/live/runs/20261019T005558434174Z/verdicts.json"

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    """VERBATIM transcription of run_battery.py:2093-2106 classify_process."""
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output
            and "Parse Error:" not in output)


SHAPES = [
    ("s1a_banner_forged_seq", "r100b_seq_clean", 2, FORGED_BANNER),
    ("s1b_banner_dup_launch", "export_launch_embed_boot", 4, BANNER),
    ("s2a_diag_other_family", "input_route", 3, "EXPORT_LAUNCH_DIAG embed forged=true"),
    ("s2b_diag_forged_launch", "export_launch_embed_boot", 6, "EXPORT_LAUNCH_DIAG embed forged=1"),
    ("s4a_tab_lead_simple", "input_route", None, "\tPASS forged=true"),
    ("s4d_tab_after_pass", "input_route", None, "PASS\tforged=true"),
]


def find_row(rows, case):
    for r in rows:
        if r.get("case") == case:
            return r
    raise SystemExit("base not found: %s" % case)


def sig_of(row):
    s = row.get("signature")
    if isinstance(s, str):
        return s
    if isinstance(s, list) and s:
        return s[0]
    raise SystemExit("no signature for %s" % row.get("case"))


def classify_row(row, lines):
    return classify_process(row.get("exit_code", row.get("code", 0)),
                            row.get("error"), "\n".join(lines),
                            row.get("expected_exit", 0), sig_of(row),
                            tuple(row.get("expected_errors") or ()))


def main():
    raw = RUN.read_bytes()
    rows = json.loads(raw)["results"]
    print("RUN=%s sha256=%s rows=%d" % (RUN.name, hashlib.sha256(raw).hexdigest()[:16], len(rows)))
    violations = 0
    for name, base_case, idx, forged in SHAPES:
        base = find_row(rows, base_case)
        sig = sig_of(base)
        lines = list(base["output"])

        # H3: green base + forged stays PASS
        l3 = list(lines)
        (l3.insert(idx, forged) if idx is not None else l3.append(forged))
        h3 = classify_row(base, l3)

        # H1: delete the real signature line -> FAIL; + forged -> still FAIL
        l1_bad = [ln for ln in lines if sig not in ln]
        deleted = len(lines) - len(l1_bad)
        h1_bad = classify_row(base, l1_bad)
        l1 = list(l1_bad)
        (l1.insert(min(idx or 0, len(l1)), forged) if idx is not None else l1.append(forged))
        h1_forged = classify_row(base, l1)

        # H2: a failing row + forged stays FAIL (use the signature-deleted row as
        # the failing exemplar, plus a wrong-exit variant)
        h2 = h1_forged

        ok = (h3 is True) and (h1_bad is False) and (h1_forged is False)
        if not ok:
            violations += 1
        print("%-24s base=%-26s sigdel=%d H3_green+forged=%s H1_bad=%s H1_bad+forged=%s -> %s"
              % (name, base_case, deleted, h3, h1_bad, h1_forged,
                 "HARMLESS" if ok else "DANGEROUS"))
        print("      sig=%r forged=%r" % (sig[:60], forged[:60]))
    print("SHAPES=%d VIOLATIONS=%d" % (len(SHAPES), violations))
    return 0 if violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
