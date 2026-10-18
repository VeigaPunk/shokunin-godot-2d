#!/usr/bin/env python3
"""mut08b — r102 seat M8: attack the LANDED export_launch_s04.gd output.

Inputs (produced by the phase-1/2 runs in /var/tmp/r102-mut8):
  s04_run1.out, s04_run2.out  — landed fixture, warm-warm pair (honest)
  s04_mut.out                 — landing fixture with INC_LOWER case-token flipped
                                ("case/*.txt" -> "case/*.TXT", scratch copy only)

Analysis (harness predicate = verbatim replica of run_battery.py:1775-1792;
s04 battery launch shape: run_battery.py:1912, 8s bound :1913):
  1. determinism: PASS lines of run1 vs run2 byte-equal?
  2. V1 pattern-payload swap: expected include=/exclude= payloads exchanged.
  3. V2 membership-set swap: the expected in-set (case plain files) becomes the
     out-set — boolean values of the plain-file membership partition inverted.
  4. V3 case-token flip on the fixture: mutant output vs honest pins, plus a
     pin-shape blindness matrix (which pin reductions still reject the flip).
  5. verdict lines MUT08B_*; receipt /var/tmp/r102-mut8/receipt_s04_landed.json.
"""
import json
import re
import sys

ROOT = "/var/tmp/r102-mut8"
PASS_RE = re.compile(r"^PASS export_launch_s04 \S+ .*$")
# membership partition of plain files in the case/ dir (E4 fixture design)
IN_FIELDS = ["one_in", "two_in", "three_in"]
OUT_FIELDS = ["other_in"]


def read_pass_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError as exc:
        return None, "", str(exc)
    lines = [ln for ln in text.splitlines() if PASS_RE.match(ln)]
    return lines, text, None


def fields(line):
    parts = line.split(" ")
    kind = parts[2]
    out = {}
    for tok in parts[3:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return kind, out


def rebuild(kind, f):
    return ("PASS export_launch_s04 %s %s"
            % (kind, " ".join("%s=%s" % (k, v) for k, v in f.items())))


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    """Verbatim replica of run_battery.py:1775-1792 (r101 tree, read-only copy)."""
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed)
                                    for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output
            and "Parse Error:" not in output)


def main():
    receipt = {"inputs": {}}
    run1, text1, err1 = read_pass_lines(ROOT + "/s04_run1.out")
    run2, text2, err2 = read_pass_lines(ROOT + "/s04_run2.out")
    mut, textm, errm = read_pass_lines(ROOT + "/s04_mut.out")

    if not run1 or not run2:
        print(f"MUT08B_MISSING run1={err1} run2={err2}")
        sys.exit(2)

    det = {
        "run1_lines": run1, "run2_lines": run2,
        "pass_lines_byte_equal": run1 == run2,
        "stdout_byte_equal": text1 == text2,
        "line_count": len(run1),
    }
    print(f"MUT08B_DETERMINISM pass_lines_equal={det['pass_lines_byte_equal']} "
          f"stdout_equal={det['stdout_byte_equal']} n={len(run1)}")
    receipt["determinism"] = det

    # ---- V1/V2 on each honest line.
    swaps = {}
    for line in run1:
        kind, f = fields(line)
        # V1: swap include/exclude pattern payloads.
        v1 = dict(f)
        v1["include"], v1["exclude"] = f["exclude"], f["include"]
        v1_line = rebuild(kind, v1)
        # V2: swap the expected membership sets (in-partition booleans inverted
        # on the plain-file partition; equal to swapping in-set and out-set).
        v2 = dict(f)
        for k in IN_FIELDS + OUT_FIELDS:
            v2[k] = "false" if f[k] == "true" else "true"
        v2_line = rebuild(kind, v2)
        swaps[kind] = {
            "honest_line": line,
            "v1_swap_include_exclude_literals": v1_line,
            "v2_swap_membership_sets": v2_line,
            "v1_in_stdout": v1_line in text1,
            "v2_in_stdout": v2_line in text1,
            "honest_pin_in_stdout": classify_process(0, None, text1, 0, line),
            "v1_row_rejects": not classify_process(0, None, text1, 0, v1_line),
            "v2_row_rejects": not classify_process(0, None, text1, 0, v2_line),
        }
        print(f"MUT08B_SWAP kind={kind} v1_swap_rejected={swaps[kind]['v1_row_rejects']} "
              f"v2_swap_rejected={swaps[kind]['v2_row_rejects']} "
              f"honest_in_stdout={swaps[kind]['honest_pin_in_stdout']}")
    receipt["setswap"] = swaps

    # ---- V3: case-token flip on the fixture (mutant copy) vs honest pins.
    v3 = {"available": False}
    if mut:
        v3["available"] = True
        v3["mutant_lines"] = mut
        kinds = {fields(l)[0]: l for l in mut}
        v3["field_diff"] = {}
        blind = {}
        for line in run1:
            kind, f = fields(line)
            if kind not in kinds:
                continue
            mline = kinds[kind]
            _, mf = fields(mline)
            diff = {k: {"honest": f.get(k), "mutant": mf.get(k)}
                    for k in f if f.get(k) != mf.get(k)}
            v3["field_diff"][kind] = diff
            # Pin-shape matrix, all evaluated against the MUTANT stdout:
            #  (a) full honest line, (b) contiguous behavior-only pin = the
            #  emitted fields AFTER the literal fields (membership booleans to
            #  bytes), (c) include literal only.
            toks = line.split(" ")
            lit_idx = [i for i, t in enumerate(toks)
                       if t.startswith("include=") or t.startswith("exclude=")]
            behavior_toks = toks[max(lit_idx) + 1:] if lit_idx else toks[3:]
            sig_b = " ".join(behavior_toks)
            sig_c = "include=%s" % f["include"]
            blind[kind] = {
                "diff_keys": sorted(diff),
                "full_line_rejects": not classify_process(0, None, textm, 0, line),
                "behavior_only_pin_rejects": not classify_process(0, None, textm, 0, sig_b),
                "behavior_only_pin": sig_b[:110],
                "literal_only_pin_rejects": not classify_process(0, None, textm, 0, sig_c),
                "mutant_names_digest_equal": f.get("names_sha256") == mf.get("names_sha256"),
                "mutant_bytes_equal": f.get("bytes") == mf.get("bytes"),
            }
            print(f"MUT08B_CASEFLIP kind={kind} diff_keys={sorted(diff)} "
                  f"full_rejects={blind[kind]['full_line_rejects']} "
                  f"behavior_only_rejects={blind[kind]['behavior_only_pin_rejects']} "
                  f"literal_only_rejects={blind[kind]['literal_only_pin_rejects']} "
                  f"names_digest_equal={blind[kind]['mutant_names_digest_equal']}")
        v3["blindness"] = blind
    else:
        print(f"MUT08B_CASEFLIP unavailable mut_err={errm}")
    receipt["caseflip"] = v3

    with open(ROOT + "/receipt_s04_landed.json", "w") as fh:
        json.dump(receipt, fh, indent=1)
    print("MUT08B_RECEIPT " + ROOT + "/receipt_s04_landed.json")


if __name__ == "__main__":
    main()
