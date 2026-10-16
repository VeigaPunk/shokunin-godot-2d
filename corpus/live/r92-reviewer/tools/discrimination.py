#!/usr/bin/env python3
"""r92-reviewer discrimination matrix on REAL receipts.

For the r92 rows the landing pins, classify a real receipt under the committed
clause and then under deliberate forgeries (fragment dropped, signature moved
to stderr, wrong signal class, foreign ERROR line, envelope payload removed,
allowlist entry dropped) — each cell must land in the DECLARED direction.

usage: discrimination.py [--json out.json]
"""
import argparse, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ufo_r92

LOAD = HERE.parent / "fresh-load"
AUTHOR = HERE.parent.parent / "r92-author" / "fresh-reps"


def read_receipt(dirp, arm, rep=1):
    o = (dirp / f"{arm}.rep{rep}.out").read_text()
    e = (dirp / f"{arm}.rep{rep}.err").read_text()
    rc = int((dirp / f"{arm}.rep{rep}.rc").read_text().strip())
    return o, e, rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=pathlib.Path, default=None)
    args = ap.parse_args()
    C = ufo_r92.load()
    out_rows = []

    def cell(name, case, passed, want, note):
        ok = (bool(passed) == want)
        out_rows.append({"cell": name, "case": case, "got": bool(passed),
                         "want": want, "ok": ok, "note": note})
        print(f"{'OK  ' if ok else 'BAD '} {name:52s} got={bool(passed)} want={want}  {note}")
        return ok

    # ---- crash row: real receipt + forgery shapes -------------------------
    o, e, rc = read_receipt(LOAD, "nullts")
    sig = C["cases"]["r92_tilemap_nullts_crash"]["signature"]
    frags = C["req_err"]["r92_tilemap_nullts_crash"]
    base = ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", o, e, rc)
    cell("nullts/clean-receipt", "nullts", base, True, f"rc={rc} both fragments on stderr, sig on stdout")
    cell("nullts/clean-receipt/author-committed", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", *read_receipt(AUTHOR, "nullts")), True,
         "committed author receipt")
    cell("nullts/fragment-dropped", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", o, e.replace(frags[0], ""), rc),
         False, "signal-11 header removed from stderr")
    cell("nullts/site-fragment-dropped", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", o, e.replace(frags[1], ""), rc),
         False, "backtrace site fragment removed")
    cell("nullts/signature-on-stderr-only", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", "", o + e, rc), False,
         "stdout anchor must fail (merged-blob spoof)")
    cell("nullts/wrong-signal-class-rc0", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", o, e, 0), False,
         "right fragments, rc=0 (not the crash class)")
    cell("nullts/foreign-error-line", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", o, e + "\nERROR: unrelated\n", rc),
         False, "foreign ERROR line rejects")
    cell("nullts/rc-134-shell-encoding", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", o, e, 134), False,
         "the scout's 128+6 shell encoding must NOT classify (battery wants -6)")
    cell("nullts/pass-line-forged-rc0", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash",
                              o + "\nPASS tilemap_lattice nullts\n", e, 0), False,
         "forged PASS + rc=0 without the crash")
    cell("nullts/rc-minus-11", "nullts",
         ufo_r92.classify_row(C, "r92_tilemap_nullts_crash", o, e, -11), False,
         "raw SIGSEGV rc must NOT classify (row pins -6)")

    # ---- allowlist load-bearing (each of the 9 entry-bearing rows) --------
    for case in sorted(C["exp_err"]):
        arm = case.removeprefix("r92_tilemap_")
        o, e, rc = read_receipt(LOAD, arm)
        with_ee = ufo_r92.classify_row(C, case, o, e, rc)
        bare = ufo_r92.classify_row(C, case, o, e, rc, override_ee=())
        cell(f"{arm}/allowlisted-passes", case, with_ee, True, "production clause + committed allowlist")
        cell(f"{arm}/bare-classifier-rejects", case, bare, False,
             "without the allowlist the row is rejected (entry is load-bearing)")
        ee = C["exp_err"][case]
        if ee:
            cell(f"{arm}/one-entry-dropped-rejects", case,
                 ufo_r92.classify_row(C, case, o, e, rc, override_ee=ee[1:]), False,
                 f"drop first of {len(ee)} entries -> must reject")
        cell(f"{arm}/author-receipt", case, ufo_r92.classify_row(C, case, *read_receipt(AUTHOR, arm)), True,
             "committed author receipt")

    # ---- envelope row: both payloads, and the falsified payload on a real 0-state
    o, e, rc = read_receipt(LOAD, "nav")
    p0, p1 = C["cases"]["r92_tilemap_nav"]["signature"]
    cell("nav/clean-receipt-payload0", "r92_tilemap_nav",
         ufo_r92.classify_row(C, "r92_tilemap_nav", o, e, rc), True,
         "production receipt matches payload[0] (regions_f1=1)")
    nav0 = o.replace("regions_f1=1 regions_f2=1", "regions_f1=0 regions_f2=1")
    cell("nav/f1-zero-admitted-by-payload1", "r92_tilemap_nav",
         ufo_r92.classify_row(C, "r92_tilemap_nav", nav0, e, rc), True,
         "the declared envelope admits the ff>=150 state (payload[1])")
    cell("nav/f1-zero-under-payload0-only", "r92_tilemap_nav",
         ufo_r92.classify_row(C, "r92_tilemap_nav", nav0, e, rc, override_sig=p0), False,
         "the falsified one-step read is NOT admitted by payload[0]")
    nav_bad = o.replace("regions_f2=1", "regions_f2=0")
    cell("nav/f2-zero-rejects-both-payloads", "r92_tilemap_nav",
         ufo_r92.classify_row(C, "r92_tilemap_nav", nav_bad, e, rc), False,
         "settled registration law is single-valued: f2=0 rejects")
    nav_tail = o.replace("regions_erased_f1=0", "regions_erased_f1=1")
    cell("nav/lever-tail-drift-rejects", "r92_tilemap_nav",
         ufo_r92.classify_row(C, "r92_tilemap_nav", nav_tail, e, rc), False,
         "erase-lever read outside both payloads")
    cell("nav/foreign-error-rejects", "r92_tilemap_nav",
         ufo_r92.classify_row(C, "r92_tilemap_nav", o, e + "ERROR: foreign\n", rc), False,
         "no-entry row: any ERROR line rejects")
    for name, fps_dir, want in (("ff120", "ff120", True), ("ff150", "ff150", False), ("ff600", "ff600", False)):
        d = HERE.parent / fps_dir
        if not d.is_dir():
            continue
        o2, e2, rc2 = read_receipt(d, "nav")
        got = ufo_r92.classify_row(C, "r92_tilemap_nav", o2, e2, rc2)
        which = "payload[0]" if p0 in o2 else ("payload[1]" if p1 in o2 else "neither")
        cell(f"nav/{name}-classifies", "r92_tilemap_nav", got, want,
             f"{fps_dir} receipt matches {which}")

    # ---- non-envelope PASS rows: one forged byte anywhere in the pin rejects
    for arm in ("census", "atlas", "cells", "custom", "terrain", "pattern",
                "encoding", "fixinvalid", "srcids", "physics", "timing", "quadrant"):
        case = f"r92_tilemap_{arm}"
        o, e, rc = read_receipt(LOAD, arm)
        pin = C["cases"][case]["signature"]
        cell(f"{arm}/clean", case, ufo_r92.classify_row(C, case, o, e, rc), True, "clean receipt")
        # single-byte mutation inside the pinned prefix
        idx = len(pin) // 2
        mut = pin[:idx] + ("X" if pin[idx] != "X" else "Y") + pin[idx + 1:]
        o2 = o.replace(pin, mut, 1)
        cell(f"{arm}/pin-byte-mutated", case,
             ufo_r92.classify_row(C, case, o2, e, rc), False, "one byte inside the pin flipped")

    bad = [r for r in out_rows if not r["ok"]]
    print(f"\ncells={len(out_rows)} bad={len(bad)}")
    for r in bad:
        print("  BAD:", r)
    if args.json:
        args.json.write_text(json.dumps({"cells": out_rows, "bad": bad}, indent=1))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
