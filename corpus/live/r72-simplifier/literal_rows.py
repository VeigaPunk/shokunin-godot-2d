"""r72-simplifier scratch: AST census of emit() literal arguments + row join.

Two reports, no regex on raw text (the r71 regex false-positived on a
docstring `driver=dummy` mention):

1. For every `emit("<arm>", **kw)` call in the probe, classify each
   keyword argument as LITERAL (ast.Constant -- a battery row asserting it
   is assertion-carried, cannot fail for a mechanism reason) or COMPUTED
   (any expression -- measurement-carried).

2. For a battery CASES table, join each row against the probe's emitted
   literals: a row whose pinned value equals a literal the probe emits for
   that (arm, key) is assertion-carried.

Caveats: `emit` calls with non-constant arm (f-string) are skipped and
reported; keyword splats (**kw) are reported. No dynamic access assumed
(probe files verified to have none by unused_locals.py).
"""
import argparse
import ast
from pathlib import Path


def emit_literals(probe_src):
    """{(arm, key): literal_value} for every constant-valued emit kwarg."""
    tree = ast.parse(probe_src)
    literals = {}
    skipped = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "emit" and node.args):
            continue
        a0 = node.args[0]
        if not (isinstance(a0, ast.Constant) and isinstance(a0.value, str)):
            skipped.append((node.lineno, ast.unparse(a0)[:60]))
            continue
        arm = a0.value
        for kw in node.keywords:
            if kw.arg is None:
                skipped.append((node.lineno, "**splat"))
                continue
            if isinstance(kw.value, ast.Constant):
                literals[(arm, kw.arg)] = (kw.value.value, node.lineno)
    return literals, skipped


def load_cases(path, table="CASES"):
    tree = ast.parse(Path(path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == table for t in node.targets):
            rows = []
            for r in node.value.elts:
                if isinstance(r, (ast.Tuple, ast.List)) and len(r.elts) >= 4:
                    rows.append(tuple(
                        ast.literal_eval(e) if isinstance(e, ast.Constant)
                        else ast.unparse(e) for e in r.elts[:4]))
            return rows
    raise SystemExit(f"table {table} not found in {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--cases", default=None)
    ap.add_argument("--table", default="CASES")
    args = ap.parse_args()

    src = Path(args.probe).read_text()
    literals, skipped = emit_literals(src)
    print(f"== emit literal census: {args.probe}")
    print(f"literal-valued (arm,key) pairs: {len(literals)}")
    for (arm, key), (val, ln) in sorted(literals.items()):
        print(f"   {arm}|{key} = {val!r}  (emit at line {ln})")
    if skipped:
        print(f"skipped emit calls (non-constant arm / splat): {skipped}")
    if not args.cases:
        return
    rows = load_cases(args.cases, args.table)
    print(f"\n== row join: {args.cases} ({len(rows)} rows)")
    carried = []
    for name, arm, key, pinned in rows:
        if (arm, key) in literals:
            val, ln = literals[(arm, key)]
            same = (val == pinned) or (str(val) == str(pinned))
            carried.append((name, arm, key, pinned, val, same, ln))
    if not carried:
        print("   no row pins a literal-valued emitted key")
    for name, arm, key, pinned, val, same, ln in carried:
        tag = "MATCH" if same else f"literal={val!r} vs pinned={pinned!r}"
        print(f"   {name:26} {arm}|{key}  {tag}  (emit line {ln})")
    print(f"assertion-carried rows (pinned == emitted literal): "
          f"{sum(1 for c in carried if c[5])}")


if __name__ == "__main__":
    main()
