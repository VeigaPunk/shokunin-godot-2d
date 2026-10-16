#!/usr/bin/env python3
"""r93-simplifier static audit.

Scope-aware write-only-store scan (file scope + per function, assignment-target
aware) over BOTH r93 fixtures, function/call-site census, print-site census,
arm census, CLI-knob census, and the harness-side r93 block census
(row<->arm bijection, expected_errors / required_stderr entries, floor-gate
prefix coverage, insertion shape).

Usage: python3 audit_static.py > audit-static.txt
"""
import ast
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXES = [HERE / "committed-fixtures" / "anim_lattice.gd",
         HERE / "committed-fixtures" / "r93b_anim.gd"]
HARNESS = HERE / "committed-fixtures" / "run_battery.py"

IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
KEYWORDS = {
    "if", "elif", "else", "for", "while", "match", "return", "func", "var",
    "const", "class", "extends", "await", "and", "or", "not", "in", "is",
    "null", "true", "false", "self", "break", "continue", "pass", "static",
    "enum", "signal", "class_name", "super", "as", "when", "void", "int",
    "float", "bool", "String", "StringName", "Array", "Dictionary", "Node",
    "Node2D", "Object", "RefCounted", "Resource", "SceneTree", "Tween",
    "Animation", "AnimationPlayer", "AnimationMixer", "AnimationLibrary",
    "AnimationNode", "ClassDB", "Engine", "OS", "Time", "NodePath",
    "PackedStringArray", "Callable", "TYPE_VALUE", "TYPE_METHOD",
    "TYPE_POSITION_3D", "TRANS_LINEAR", "TRANS_BACK", "TRANS_SPRING",
    "TRANS_EXPO", "TRANS_ELASTIC", "EASE_IN", "EASE_OUT", "EASE_IN_OUT",
    "EASE_OUT_IN", "TWEEN_PROCESS_IDLE", "TWEEN_PROCESS_PHYSICS",
    "ANIMATION_PROCESS_MANUAL", "ANIMATION_PROCESS_IDLE",
    "ANIMATION_PROCESS_PHYSICS", "ANIMATION_METHOD_CALL_DEFERRED",
    "ANIMATION_METHOD_CALL_IMMEDIATE", "LOOP_NONE", "LOOP_LINEAR",
    "Vector2", "Vector3", "Color", "range", "print", "push_error",
}


def strip_code(line: str) -> str:
    """Remove strings and comments (approximate but adequate for these files)."""
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
    r = []
    r.append("### fixture: %s (%d lines)" % (path.name, len(lines)))

    # scope map: line index -> enclosing scope ("" = file scope). Inner
    # classes get their own namespace (`class:X`), and a member read inside a
    # method of X is also credited to X itself (so class members are not
    # mis-reported as cross-scope).
    scopes = {}
    scope = ""
    cls = None
    for idx, l in enumerate(code):
        mc = re.match(r"^(\s*)class\s+(\w+)", l)
        if mc:
            cls = mc.group(2)
            scope = "class:%s" % cls
            scopes[idx] = scope
            continue
        m = re.match(r"^(\s*)func\s+(\w+)", l)
        if m:
            scope = ("%s.%s" % (scope.split(".")[0], m.group(2))
                     if scope.startswith("class:") else m.group(2))
        scopes[idx] = scope

    decls = []  # (scope, kind, name, line_no)
    for idx, l in enumerate(code):
        m = re.match(r"^\s*(?:@\w+\s+)*(var|const|signal)\s+(\w+)", l)
        if m:
            decls.append((scopes[idx], m.group(1), m.group(2), idx + 1))

    # per-scope read counts: identifiers in non-declaration-target,
    # non-assignment-target position.
    reads = {}
    for idx, l in enumerate(code):
        sc = scopes[idx]
        stripped = l.strip()
        decl_m = re.match(r"^(?:@\w+\s+)*(var|const|signal)\s+(\w+)", stripped)
        assign_m = re.match(r"^(\w+)\s*(?::=|[+\-*/]?=)\s*[^=]", stripped)
        for tok in IDENT.findall(l):
            if tok in KEYWORDS:
                continue
            if decl_m and tok == decl_m.group(2):
                continue  # declaration name token
            if assign_m and tok == assign_m.group(1):
                continue  # assignment target: a write, not a read
            reads[(sc, tok)] = reads.get((sc, tok), 0) + 1
            if sc.startswith("class:") and "." in sc:
                reads[(sc.split(".")[0], tok)] = reads.get((sc.split(".")[0], tok), 0) + 1

    global_reads = {}
    for (sc, tok), n in reads.items():
        global_reads[tok] = global_reads.get(tok, 0) + n

    write_only = [(sc, kind, name, ln) for sc, kind, name, ln in decls
                  if global_reads.get(name, 0) == 0]
    r.append("declarations: %d (%s)"
             % (len(decls), ", ".join(sorted({d[1] for d in decls})) or "none"))
    r.append("write-only stores (zero reads anywhere): %d" % len(write_only))
    for sc, kind, name, ln in write_only:
        r.append("  WO  scope=%-22s %-7s %s:%d" % (sc or "<file>", kind, name, ln))
    r.append("declared names read only OUTSIDE their own scope: %d"
             % sum(1 for sc, _, name, _ in decls
                   if reads.get((sc, name), 0) == 0 and global_reads.get(name, 0) > 0))
    for sc, kind, name, ln in decls:
        if reads.get((sc, name), 0) == 0 and global_reads.get(name, 0) > 0:
            r.append("  XS  scope=%-22s %-20s line=%-4d global_reads=%d"
                     % (sc or "<file>", name, ln, global_reads[name]))

    # function census
    funcs = [(m.group(1), idx + 1) for idx, l in enumerate(code)
             for m in [re.match(r"^\s*func\s+(\w+)", l)] if m]
    r.append("")
    r.append("== function census (%d funcs) ==" % len(funcs))
    for name, ln in funcs:
        calls = 0
        for idx, l in enumerate(code):
            if idx + 1 == ln:
                continue
            calls += len(re.findall(r"(?<![\w.])%s\s*\(" % re.escape(name), l))
        r.append("  %-24s line=%-4d call_sites=%d" % (name, ln, calls))

    # print sites
    r.append("")
    r.append("== print-site census ==")
    for idx, l in enumerate(code):
        if re.search(r"\bprint\(", l):
            r.append("  line=%-4d %s" % (idx + 1, lines[idx].strip()[:160]))

    # arm census (scoped to the `match arm:` block only)
    r.append("")
    r.append("== arm census ==")
    arms = []
    match_indent = None
    in_match = False
    for l in lines:
        if re.match(r"^\s*match\s+arm\s*:", l):
            in_match = True
            match_indent = len(l) - len(l.lstrip())
            continue
        if in_match:
            if not l.strip():
                continue
            indent = len(l) - len(l.lstrip())
            m = re.match(r'^"([\w_]+)":', l.strip())
            if indent > match_indent and m:
                arms.append(m.group(1))
            elif indent <= match_indent:
                in_match = False
    r.append("  match arms (%d): %s" % (len(arms), ", ".join(arms)))
    default_arg = None
    for idx, l in enumerate(lines):
        m = re.search(r'_arg\(\s*"arm"\s*,\s*"([^"]*)"', l)
        if m:
            default_arg = m.group(1)
            r.append("  default arm (line %d): %s" % (idx + 1, m.group(1)))
    r.append("  fixture fallback: %s"
             % ("unknown-arm print present" if any("unknown arm=" in l for l in lines)
                else "MISSING"))
    r.append("  arms covered by match: %d  (+default %s)"
             % (len(arms), default_arg))

    # CLI knobs
    r.append("")
    r.append("== CLI knob census ==")
    for idx, l in enumerate(code):
        if "cmdline" in l or "_arg(" in l:
            r.append("  line=%-4d %s" % (idx + 1, lines[idx].strip()[:140]))
    return "\n".join(r), arms, default_arg


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
                               "signature": t[4]}
    r93 = {k: v for k, v in cases.items() if k.startswith("r93_")}
    out.append("### harness: %s" % path.name)
    out.append("== CASES rows ==")
    out.append("total rows: %d  r93 rows: %d" % (len(cases), len(r93)))
    for k, v in r93.items():
        sig = v["signature"]
        out.append("  %-38s script=%-18s flags=%s exit=%s sig_len=%d"
                   % (k, v["script"], v["flags"], v["expected_exit"],
                      len(sig) if isinstance(sig, str) else -1))

    # ordering / adjacency of the r93 block
    names = list(cases)
    idx = [i for i, n in enumerate(names) if n.startswith("r93_")]
    out.append("")
    out.append("== block position ==")
    out.append("  r93 index range: %d..%d (contiguous=%s)"
               % (min(idx), max(idx), max(idx) - min(idx) + 1 == len(idx)))
    out.append("  predecessor: %s" % names[min(idx) - 1])
    out.append("  successor:   %s" % names[max(idx) + 1])

    # allowlists + required_stderr dicts
    exp_err, req_err = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            dict_keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
            is_req = "r92_tilemap_nullts_crash" in dict_keys
            for k, v in zip(node.keys, node.values):
                if not isinstance(k, ast.Constant):
                    continue
                key = str(k.value)
                if not key.startswith("r93_") or key.endswith("_all_matched"):
                    continue  # gate dicts hold all(...) comprehensions, not allowlists
                if isinstance(v, (ast.Tuple, ast.List)):
                    (req_err if is_req else exp_err)[key] = ast.literal_eval(v)
    out.append("")
    out.append("== r93 expected_errors ==")
    out.append("  rows carrying entries: %d  total entries: %d"
               % (len(exp_err), sum(len(v) for v in exp_err.values())))
    for k, v in exp_err.items():
        for e in v:
            out.append("      %-38s %s" % (k, e))
    out.append("")
    out.append("== r93 required_stderr ==")
    out.append("  rows carrying entries: %d  total entries: %d"
               % (len(req_err), sum(len(v) for v in req_err.values())))
    for k, v in req_err.items():
        for e in v:
            out.append("      %-38s %s" % (k, e))

    # gate prefix coverage
    out.append("")
    out.append("== expected_errors floor gates ==")
    lines = src.splitlines()
    for i, l in enumerate(lines):
        if "expected_errors_all_matched" in l:
            prefix = re.search(r'startswith\("([^"]+)"\)', "\n".join(lines[i:i + 9]))
            out.append("  line=%-5d %-46s prefix=%s"
                       % (i + 1, l.strip().rstrip('":'), prefix.group(1) if prefix else "?"))

    # row<->arm bijection
    out.append("")
    out.append("== row<->arm bijection ==")
    per_script = {}
    for k, v in r93.items():
        arm = v["flags"][0].split("=", 1)[1] if v["flags"] and "=" in v["flags"][0] else "?"
        per_script.setdefault(v["script"], []).append((k, arm, v["expected_exit"]))
    for script, rows in per_script.items():
        arms = [a for _, a, _ in rows]
        out.append("  %s: %d rows" % (script, len(rows)))
        dup = sorted({a for a in arms if arms.count(a) > 1})
        out.append("    duplicate arms: %s" % (", ".join(dup) or "none"))
        out.append("    exits: %s" % sorted({e for _, _, e in rows}))
        for k, a, e in rows:
            out.append("      %-38s arm=%-12s exit=%s" % (k, a, e))
    return "\n".join(out), r93


if __name__ == "__main__":
    fixtures = {}
    for f in FIXES:
        text, arms, default = scan_fixture(f)
        fixtures[f.name] = (arms, default)
        print(text)
        print()
    print(harness_census(HARNESS)[0])
    print()
    print("== cross-check: harness arms vs fixture arms ==")
    r93 = harness_census(HARNESS)[1]
    used = {}
    for k, v in r93.items():
        arm = v["flags"][0].split("=", 1)[1]
        used.setdefault(v["script"], set()).add(arm)
    for script, (arms, default) in fixtures.items():
        u = used.get(script, set())
        missing_rows = [a for a in arms if a not in u]
        phantom = sorted(a for a in u if a not in arms)
        print("  %s: fixture arms=%d  referenced=%d" % (script, len(arms), len(u)))
        print("    arms with NO row: %s" % (", ".join(missing_rows) or "none"))
        print("    rows referencing a non-existent arm: %s" % (", ".join(phantom) or "none"))
