#!/usr/bin/env python3
"""r88 BOUNDARY seat analyzer — per-tag stability table over runs/.

For each tag: rc vector, wall range, out/err sha256 uniq, ERROR-line counts per rep,
and a uid-normalized out uniq (`\\d{6,}` -> <UID>). Any tag with >1 distinct payload
prints every distinct payload verbatim (modulo the uid normalization note).
"""
import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
UID_RE = re.compile(rb"\d{6,}")


def h(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def err_counts(err: bytes) -> tuple[int, int]:
    lines = err.splitlines()
    plain = sum(1 for ln in lines if ln.startswith(b"ERROR:"))
    script = sum(1 for ln in lines if ln.startswith(b"SCRIPT ERROR:"))
    return plain, script


def main() -> int:
    tags = sorted({p.name.rsplit(".rep", 1)[0] for p in RUNS.glob("*.rep*.out")})
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for tag in tags:
        if only and only not in tag:
            continue
        outs = sorted(RUNS.glob(f"{tag}.rep*.out"))
        errs = sorted(RUNS.glob(f"{tag}.rep*.err"))
        rcs = sorted(RUNS.glob(f"{tag}.rep*.rc"))
        walls = sorted(RUNS.glob(f"{tag}.rep*.wall"))
        rc_v = [p.read_text().strip() for p in rcs]
        wall_v = [float(p.read_text().strip()) for p in walls if p.exists()]
        out_u = {h(p.read_bytes()) for p in outs}
        err_u = {h(p.read_bytes()) for p in errs}
        out_norm = {UID_RE.sub(b"<UID>", p.read_bytes()) for p in outs}
        ec = [err_counts(p.read_bytes()) for p in errs]
        flag = "  <-- UNSTABLE" if len(out_u) > 1 else ""
        wall_s = f"{min(wall_v):.2f}-{max(wall_v):.2f}s" if wall_v else "-"
        print(f"{tag:32s} n={len(outs)} rc=[{','.join(rc_v)}] wall={wall_s} "
              f"out_uniq={len(out_u)} norm_uniq={len(out_norm)} err_uniq={len(err_u)} "
              f"ERR={[e[0] for e in ec]} SERR={[e[1] for e in ec]}{flag}")
        if len(out_u) > 1 or len(out_norm) > 1:
            payloads = sorted({p.read_bytes() for p in outs})
            for i, pl in enumerate(payloads):
                text = pl.decode("utf-8", "replace")
                if len(text) > 4000:
                    text = text[:2000] + "\n...[truncated]...\n" + text[-1000:]
                print(f"--- payload {i} ({len(pl)}B) ---")
                print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
