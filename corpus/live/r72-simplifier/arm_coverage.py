"""r71 simplifier scratch: arm/key coverage between a probe's emitted lines
and a battery's pinned CASES table.

Inputs:
  --arm-regex   regex with one group capturing the arm name (default LOVE)
  --probe-out   captured probe stdout file
  --cases-file  python file whose CASES table is [(name, arm, key, pinned)]
  --table       table variable name (default CASES)

Reports:
  * emitted (arm,key) pairs not pinned by any case row  -> unpinned surface
  * case rows whose (arm,key) is never emitted           -> unrunnable pin
  * rows whose pinned value is a *literal* in the probe  -> assertion-carried
    (the probe states the conclusion; the row cannot fail for a mechanism
    reason), vs computed (measurement-carried).
"""
import argparse
import ast
import re
from pathlib import Path


def load_cases(path, table):
    src = Path(path).read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == table
                for t in node.targets):
            rows = []
            for r in node.value.elts:
                if isinstance(r, (ast.Tuple, ast.List)) and len(r.elts) >= 4:
                    rows.append(tuple(
                        ast.literal_eval(e) if isinstance(e, ast.Constant) else
                        ast.unparse(e) for e in r.elts[:4]))
            return rows
    raise SystemExit(f"table {table} not found in {path}")


def parse_arms(text, arm_regex):
    rx = re.compile(arm_regex)
    arms = {}
    for line in text.splitlines():
        m = rx.match(line.strip())
        if not m:
            continue
        arm = m.group(1)
        body = m.group(2)
        kv = dict(p.split("=", 1) for p in body.split() if "=" in p)
        arms.setdefault(arm, {}).update(kv)
    return arms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm-regex", default=r"^([A-Z]+-ARM) (\S+) \| (.*)$")
    ap.add_argument("--arm-group", type=int, default=2)
    ap.add_argument("--probe-out", required=True)
    ap.add_argument("--cases-file", required=True)
    ap.add_argument("--table", default="CASES")
    ap.add_argument("--probe-src", default=None)
    args = ap.parse_args()

    rx = re.compile(args.arm_regex)
    text = Path(args.probe_out).read_text()
    emitted = {}
    for line in text.splitlines():
        m = rx.match(line.strip())
        if not m:
            continue
        arm = m.group(args.arm_group)
        kv = dict(p.split("=", 1) for p in m.group(args.arm_group + 1).split()
                  if "=" in p)
        emitted.setdefault(arm, {}).update(kv)

    rows = load_cases(args.cases_file, args.table)
    pinned = {(r[1], r[2]) for r in rows}
    emitted_pairs = {(a, k) for a, kv in emitted.items() for k in kv}

    print(f"emitted arms={len(emitted)} keys={len(emitted_pairs)}  "
          f"cases={len(rows)}")
    print("\n-- emitted but UNPINNED (measured surface with no assertion):")
    for a, k in sorted(emitted_pairs - pinned):
        print(f"   {a}|{k} = {emitted[a][k]!r}")
    print("\n-- pinned but NEVER EMITTED (row cannot pass):")
    for a, k in sorted(pinned - emitted_pairs):
        print(f"   {a}|{k}")
    if args.probe_src:
        psrc = Path(args.probe_src).read_text()
        print("\n-- pinned value is a probe LITERAL (assertion-carried):")
        for name, arm, key, val in rows:
            got = emitted.get(arm, {}).get(key)
            if got is None:
                continue
            # literal in probe source that would produce exactly this value
            # (quoted or bare key: Python dict, Lua table, JS object; the
            # emitted literal may itself be quoted -- "false" vs false)
            v = re.escape(str(val))
            pat = (rf'(?:["\']{re.escape(key)}["\']|\b{re.escape(key)}\b)'
                   rf'\s*[:=]\s*["\']?{v}["\']?\b')
            if re.search(pat, psrc):
                print(f"   {name:24} {arm}|{key}={got!r} "
                      f"(probe emits a literal)")


if __name__ == "__main__":
    main()
