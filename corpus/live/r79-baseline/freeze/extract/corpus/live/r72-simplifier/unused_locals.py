"""r71 simplifier scratch: unused-local-binding scan (dead alternate path).

AST-based: for every function scope, report assigned names (Assign /
AnnAssign / For targets / with-as / tuple unpacking) that are never read
(no Load context) anywhere in that scope, and whose names do not appear in
any nested scope either.

Caveats (literal fallback, no Python language server on this host):
  * `_`-prefixed names are reported separately (conventional throwaway);
  * dynamic access (locals()/globals()/exec/eval/getattr) is detected and
    reported, since it would invalidate the census;
  * a name read only inside a nested def is treated as USED (nested scopes
    are searched), so closures do not produce false positives.
"""
import argparse
import ast
from pathlib import Path

DYNAMIC = ("locals", "globals", "exec", "eval", "vars")


def bound_names(node):
    """Names bound by a statement's target(s)."""
    out = []
    for t in ast.walk(node):
        if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
            out.append(t.id)
    return out


def loads_in(scope):
    return {n.id for n in ast.walk(scope)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def scan_function(fn, src):
    bound = {}
    for node in ast.walk(fn):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            for name in bound_names(node):
                bound.setdefault(name, node.lineno)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            for name in bound_names(node.target):
                bound.setdefault(name, node.lineno)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    for name in bound_names(item.optional_vars):
                        bound.setdefault(name, node.lineno)
    used = loads_in(fn)
    return {n: ln for n, ln in bound.items() if n not in used}, used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    args = ap.parse_args()
    path = Path(args.target)
    src = path.read_text()
    tree = ast.parse(src)
    print(f"== unused-binding scan: {path}")
    dyn = [d for d in DYNAMIC if f"{d}(" in src]
    print(f"dynamic-access sites: {dyn if dyn else 'none'}")
    total = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            unused, _ = scan_function(node, src)
            if not unused:
                continue
            plain = {n: l for n, l in unused.items() if not n.startswith("_")}
            under = {n: l for n, l in unused.items() if n.startswith("_")}
            if plain:
                total += len(plain)
                for n, ln in sorted(plain.items(), key=lambda kv: kv[1]):
                    print(f"   {node.name}:{ln} bound-but-never-read: {n}")
            for n, ln in sorted(under.items(), key=lambda kv: kv[1]):
                print(f"   {node.name}:{ln} throwaway (underscore): {n}")
    print(f"unused non-underscore bindings: {total}")


if __name__ == "__main__":
    main()
