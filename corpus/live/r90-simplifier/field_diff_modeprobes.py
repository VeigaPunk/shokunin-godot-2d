#!/usr/bin/env python3
"""r90-simplifier — full field-level diff of the mode probes against the row pins.

For each r90 row and each mode dir (runs-tps30, runs-dummy), print every pinned
field whose emitted value differs, plus the pairing-field status (ncb/pf_delta/
cb0_rel/tick_dh) so the effective-rate evidence can be attributed correctly.
"""
import ast
import os
import pathlib
import re

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent.parent
BATTERY = pathlib.Path(os.environ.get("R90_BATTERY", REPO / "corpus/fixtures/run_battery.py"))
PAIR_KEYS = ("ncb", "cb0_rel", "obs0_rel", "pf_delta", "tick_dh", "cbpf_dh")


def load_rows():
    src = BATTERY.read_text()
    tree = ast.parse(src)
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            for elt in node.value.elts:
                vals = [e.value for e in elt.elts if isinstance(e, ast.Constant)]
                if vals and str(vals[0]).startswith("r90_"):
                    flags = [e.value for e in elt.elts if isinstance(e, ast.List)
                             for e in e.elts if isinstance(e, ast.Constant)]
                    rows.append((vals[0], flags, vals[2], vals[3]))
    return rows


def main():
    rows = load_rows()
    for mode in ("tps30", "dummy"):
        print("=" * 100)
        print(f"MODE {mode}")
        for name, flags, rc, pin in rows:
            arm = next(f.split("=", 1)[1] for f in flags if f.startswith("--arm="))
            out = (HERE / f"runs-{mode}" / f"{arm}.rep1.out").read_text()
            lines = [l for l in out.splitlines() if l.startswith("PASS r90_lattice")]
            if not lines:
                print(f"  {name:24s} NO PASS LINE")
                continue
            payload = lines[0][len("PASS r90_lattice "):]
            # positional token alignment (pins may repeat a key inside one field,
            # e.g. comrefuse's five `mode=` tokens) -> compare ordered token lists
            etoks = re.findall(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=(\S+)", payload)
            ptoks = re.findall(r"(?:^|\s)([A-Za-z_][A-Za-z0-9_]*)=(\S+)", pin)
            # exact payload equality = row passes on the value axis
            if payload == pin:
                print(f"  {name:24s} payload byte-identical to pin")
                continue
            # first character where they diverge
            idx = next((i for i, (a, b) in enumerate(zip(payload, pin)) if a != b),
                       min(len(payload), len(pin)))
            diffs = [(pk, pv, ev) for (pk, pv), (_ek, ev) in zip(ptoks, etoks) if pv != ev]
            pair_diffs = [d for d in diffs if d[0] in PAIR_KEYS]
            value_diffs = [d for d in diffs if d[0] not in PAIR_KEYS]
            print(f"  {name:24s} differing_fields={len(diffs)} "
                  f"pairing_fields_differing={[d[0] for d in pair_diffs]} "
                  f"first_char_at={idx}")
            for k, pv, gv in value_diffs[:6]:
                print(f"        value {k}: pin={pv}  got={gv}")
            if len(value_diffs) > 6:
                print(f"        ... {len(value_diffs) - 6} more value diffs")
        print()


if __name__ == "__main__":
    main()
