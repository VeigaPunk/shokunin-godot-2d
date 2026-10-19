#!/usr/bin/env python3
"""r103 W10: mechanical splice for the receipt-shape META gate.

Inserts two blocks into a COPY of corpus/fixtures/run_battery.py:
  (A) the gate fragment (tables + receipt_allowed_error + receipt_shape_flag
      + receipt_shape_audit) at module level, immediately before `def main():`
  (B) the call-site meta row immediately before the verdicts.json payload is
      written, so the gate runs on every battery run and its verdict lands in
      the stored record set.

Never touches the repo file: the target path is an argument (a worktree copy).
Anchors are asserted present exactly once, so a drifted file fails loudly.
"""
import hashlib
import sys
from pathlib import Path

ANCHOR_MAIN = "\n\ndef main():\n    parser = argparse.ArgumentParser(description=__doc__)\n"
ANCHOR_PAYLOAD = ('    payload = {"godot": args.godot, "seed": str(HERE), "scratch": str(scratch),\n'
                  '               "probe_failing": args.probe_failing, "results": results,\n')

CALL_SITE = '''    # r103 author (W10): receipt-shape META gate over the rows this run stored
    # (see receipt_shape_audit): unaccounted PASS lines, foreign content
    # inside a declared span or diagnostic window, non-unique anchor lines,
    # missing receipt fields, and dead shape-allowlist entries surface as a
    # FAIL meta row; the classifiers are untouched.
    receipt_audit = receipt_shape_audit(results)
    results.append({"case": "probe_receipt_shape_gate",
                    "verdict": "PASS" if not receipt_audit["flags"] else "FAIL",
                    "audited_rows": receipt_audit["audited"],
                    "flag_count": len(receipt_audit["flags"]),
                    "flags": receipt_audit["flags"][:20],
                    "bounded_claim": "stored per-row stdout receipts only: classification text that never reaches the record (r102-mut9 whole-stream closure, canned-receipt ceiling) stays invisible; the shape tables are carried as data and extended deliberately"})
    print(f"{results[-1]['verdict']} receipt-shape gate: "
          f"audited={receipt_audit['audited']} flags={len(receipt_audit['flags'])}",
          flush=True)

'''


def main():
    target = Path(sys.argv[1])
    fragment = Path(sys.argv[2])
    text = target.read_text()
    before = hashlib.sha256(text.encode()).hexdigest()
    if text.count(ANCHOR_MAIN) != 1:
        raise SystemExit(f"anchor def main() count={text.count(ANCHOR_MAIN)}")
    if text.count(ANCHOR_PAYLOAD) != 1:
        raise SystemExit(f"anchor payload count={text.count(ANCHOR_PAYLOAD)}")
    gate = fragment.read_text()
    patched = text.replace(
        ANCHOR_MAIN,
        "\n\n" + gate.rstrip("\n") + "\n\n\ndef main():\n    parser = argparse.ArgumentParser(description=__doc__)\n")
    patched = patched.replace(ANCHOR_PAYLOAD, CALL_SITE + ANCHOR_PAYLOAD)
    target.write_text(patched)
    after = hashlib.sha256(patched.encode()).hexdigest()
    print(f"target {target}")
    print(f"before sha256 {before}")
    print(f"after  sha256 {after}")
    print(f"lines  before={text.count(chr(10))} after={patched.count(chr(10))}")
    print(f"inserted gate lines={gate.rstrip(chr(10)).count(chr(10)) + 1} "
          f"call_site lines={CALL_SITE.count(chr(10))}")


if __name__ == "__main__":
    main()
