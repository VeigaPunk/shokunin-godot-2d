#!/usr/bin/env python3
"""r92-simplifier static audit.

Scope-aware write-only-store scan (file scope + per function, assignment-target
aware), function/call-site census, print-site census, arm census, CLI-knob
census, and the harness-side r92 block census (row<->arm bijection, allowlist
entries, required_stderr entries, gate prefix coverage, insertion shape).

Usage: python3 audit_static.py > audit-static.txt
"""
import ast
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "committed-fixtures" / "tilemap_lattice.gd"
HARNESS = HERE / "committed-fixtures" / "run_battery.py"

IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
KEYWORDS = {
    "if", "elif", "else", "for", "while", "match", "return", "func", "var",
    "const", "class", "extends", "await", "and", "or", "not", "in", "is",
    "null", "true", "false", "self", "break", "continue", "pass", "static",
    "enum", "signal", "class_name", "super", "as", "when", "void", "int",
    "float", "bool", "String", "Vector2", "Vector2i", "Array", "Dictionary",
    "PackedStringArray", "PackedByteArray", "PackedVector2Array", "RID",
    "Color", "Image", "ImageTexture", "TileSet", "TileSetAtlasSource",
    "TileData", "TileMapLayer", "TileMapPattern", "CharacterBody2D",
    "CollisionShape2D", "RectangleShape2D", "NavigationPolygon",
    "NavigationServer2D", "ClassDB", "SceneTree", "Object", "TYPE_INT",
    "TYPE_STRING", "TYPE_STRING_NAME", "TYPE_BOOL", "TYPE_FLOAT", "TYPE_COLOR",
}


def strip_code(line: str) -> str:
    """Remove strings and comments (approximate but adequate for this file)."""
    out = []
    i = 0
    in_str = None
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = ch
            i += 1
            continue
        if ch == "#":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def scan_fixture(path: Path):
    lines = path.read_text().splitlines()
    code = [strip_code(l) for l in lines]

    # scope map: line index -> scope name ("" for file scope)
    scopes = {}
    scope = ""
    for idx, l in enumerate(code):
        m = re.match(r"^(\s*)func\s+(\w+)", l)
        if m:
            scope = m.group(2)
        scopes[idx] = scope

    decls = []  # (scope, name, line_no)
    for idx, l in enumerate(code):
        m = re.match(r"^\s*(?:@\w+\s+)*(var|const)\s+(\w+)", l)
        if m:
            decls.append((scopes[idx], m.group(2), idx + 1))

    # per-scope read counts
    reads = {}
    for idx, l in enumerate(code):
        sc = scopes[idx]
        # tokenize identifiers outside declaration/assignment target position
        stripped = l.strip()
        decl_m = re.match(r"^(?:@\w+\s+)*(var|const)\s+(\w+)", stripped)
        assign_m = re.match(r"^(\w+)\s*(?::=|[+\-*/]?=)\s*[^=]", stripped)
        for tok in IDENT.findall(l):
            if tok in KEYWORDS:
                continue
            if decl_m and tok == decl_m.group(2) and tok not in l.split("=", 1)[0]:
                # declaration name itself: the read is in the initializer
                continue
            if decl_m and tok == decl_m.group(2):
                # declaration token: skip only the first occurrence
                continue
            if assign_m and tok == assign_m.group(1):
                continue  # assignment target: a write, not a read
            reads[(sc, tok)] = reads.get((sc, tok), 0) + 1

    report = []
    report.append("== scope-aware store scan ==")
    report.append("declarations: %d" % len(decls))
    global_reads = {}
    for (sc, tok), n in reads.items():
        global_reads[tok] = global_reads.get(tok, 0) + n
    write_only = []
    for sc, name, ln in decls:
        n = global_reads.get(name, 0)
        if n == 0:
            write_only.append((sc, name, ln))
    report.append("write-only stores (zero reads anywhere): %d" % len(write_only))
    for sc, name, ln in write_only:
        report.append("  WO  scope=%-22s %s:%d" % (sc or "<file>", name, ln))
    report.append("declared names with a read only OUTSIDE their own scope:")
    for sc, name, ln in decls:
        local = reads.get((sc, name), 0)
        if local == 0 and global_reads.get(name, 0) > 0:
            report.append("  XS  scope=%-22s %-20s line=%-4d global_reads=%d"
                          % (sc or "<file>", name, ln, global_reads[name]))

    # per-function declared/read table
    report.append("")
    report.append("== per-function store table ==")
    for sc, name, ln in decls:
        report.append("  %-22s %-24s line=%-4d reads=%d"
                      % (sc or "<file>", name, ln, reads.get((sc, name), 0)))

    # function census
    funcs = []
    for idx, l in enumerate(code):
        m = re.match(r"^\s*func\s+(\w+)", l)
        if m:
            funcs.append((m.group(1), idx + 1))
    report.append("")
    report.append("== function census ==")
    for name, ln in funcs:
        calls = 0
        for idx, l in enumerate(code):
            if idx + 1 == ln:
                continue
            calls += len(re.findall(r"(?<![\w.])%s\s*\(" % re.escape(name), l))
        report.append("  %-24s line=%-4d call_sites=%d" % (name, ln, calls))

    # print sites
    report.append("")
    report.append("== print-site census ==")
    for idx, l in enumerate(code):
        if "print(" in l:
            report.append("  line=%-4d %s" % (idx + 1, lines[idx].strip()))

    # arm census
    report.append("")
    report.append("== arm census ==")
    arms = [m.group(1) for m in
            (re.match(r'\s*"(\w+)":', l) for l in lines) if m]
    report.append("  match arms: %s" % ", ".join(arms))

    # CLI knobs
    report.append("")
    report.append("== CLI knob census ==")
    for idx, l in enumerate(code):
        if "cmdline" in l or "--" in l:
            report.append("  line=%-4d %s" % (idx + 1, lines[idx].strip()))

    return "\n".join(report)


def harness_census(path: Path):
    src = path.read_text()
    tree = ast.parse(src)
    out = []
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": t[2],
                               "expected_exit": t[3],
                               "signature": t[4] if not isinstance(t[4], tuple)
                               else "ENVELOPE(%d payloads)" % len(t[4]),
                               "envelope": t[4] if isinstance(t[4], tuple) else None}
    r92 = {k: v for k, v in cases.items() if k.startswith("r92_")}
    out.append("== r92 CASES rows ==")
    out.append("total rows: %d  r92 rows: %d" % (len(cases), len(r92)))
    for k, v in r92.items():
        out.append("  %-28s script=%-20s flags=%s exit=%s"
                   % (k, v["script"], v["flags"], v["expected_exit"]))

    # allowlists + required_stderr
    exp_err, req_err = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "r92_tilemap_atlas" in keys and "nav_lattice_bake" in keys:
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_"):
                        exp_err[k.value] = ast.literal_eval(v)
            if "r92_tilemap_nullts_crash" in keys and "nav_lattice_teardown_crash" in keys:
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_"):
                        req_err[k.value] = ast.literal_eval(v)
    out.append("")
    out.append("== r92 expected_errors ==")
    n_entries = 0
    for k, v in exp_err.items():
        n_entries += len(v)
        out.append("  %-28s n=%d" % (k, len(v)))
        for e in v:
            out.append("      %s" % e)
    out.append("  total entries: %d across %d rows" % (n_entries, len(exp_err)))
    out.append("")
    out.append("== r92 required_stderr ==")
    for k, v in req_err.items():
        out.append("  %-28s n=%d" % (k, len(v)))
        for e in v:
            out.append("      %s" % e)

    # gate prefix coverage
    out.append("")
    out.append("== expected_errors floor gates (prefix coverage) ==")
    gate_lines = [(i + 1, l) for i, l in enumerate(src.splitlines())
                  if "expected_errors_all_matched" in l]
    for ln, l in gate_lines:
        out.append("  line=%-5d %s" % (ln, l.strip()))

    # arm bijection: flags --arm=<name> vs fixture match arms
    out.append("")
    out.append("== row<->arm bijection ==")
    flags = [v["flags"][0].split("=", 1)[1] for v in r92.values()]
    out.append("  arms referenced by r92 rows: %s" % ", ".join(flags))
    dup = [a for a in set(flags) if flags.count(a) > 1]
    out.append("  duplicate arms: %s" % (dup or "none"))
    out.append("  scripts referenced: %s"
               % ", ".join(sorted({v["script"] for v in r92.values()})))
    return "\n".join(out)


if __name__ == "__main__":
    print("### fixture: %s" % FIX)
    print(scan_fixture(FIX))
    print()
    print("### harness: %s" % HARNESS)
    print(harness_census(HARNESS))
