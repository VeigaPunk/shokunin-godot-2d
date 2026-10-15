#!/usr/bin/env python3
"""r88-simplifier rep analysis: normalize + compare before/after rep receipts.

Normalization covers the declared-volatile tokens with a uid rule that also
catches letter-glued runs (the reviewer's F5 gap in the r79 compare tool):
  - `.gd:NNN` -> `.gd:<N>`   (traceback line numbers, declared volatile)
  - digit runs >= 4 -> `<UID>` (client peer id, incl. `s_conn<uid>` glue and
    the measured 4-5 digit tail; no other 4+ digit run exists in these arms)
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARMS = ["mp_loopback", "light_props", "sprite_phys", "vis_not"]
NORM = [
    (re.compile(r"\.(gd|lua|py):\d+"), r".\1:<N>"),
    (re.compile(r"\d{4,}"), "<UID>"),
]


def normalize(text: str) -> str:
    for pat, repl in NORM:
        text = pat.sub(repl, text)
    return text


def reps(side: str, arm: str):
    return sorted((ROOT / side).glob(f"{arm}.rep*.out"))


def main() -> None:
    print("side | arm | reps | norm_uniq | norm_sha | pass_uniq")
    table = {}
    for side in ("reps-before", "reps-after"):
        for arm in ARMS:
            files = reps(side, arm)
            norms, passes = [], []
            for f in files:
                t = f.read_text()
                norms.append(hashlib.sha256(normalize(t).encode()).hexdigest())
                m = [l for l in t.splitlines() if l.startswith("PASS r88_surfaces")]
                passes.append(m[0] if m else "<none>")
            table[(side, arm)] = (norms, passes)
            print(f"{side} | {arm} | {len(files)} | {len(set(norms))} | "
                  f"{norms[0][:16] if norms else '-'} | {len(set(passes))}")
    print()
    print("cross-side per-rep comparison (normalized merged output):")
    ok = True
    for arm in ARMS:
        for i, (nb, pa) in enumerate(zip(*table[("reps-before", arm)])):
            na = table[("reps-after", arm)][0][i]
            same = nb == na
            ok &= same
            print(f"  {arm} rep{i}: before={nb[:16]} after={na[:16]} same={same}")
    print()
    print("PASS-line cross-side equality:")
    for arm in ARMS:
        pb = set(table[("reps-before", arm)][1])
        pa = set(table[("reps-after", arm)][1])
        print(f"  {arm}: before_uniq={len(pb)} after_uniq={len(pa)} "
              f"identical={pb == pa}")
        ok &= pb == pa
    print()
    print("sprite_phys stderr backtrace lines (raw):")
    for side in ("reps-before", "reps-after"):
        t = (ROOT / side / "sprite_phys.rep0.out").read_text()
        bt = [l.strip() for l in t.splitlines() if "r88_surfaces.gd:" in l]
        print(f"  {side}: {bt}")
    print()
    print("OVERALL:", "IDENTICAL" if ok else "DIFFERS")


if __name__ == "__main__":
    main()
