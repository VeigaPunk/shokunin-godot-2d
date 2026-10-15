"""r71 simplifier scratch: weight census for a Python battery runner.

Usage:
    python3 weight_census.py <target.py> [--sibling other.py] [--table NAME]

Reports, for the target file:
  1. top-level defs, their line spans, and their *static* reference count
     (Name / Attribute / string-literal mentions anywhere in the file)
     -- a def with 0 references outside its own body is a dead-code
     candidate (literal fallback: no Python language server on this host;
     this is a textual/AST census, NOT semantic proof).
  2. dynamic-name escape hatches (getattr/locals/globals/exec/eval/
     importlib) that would invalidate the census.
  3. verbatim/near-verbatim function duplication against a sibling file
     (normalized-token SequenceMatcher ratio per def, plus whole-file
     ratio) -- the "duplicate authority" measurement.
  4. table rows of a named list constant (e.g. CASES): name, and whether
     the row's pinned key string appears anywhere in the file.
"""
import argparse
import ast
import difflib
import re
import sys
from pathlib import Path

DYNAMIC = ("getattr", "setattr", "locals", "globals", "exec", "eval",
           "vars", "__dict__", "importlib")


def norm_tokens(src):
    """Whitespace-insensitive token stream, comments/strings folded."""
    src = re.sub(r"#.*", "", src)
    src = re.sub(r"\s+", " ", src)
    return src.strip()


def collect_defs(tree, src):
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            seg = ast.get_source_segment(src, node) or ""
            out.append((node.name, node.lineno, node.end_lineno, seg))
    return out


def name_mentions(src, tree):
    """Count identifier mentions per name across the whole file."""
    counts = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            counts[node.id] = counts.get(node.id, 0) + 1
        elif isinstance(node, ast.Attribute):
            counts[node.attr] = counts.get(node.attr, 0) + 1
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            for word in re.findall(r"[A-Za-z_][A-Za-z_0-9]*", node.value):
                counts[word] = counts.get(word, 0) + 1
    return counts


def body_mentions(name, seg):
    return len(re.findall(rf"\b{re.escape(name)}\b", seg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--sibling")
    ap.add_argument("--table", default="CASES")
    args = ap.parse_args()

    tpath = Path(args.target)
    src = tpath.read_text()
    tree = ast.parse(src)
    print(f"== census: {tpath} ({len(src.splitlines())} lines, "
          f"sha256={__import__('hashlib').sha256(src.encode()).hexdigest()[:16]})")

    defs = collect_defs(tree, src)
    counts = name_mentions(src, tree)
    print("\n-- top-level defs: name lines refs_outside_own_body")
    for name, lo, hi, seg in defs:
        # the def line itself contributes exactly one textual mention and
        # never a Name node; subtract it (plus any self-recursion).
        inside_recursive = max(0, body_mentions(name, seg) - 1)
        total = counts.get(name, 0)
        outside = total - inside_recursive
        flag = "  <-- DEAD-CANDIDATE" if outside <= 0 else ""
        print(f"   {name:24} {lo:>5}-{hi:<5} refs_total={total:<3} "
              f"outside_own_body={outside}{flag}")

    print("\n-- dynamic-name escape hatches")
    found = [d for d in DYNAMIC if re.search(rf"\b{re.escape(d)}\b", src)]
    print(f"   {found if found else 'none'}")

    if args.sibling:
        spath = Path(args.sibling)
        ssrc = spath.read_text()
        stree = ast.parse(ssrc)
        sdefs = {n: seg for n, _, _, seg in collect_defs(stree, ssrc)}
        print(f"\n-- duplication vs {spath}")
        whole = difflib.SequenceMatcher(
            None, norm_tokens(src).split(" "),
            norm_tokens(ssrc).split(" ")).ratio()
        print(f"   whole-file normalized-token ratio: {whole:.3f}")
        for name, lo, hi, seg in defs:
            if name in sdefs:
                r = difflib.SequenceMatcher(
                    None, norm_tokens(seg).split(" "),
                    norm_tokens(sdefs[name]).split(" ")).ratio()
                print(f"   {name:24} ratio_vs_sibling={r:.3f}"
                      f"{'  <-- VERBATIM' if r > 0.98 else ''}")

    tbl = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == args.table
                for t in node.targets):
            tbl = node
    if tbl is not None:
        rows = [r for r in tbl.value.elts if isinstance(r, (ast.Tuple, ast.List))]
        print(f"\n-- table {args.table}: {len(rows)} rows "
              f"(lines {tbl.lineno}-{tbl.end_lineno})")
        for r in rows:
            try:
                name = ast.literal_eval(r.elts[0])
            except Exception:
                name = "<expr>"
            seg = ast.get_source_segment(src, r) or ""
            keys = [ast.literal_eval(e) for e in r.elts[1:]
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            # is each key emitted as a literal anywhere in the file?
            hits = {k: len(re.findall(rf'["\']{re.escape(k)}["\']', src))
                    for k in keys}
            print(f"   {name:28} line {r.lineno:>5}  key_literal_hits={hits}")


if __name__ == "__main__":
    main()
