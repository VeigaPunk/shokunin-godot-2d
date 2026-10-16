#!/usr/bin/env python3
"""r91-simplifier static audit of the committed r91 landing.

Reads (never writes) the byte-exact 77d2f7e snapshot in committed-fixtures/:
  - nav_lattice.gd      (the probe)
  - run_battery.py      (the harness; nav_lattice_* CASES rows)
Emits a receipt on stdout.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "committed-fixtures"
GD = (FIX / "nav_lattice.gd").read_text()
PY = (FIX / "run_battery.py").read_text()
gd_lines = GD.splitlines()
py_lines = PY.splitlines()

out = []
def emit(s=""):
    out.append(s)

emit("== r91-simplifier static audit (committed 77d2f7e snapshot) ==")
emit()

# ---------------------------------------------------------------- 1. arm <-> row bijection
emit("-- 1. arm <-> row bijection --")
match_arms = re.findall(r'^\t\t"([a-z_]+)": (await )?(_arm_[a-z_]+)\(\)', GD, re.M)
dispatch = [(a, f) for a, _, f in match_arms]
emit("dispatch branches (%d):" % len(dispatch))
for a, f in dispatch:
    emit("  arm=%-16s -> %s" % (a, f))

rows = re.findall(r"\('(nav_lattice_[a-z_]+)', 'nav_lattice\.gd', (\[[^\]]*\]), (-?\d+),", PY)
emit("CASES rows (%d):" % len(rows))
for name, flags, rc in rows:
    arm = re.search(r"--arm=([a-z_]+)", flags).group(1)
    emit("  row=%-28s arm=%-16s rc=%s" % (name, arm, rc))

row_arms = [re.search(r"--arm=([a-z_]+)", f).group(1) for _, f, _ in rows]
disp_arms = [a for a, _ in dispatch]
emit("row arms == dispatch arms: %s" % (sorted(row_arms) == sorted(disp_arms)))
emit("orphan rows (row without arm): %s" % sorted(set(row_arms) - set(disp_arms)))
emit("orphan arms (arm without row): %s" % sorted(set(disp_arms) - set(row_arms)))
emit("duplicate rows: %s" % sorted(n for n in [r[0] for r in rows] if [r[0] for r in rows].count(n) > 1))
emit("non-nav rows that use nav_lattice.gd: %s" % sorted(
    set(re.findall(r"\('([a-z0-9_]+)', 'nav_lattice\.gd'", PY)) - set(r[0] for r in rows)))
emit()

# ---------------------------------------------------------------- 2. function census
emit("-- 2. function census --")
funcs = [(i + 1, m.group(1)) for i, l in enumerate(gd_lines)
         for m in [re.match(r"func ([a-z_0-9]+)\(", l)] if m]
emit("func definitions (%d):" % len(funcs))
for ln, fn in funcs:
    # call sites: `fn(` anywhere except the definition line
    calls = [i + 1 for i, l in enumerate(gd_lines) if i + 1 != ln and re.search(r"\b%s\(" % fn, l)]
    emit("  %-24s def@%-5d callsites=%d %s" % (fn, ln, len(calls), calls if len(calls) <= 6 else str(calls[:6]) + "..."))
zero = [(ln, fn) for ln, fn in funcs if not [i for i, l in enumerate(gd_lines)
                                             if i + 1 != ln and re.search(r"\b%s\(" % fn, l)]]
emit("funcs with zero call sites: %s" % zero)
emit("match branches naming a missing func: %s" % sorted(
    set(f for _, f in dispatch) - set(fn for _, fn in funcs)))
emit()

# ---------------------------------------------------------------- 3. write-only store scan
emit("-- 3. write-only store scan (var/const) --")
decls = []
for i, l in enumerate(gd_lines):
    m = re.match(r"^(?:var|const) ([a-zA-Z_0-9]+)", l)
    if m:
        decls.append((i + 1, m.group(1), "file"))
    m2 = re.match(r"^\tvar ([a-zA-Z_0-9]+)", l)
    if m2:
        decls.append((i + 1, m2.group(1), "local"))
for ln, name, kind in decls:
    reads = []
    for j, l in enumerate(gd_lines):
        if j + 1 == ln:
            continue
        for m in re.finditer(r"\b%s\b" % re.escape(name), l):
            before = l[:m.start()].rstrip()
            # a bare assignment target (`name =` / `name.x =`) is a write, not a read
            if re.search(r"\b%s(\.\w+(\[\w*\])?)*\s*=[^=]" % re.escape(name), l[m.start():]) and \
               (before == "" or before.endswith(("\t", ":")) or re.search(r"^\s*(var|for)\b.*$", l[:m.start()])):
                continue
            reads.append(j + 1)
    emit("  %-5s %-10s decl@%-5d read_lines=%s" % (kind, name, ln, reads if reads else "NONE"))
emit("write-only stores: %s" % [n for ln, n, k in decls if not any(
    (lambda name=ln, nm=n: [j for j, l in enumerate(gd_lines) if j + 1 != ln and re.search(r"\b%s\b" % re.escape(nm), l)])())])
emit()

# ---------------------------------------------------------------- 4. print site census
emit("-- 4. print site census --")
prints = [(i + 1, l.strip()) for i, l in enumerate(gd_lines) if re.search(r"\bprint\(", l)]
emit("print( sites: %d" % len(prints))
for ln, t in prints:
    emit("  %-5d %s" % (ln, t[:100]))
pass_lines = [i + 1 for i, l in enumerate(gd_lines)
              if re.search(r'print\("PASS nav_lattice ', l)]
fallback = [i + 1 for i, l in enumerate(gd_lines)
            if re.search(r'print\("PASS nav_lattice unknown', l)]
emit("PASS-shaped print sites: %d = %d real arm lines + %d unknown-arm fallback "
     "(the fallback also starts with `PASS nav_lattice `, hence a naive grep "
     "counts 11)" % (len(pass_lines), len(pass_lines) - len(fallback), len(fallback)))
emit("STALE sites: %d ; crash-marker sites: %d ; total = %d" % (
    len(re.findall(r'print\("STALE nav_lattice ', GD)),
    len(re.findall(r'print\("NAV_LATTICE_TEARDOWN_CRASH', GD)),
    len(pass_lines) + len(re.findall(r'print\("STALE nav_lattice ', GD))
    + len(re.findall(r'print\("NAV_LATTICE_TEARDOWN_CRASH', GD))))
emit()

# ---------------------------------------------------------------- 5. CLI knobs
emit("-- 5. CLI knob usage in nav_lattice.gd --")
for knob in ["arm", "frames", "fixed-fps", "physics-ticks"]:
    hits = [i + 1 for i, l in enumerate(gd_lines) if knob in l]
    emit("  %-14s occurrences=%d %s" % (knob, len(hits), hits))
emit()

# ---------------------------------------------------------------- 6. tail markers per arm
emit("-- 6. declared diagnostic tail fields vs pinned signatures --")
TAIL = ["settle=", "iter=", "ladder=", "first_reach=", "first_reach_sync=", "walk_steps=",
        "reached_at=", "first_reachable=", "iter_b=", "link_iter=", "gate=",
        "chg_iter_same=", "chg_iter_settled=", "dis_same=", "fwd_disabled_same=",
        "seq_a=", "seq_b=", "vel_a=", "vel_b=", "sum_max="]
for name, flags, rc in rows:
    sig = re.search(r"\('" + re.escape(name) + r"', 'nav_lattice\.gd', \[[^\]]*\], -?\d+,\s*\n?\s*'((?:[^'\\]|\\.)*)'", PY)
    if not sig:
        sig = re.search(r"\('" + re.escape(name) + r"'.*?\n\s*'([^']*)'", PY, re.S)
    s = sig.group(1) if sig else "<UNPARSED>"
    arm = re.search(r"--arm=([a-z_]+)", flags).group(1)
    # word-boundary match: `pre_iter=` must NOT count as the tail field `iter=`
    present = [t for t in TAIL if re.search(r"(?<![a-z_])%s" % re.escape(t), s)]
    emit("  %-28s pinned_len=%-4d tail_fields_inside_pin=%s" % (name, len(s), present))
emit()
emit("== end static audit ==")
print("\n".join(out))
