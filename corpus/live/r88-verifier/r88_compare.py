#!/usr/bin/env python3
"""r88-baseline compare — frozen-tree replay vs reps / r87 canonical receipts.

Wraps compare.py's Godot comparison with the r88 envelope-cell taxonomy:

  * tuple byte-identical  — canonical stable verdict tuple byte-equal
  * raw stdout identical  — merged output list joined, NO normalization
  * normalized identical  — r81 declared-volatile masking (compare.norm)
  * envelope cells        — the 5 r87 mode-envelope rows
                            (input_lattice_{pre_frame,press_phys,release_edge,
                            ui_ns,api_press}); raw stdout may legitimately
                            differ when the observed mode flips. The tuple
                            carries the full whitelisted payload set, so tuple
                            identity must still hold on these rows.
  * volatile-class rows   — the declared pid/path/ASLR/tween-float class.

Usage: r88_compare.py <mine-verdicts.json> <tag>=<ref-verdicts.json> ...
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare import (GODOT_VOLATILE_KEYS, canon, godot_output_norm,  # noqa: E402
                     godot_tuple, norm)

ENVELOPE_CELLS = {
    "input_lattice_pre_frame", "input_lattice_press_phys",
    "input_lattice_release_edge", "input_lattice_ui_ns",
    "input_lattice_api_press",
}
# Declared-volatile raw-stdout rows (r81/r86/r87 class): ASLR / pid / run-path /
# tween transient floats. Enumerated by name, then verified by normalized identity.
VOLATILE_ROWS = {
    "crash_spontaneous_sigabrt", "descendant_pipe_detached_control",
    "descendant_pipe_forged_signature_release", "save_process_writer",
    "save_process_reader", "save_process_missing", "save_roundtrip",
    "tween_flash",
}


def raw_output(row):
    if "output" in row and isinstance(row["output"], list):
        return "\n".join(row["output"])
    return None


def envelope_mode(row, payloads):
    """Which whitelisted payload the row's raw output matches (or None)."""
    if not isinstance(payloads, list):
        return "no-payload-list"
    text = raw_output(row) or ""
    hits = [i for i, p in enumerate(payloads) if p in text]
    return f"mode{hits}" if hits else "none"


def main():
    mine_p = Path(sys.argv[1])
    mine = json.loads(mine_p.read_text())
    m = {r["case"]: r for r in mine["results"]}
    print(f"=== mine {mine_p} rows={len(mine['results'])} "
          f"verdict={mine['verdict']} sha256="
          f"{hashlib.sha256(mine_p.read_bytes()).hexdigest()} ===")
    for arg in sys.argv[2:]:
        tag, ref_p = arg.split("=", 1)
        p = Path(ref_p)
        if not p.exists():
            print(f"\n{tag}: SKIP missing ref {ref_p}")
            continue
        ref = json.loads(p.read_text())
        r = {x["case"]: x for x in ref["results"]}
        common = sorted(set(m) & set(r))
        new_only = sorted(set(m) - set(r))
        old_only = sorted(set(r) - set(m))
        tuple_same, tuple_mism = [], []
        raw_same = raw_diff = raw_missing = 0
        nrm_same = nrm_diff = nrm_missing = 0
        raw_diffs = []
        for c in common:
            a, b = m[c], r[c]
            if canon(godot_tuple(a)) == canon(godot_tuple(b)):
                tuple_same.append(c)
            else:
                tuple_mism.append(c)
            ra, rb = raw_output(a), raw_output(b)
            if ra is None or rb is None:
                raw_missing += 1
            elif ra == rb:
                raw_same += 1
            else:
                raw_diff += 1
                raw_diffs.append(c)
            na, nb = godot_output_norm(a), godot_output_norm(b)
            if na is None or nb is None:
                nrm_missing += 1
            elif na == nb:
                nrm_same += 1
            else:
                nrm_diff += 1
        env_diffs = [c for c in raw_diffs if c in ENVELOPE_CELLS]
        vol_diffs = [c for c in raw_diffs if c in VOLATILE_ROWS]
        other_diffs = [c for c in raw_diffs
                       if c not in ENVELOPE_CELLS and c not in VOLATILE_ROWS]
        print(f"\n{tag}: ref={ref_p} ref_rows={len(ref['results'])} "
              f"ref_verdict={ref['verdict']} ref_sha256="
              f"{hashlib.sha256(p.read_bytes()).hexdigest()}")
        print(f"  common={len(common)} new_only={len(new_only)} "
              f"old_only={len(old_only)}")
        print(f"  tuple byte-identical={len(tuple_same)}/{len(common)} "
              f"tuple_mismatches={len(tuple_mism)}")
        print(f"  output RAW byte-identical={raw_same}/{len(common)} "
              f"differing={raw_diff} not-carried={raw_missing} "
              f"[envelope={len(env_diffs)} volatile={len(vol_diffs)} "
              f"other={len(other_diffs)}]")
        print(f"  output NORMALIZED identical={nrm_same}/{len(common)} "
              f"differing={nrm_diff} not-carried={nrm_missing}")
        if new_only:
            print(f"  new_only_cases({len(new_only)}): {new_only}")
        if old_only:
            print(f"  old_only_cases({len(old_only)}): {old_only}")
        for c in tuple_mism:
            a, b = m[c], r[c]
            diff = {k: (str(a.get(k))[:120], str(b.get(k))[:120])
                    for k in sorted(set(a) | set(b))
                    if a.get(k) != b.get(k) and k not in GODOT_VOLATILE_KEYS}
            print(f"  TUPLE-MISMATCH {c}: {json.dumps(diff)[:500]}")
        # envelope-cell mode table (only rows present in both)
        for c in sorted(ENVELOPE_CELLS & set(common)):
            a, b = m[c], r[c]
            print(f"  ENVELOPE {c}: mode_mine={envelope_mode(a, a.get('signature'))} "
                  f"mode_ref={envelope_mode(b, b.get('signature'))} "
                  f"tuple_identical="
                  f"{canon(godot_tuple(a)) == canon(godot_tuple(b))} "
                  f"raw_identical={raw_output(a) == raw_output(b)}")
        for c in raw_diffs:
            a, b = m[c], r[c]
            la, lb = (raw_output(a) or "").splitlines(), (raw_output(b) or "").splitlines()
            shown = False
            for i, (x, y) in enumerate(zip(la, lb)):
                if x != y:
                    cls = ("ENVELOPE" if c in ENVELOPE_CELLS else
                           "VOLATILE" if c in VOLATILE_ROWS else "OTHER")
                    print(f"  RAW-OUT-DIFF[{cls}] {c} line {i}:\n"
                          f"      mine={x[:150]!r}\n      ref ={y[:150]!r}")
                    shown = True
                    break
            if not shown:
                print(f"  RAW-OUT-DIFF {c}: line-count mine={len(la)} "
                      f"ref={len(lb)} "
                      f"(normalized-equal={godot_output_norm(a) == godot_output_norm(b)})")


if __name__ == "__main__":
    main()
