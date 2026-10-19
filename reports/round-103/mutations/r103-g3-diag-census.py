#!/usr/bin/env python3
"""r103 G3 — diagnostics-prefix family census + diag-account coverage proof.

Deliverable for seat G3-REGRESSION (C2): enumerate every diagnostics-prefix
family emitted by corpus fixtures that the receipt-shape META gate's diag
account (regex set) must accept, prove coverage over ALL stored per-row
stdout records (corpus/live/runs/*/verdicts.json), and list false-flag risks.

Never runs run_battery.py; read-only over the repo. All writes go to
/var/tmp/r103c-G3/ plus stdout.

Modes (default = all):
  A  static census: extract print-family call literals from every fixture .gd
     (incl. subdirs), resolve bare-identifier args via per-file const map,
     histogram first tokens -> designed-verb families.
  B  empirical census: every line of every stored verdict record across all
     run dirs; classify by envelope ladder; histogram first tokens; list the
     designed-verb lines actually observed per row.
  C  coverage proof: define the diag account predicate (envelope regexes +
     PASS grammar + per-row observed-family account) and assert 100% coverage
     of every stored line; print any uncovered line verbatim (must be none).
  D  false-flag risk probes: craft real-evidence lines (banner variants,
     backtraces, whitespace evasions from mut05, prefix-collision tokens) and
     report account accept/reject + which naive variants would mis-handle.
"""
import collections
import glob
import hashlib
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
FIX = REPO / "corpus/fixtures"
RUNS = REPO / "corpus/live/runs"
SCRATCH = pathlib.Path("/var/tmp/r103c-G3")

PRINT_RE = re.compile(
    r'\b(print|print_rich|printraw|prints|printerr|push_error|push_warning)\s*\(')
CONST_RE = re.compile(
    r'^\s*const\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*[A-Za-z_][\w\[\]]*\s*)?(?:=|:=)\s*"((?:[^"\\]|\\.)*)"',
    re.M)
IDENT_RE = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*$')


def read(p):
    return p.read_text(encoding="utf-8", errors="replace")


def call_args(src, open_paren):
    """Return the text of the call argument list starting after '(' at open_paren."""
    depth = 1
    i = open_paren
    in_str = False
    esc = False
    while i < len(src):
        c = src[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return src[open_paren:i]
        i += 1
    return src[open_paren:]


def first_literal(arg):
    """First double-quoted literal in arg text, unescaped (approx)."""
    m = re.search(r'"((?:[^"\\]|\\.)*)"', arg)
    if not m:
        return None
    return m.group(1).encode().decode("unicode_escape")


def first_token_of_literal(lit):
    """Design: the verb token a receipt line starts with."""
    tok = lit.split(" ", 1)[0]
    tok = tok.split("%", 1)[0]
    return tok


def static_census():
    files = sorted(glob.glob(str(FIX / "**" / "*.gd"), recursive=True))
    fam = collections.defaultdict(list)
    n_calls = 0
    per_file = {}
    for path in files:
        src = read(pathlib.Path(path))
        consts = {m.group(1): m.group(2).encode().decode("unicode_escape")
                  for m in CONST_RE.finditer(src)}
        rel = str(pathlib.Path(path).relative_to(FIX))
        toks = []
        for m in PRINT_RE.finditer(src):
            n_calls += 1
            arg = call_args(src, m.end())
            first = re.split(r"\s*,\s*", arg, 1)[0]  # first argument only
            lit = None
            im = IDENT_RE.match(first)
            if im and im.group(1) in consts:
                lit = consts[im.group(1)]
            else:
                lit = first_literal(first)
                if lit is None:
                    # concat / format where literal is not leading; search all args
                    lit = first_literal(arg)
            if lit is None:
                toks.append(("<no-literal>", rel))
                continue
            tok = first_token_of_literal(lit)
            toks.append((tok, rel))
            fam[tok].append((rel, lit))
        per_file[rel] = toks
    return files, n_calls, fam, per_file


# ---------------------------------------------------------------- envelope
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
BANNER_RE = re.compile(r'^Godot Engine v\d+\.\d+')
ENGINE_HDR_RE = re.compile(
    r'^(ERROR|WARNING|SCRIPT ERROR|USER ERROR|USER WARNING|SCRIPT ERROR IN)')
AT_RE = re.compile(r'^   at: ')
BT_RE = re.compile(r'^   GDScript backtrace \(most recent call first\):')
FRAME_RE = re.compile(r'^       \[\d+\] ')
LEAK_RE = re.compile(r'^(ObjectDB|Object::|Leaked instance|Orphan StringName)')
# export CLI progress/noise (measured: export_readiness, export_preset_missing,
# r88/r92 crash rows carrying `=====` dumps + gdb-style frames)
CLI_PROGRESS_RE = re.compile(r'^\[ *\d+% \] ')
CLI_DONE_RE = re.compile(r'^\x1b\[92m\[ DONE \]\x1b\[39m')
ANSI_ONLY_RE = re.compile(r'^\x1b\[0m$')
CRASH_RULE_RE = re.compile(r'^={16,}$')
CRASH_HDR_RE = re.compile(
    r'^(handle_crash:|Engine version:|Command line:|Load address:|Dumping the backtrace|'
    r'ERROR: Program crashed|Program crashed)')
GDB_FRAME_RE = re.compile(r'^\[\d+\] [0-9a-f]{6,} ')
END_BT_RE = re.compile(r'^-- END OF (C\+\+ |GDSCRIPT )?BACKTRACE --$')
GLIBC_ABORT_RE = re.compile(
    r'^(double free or corruption|free\(\): |malloc\(\): |munmap_chunk\(\): |corrupted size vs)')
CPP_ASSERT_RE = re.compile(r'^(/|\.\./)[^\s]*:\d+: .*(Assertion|assertion|failed\.)')
# variable-indent runtime continuations (measured: 3-space error form and
# 5-space deprecated-warning form in nav_lattice_bake / r92_tilemap_nav)
RUNTIME_AT_RE = re.compile(r'^ *at: ')
RUNTIME_BT_RE = re.compile(r'^ *GDScript backtrace \(most recent call first\):')
RUNTIME_FRAME_RE = re.compile(r'^ *\[\d+\] ')
WARN_SOLUTION_RE = re.compile(
    r'^Use (NavigationServer2D|NavigationServer3D|ResourceLoader|Godot)[^\n]* instead\.$')
ENGINE_ADVICE_RE = re.compile(
    r'^\t(NavigationServer|PhysicsServer|RenderingServer|DisplayServer|AudioServer) ')
EXPORT_CLI_PROSE_RE = re.compile(
    r"^The following presets were detected in this project's `export_presets\.cfg`:")


def envelope(line):
    """Globally-ignorable engine envelope lines (stream-level, row-independent)."""
    if line == "":
        return "blank"
    if BANNER_RE.match(line):
        return "banner"
    if ENGINE_HDR_RE.match(line):
        return "engine-diag"
    if RUNTIME_AT_RE.match(line):
        return "engine-at"
    if RUNTIME_BT_RE.match(line):
        return "engine-backtrace-hdr"
    if RUNTIME_FRAME_RE.match(line):
        return "engine-frame"
    if LEAK_RE.match(line):
        return "engine-leak"
    if WARN_SOLUTION_RE.match(line):
        return "engine-warn-solution"
    if ENGINE_ADVICE_RE.match(line):
        return "engine-advice"
    if EXPORT_CLI_PROSE_RE.match(line):
        return "export-cli-prose"
    if CLI_PROGRESS_RE.match(line) or CLI_DONE_RE.match(line) or ANSI_ONLY_RE.match(line):
        return "cli-progress"
    if CRASH_RULE_RE.match(line):
        return "crash-rule"
    if CRASH_HDR_RE.match(line):
        return "crash-hdr"
    if GDB_FRAME_RE.match(line):
        return "crash-frame"
    if END_BT_RE.match(line):
        return "crash-end"
    if GLIBC_ABORT_RE.match(line):
        return "glibc-abort"
    if CPP_ASSERT_RE.match(line):
        return "cpp-assert"
    return None


def shape(ln):
    s = ANSI_RE.sub("<A>", ln)
    s = re.sub(r'\b[0-9a-f]{8,}\b', "<HEX>", s)
    s = re.sub(r'\d+', "#", s)
    return s[:150]


def pass_line(line):
    return line.startswith("PASS ") or line == "PASS"


def run_records():
    recs = []
    for vp in sorted(glob.glob(str(RUNS / "*" / "verdicts.json"))):
        raw = pathlib.Path(vp).read_bytes()
        d = json.loads(raw)
        recs.append({
            "path": vp,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "verdict": d.get("verdict"),
            "rows": d["results"],
        })
    return recs


def empirical(runs):
    total_lines = 0
    token_hist = collections.Counter()
    envelope_hist = collections.Counter()
    designed_rows = {}   # case -> {family:count}
    first_tokens = collections.Counter()
    for run in runs:
        for r in run["rows"]:
            out = r.get("output") or []
            for ln in out:
                total_lines += 1
                env = envelope(ln)
                if env:
                    envelope_hist[env] += 1
                    continue
                if pass_line(ln):
                    envelope_hist["PASS"] += 1
                    continue
                tok = ln.split(" ", 1)[0]
                first_tokens[tok] += 1
                if re.match(r'^(FAIL|FAILED)\b', ln):
                    envelope_hist["FAIL"] += 1
                    continue
                env = "designed-verb"
                envelope_hist[env] += 1
                fam = re.match(r'^([A-Z][A-Z0-9_]*)', ln)
                fam = fam.group(1) if fam else tok
                designed_rows.setdefault(r["case"], collections.Counter())[fam] += 1
    return total_lines, envelope_hist, first_tokens, designed_rows


def emit_report(static_infos, runs, emp):
    files, n_calls, fam, per_file = static_infos
    total_lines, envelope_hist, first_tokens, designed_rows = emp
    SCRATCH.mkdir(parents=True, exist_ok=True)
    print("=" * 72)
    print("A. STATIC CENSUS — fixture print-family call sites")
    print(f"   files={len(files)} calls={n_calls} distinct-first-tokens={len(fam)}")
    tok_rows = sorted(fam.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    for tok, occ in tok_rows:
        nfiles = len({rel for rel, _ in occ})
        sample = occ[0][1][:70]
        print(f"   {len(occ):4d} call(s) in {nfiles:2d} file(s)  TOKEN={tok!r:32s} e.g. {sample!r}")
    print("=" * 72)
    print("B. EMPIRICAL CENSUS — stored stdout lines across runs")
    for run in runs:
        print(f"   run {pathlib.Path(run['path']).parent.name} sha256={run['sha256'][:16]} "
              f"rows={len(run['rows'])} verdict={run['verdict']}")
    print(f"   total stored lines={total_lines}")
    for k, v in envelope_hist.most_common():
        print(f"   class {k:24s} {v}")
    print("   non-envelope first tokens (top 40):")
    for tok, n in first_tokens.most_common(40):
        print(f"     {n:5d}  {tok!r}")
    print("   rows with designed-verb non-PASS lines: %d" % len(designed_rows))
    for case, fams in sorted(designed_rows.items()):
        print(f"     {case:36s} {dict(fams)}")
    return tok_rows


def designed_match(ln, tokens):
    """Fixture-token membership: exact first token, or prefix for tokens that
    end in '=' / ':' (measured 'arm=', 'ei=', 'SPONTANEOUS_CRASH_PROBE:')."""
    tok = ln.split(" ", 1)[0]
    if tok in tokens:
        return True
    return any(t.endswith(("=", ":")) and ln.startswith(t) for t in tokens)


def coverage(runs, designed_tokens):
    """C: account = envelope ∪ PASS ∪ FAIL ∪ static-fixture first-token set
    (row-level exact account required for designed lines). Report any line
    outside that closure (must be none) grouped by normalized shape."""
    bad = []
    n_lines = 0
    n_banner_pos0 = 0
    banner_counts = collections.Counter()
    n_rows = 0
    for run in runs:
        for r in run["rows"]:
            out = r.get("output") or []
            n_rows += 1
            bc = sum(1 for ln in out if envelope(ln) == "banner")
            banner_counts[bc] += 1
            if out and envelope(out[0]) == "banner":
                n_banner_pos0 += 1
            for i, ln in enumerate(out):
                n_lines += 1
                if envelope(ln) or pass_line(ln) or re.match(r'^(FAIL|FAILED)\b', ln):
                    continue
                if designed_match(ln, designed_tokens):
                    continue  # designed-verb family line (row-level account)
                bad.append((run["path"], r["case"], i, ln))
    print("=" * 72)
    print("C. COVERAGE — lines outside envelope ∪ PASS ∪ FAIL ∪ fixture-token set")
    print(f"   lines scanned={n_lines} rows={n_rows} uncovered={len(bad)}")
    print(f"   rows with banner at index 0: {n_banner_pos0}; banner-count "
          f"histogram {dict(sorted(banner_counts.items()))}")
    groups = collections.defaultdict(list)
    for p, c, i, ln in bad:
        groups[shape(ln)].append((p, c, i, ln))
    for sh, items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        p, c, i, ln = items[0]
        print(f"   UNCOVERED x{len(items):4d} {pathlib.Path(p).parent.name} {c}[{i}] {ln!r}")
        print(f"                    shape={sh!r}")
    return n_lines, bad


# ---------------------------------------------------------------- risks
BANNER_ARCH = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
               "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
BANNER_OFFICIAL = ("Godot Engine v4.7.2.stable.official.ed1daf0bf - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe - https://godotengine.org")
S2A = "EXPORT_LAUNCH_DIAG embed forged=true"
S2B = "EXPORT_LAUNCH_DIAG embed forged=1"
S4A = "\tPASS forged=true"
S4B_TRAIL = "PASS forged=true\u00a0"
BACKTRACE = ["ERROR: negative control: expected collected signal was absent with disabled mask",
             "   at: push_error (core/variant/variant_utility.cpp:1023)",
             "   GDScript backtrace (most recent call first):",
             "       [0] _run (res://controls/overlap_negative.gd:28)"]
MARKERS = ["LAUNCH_S02_MARKER boot=true", "LAUNCH_S02_FRAME 2",
           "EXPORT_DIV_DIAG s01 key=value", "FOREIGN_EXTRA injected=into_span"]


def sensitivity(runs):
    """D2: counterfactual per family — lines the general family matches that a
    naive narrower variant misses (each miss = one false flag)."""
    strict_at = re.compile(r'^   at: ')
    strict_bt = re.compile(r'^   GDScript backtrace')
    strict_frame = re.compile(r'^       \[\d+\] ')
    strict_banner = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
                     "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
    c = collections.Counter()
    for run in runs:
        for r in run["rows"]:
            for ln in r.get("output") or []:
                if RUNTIME_AT_RE.match(ln) and not strict_at.match(ln):
                    c["at_indent_missed"] += 1
                if RUNTIME_BT_RE.match(ln) and not strict_bt.match(ln):
                    c["bt_indent_missed"] += 1
                if RUNTIME_FRAME_RE.match(ln) and not strict_frame.match(ln):
                    c["frame_indent_missed"] += 1
                if BANNER_RE.match(ln) and ln != strict_banner:
                    c["banner_exact_missed"] += 1
                if CLI_PROGRESS_RE.match(ln):
                    c["cli_progress"] += 1
                if CPP_ASSERT_RE.match(ln):
                    c["cpp_assert"] += 1
                if GLIBC_ABORT_RE.match(ln):
                    c["glibc_abort"] += 1
    print("=" * 72)
    print("D2. SENSITIVITY — false flags if a family regex is narrowed")
    for k, v in sorted(c.items()):
        print(f"   {k:24s} {v}")
    return c


def risk_probes(designed_tokens=None):
    print("=" * 72)
    print("D. FALSE-FLAG / FALSE-ACCEPT RISK PROBES (account semantics)")
    if designed_tokens:
        print("   global-token-set probes (why a global account is not enough):")
        for name, ln in [("s2a forge on no-DIAG row", S2A), ("s2b forge on DIAG row", S2B),
                         ("foreign FOREIGN_EXTRA line", MARKERS[3]),
                         ("legit same-row DIAG line", MARKERS[2])]:
            g = designed_match(ln, designed_tokens) if designed_tokens else None
            print(f"     {name:28s} global_token_account={g} -> "
                  f"{'ACCEPTS (insufficient alone)' if g else 'rejects'}")
    rows = [
        ("envelope banner (arch build, stored)", BANNER_ARCH, "accept"),
        ("envelope banner (official build, r102-mut9 measured)", BANNER_OFFICIAL, "accept"),
        ("forged banner v9.9.9", FORGED_BANNER, "flag"),
        ("backtrace ERROR line", BACKTRACE[0], "accept-or-row-account"),
        ("backtrace at: line", BACKTRACE[1], "accept"),
        ("backtrace header", BACKTRACE[2], "accept"),
        ("backtrace frame", BACKTRACE[3], "accept"),
        ("designed verb same-row (marker)", MARKERS[0], "accept-via-row-account"),
        ("designed verb same-row (frame)", MARKERS[1], "accept-via-row-account"),
        ("designed verb export_div diag", MARKERS[2], "accept-via-row-account"),
        ("foreign token", MARKERS[3], "flag"),
        ("s2a diag-prefixed forge on no-DIAG row", S2A, "flag"),
        ("s2b diag-prefixed forge on DIAG row", S2B, "flag-via-exact-account"),
        ("s4a leading tab PASS", S4A, "flag"),
        ("s4b trailing NBSP PASS", S4B_TRAIL, "flag"),
    ]
    for name, ln, expect in rows:
        env = envelope(ln)
        p = pass_line(ln)
        strip_p = pass_line(ln.strip()) if ln != ln.strip() else p
        print(f"   {name:48s} env={env!s:10s} pass={p} pass_stripped={strip_p} expect={expect}")
    print()
    print("   whitespace semantics: '\\u00a0'.isspace()=%s  '\\tPASS forged'.strip()=%r"
          % ("\u00a0".isspace(), "\tPASS forged=true".strip()))
    print("   NBSP-stripped PASS line is indistinguishable under a .strip() scan ->")
    print("   gate must compare exact bytes for the accounted PASS set, not stripped forms.")
    return rows


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    static_infos = static_census()
    runs = run_records()
    emp = empirical(runs)
    tok_rows = emit_report(static_infos, runs, emp)
    designed_tokens = set(static_infos[2]) | {"PASS", "FAIL"}
    n_lines, bad = coverage(runs, designed_tokens)
    sens = sensitivity(runs)
    risk_probes(designed_tokens)
    # machine artifact
    art = {
        "static": {"files": len(static_infos[0]), "calls": static_infos[1],
                   "tokens": {t: len(o) for t, o in tok_rows}},
        "runs": [{"path": r["path"], "sha256": r["sha256"], "rows": len(r["rows"]),
                  "verdict": r["verdict"]} for r in runs],
        "lines_scanned": n_lines, "uncovered": len(bad),
        "sensitivity": dict(sens),
        "designed_rows": {c: dict(f) for c, f in emp[3].items()},
    }
    dest = SCRATCH / "diag-census.json"
    dest.write_text(json.dumps(art, indent=1) + "\n")
    print("=" * 72)
    print(f"artifact: {dest} ({dest.stat().st_size} bytes)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
