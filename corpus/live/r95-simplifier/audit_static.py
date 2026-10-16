#!/usr/bin/env python3
"""r95-simplifier static audit (committed tree 9cd47507).

Sections
  A. fixture census (dss_lattice.gd, r95b_order.gd): lines/sha, declarations,
     value-observation scan (dead stores: declaration + writes with zero
     observational reads; _pile out-parameter writes classified separately),
     function call-site census, print-site census, match-arm census, CLI knobs.
  B. harness census (committed run_battery.py): CASES totals, r95 block
     position, r95 expected_errors/required_stderr entries, floor gates and
     gate-prefix non-redundancy, signature redundancy (exact + substring
     subsumption within identical launches), row<->arm bijection, arm coverage.
  C. cross-check: fixture arms vs row-referenced arms; ghost rows.

Reads only the committed-fixtures/ snapshot. Usage:
  python3 audit_static.py > audit-static.txt
"""
import ast
import hashlib
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CF = HERE / "committed-fixtures"

IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
KEYWORDS = {
    "if", "elif", "else", "for", "while", "match", "return", "func", "var",
    "const", "class", "extends", "await", "and", "or", "not", "in", "is",
    "null", "true", "false", "self", "break", "continue", "pass", "static",
    "enum", "signal", "class_name", "super", "as", "when", "void", "int",
    "float", "bool", "String", "StringName", "Array", "Dictionary", "Node",
    "Node2D", "Object", "RefCounted", "Resource", "SceneTree", "Tween",
    "Animation", "ClassDB", "Engine", "OS", "Time", "NodePath", "Vector2",
    "Vector3", "Color", "Rect2", "Transform2D", "range", "print", "str",
    "RID", "PackedStringArray", "Vector2i", "PhysicsServer2D",
    "PhysicsDirectSpaceState2D", "CollisionObject2D", "CollisionShape2D",
    "RectangleShape2D", "CircleShape2D", "Shape2D", "SubViewport",
    "CanvasLayer", "Sprite2D", "StaticBody2D", "RigidBody2D",
    "CharacterBody2D", "Area2D", "PhysicsRayQueryParameters2D",
    "PhysicsPointQueryParameters2D", "PhysicsShapeQueryParameters2D",
    "BODY_MODE_STATIC", "BODY_STATE_TRANSFORM",
}


def strip_code(line: str) -> str:
    out, i, in_str = [], 0, None
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


def fixture_census(path: Path) -> tuple[str, list[str]]:
    lines = path.read_text().splitlines()
    code = [strip_code(l) for l in lines]
    r = [f"### fixture: {path.name} ({len(lines)} lines, sha256 "
         f"{hashlib.sha256(path.read_bytes()).hexdigest()})"]

    # scopes: file scope, func scope
    scopes, scope = {}, "<file>"
    for idx, l in enumerate(code):
        m = re.match(r"^(\s*)func\s+(\w+)", l)
        if m:
            scope = m.group(2)
        scopes[idx] = scope

    decls = []  # (scope, kind, name, line)
    for idx, l in enumerate(code):
        m = re.match(r"^\s*(?:@\w+\s+)*(var|const|signal)\s+(\w+)", l)
        if m:
            decls.append((scopes[idx], m.group(1), m.group(2), idx + 1))

    # occurrence classification per declared name (scope-aware: function locals
    # are counted inside their own scope only; file-scope names file-wide)
    r.append("")
    r.append("== declarations and value observation (%d) ==" % len(decls))
    dead = []
    for sc, kind, name, dline in decls:
        occ = []
        for idx, l in enumerate(code):
            if sc != "<file>" and scopes[idx] != sc:
                continue
            if not re.search(r"(?<![\w.])%s(?![\w])" % re.escape(name), l):
                continue
            if idx + 1 == dline:
                occ.append((idx + 1, "decl"))
                continue
            stripped = l.strip()
            if re.match(r"^(?:%s)\s*(?::=|[+\-*/]?=)(?!=)" % re.escape(name), stripped):
                occ.append((idx + 1, "assign"))
            elif re.search(r"(?<![\w.])%s\.(append|push_back)\s*\(" % re.escape(name), l):
                occ.append((idx + 1, "append"))
            elif "_pile(" in l:
                occ.append((idx + 1, "out-arg"))
            else:
                occ.append((idx + 1, "read"))
        reads = [o for o in occ if o[1] == "read"]
        assigns = [o for o in occ if o[1] == "assign"]
        outargs = [o for o in occ if o[1] == "out-arg"]
        decl_line = lines[dline - 1].strip()
        if not reads:
            cls = ("dead-out-param" if outargs and not assigns
                   else "dead-assign" if assigns and not outargs
                   else "dead-append-only" if any(o[1] == "append" for o in occ)
                   else "dead-no-read")
            dead.append((name, dline, cls, occ))
        r.append("  %-22s %-5s %-16s line=%-4d reads=%-2d assigns=%-2d outargs=%-2d %s"
                 % (sc, kind, name, dline, len(reads), len(assigns), len(outargs),
                    "  <== " + cls if not reads else ""))
        if not reads:
            r.append("        decl: %s" % decl_line)
            for ln, how in occ:
                r.append("        occ line=%-4d %-8s %s" % (ln, how, lines[ln - 1].strip()[:120]))

    # _pile call-result stores: `var X := _pile(...)` never read afterwards
    r.append("")
    r.append("== _pile call-result stores (var X := _pile(...)) ==")
    for idx, l in enumerate(code):
        m = re.match(r"^\s*var\s+(\w+)\s*:=\s*_pile\(", l)
        if not m:
            continue
        name = m.group(1)
        later = [i + 1 for i, ll in enumerate(code)
                 if i > idx and re.search(r"(?<![\w.])%s(?![\w])" % re.escape(name), ll)]
        r.append("  %-10s line=%-4d later_occurrences=%s %s"
                 % (name, idx + 1, later or "NONE",
                    "<== dead-call-result" if not later else ""))

    r.append("")
    r.append("== function call-site census ==")
    funcs = [(m.group(1), idx + 1) for idx, l in enumerate(code)
             for m in [re.match(r"^\s*func\s+(\w+)", l)] if m]
    for name, ln in funcs:
        calls = sum(len(re.findall(r"(?<![\w.])%s\s*\(" % re.escape(name), l))
                    for idx, l in enumerate(code) if idx + 1 != ln)
        r.append("  %-22s line=%-4d call_sites=%d" % (name, ln, calls))

    r.append("")
    r.append("== print-site census ==")
    for idx, l in enumerate(code):
        if re.search(r"\bprint\(", l):
            r.append("  line=%-4d %s" % (idx + 1, lines[idx].strip()[:150]))

    r.append("")
    r.append("== match-arm census ==")
    arms, in_match, m_indent = [], False, 0
    for l in lines:
        if re.match(r"^\s*match\s+arm\s*:", l):
            in_match, m_indent = True, len(l) - len(l.lstrip())
            continue
        if in_match:
            if not l.strip():
                continue
            indent = len(l) - len(l.lstrip())
            m = re.match(r'^"([\w_]+)":', l.strip())
            if indent > m_indent and m:
                arms.append(m.group(1))
            elif indent <= m_indent:
                in_match = False
    r.append("  arms (%d): %s" % (len(arms), ", ".join(arms)))

    r.append("")
    r.append("== CLI knob census ==")
    for idx, l in enumerate(code):
        if "cmdline" in l or "_arg(" in l or "opt.get" in l:
            r.append("  line=%-4d %s" % (idx + 1, lines[idx].strip()[:140]))
    return "\n".join(r), arms


def harness_census(path: Path) -> tuple[str, dict, list[str]]:
    src = path.read_text()
    tree = ast.parse(src)
    out = [f"### harness: {path.name} (sha256 "
           f"{hashlib.sha256(path.read_bytes()).hexdigest()})"]
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": list(t[2]),
                               "expected_exit": t[3], "signature": t[4]}
    r95 = {k: v for k, v in cases.items()
           if k.startswith("dss_lattice_") or k.startswith("r95b_order_")}
    out.append("== CASES rows ==")
    out.append("  total rows: %d   r95 rows: %d (dss_lattice_ %d, r95b_order_ %d)"
               % (len(cases), len(r95),
                  sum(1 for k in r95 if k.startswith("dss_lattice_")),
                  sum(1 for k in r95 if k.startswith("r95b_order_"))))
    names = list(cases)
    idx = [i for i, n in enumerate(names) if n in r95]
    out.append("  r95 index range: %d..%d contiguous=%s"
               % (min(idx), max(idx), max(idx) - min(idx) + 1 == len(idx)))
    out.append("  predecessor: %s   successor: %s"
               % (names[min(idx) - 1], names[max(idx) + 1]))
    out.append("")
    out.append("== r95 rows ==")
    for k, v in r95.items():
        out.append("  %-34s script=%-18s flags=%-42s exit=%s sig_len=%d"
                   % (k, v["script"], v["flags"], v["expected_exit"], len(v["signature"])))

    exp_err, req_err = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            dict_keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
            is_req = "r92_tilemap_nullts_crash" in dict_keys
            for k, v in zip(node.keys, node.values):
                if not isinstance(k, ast.Constant):
                    continue
                key = str(k.value)
                if not (key.startswith("dss_lattice_") or key.startswith("r95b_order_")
                        or key in ("r95_expected_errors_all_matched",)):
                    continue
                if isinstance(v, (ast.Tuple, ast.List)):
                    (req_err if is_req else exp_err)[key] = ast.literal_eval(v)
    out.append("")
    out.append("== r95 expected_errors / required_stderr entries ==")
    out.append("  expected_errors rows=%d entries=%d"
               % (len(exp_err), sum(len(v) for v in exp_err.values())))
    for k, v in exp_err.items():
        for e in v:
            out.append("      %-34s %s" % (k, e))
    out.append("  required_stderr rows=%d entries=%d"
               % (len(req_err), sum(len(v) for v in req_err.values())))
    for k, v in req_err.items():
        for e in v:
            out.append("      %-34s %s" % (k, e))

    out.append("")
    out.append("== expected_errors floor gates ==")
    lines = src.splitlines()
    gates = []
    for i, l in enumerate(lines):
        if "expected_errors_all_matched" in l:
            m = re.search(r'startswith\(\(?([^)]*)\)?\)', "\n".join(lines[i:i + 9]))
            prefixes = re.findall(r'"([^"]+)"', m.group(1)) if m else []
            gates.append(prefixes)
            out.append("  line=%-5d %-54s prefixes=%s"
                       % (i + 1, l.strip().rstrip('":'), prefixes))
    out.append("")
    out.append("== gate-prefix non-redundancy (which gate can match an r95 case?) ==")
    hit = []
    for gi, prefixes in enumerate(gates):
        for p in prefixes:
            if "dss_lattice_".startswith(p) or "r95b_order_".startswith(p):
                hit.append((gi, p))
    out.append("  gates matching a dss_lattice_/r95b_order_ case: %s"
               % (", ".join("%s" % p for _, p in hit) or "NONE"))

    # signature redundancy within identical launches
    out.append("")
    out.append("== signature redundancy ==")
    by_sig = {}
    for k, v in cases.items():
        by_sig.setdefault(v["signature"], []).append(k)
    exact = {s: ks for s, ks in by_sig.items() if len(ks) > 1}
    out.append("  exact-duplicate signatures across all %d rows: %d"
               % (len(cases), len(exact)))
    for s, ks in exact.items():
        out.append("    %s <- %s" % (s[:70], ks))
    groups = {}
    for k, v in r95.items():
        groups.setdefault((v["script"], tuple(v["flags"])), []).append(k)
    sub, dup = [], []
    for g, ks in groups.items():
        for a in ks:
            for b in ks:
                if a == b:
                    continue
                sa, sb = r95[a]["signature"], r95[b]["signature"]
                if sa == sb:
                    dup.append((a, b))
                elif sb in sa:
                    sub.append((a, b, len(sa), len(sb)))
    out.append("  shared-launch groups: %d  (sizes %s)"
               % (len(groups), sorted(len(v) for v in groups.values())))
    out.append("  identical-launch exact dups: %d  substring subsumption pairs: %d"
               % (len(dup), len(sub)))
    for a, b in dup:
        out.append("    DUP %s == %s" % (a, b))
    for a, b, la, lb in sub:
        out.append("    %s (%d) subsumes %s (%d)" % (a, la, b, lb))
    cross = []
    for a, va in r95.items():
        for b, vb in cases.items():
            if b in r95 or not isinstance(vb["signature"], str):
                continue
            if vb["signature"] in va["signature"] and len(vb["signature"]) > 0:
                cross.append((a, b))
    out.append("  r95 signatures containing a foreign row's signature: %d" % len(cross))
    for a, b in cross[:20]:
        out.append("    %s contains %s" % (a, b))

    out.append("")
    out.append("== row<->arm bijection ==")
    per_script = {}
    for k, v in r95.items():
        arm = v["flags"][0].split("=", 1)[1] if v["flags"] and "=" in v["flags"][0] else "?"
        per_script.setdefault(v["script"], []).append((k, arm, v["flags"][1:] , v["expected_exit"]))
    for script, rows in per_script.items():
        arms = [a for _, a, _, _ in rows]
        dups = sorted({a for a in arms if arms.count(a) > 1})
        out.append("  %s: %d rows, exits=%s"
                   % (script, len(rows), sorted({e for _, _, _, e in rows})))
        out.append("    duplicate arms: %s" % (", ".join(dups) or "none"))
        for k, a, extra, e in rows:
            out.append("      %-34s arm=%-12s extra=%s exit=%s" % (k, a, extra, e))
    return "\n".join(out), r95, [p for ps in gates for p in ps]


if __name__ == "__main__":
    for name in ("dss_lattice.gd", "r95b_order.gd"):
        text, arms = fixture_census(CF / name)
        print(text)
        print()
    htext, r95, gate_prefixes = harness_census(CF / "run_battery.py")
    print(htext)
    print()
    print("== cross-check: fixture arms vs row-referenced arms ==")
    used = {}
    for k, v in r95.items():
        arm = v["flags"][0].split("=", 1)[1]
        used.setdefault(v["script"], set()).add(arm)
    for name in ("dss_lattice.gd", "r95b_order.gd"):
        _, arms = fixture_census(CF / name)
        s = set(arms)
        u = used.get(name, set())
        print("  %-18s fixture_arms=%d referenced=%d  no_row=%s  ghost_rows=%s"
              % (name, len(s), len(u),
                 ", ".join(sorted(s - u)) or "none",
                 ", ".join(sorted(u - s)) or "none"))
