#!/usr/bin/env python3
"""r93-reviewer discrimination matrix: prove the committed pins REJECT forged
receipts (not merely accept genuine ones). Uses the production classify_process
extracted from the pinned harness and the committed per-row pins.

Cells per row:
  genuine            (rep1 receipt unchanged)                     -> PASS
  pin_dropped        (pinned substring replaced by a sentinel)    -> FAIL
  pin_flipped        (first digit inside the pin changed)         -> FAIL
  sig_to_stderr      (signature moved from stdout to stderr)      -> FAIL
  wrong_rc           (rc forced to 1)                             -> FAIL
  extra_error        (foreign ERROR: line appended to stdout)     -> FAIL
  truncate           (output cut before the pin ends)             -> FAIL
  tail_appended      (extra token appended to the PASS line)      -> PASS by design
                     (the production classifier is substring-anchored; recorded
                      as an observation, not a defect)

usage: discrimination.py --dir <receipts> [--reps 1]
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ufo_r93


def mutate_drop(out, sig):
    return out.replace(sig, "<PIN-DROPPED>", 1)


def mutate_flip(out, sig):
    """Change the first digit found inside the pin (else the first true/false
    token) to a different value."""
    m = re.search(r"\d", sig)
    if m:
        i = m.start()
        nd = "7" if sig[i] != "7" else "3"
        flipped = sig[:i] + nd + sig[i + 1:]
        return out.replace(sig, flipped, 1)
    m = re.search(r"true|false", sig)
    if m:
        flip = "false" if m.group(0) == "true" else "true"
        flipped = sig[:m.start()] + flip + sig[m.end():]
        return out.replace(sig, flipped, 1)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=pathlib.Path, required=True)
    ap.add_argument("--json", type=pathlib.Path, default=None)
    args = ap.parse_args()
    C, rows = ufo_r93.load_rows()
    results = {}
    for case, row in sorted(rows.items()):
        arm = [f.removeprefix("--arm=") for f in row["flags"] if f.startswith("--arm=")][0]
        stem = row["script"][:-3] if row["script"].endswith(".gd") else row["script"]
        stem_path = args.dir / f"{arm}.rep1"
        if not (args.dir / f"{arm}.rep1.out").is_file():
            stem_path = args.dir / f"{stem}.{arm}.rep1"
        out = pathlib.Path(str(stem_path) + ".out").read_text()
        err = pathlib.Path(str(stem_path) + ".err").read_text()
        rc = int(pathlib.Path(str(stem_path) + ".rc").read_text().strip())
        sigs = ufo_r93.sigs_of(row)
        sig = sigs[0]
        cells = {}
        cells["genuine"] = ufo_r93.classify_row(C, case, out, err, rc)
        cells["pin_dropped"] = ufo_r93.classify_row(C, case, mutate_drop(out, sig), err, rc)
        flipped = mutate_flip(out, sig)
        cells["pin_flipped"] = (ufo_r93.classify_row(C, case, flipped, err, rc)
                                if flipped is not None else "n/a-no-digit")
        # signature present but only on stderr: strip it from stdout
        cells["sig_to_stderr"] = ufo_r93.classify_row(C, case, out.replace(sig, "", 1), err + sig, rc)
        cells["wrong_rc"] = ufo_r93.classify_row(C, case, out, err, 1)
        cells["extra_error"] = ufo_r93.classify_row(
            C, case, out, err, rc, extra_error="ERROR: foreign diagnostic line\n")
        # truncate stdout immediately after the pin's first half
        cut = out.find(sig)
        cells["truncate"] = ufo_r93.classify_row(C, case, out[:cut + len(sig) // 2], err, rc)
        # prefix-anchoring observation: append a tail to the PASS line
        i = out.find(sig)
        j = out.find("\n", i + len(sig))
        tailed = out[:j] + " EXTRA_TAIL=1" + out[j:] if j > 0 else out
        cells["tail_appended"] = ufo_r93.classify_row(C, case, tailed, err, rc)
        results[case] = cells
        print(f"{case:34s} " + " ".join(f"{k}={'P' if v is True else 'F' if v is False else v}"
                                        for k, v in cells.items()), flush=True)
    # summary
    bad = []
    for case, cells in results.items():
        if cells["genuine"] is not True:
            bad.append((case, "genuine-fail"))
        for k, v in cells.items():
            if k in ("genuine", "tail_appended"):
                continue
            if v is True:
                bad.append((case, f"{k}-accepted"))
    print(f"\nrows={len(results)} discriminations_ok={not bad} bad={bad}")
    if args.json:
        args.json.write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
