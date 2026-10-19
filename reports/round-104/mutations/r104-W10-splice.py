#!/usr/bin/env python3
"""r104 W10 — mechanical combined-splice planner for `corpus/fixtures/run_battery.py`.

Answers, from HEAD bytes only (run_battery.py is NEVER executed):

  1. ANCHOR TABLE   — every r104 candidate hunk's anchor, its uniqueness count and
                      line offset in HEAD, and whether it is INSERT or REPLACE.
  2. OVERLAP MATRIX — for each ordered pair, does hunk A's edited byte-range
                      intersect hunk B's anchor line? (conflict / disjoint)
  3. COMMUTATIVITY  — apply every permutation of the hunk set to a scratch copy and
                      assert all permutations produce identical output bytes.
  4. DRIFT TABLE    — post-apply line offset of every anchor under the canonical
                      order, so a later `git apply` of a patch built against HEAD
                      can be checked for offset drift.
  5. COMPILE        — py_compile the spliced copy; sha256 + byte/line delta.

Hunk payloads are RECONSTRUCTED from the r104 sibling shards' published specs
(G1/r104-w5 for the tab-PASS census tightening, S0 for the in-battery replay
probe, W4 for the res_uid_* CASES rows). No hunk is applied to the lane repo.

Usage: python3 r104-W10-splice.py [--out DIR]
"""
import argparse
import hashlib
import itertools
import json
import py_compile
import re
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
HEAD = REPO / "corpus/fixtures/run_battery.py"
SCRATCH = Path("/var/tmp/r104-W10")

# ---------------------------------------------------------------------------
# Hunk table.  Each hunk is a (anchor_text, kind, payload) triple.
#   INSERT  : anchor is kept, payload is inserted AFTER the anchor line.
#   REPLACE : anchor line is replaced by payload (anchor must be unique).
#   BEFORE  : anchor is kept, payload is inserted BEFORE the anchor line.
# ---------------------------------------------------------------------------
PASS_RE_DECL = 'RECEIPT_PASS_RE = re.compile(r"^PASS(?=[\\s]|$)")\n'

HUNKS = [
    # ---- H1: C2(a) tab-PASS census tightening (G1, spec r104-G1.md:6,
    #      measured variant set r104-w5-blast-radius.py) -----------------------
    dict(id="H1a-decl",
         owner="G1 (C2a)",
         kind="INSERT",
         anchor='RECEIPT_ANSI_ONLY_RE = re.compile(r"^(?:\\x1b\\[[0-9;]*m)+$")\n',
         payload="\n" + PASS_RE_DECL,
         note="declares the PASS-prefix regex next to the other receipt REs"),
    dict(id="H1b-census",
         owner="G1 (C2a)",
         kind="REPLACE",
         anchor='    pass_lines = [line for line in output if line.startswith("PASS ")]\n',
         payload='    pass_lines = [line for line in output if RECEIPT_PASS_RE.match(line)]\n',
         note="the load-bearing census widening (space -> PASS-prefix)"),
    dict(id="H1c-seq-in",
         owner="G1 (C2a) / W5 V2_full",
         kind="REPLACE",
         anchor='                if not (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)):\n',
         payload='                if not (RECEIPT_PASS_RE.match(line) or RECEIPT_SEQ_RE.match(line)):\n',
         note="in-span accounting predicate"),
    dict(id="H1d-seq-post",
         owner="G1 (C2a) / W5 V2_full",
         kind="REPLACE",
         anchor='                if (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)\n',
         payload='                if (RECEIPT_PASS_RE.match(line) or RECEIPT_SEQ_RE.match(line)\n',
         note="post-span accounting predicate"),
    dict(id="H1e-diag",
         owner="G1 (C2a) / W5 V2_full",
         kind="REPLACE",
         anchor='            if (line.startswith("PASS ") or RECEIPT_BANNER_RE.match(line)\n',
         payload='            if (RECEIPT_PASS_RE.match(line) or RECEIPT_BANNER_RE.match(line)\n',
         note="DIAG-window accounting predicate"),
    # ---- H2: C3(a) in-battery gate-evasion replay probe (S0, spec r104-S0.md) -
    dict(id="H2a-probe",
         owner="S0 (C3a)",
         kind="BEFORE",
         anchor='    payload = {"godot": args.godot, "seed": str(HERE), "scratch": str(scratch),\n',
         payload=(
             "    # r104 S0 (C3a): stored in-battery gate-evasion replay probe.\n"
             "    # Replays the K>=8 stored synthetic shapes against the LIVE\n"
             "    # receipt_shape_flag predicate; green only if every shape flags.\n"
             "    evasion_flags = {name: [f.get(\"why\") for f in receipt_shape_flag(row)]\n"
             "                     for name, row in RECEIPT_EVASION_SHAPES}\n"
             "    evasion_missed = sorted(n for n, f in evasion_flags.items() if not f)\n"
             "    results.append({\"case\": \"probe_gate_evasion_replay\",\n"
             "                    \"verdict\": \"PASS\" if not evasion_missed else \"FAIL\",\n"
             "                    \"shapes\": len(evasion_flags),\n"
             "                    \"missed\": evasion_missed,\n"
             "                    \"flags\": evasion_flags,\n"
             "                    \"bounded_claim\": \"stored synthetic shapes only\"})\n"),
         note="call-site for the replay probe, immediately before the verdicts write"),
    dict(id="H2b-store",
         owner="S0 (C3a)",
         kind="BEFORE",
         anchor='def receipt_shape_audit(rows):\n',
         payload=(
             "# r104 S0 (C3a): the stored synthetic evasion catalogue.  Each entry is\n"
             "# a (name, row) pair whose `output` carries one evasion shape; the probe\n"
             "# in main() asserts every shape flags under the live predicate.\n"
             "RECEIPT_EVASION_SHAPES = []\n"
             "\n"
             "\n"),
         note="module-level store declaration, between flag() and audit()"),
    # ---- H3: res_uid_* CASES rows (W4 / E1-E4 registrations) ----------------
    dict(id="H3a-rows",
         owner="W4 (rows)",
         kind="BEFORE",
         anchor=']\n\n\n# r103 author (W10): receipt-shape META gate.',
         payload=(
             "    # r104 — C1: res_uid_* family (ResourceLoader / UID-cache lattice).\n"
             "    ('res_uid_s01_census', 'res_uid_s01.gd', ['--arm=census'], 0,\n"
             "     'PASS res_uid s01 census builtin_n=0 custom_n=0 roundtrip=0'),\n"
             "    ('res_uid_s02_cache_identity', 'res_uid_s02.gd', ['--arm=reuse'], 0,\n"
             "     'PASS res_uid s02 reuse same_object=true'),\n"
             "    ('res_uid_s03_remap', 'res_uid_s03.gd', ['--arm=remap'], 0,\n"
             "     'PASS res_uid s03 remap resolved=true'),\n"
             "    ('res_uid_s04_persist', 'res_uid_s04.gd', ['--arm=persist'], 0,\n"
             "     'PASS res_uid s04 persist cross_process=true'),\n"),
         note="CASES append; lands before the receipt-shape table block"),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def find_line(text, anchor):
    """Return (count, first 1-based line number)."""
    n = text.count(anchor)
    if n == 0:
        return 0, None
    return n, text[: text.index(anchor)].count("\n") + 1


def apply_hunks(text, hunks):
    """Apply an ordered sequence of hunks; each must match uniquely."""
    for h in hunks:
        cnt = text.count(h["anchor"])
        if cnt != 1:
            raise AssertionError(
                f"{h['id']}: anchor count {cnt} (need 1) for {h['anchor']!r}")
        if h["kind"] == "REPLACE":
            text = text.replace(h["anchor"], h["payload"])
        elif h["kind"] == "INSERT":
            text = text.replace(h["anchor"], h["anchor"] + h["payload"])
        elif h["kind"] == "BEFORE":
            text = text.replace(h["anchor"], h["payload"] + h["anchor"])
        else:
            raise AssertionError(h["kind"])
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(SCRATCH))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    head_bytes = HEAD.read_bytes()
    text = head_bytes.decode()
    report = {"head_sha256": sha(head_bytes),
              "head_lines": text.count("\n") + 1,
              "head_bytes": len(head_bytes)}

    # ---- 1. anchor table --------------------------------------------------
    anchors = []
    for h in HUNKS:
        cnt, ln = find_line(text, h["anchor"])
        anchors.append({"id": h["id"], "owner": h["owner"], "kind": h["kind"],
                        "anchor_count": cnt, "head_line": ln,
                        "anchor_bytes": len(h["anchor"]),
                        "payload_bytes": len(h["payload"]),
                        "payload_lines": h["payload"].count("\n"),
                        "note": h["note"]})
    report["anchors"] = anchors
    print("== ANCHOR TABLE (HEAD sha256 %s, %d lines) ==" % (
        report["head_sha256"][:16], report["head_lines"]))
    for a in anchors:
        print("  %-13s %-7s count=%d line=%-5s +%dB/+%dL  %s" % (
            a["id"], a["kind"], a["anchor_count"], a["head_line"],
            a["payload_bytes"], a["payload_lines"], a["note"]))
    uniq = all(a["anchor_count"] == 1 for a in anchors)
    print("  ALL ANCHORS UNIQUE: %s" % uniq)

    # ---- 2. overlap matrix -------------------------------------------------
    # Line-span of each hunk's edit in HEAD terms.  A REPLACE touches its anchor
    # line; an INSERT/BEFORE touches the boundary at its anchor line (a
    # zero-width insertion point).  Two edits CONFLICT iff a REPLACE line is
    # equal to another hunk's anchor line, or two REPLACEs share a line.
    repl_lines = {a["head_line"] for a in anchors if a["kind"] == "REPLACE"}
    matrix = []
    for a, b in itertools.permutations(anchors, 2):
        conflict = (a["kind"] == "REPLACE" and b["kind"] == "REPLACE"
                    and a["head_line"] == b["head_line"])
        matrix.append({"a": a["id"], "b": b["id"],
                       "conflict": conflict,
                       "same_line": a["head_line"] == b["head_line"]})
    conflicts = [m for m in matrix if m["conflict"]]
    report["conflicts"] = conflicts
    print("\n== OVERLAP MATRIX ==")
    print("  replace-lines: %s" % sorted(x for x in repl_lines if x))
    print("  REPLACE-vs-REPLACE same-line conflicts: %d" % len(conflicts))
    for c in conflicts:
        print("   CONFLICT %s <-> %s @ line %s" % (c["a"], c["b"], c["same_line"]))
    # An INSERT whose anchor line is also a REPLACE line IS order-dependent:
    # the replace rewrites the anchor bytes, so a later insert can no longer
    # match its anchor.  Report that class explicitly.
    boundary_clashes = []
    for a in anchors:
        for b in anchors:
            if a["id"] == b["id"]:
                continue
            if a["kind"] in ("INSERT", "BEFORE") and b["kind"] == "REPLACE" \
                    and a["head_line"] == b["head_line"]:
                boundary_clashes.append((a["id"], b["id"], a["head_line"]))
    report["boundary_clashes"] = boundary_clashes
    print("  INSERT/BEFORE-anchor-on-REPLACE-line clashes: %d %s" % (
        len(boundary_clashes), boundary_clashes))

    # ---- 3a. complete pairwise-independence proof (rigorous, cheap) -------
    # Each hunk is a single unique-anchor substitution.  Substitutions over
    # disjoint byte regions compose order-independently; the ONLY way order can
    # matter is if applying hunk A changes the match count of hunk B's anchor.
    # So the complete criterion is: for every ordered pair (A,B), applying A
    # alone still leaves count(B.anchor) == 1.  That is 8*7 = 56 checks and is
    # exhaustive over the order relation, not a sample.
    pair_fail = []
    for a in HUNKS:
        after_a = apply_hunks(text, [a])
        for b in HUNKS:
            if a["id"] == b["id"]:
                continue
            cnt = after_a.count(b["anchor"])
            if cnt != 1:
                pair_fail.append({"after": a["id"], "anchor_of": b["id"], "count": cnt})
    # Second overlap class: an anchor nested inside another hunk's payload
    # (would create a duplicate occurrence and break uniqueness).
    nested = []
    for a in HUNKS:
        for b in HUNKS:
            if a["id"] != b["id"] and b["anchor"] in a["payload"]:
                nested.append((a["id"], b["id"]))
    report["pairwise_independence"] = {"checks": len(HUNKS) * (len(HUNKS) - 1),
                                       "failures": pair_fail,
                                       "nested_anchor_in_payload": nested,
                                       "holds": not pair_fail and not nested}
    print("\n== PAIRWISE INDEPENDENCE (complete, %d ordered pairs) ==" % (
        len(HUNKS) * (len(HUNKS) - 1)))
    print("  count-preservation failures : %d %s" % (len(pair_fail), pair_fail))
    print("  anchor nested in a payload  : %d %s" % (len(nested), nested))
    print("  INDEPENDENT (=> all orders commute): %s" % report["pairwise_independence"]["holds"])

    # ---- 3b. full factorial confirmation (8! = 40320) ----------------------
    outputs = {}
    perms = list(itertools.permutations(HUNKS))
    capped = False
    for perm in perms:
        order = "+".join(h["id"] for h in perm)
        try:
            outputs[order] = sha(apply_hunks(text, list(perm)).encode())
        except AssertionError as exc:
            outputs[order] = "FAIL:%s" % exc
    distinct = sorted(set(outputs.values()))
    report["permutations_tested"] = len(perms)
    report["permutations_capped"] = capped
    report["distinct_outputs"] = len(distinct)
    report["distinct_sha256"] = distinct
    print("\n== COMMUTATIVITY (full factorial) ==")
    print("  permutations tested: %d%s" % (len(perms), " (CAPPED)" if capped else ""))
    print("  distinct outputs   : %d" % len(distinct))
    for s in distinct:
        print("    %s" % (s if len(s) < 100 else s[:100]))
    commutes = len(distinct) == 1 and not distinct[0].startswith("FAIL")
    report["order_free_empirical"] = commutes
    print("  ORDER-FREE (all %d permutations byte-identical): %s" % (len(perms), commutes))
    if not commutes:
        bad = [(o, s) for o, s in outputs.items() if s != distinct[0]][:8]
        print("  first divergent orders:")
        for o, s in bad:
            print("    %-70s %s" % (o, s))

    # ---- 4. canonical order + drift ---------------------------------------
    canonical = sorted(HUNKS, key=lambda h: (find_line(text, h["anchor"])[1], h["id"]))
    order = [h["id"] for h in canonical]
    spliced = apply_hunks(text, canonical)
    spliced_bytes = spliced.encode()
    drift = []
    for h in canonical:
        cnt, ln = find_line(spliced, h["anchor"])
        _, head_ln = find_line(text, h["anchor"])
        if h["kind"] == "REPLACE":
            # The anchor text is consumed by the substitution, so a post-apply
            # search for it is empty BY DESIGN; report the payload's own line.
            post_cnt, post_ln = find_line(spliced, h["payload"])
            drift.append({"id": h["id"], "kind": h["kind"], "head_line": head_ln,
                          "post_line": post_ln, "post_count": post_cnt,
                          "anchor_consumed": True,
                          "delta": (post_ln - head_ln) if (post_ln and head_ln) else None})
        else:
            drift.append({"id": h["id"], "kind": h["kind"], "head_line": head_ln,
                          "post_line": ln, "post_count": cnt,
                          "anchor_consumed": False,
                          "delta": (ln - head_ln) if (ln and head_ln) else None})
    report["canonical_order"] = order
    report["drift"] = drift
    print("\n== CANONICAL ORDER (ascending anchor line) ==")
    print("  " + " -> ".join(order))
    for d in drift:
        tag = " (anchor consumed; payload line)" if d["anchor_consumed"] else ""
        print("  %-13s %-7s HEAD:%-5s post:%-5s drift=%+d%s" % (
            d["id"], d["kind"], d["head_line"], d["post_line"], d["delta"] or 0, tag))

    # ---- 5. compile + emit -------------------------------------------------
    dst = out / "run_battery_spliced.py"
    dst.write_bytes(spliced_bytes)
    try:
        py_compile.compile(str(dst), cfile=str(out / "run_battery_spliced.pyc"),
                           doraise=True)
        compile_ok, compile_err = True, None
    except py_compile.PyCompileError as exc:
        compile_ok, compile_err = False, str(exc)
    report["spliced"] = {"path": str(dst), "sha256": sha(spliced_bytes),
                         "bytes": len(spliced_bytes), "lines": spliced.count("\n") + 1,
                         "byte_delta": len(spliced_bytes) - len(head_bytes),
                         "line_delta": (spliced.count("\n") + 1) - (text.count("\n") + 1),
                         "py_compile": compile_ok, "py_compile_error": compile_err}
    print("\n== SPLICED COPY ==")
    print("  %s" % dst)
    print("  sha256=%s  bytes=%d (%+d)  lines=%d (%+d)  py_compile=%s" % (
        report["spliced"]["sha256"], len(spliced_bytes),
        report["spliced"]["byte_delta"], spliced.count("\n") + 1,
        report["spliced"]["line_delta"], compile_ok))

    # ---- 6. negative control: the permutation test must have teeth --------
    # Construct a deliberately order-dependent pair whose anchor IS a REPLACE
    # line: applying the REPLACE first destroys the INSERT's anchor, so the
    # second application must raise.  If this control did NOT fail, the
    # commutativity result above would be vacuous (an apply that silently
    # no-ops).  Control hunks live only in this report, never in HUNKS.
    ctl_replace = dict(id="CTL-replace", kind="REPLACE",
                       anchor='    pass_lines = [line for line in output if line.startswith("PASS ")]\n',
                       payload='    pass_lines = [line for line in output if RECEIPT_PASS_RE.match(line)]\n')
    ctl_insert = dict(id="CTL-insert", kind="INSERT",
                      anchor='    pass_lines = [line for line in output if line.startswith("PASS ")]\n',
                      payload="    # control insertion on the same line\n")
    control = {}
    for label, seq in (("insert_then_replace", [ctl_insert, ctl_replace]),
                       ("replace_then_insert", [ctl_replace, ctl_insert])):
        try:
            res = apply_hunks(text, seq)
            control[label] = {"applied": True, "sha256": sha(res.encode())}
        except AssertionError as exc:
            control[label] = {"applied": False, "error": str(exc)}
    report["negative_control"] = control
    print("\n== NEGATIVE CONTROL (same-line INSERT vs REPLACE) ==")
    for label, r in control.items():
        print("  %-20s applied=%s %s" % (
            label, r["applied"], r.get("error", r.get("sha256", ""))[:90]))
    teeth = (control["insert_then_replace"]["applied"] is True
             and control["replace_then_insert"]["applied"] is False)
    report["negative_control_has_teeth"] = teeth
    print("  order-dependent pair correctly detected: %s" % teeth)

    # ---- 7. semantic effect of the spliced copy ---------------------------
    # Import the spliced module and drive the TIGHTENED predicate with the two
    # byte-shapes the tightening is about, plus a control on a real stored
    # receipt.  Proves the splice produced working code, not just valid syntax.
    import importlib.util
    spec = importlib.util.spec_from_file_location("w10_spliced", dst)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    semantic = {"import_ok": True,
                "has_RECEIPT_PASS_RE": hasattr(mod, "RECEIPT_PASS_RE"),
                "has_evasion_store": hasattr(mod, "RECEIPT_EVASION_SHAPES"),
                "cases_rows": len(mod.CASES),
                "res_uid_rows": [c[0] for c in mod.CASES if c[0].startswith("res_uid_")],
                "grammar_rows": len(mod.RECEIPT_MULTI_PASS_GRAMMAR)}
    # A tab-separated PASS line is grammar-invisible to the OLD census but must
    # be seen by the tightened one.
    base_case = next(c for c in mod.CASES if c[0] == "input_route")[0]
    base_sig = mod.CASES_SIG_BY_CASE[base_case]
    tab_row = {"case": base_case, "verdict": "PASS",
               "output": [base_sig, "PASS\t" + base_sig]}
    space_row = {"case": base_case, "verdict": "PASS", "output": [base_sig]}
    semantic["tab_shape_flags"] = [f.get("why") for f in mod.receipt_shape_flag(tab_row)]
    semantic["clean_shape_flags"] = [f.get("why") for f in mod.receipt_shape_flag(space_row)]
    report["semantic"] = semantic
    print("\n== SEMANTIC EFFECT OF SPLICED COPY ==")
    print("  import_ok=%s RECEIPT_PASS_RE=%s evasion_store=%s CASES=%d res_uid_rows=%d" % (
        semantic["import_ok"], semantic["has_RECEIPT_PASS_RE"],
        semantic["has_evasion_store"], semantic["cases_rows"],
        len(semantic["res_uid_rows"])))
    print("  tab-PASS shape flags : %s" % (semantic["tab_shape_flags"] or "[] (UNFLAGGED)"))
    print("  clean shape flags    : %s" % (semantic["clean_shape_flags"] or "[] (clean)"))

    (out / "splice_report.json").write_text(json.dumps(report, indent=1) + "\n")
    print("  report -> %s" % (out / "splice_report.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
