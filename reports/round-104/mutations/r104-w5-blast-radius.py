#!/usr/bin/env python3
"""r104-W5 blast-radius harness.

Question: does the C2(a) PASS-prefix census tightening change any
RECEIPT_MULTI_PASS_GRAMMAR observed-shape computation (or any other clause
that consumes the same census)?

Method: textual variant generation over a scratch copy of HEAD
`corpus/fixtures/run_battery.py` (never the lane repo file), import each
variant as a module, replay every stored verdicts.json row through
`receipt_shape_audit` + `receipt_shape_flag`, and diff.

Variants (all generated from the same base bytes):
  base        HEAD, unmodified
  V1_census   pass_lines census widened only (`^PASS\s|^PASS$`)
  V2_full     census + the three SEQ/DIAG accounting predicates widened
  V3_prefix   census widened to bare `startswith("PASS")` (no separator guard)

No battery run. No lane-repo write.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = Path("/var/tmp/r104-W5")
SRC = REPO / "corpus" / "fixtures" / "run_battery.py"

RE_CENSUS = '    pass_lines = [line for line in output if line.startswith("PASS ")]\n'
RE_SEQ_IN = '                if not (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)):\n'
RE_SEQ_POST_A = '                if (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)\n'
RE_DIAG = '            if (line.startswith("PASS ") or RECEIPT_BANNER_RE.match(line)\n'
RE_ANSI_ANCHOR = 'RECEIPT_ANSI_ONLY_RE = re.compile(r"^(?:\\x1b\\[[0-9;]*m)+$")\n'

DECL = 'RECEIPT_PASS_RE = re.compile(r"^PASS(?=[\\s]|$)")\n'


def build(text, mode):
    if mode == "base":
        return text
    assert text.count(RE_ANSI_ANCHOR) == 1, "anchor missing"
    text = text.replace(RE_ANSI_ANCHOR, RE_ANSI_ANCHOR + DECL)
    if mode == "V3_prefix":
        new_census = '    pass_lines = [line for line in output if line.startswith("PASS")]\n'
    else:
        new_census = '    pass_lines = [line for line in output if RECEIPT_PASS_RE.match(line)]\n'
    assert text.count(RE_CENSUS) == 1, "census anchor"
    text = text.replace(RE_CENSUS, new_census)
    if mode == "V2_full":
        for old, new in (
            (RE_SEQ_IN, '                if not (RECEIPT_PASS_RE.match(line) or RECEIPT_SEQ_RE.match(line)):\n'),
            (RE_SEQ_POST_A, '                if (RECEIPT_PASS_RE.match(line) or RECEIPT_SEQ_RE.match(line)\n'),
            (RE_DIAG, '            if (RECEIPT_PASS_RE.match(line) or RECEIPT_BANNER_RE.match(line)\n'),
        ):
            assert text.count(old) == 1, f"anchor {old!r}"
            text = text.replace(old, new)
    return text


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    base_text = SRC.read_text()
    print(f"HEAD sha256 {hashlib.sha256(base_text.encode()).hexdigest()}")
    print(f"HEAD lines {len(base_text.splitlines())}")
    mods = {}
    for mode in ("base", "V1_census", "V2_full", "V3_prefix"):
        p = SCRATCH / f"rb_{mode}.py"
        p.write_text(build(base_text, mode))
        mods[mode] = load(p, f"rb_{mode}")
        print(f"{mode:10s} {p} sha256={hashlib.sha256(p.read_bytes()).hexdigest()[:16]} "
              f"lines={len(p.read_text().splitlines())}")

    runs = sorted((REPO / "corpus" / "live" / "runs").glob("*/verdicts.json"))
    runs = [r for r in runs if r.parent.name.startswith("2026")]
    print(f"\nstored runs with verdicts.json: {len(runs)}")

    summary = {}
    for rp in runs:
        payload = json.loads(rp.read_text())
        rows = payload.get("rows") or payload.get("results") or []
        if isinstance(payload, list):
            rows = payload
        per = {}
        for mode, mod in mods.items():
            per[mode] = mod.receipt_shape_audit(rows)
        base_flags = per["base"]["flags"]
        line = (f"{rp.parent.name} rows={len(rows)} audited={per['base']['audited']} "
                f"base_flags={len(base_flags)}")
        for mode in ("V1_census", "V2_full", "V3_prefix"):
            f = per[mode]["flags"]
            line += f" {mode}={len(f)}"
        print(line)
        summary[rp.parent.name] = per
        for mode in ("V1_census", "V2_full", "V3_prefix"):
            new = [f for f in per[mode]["flags"] if f not in base_flags]
            gone = [f for f in base_flags if f not in per[mode]["flags"]]
            if new or gone:
                print(f"   {mode}: +{len(new)} -{len(gone)}")
                for f in new[:10]:
                    print(f"     + {json.dumps(f)[:200]}")
                for f in gone[:10]:
                    print(f"     - {json.dumps(f)[:200]}")

    out = SCRATCH / "summary.json"
    out.write_text(json.dumps({
        "runs": {k: {m: v[m] for m in v} for k, v in summary.items()},
    }, indent=1))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
