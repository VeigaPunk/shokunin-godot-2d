#!/usr/bin/env python3
"""r94-simplifier static audit (committed tree c7228893).

Scope-aware write-only-store scan (file scope + per function, assignment-target
aware) over the committed particles fixture, function/print/arm/CLI census,
harness-side r94 block census (row<->arm bijection, expected_errors /
required_stderr entries, floor-gate prefix coverage, insertion shape),
signature redundancy census (exact duplicates + substring subsumption) over
every r94 row and across the whole CASES table, and gate-prefix
non-redundancy (can any sibling gate's case prefix match an r94_ case?).

Usage: python3 audit_static.py > audit-static.txt
"""
import ast
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "committed-fixtures" / "particles_lattice.gd"
HARNESS = HERE / "committed-fixtures" / "run_battery.py"

IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
KEYWORDS = {
    "if", "elif", "else", "for", "while", "match", "return", "func", "var",
    "const", "class", "extends", "await", "and", "or", "not", "in", "is",
    "null", "true", "false", "self", "break", "continue", "pass", "static",
    "enum", "signal", "class_name", "super", "as", "when", "void", "int",
    "float", "bool", "String", "StringName", "Array", "Dictionary", "Node",
    "Node2D", "Object", "RefCounted", "Resource", "SceneTree", "Tween",
    "Animation", "ClassDB", "Engine", "OS", "Time", "NodePath", "Vector2",
    "Vector3", "Color", "Rect2", "Transform2D", "GradientTexture1D",
    "GradientTexture2D", "CPUParticles2D", "GPUParticles2D",
    "ParticleProcessMaterial", "PROPERTY_USAGE_GROUP",
    "PROPERTY_USAGE_CATEGORY", "PROPERTY_USAGE_EDITOR",
    "PROPERTY_USAGE_STORAGE", "PROCESS_MODE_DISABLED",
    "PROCESS_MODE_INHERIT", "range", "print", "push_error", "str",
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
    r = []
    r.append("### fixture: %s (%d lines, sha256 %s)"
             % (path.name, len(lines), __import__("hashlib").sha256(
                 path.read_bytes()).hexdigest()))

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

    decls = []
    for idx, l in enumerate(code):
        m = re.match(r"^\s*(?:@\w+\s+)*(var|const|signal)\s+(\w+)", l)
        if m:
            decls.append((scopes[idx], m.group(1), m.group(2), idx + 1))

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
                continue
            if assign_m and tok == assign_m.group(1):
                continue
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
    for sc, kind, name, ln in decls:
        r.append("  decl scope=%-22s %-7s %-22s line=%-4d reads=%d"
                 % (sc or "<file>", kind, name, ln, global_reads.get(name, 0)))
    r.append("write-only stores (zero reads anywhere): %d" % len(write_only))
    for sc, kind, name, ln in write_only:
        r.append("  WO  scope=%-22s %-7s %s:%d" % (sc or "<file>", kind, name, ln))

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

    r.append("")
    r.append("== print-site census ==")
    for idx, l in enumerate(code):
        if re.search(r"\bprint\(", l):
            r.append("  line=%-4d %s" % (idx + 1, lines[idx].strip()[:160]))

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
    r.append("  arms covered by match: %d  (+default %s)" % (len(arms), default_arg))

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
    r94 = {k: v for k, v in cases.items() if k.startswith("r94_")}
    out.append("### harness: %s (sha256 %s)"
               % (path.name, __import__("hashlib").sha256(
                   path.read_bytes()).hexdigest()))
    out.append("== CASES rows ==")
    out.append("total rows: %d  r94 rows: %d" % (len(cases), len(r94)))
    for k, v in r94.items():
        sig = v["signature"]
        out.append("  %-38s script=%-22s flags=%s exit=%s sig_len=%d"
                   % (k, v["script"], v["flags"], v["expected_exit"],
                      len(sig) if isinstance(sig, str) else -1))

    names = list(cases)
    idx = [i for i, n in enumerate(names) if n.startswith("r94_")]
    out.append("")
    out.append("== block position ==")
    out.append("  r94 index range: %d..%d (contiguous=%s)"
               % (min(idx), max(idx), max(idx) - min(idx) + 1 == len(idx)))
    out.append("  predecessor: %s" % names[min(idx) - 1])
    out.append("  successor:   %s" % names[max(idx) + 1])

    exp_err, req_err = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            dict_keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
            is_req = "r92_tilemap_nullts_crash" in dict_keys
            for k, v in zip(node.keys, node.values):
                if not isinstance(k, ast.Constant):
                    continue
                key = str(k.value)
                if not key.startswith("r94_") or key.endswith("_all_matched"):
                    continue
                if isinstance(v, (ast.Tuple, ast.List)):
                    (req_err if is_req else exp_err)[key] = ast.literal_eval(v)
    out.append("")
    out.append("== r94 expected_errors ==")
    out.append("  rows carrying entries: %d  total entries: %d"
               % (len(exp_err), sum(len(v) for v in exp_err.values())))
    for k, v in exp_err.items():
        for e in v:
            out.append("      %-38s %s" % (k, e))
    out.append("")
    out.append("== r94 required_stderr ==")
    out.append("  rows carrying entries: %d  total entries: %d"
               % (len(req_err), sum(len(v) for v in req_err.values())))
    for k, v in req_err.items():
        for e in v:
            out.append("      %-38s %s" % (k, e))

    out.append("")
    out.append("== expected_errors floor gates ==")
    lines = src.splitlines()
    gate_prefixes = []
    for i, l in enumerate(lines):
        if "expected_errors_all_matched" in l:
            prefix = re.search(r'startswith\("([^"]+)"\)', "\n".join(lines[i:i + 9]))
            p = prefix.group(1) if prefix else "?"
            gate_prefixes.append(p)
            out.append("  line=%-5d %-52s prefix=%s"
                       % (i + 1, l.strip().rstrip('":'), p))

    # gate-prefix non-redundancy: which gate prefixes could match an r94_ case?
    out.append("")
    out.append("== gate-prefix non-redundancy ==")
    matching = [p for p in gate_prefixes if "r94_".startswith(p)]
    out.append("  gate prefixes: %s" % ", ".join(gate_prefixes))
    out.append("  prefixes that can match an r94_ case: %s"
               % (", ".join(matching) or "NONE"))

    # signature redundancy census (exact + substring subsumption)
    out.append("")
    out.append("== signature redundancy ==")
    by_sig = {}
    for k, v in cases.items():
        by_sig.setdefault(v["signature"], []).append(k)
    exact = {s: ks for s, ks in by_sig.items() if len(ks) > 1}
    out.append("  exact-duplicate signatures across all %d rows: %d"
               % (len(cases), len(exact)))
    for s, ks in exact.items():
        out.append("    %s <- %s" % (s[:80], ks))
    r94_sigs = {k: v["signature"] for k, v in r94.items()}
    subs = []
    for a, sa in r94_sigs.items():
        for b, sb in r94_sigs.items():
            if a == b:
                continue
            if sb in sa and len(sb) < len(sa):
                subs.append((a, b, len(sa), len(sb)))
    out.append("  r94 substring-subsumption pairs: %d" % len(subs))
    for a, b, la, lb in subs:
        out.append("    %s (%d) subsumes %s (%d)" % (a, la, b, lb))
    # cross-round subsumption: is any r94 signature a substring of a non-r94 row?
    cross = []
    for a, sa in r94_sigs.items():
        for b, vb in cases.items():
            if b.startswith("r94_"):
                continue
            sb = vb["signature"]
            if isinstance(sb, str) and sb in sa:
                cross.append((a, b))
    out.append("  r94 signatures subsuming/containing a foreign row's signature: %d"
               % len(cross))
    for a, b in cross:
        out.append("    %s contains %s" % (a, b))

    # row<->arm bijection
    out.append("")
    out.append("== row<->arm bijection ==")
    per_script = {}
    for k, v in r94.items():
        arm = v["flags"][0].split("=", 1)[1] if v["flags"] and "=" in v["flags"][0] else "?"
        per_script.setdefault(v["script"], []).append((k, arm, v["expected_exit"]))
    for script, rows in per_script.items():
        arms = [a for _, a, _ in rows]
        out.append("  %s: %d rows" % (script, len(rows)))
        dup = sorted({a for a in arms if arms.count(a) > 1})
        out.append("    duplicate arms: %s" % (", ".join(dup) or "none"))
        out.append("    exits: %s" % sorted({e for _, _, e in rows}))
        for k, a, e in rows:
            out.append("      %-38s arm=%-14s exit=%s" % (k, a, e))
    return "\n".join(out), r94, gate_prefixes


if __name__ == "__main__":
    text, arms, default = scan_fixture(FIXTURE)
    print(text)
    print()
    htext, r94, gates = harness_census(HARNESS)
    print(htext)
    print()
    print("== cross-check: harness arms vs fixture arms ==")
    used = set()
    for k, v in r94.items():
        used.add(v["flags"][0].split("=", 1)[1])
    fixture_arms = set(arms)
    missing_rows = sorted(a for a in fixture_arms if a not in used)
    phantom = sorted(a for a in used if a not in fixture_arms)
    print("  fixture arms=%d  referenced=%d" % (len(fixture_arms), len(used)))
    print("    arms with NO row: %s" % (", ".join(missing_rows) or "none"))
    print("    rows referencing a non-existent arm: %s" % (", ".join(phantom) or "none"))
    print("  gates: %s" % ", ".join(gates))
