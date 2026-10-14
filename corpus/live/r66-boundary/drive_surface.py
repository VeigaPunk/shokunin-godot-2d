#!/usr/bin/env python3
"""r66 boundary edge driver: rejection-clause SURFACE map.

Verdict-path evidence comes from functions VERBATIM-EXTRACTED from the
working-tree runner (ast.get_source_segment -> exec): run_process,
classify_process, classify_streams, pid_alive, kernel_ppid, and the landed
r64 gated_signature_run. Rows tagged vg_*/comm_*/st_* run production code.

Instrumented replicas (eval_with_trace clause-order probe, per-clause truth
tables, the allowed_error replica) are corroborating evidence; differences
are disclosed in-record. The census replays the r65-author battery receipt
through the verbatim classifier to anchor extraction fidelity.

Writes only under corpus/live/r66-boundary/. Never touches tracked files.

Reaper safety: SIGKILLs only pids this driver's own run printed AND only
when /proc/<pid>/cmdline carries this fixture's unique tokens
(FORGED_DESCENDANT_ERROR / DESCENDANT_PIPE_ERRFORGE / DESCENDANT_PIPE_FORGE /
PHANTOM_ / DESCENDANT_PIPE_SPLICE / DESCENDANT_PIPE_NEGROW / FORGE_MARKER).
Sibling seats' stock descendants carry the same DESCENDANT_PIPE_ERRFORGE
token — but a different pid; the pid gate makes the match unique.
"""
import ast
import fcntl
import hashlib
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

EDGE = Path(__file__).resolve().parent
REPO = EDGE.parents[1]
RUNNER = REPO / "fixtures" / "run_battery.py"
PROJ = EDGE / "proj_r66"
RAW = EDGE / "raw"
RAW.mkdir(exist_ok=True)
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
ERR_LINE = "ERROR: FORGED_DESCENDANT_ERROR injected diagnostic"
SAVE_SIG = ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected "
            "signature=JSON_PARSE_ERROR")
SCRIPT_LINE = "SCRIPT ERROR: FORGED_DESCENDANT_ERROR injected script diagnostic"
PARSE_LINE = "Parse Error: FORGED_DESCENDANT_ERROR injected parse diagnostic"
COMMA_ENTRY = ("ERROR: ANIMATION ASSERTION FAILED: expected animated "
               "property x=60 after bounded advance,")
COMMA_LINE = COMMA_ENTRY + " got 999.0"
CHAIN_ENTRY = "ERROR: chain incomplete"
CHAIN_LINE = ("ERROR: chain incomplete collections=7 scene=SceneB:<Node#4242> "
              "old_alive=false forged=1")
CHAIN_ESC = ("ERROR: chain incomplete collections=7 scene=SceneC:<Node#4242> "
             "old_alive=false forged=1")
NOISE_LINE = "INNOCENT_DESCENDANT_CHATTER not an error token"
GODOT = "godot"
# Unique tokens only this fixture's descendants can carry in cmdline.
REAP_TOKENS = (b"FORGED_DESCENDANT_ERROR", b"DESCENDANT_PIPE_ERRFORGE",
               b"DESCENDANT_PIPE_FORGE", b"PHANTOM_", b"INNOCENT_DESCENDANT",
               b"chain incomplete", b"ANIMATION ASSERTION",
               b"SAVE EXPECTED NEGATIVE")

# ---------------------------------------------------------------- verbatim
src = RUNNER.read_text()
tree = ast.parse(src)
runner_sha = hashlib.sha256(src.encode()).hexdigest()

ns = {
    "subprocess": subprocess, "selectors": selectors, "os": os, "re": re,
    "time": time, "signal": signal, "datetime": datetime,
    "args": SimpleNamespace(godot=GODOT),
    "scratch": PROJ, "gate_marker": MARKER, "gate_bound": 3.0,
    "gate_poll_tick": 0.005,
}
wanted = {"run_process", "classify_process", "classify_streams",
          "classify_audio_process", "pid_alive", "kernel_ppid",
          "gated_signature_run"}
found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        exec(ast.get_source_segment(src, node), ns)
        found.add(node.name)
missing = wanted - found
assert not missing, f"extraction failed: {missing}"

run_process = ns["run_process"]
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]
classify_audio_process = ns["classify_audio_process"]
pid_alive = ns["pid_alive"]
kernel_ppid = ns["kernel_ppid"]
gated_signature_run = ns["gated_signature_run"]

# --- extract the expected_errors dict literal verbatim from the runner AST
expected_errors_dict = None
cases_table = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "expected_errors":
                call = node.value
                if (isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Attribute)
                        and call.func.attr == "get"
                        and isinstance(call.func.value, ast.Dict)):
                    expected_errors_dict = ast.literal_eval(call.func.value)
            if isinstance(t, ast.Name) and t.id == "CASES":
                cases_table = ast.literal_eval(node.value)
assert expected_errors_dict and cases_table, "AST extraction of tables failed"


def allowed_error(line, allowed):
    """Byte-faithful replica of classify_process's nested allowed_error —
    used only for per-entry census labelling; verdicts always come from the
    verbatim classify_process."""
    stripped = line.strip()
    if stripped == allowed:
        return True
    if allowed.endswith(","):
        return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
    if allowed == "ERROR: chain incomplete":
        return (stripped.startswith("ERROR: chain incomplete collections=")
                and "scene=SceneB:<Node#" in stripped
                and "old_alive=false" in stripped
                and stripped.count("ERROR:") == 1)
    return False


def clauses(code, error, output, expected_exit=0, signature=MARKER,
            allowed_errors=()):
    """Per-conjunct truth table of the landed classify_process expression."""
    lines = output.splitlines()
    unrelated = [l for l in lines if "ERROR:" in l
                 and not any(allowed_error(l, a) for a in allowed_errors)]
    table = {
        "code_eq_expected": code == expected_exit,
        "error_is_none": error is None,
        "signature_present": signature in output,
        "no_unrelated_errors": not unrelated,
        "no_script_error": "SCRIPT ERROR:" not in output,
        "no_parse_error": "Parse Error:" not in output,
    }
    table["verdict"] = all(table.values())
    table["unrelated_error_lines"] = unrelated[:40]
    table["unrelated_error_count"] = len(unrelated)
    table["verbatim_classify_process"] = classify_process(
        code, error, output, expected_exit, signature, allowed_errors)
    return table


def eval_with_trace(code, error, output, expected_exit, signature,
                    allowed_errors=()):
    """Order-tracing replica of the classify_process AND chain. Evaluates
    the six conjuncts in the landed left-to-right order with Python's
    short-circuit semantics and records which were reached. NOTE: in the
    production code the unrelated_errors list-comp is computed EAGERLY
    (runner lines 174-175) before the AND — modelled as step 0 so the
    'first-false' attribution reads correctly; the AND itself begins at
    code_eq_expected."""
    lines = output.splitlines()
    unrelated = [l for l in lines if "ERROR:" in l
                 and not any(allowed_error(l, a) for a in allowed_errors)]
    seq = [
        ("code_eq_expected", code == expected_exit),
        ("error_is_none", error is None),
        ("signature_present", signature in output),
        ("no_unrelated_errors", not unrelated),
        ("no_script_error", "SCRIPT ERROR:" not in output),
        ("no_parse_error", "Parse Error:" not in output),
    ]
    evaluated = []
    verdict = True
    first_false = None
    for name, val in seq:
        evaluated.append({"conjunct": name, "value": val,
                          "reached": True})
        if not val:
            verdict = False
            first_false = name
            break
    for name, _ in seq[len(evaluated):]:
        evaluated.append({"conjunct": name, "value": None,
                          "reached": False})
    return {"verdict": verdict, "first_false": first_false,
            "eager_unrelated_error_count": len(unrelated),
            "evaluation_order": evaluated,
            "verbatim": classify_process(code, error, output, expected_exit,
                                         signature, allowed_errors)}


# ---------------------------------------------------------------- helpers
def cmd_for(extra):
    return [GODOT, "--headless", "--path", str(PROJ), "--script",
            "res://descendant_pipe_probe.gd", "--"] + list(extra)


def safe_reap(pid):
    if pid is None or not pid_alive(pid):
        return False
    try:
        cl = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False
    if not any(t in cl for t in REAP_TOKENS):
        return False
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except OSError:
        return False


def comm_run(case, extra, bound=8.0, allowed_errors=(), expected_exit=0,
             signature=MARKER):
    """Verbatim run_process + classify_process (the CASES consumer path)."""
    started = time.monotonic()
    output, code, error = run_process(cmd_for(extra), bound)
    rec = {"case": case, "consumer": "run_process+classify_process",
           "flags": list(extra), "bound": bound,
           "expected_exit": expected_exit, "signature": signature,
           "allowed_errors": list(allowed_errors),
           "actual_exit": code, "error": error,
           "elapsed_seconds": round(time.monotonic() - started, 3),
           "output_bytes": len(output.encode(errors="replace")),
           "error_lines": sum(1 for l in output.splitlines() if "ERROR:" in l),
           "marker_present": MARKER in output,
           "save_sig_present": SAVE_SIG in output,
           "clauses": clauses(code, error, output, expected_exit, signature,
                              allowed_errors),
           "trace": eval_with_trace(code, error, output, expected_exit,
                                    signature, allowed_errors),
           "output": output}
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", output)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", output)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"write_ppid=(\d+)", output)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(rec["descendant_pid"])
    (RAW / f"{case}.stdout").write_text(output)
    return rec


def streams_run(case, extra, bound=8.0, allowed_stderr=()):
    """Separate-stream consumer -> production classify_streams AND the
    merged classify_process on the same bytes."""
    try:
        proc = subprocess.run(cmd_for(extra), capture_output=True,
                              text=True, timeout=bound)
        out, err, code, error = proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        code, error = None, f"TIMEOUT after {bound} seconds"
    rec = {"case": case, "consumer": "subprocess.run + classify_streams",
           "flags": list(extra), "bound": bound, "actual_exit": code,
           "error": error, "marker_in_stdout": MARKER in out,
           "marker_in_stderr": MARKER in err,
           "errline_in_stdout": "ERROR:" in out,
           "errline_in_stderr": "ERROR:" in err,
           "streams_classification": classify_streams(
               code, error, out, err, 0, MARKER, allowed_stderr),
           "merged_classification": classify_process(
               code, error, out + err, 0, MARKER),
           "stderr_lines": err.strip().splitlines() if err else [],
           "stdout": out, "stderr": err}
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", out + err)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    rec["descendant_reaped_by_driver"] = safe_reap(rec["descendant_pid"])
    (RAW / f"{case}.out").write_text(out)
    (RAW / f"{case}.err").write_text(err)
    return rec


# ================================================================ main
def main():
    results = {"runner": {
        "path": str(RUNNER), "sha256": runner_sha,
        "extracted": sorted(found),
        "godot": subprocess.run([GODOT, "--version"], capture_output=True,
                                text=True).stdout.strip(),
        "fixture": str(PROJ / "descendant_pipe_probe.gd"),
        "fixture_sha256": hashlib.sha256(
            (PROJ / "descendant_pipe_probe.gd").read_bytes()).hexdigest(),
    }}

    # ---------------- Phase 0: replay anchor on the r65-author receipt ----
    # Re-classify every CASES/mutant row of the committed r65-author run with
    # the verbatim classifier + its own expected_errors table; proves the
    # extraction and the census wiring on real captured outputs.
    receipt_path = (REPO / "live" / "r65-author" / "runs"
                    / "20261014T023015140150Z" / "verdicts.json")
    receipt = json.loads(receipt_path.read_text())
    replay = []
    mismatches = []
    mutant_allow = {
        "mutant_broken_scene_route": ("chain incomplete",
                                      (CHAIN_ENTRY,)),
        "mutant_level_collision_removed": None,  # filled below
    }
    mutant_allow["mutant_level_collision_removed"] = (
        "LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry",
        ("ERROR: LEVEL ASSERTION FAILED: loaded level cell lacks collision "
         "geometry",))
    for r in receipt["results"]:
        case = r.get("case", "")
        out_text = "\n".join(r.get("output", []))
        if case in mutant_allow:
            sig, allow = mutant_allow[case]
            cls = classify_process(r["actual_exit"], r["error"], out_text,
                                   2, sig, allow) and "PASS " not in out_text
            replay.append({"case": case, "recorded": r["verdict"],
                           "reclassified": cls})
            if (r["verdict"] == "PASS") != bool(cls):
                mismatches.append(case)
        elif r.get("script") and case not in ("export_readiness",
                                              "export_preset_missing"):
            allow = expected_errors_dict.get(case, ())
            cls = classify_process(r["actual_exit"], r["error"], out_text,
                                   r["expected_exit"], r["signature"], allow)
            replay.append({"case": case, "recorded": r["verdict"],
                           "reclassified": cls})
            if (r["verdict"] == "PASS") != bool(cls):
                mismatches.append(case)
        # export rows + probe_* meta rows have extra record-level conditions;
        # their classification component is exercised separately below.
    results["replay_anchor"] = {
        "receipt": str(receipt_path), "rows_replayed": len(replay),
        "mismatches": mismatches,
        "note": "CASES + mutant rows only; export/probe rows carry "
                "record-level conditions beyond classify_process",
        "rows": replay}

    # ---------------- Phase 1: clause-order + blob-vs-allowlist ----------
    S = MARKER
    unit_e1 = {
        "clean": [S],
        "unrelated_only": [S, ERR_LINE],
        "script_only": [S, SCRIPT_LINE],
        "parse_only": [S, PARSE_LINE],
        "triple_all": [S, ERR_LINE, SCRIPT_LINE, PARSE_LINE],
        "triple_sig_absent": [ERR_LINE, SCRIPT_LINE, PARSE_LINE],
        "triple_all_allowlisted": [S, ERR_LINE, SCRIPT_LINE, PARSE_LINE],
        "script_only_allowlisted": [S, SCRIPT_LINE],
        "script_split_evades": [S, "SCRIPT ERR", "OR: split diagnostic"],
        "parse_split_evades": [S, "Parse Er", "ror: split diagnostic"],
        "parse_line_is_not_errorline": [S, PARSE_LINE],
        "allowed_entry_carrying_script": [S,
            "ERROR: prefix SCRIPT ERROR: self-neutralizing"],
        "allowed_entry_carrying_parse": [S,
            "ERROR: prefix Parse Error: self-neutralizing"],
        "script_splice_fabricated": [S, "tail ending in SCRIPT ERROR: phantom"],
        "sig_absent_error_masked": ["no signature here", ERR_LINE],
    }
    e1_allow_triple = (ERR_LINE, SCRIPT_LINE, PARSE_LINE)
    e1_allow_script = (SCRIPT_LINE,)
    e1_allow_selfneut = ("ERROR: prefix SCRIPT ERROR: self-neutralizing",)
    e1_allow_selfneut_parse = ("ERROR: prefix Parse Error: self-neutralizing",)
    e1_rows = []
    for label, lines in unit_e1.items():
        text = "\n".join(lines) + "\n"
        allow = ()
        if label == "triple_all_allowlisted":
            allow = e1_allow_triple
        elif label == "script_only_allowlisted":
            allow = e1_allow_script
        elif label == "allowed_entry_carrying_script":
            allow = e1_allow_selfneut
        elif label == "allowed_entry_carrying_parse":
            allow = e1_allow_selfneut_parse
        e1_rows.append({"unit": label, "lines": lines, "allowlist": list(allow),
                        "trace": eval_with_trace(0, None, text, 0, S, allow)})
        t = e1_rows[-1]["trace"]
        print(f"[e1] {label}: verdict={t['verdict']} "
              f"first_false={t['first_false']} verbatim={t['verbatim']}",
              flush=True)
    results["edge1_clause_order_units"] = e1_rows

    # ---------------- Phase 2: allowlist forms ---------------------------
    e3_units = [
        # (label, line, allowlist)
        ("exact_absorbs", SAVE_SIG, (SAVE_SIG,)),
        ("exact_suffix_escapes", SAVE_SIG + " tail", (SAVE_SIG,)),
        ("exact_prefix_escapes", "noise " + SAVE_SIG, (SAVE_SIG,)),
        ("exact_second_error_escapes", SAVE_SIG + " ERROR: second",
         (SAVE_SIG,)),
        ("exact_double_space_escapes",
         SAVE_SIG.replace("ERROR: ", "ERROR:  ", 1), (SAVE_SIG,)),
        ("comma_entry_alone_absorbs", COMMA_ENTRY, (COMMA_ENTRY,)),
        ("comma_tail_absorbs", COMMA_LINE, (COMMA_ENTRY,)),
        ("comma_tail_count2_escapes", COMMA_LINE + " ERROR: second",
         (COMMA_ENTRY,)),
        ("comma_prefix_escapes", "noise " + COMMA_LINE, (COMMA_ENTRY,)),
        ("comma_no_comma_escapes", COMMA_ENTRY[:-1], (COMMA_ENTRY,)),
        ("comma_arbitrary_tail_absorbs",
         COMMA_ENTRY + " arbitrary free text without token", (COMMA_ENTRY,)),
        ("comma_script_tail_escapes", COMMA_ENTRY + " SCRIPT ERROR: x",
         (COMMA_ENTRY,)),
        ("chain_shape_absorbs", CHAIN_LINE, (CHAIN_ENTRY,)),
        ("chain_scene_mut_escapes", CHAIN_ESC, (CHAIN_ENTRY,)),
        ("chain_no_oldalive_escapes",
         "ERROR: chain incomplete collections=7 scene=SceneB:<Node#1> x",
         (CHAIN_ENTRY,)),
        ("chain_wrong_prefix_escapes",
         "ERROR: chain incomplete scene=SceneB:<Node#1> collections=7 "
         "old_alive=false", (CHAIN_ENTRY,)),
        ("chain_count2_escapes", CHAIN_LINE + " ERROR: second",
         (CHAIN_ENTRY,)),
        ("chain_prepended_escapes", "noise " + CHAIN_LINE, (CHAIN_ENTRY,)),
        ("chain_bare_entry_absorbs", CHAIN_ENTRY, (CHAIN_ENTRY,)),
        ("chain_reordered_fields_absorbs",
         "ERROR: chain incomplete collections=9 old_alive=false "
         "scene=SceneB:<Node#9>", (CHAIN_ENTRY,)),
        ("chain_free_suffix_absorbs",
         CHAIN_LINE + " arbitrary suffix", (CHAIN_ENTRY,)),
        ("entry_cross_case_inert", COMMA_LINE, (SAVE_SIG,)),
    ]
    e3_rows = []
    for label, line, allow in e3_units:
        text = S + "\n" + line + "\n"
        rec = {"unit": label, "line": line, "allowlist": list(allow),
               "verbatim": classify_process(0, None, text, 0, S, allow),
               "line_absorbed_by_clause1": allowed_error(line, allow[0])}
        e3_rows.append(rec)
        print(f"[e3] {label}: verbatim={rec['verbatim']} "
              f"absorbed={rec['line_absorbed_by_clause1']}", flush=True)
    # streams-side allowlist asymmetry: line_allowed has NO structured branch
    for label, err_line, allow in [
            ("streams_chain_rejects", CHAIN_LINE, (CHAIN_ENTRY,)),
            ("streams_chain_bare_accepts", CHAIN_ENTRY, (CHAIN_ENTRY,)),
            ("streams_comma_accepts", COMMA_LINE, (COMMA_ENTRY,)),
            ("streams_exact_accepts", SAVE_SIG, (SAVE_SIG,))]:
        stdout_t = S + "\n"
        stderr_t = err_line + "\n"
        rec = {"unit": label, "stderr_line": err_line,
               "allowlist": list(allow),
               "verbatim_streams": classify_streams(
                   0, None, stdout_t, stderr_t, 0, S, allow),
               "verbatim_merged_same_allow": classify_process(
                   0, None, stdout_t + stderr_t, 0, S, allow)}
        e3_rows.append(rec)
        print(f"[e3s] {label}: streams={rec['verbatim_streams']} "
              f"merged={rec['verbatim_merged_same_allow']}", flush=True)
    results["edge3_allowlist_units"] = e3_rows

    # ---------------- Phase 3: real-pipe runs ----------------------------
    comm_plan = [
        # edge 1 — three clauses on real post-death records
        ("comm_err_script", ["--spawn-errforge-script"], 8.0, (), 0, MARKER),
        ("comm_err_parse", ["--spawn-errforge-parse"], 8.0, (), 0, MARKER),
        ("comm_err_triple", ["--spawn-errforge-triple"], 8.0, (), 0, MARKER),
        ("comm_err_triple_allowed", ["--spawn-errforge-triple"], 8.0,
         (ERR_LINE, SCRIPT_LINE, PARSE_LINE), 0, MARKER),
        ("comm_err_allowed_script", ["--spawn-errforge-allowed-script"], 8.0,
         (SAVE_SIG, SCRIPT_LINE), 0, MARKER),
        ("comm_err_scriptsplit", ["--spawn-errforge-scriptsplit"], 8.0,
         (), 0, MARKER),
        # edge 2 — >64KiB / pipe-buffer boundary
        ("comm_bulk_straddle", ["--spawn-errforge-bulk-straddle"], 8.0,
         (), 0, MARKER),
        ("comm_bulk_embed", ["--spawn-errforge-bulk-embed"], 8.0, (), 0, MARKER),
        ("comm_bulk_nlsplit", ["--spawn-errforge-bulk-nlsplit"], 8.0,
         (), 0, MARKER),
        # edge 3 — allowlist forms on real pipes
        ("comm_comma_absorbed", ["--spawn-errforge-comma"], 8.0,
         (COMMA_ENTRY,), 0, MARKER),
        ("comm_comma_unallowlisted", ["--spawn-errforge-comma"], 8.0,
         (), 0, MARKER),
        ("comm_comma_escape", ["--spawn-errforge-comma-escape"], 8.0,
         (COMMA_ENTRY,), 0, MARKER),
        ("comm_chain_absorbed", ["--spawn-errforge-chain"], 8.0,
         (CHAIN_ENTRY,), 0, MARKER),
        ("comm_chain_escape", ["--spawn-errforge-chain-escape"], 8.0,
         (CHAIN_ENTRY,), 0, MARKER),
        # edge 5 — dual-substring single line + negative-row fabrication
        ("comm_dualline", ["--spawn-errforge-dualline"], 8.0, (), 0, MARKER),
        ("comm_dualline_wh", ["--spawn-errforge-dualline-withheld"], 8.0,
         (), 0, MARKER),
        ("comm_negrow_fabricated", ["--spawn-errforge-negrow"], 8.0,
         (SAVE_SIG,), 2, SAVE_SIG),
        ("comm_negrow_noallow", ["--spawn-errforge-negrow"], 8.0,
         (), 2, SAVE_SIG),
        # edge (c) — splice fabrication + newline-split continuity
        ("comm_splice_self", ["--spawn-errforge-splice-self"], 8.0,
         (), 0, MARKER),
        ("comm_splice_xstream", ["--spawn-errforge-splice-xstream"], 8.0,
         (), 0, MARKER),
        ("comm_newlinesplit_rerun", ["--spawn-errforge-newlinesplit"], 8.0,
         (), 0, MARKER),
        # controls
        ("comm_default_control", [], 8.0, (), 0, MARKER),
        ("comm_err_release_control", ["--spawn-errforge-release"], 8.0,
         (), 0, MARKER),
    ]
    results["comm_runs"] = []
    for name, extra, bound, allow, ex, sig in comm_plan:
        rec = comm_run(name, extra, bound, allow, ex, sig)
        results["comm_runs"].append(rec)
        print(f"[comm] {name}: verdict={rec['clauses']['verdict']} "
              f"first_false={rec['trace']['first_false']} "
              f"exit={rec['actual_exit']} err={rec['error']!r} "
              f"bytes={rec['output_bytes']} elapsed={rec['elapsed_seconds']}",
              flush=True)

    # ---------------- Phase 4: streams cross table (edge 4) ---------------
    st_plan = [
        ("st_default", [], ()),
        ("st_err_stdout", ["--spawn-errforge-release"], ()),
        ("st_err_stderr", ["--spawn-errforge-stderr-release"], ()),
        ("st_stderr_noise", ["--spawn-errforge-stderr-noise"], ()),
        ("st_script_stdout", ["--spawn-errforge-script"], ()),
        ("st_dualline_stdout", ["--spawn-errforge-dualline"], ()),
        ("st_forge_sig_stderr", ["--spawn-forge-stderr"], ()),
        ("st_genuine_error", ["--spawn-genuine-error"], ()),
        ("st_comma_stderr_allowed", ["--spawn-errforge-stderr-release"],
         (ERR_LINE,)),
    ]
    results["stream_runs"] = []
    for name, extra, allow in st_plan:
        rec = streams_run(name, extra, 8.0, allow)
        results["stream_runs"].append(rec)
        print(f"[st] {name}: streams={rec['streams_classification']} "
              f"merged={rec['merged_classification']} "
              f"err_out={rec['errline_in_stdout']} "
              f"err_err={rec['errline_in_stderr']} "
              f"stderr_lines={len(rec['stderr_lines'])}", flush=True)

    # ---------------- Phase 5: verbatim gate on surface arms --------------
    gate_plan = [
        ("vg_default", []),
        ("vg_bulk_straddle", ["--spawn-errforge-bulk-straddle"]),
        ("vg_dualline_wh", ["--spawn-errforge-dualline-withheld"]),
        ("vg_dualline", ["--spawn-errforge-dualline"]),
        ("vg_negrow_n/a_control", ["--spawn-errforge-negrow"]),
    ]
    results["gate_runs"] = []
    for name, extra in gate_plan:
        rec = gated_signature_run(name, extra)
        rec["arm"] = extra
        rec["clauses"] = clauses(rec["actual_exit"], rec["error"],
                                 "\n".join(rec.get("output_lines", [])),
                                 0, MARKER)
        rec["descendant_reaped_by_driver"] = safe_reap(
            rec.get("descendant_pid"))
        rec.pop("command", None)
        results["gate_runs"].append(rec)
        print(f"[vg] {name}: sig_ok={rec['gated_signature_accepted']} "
              f"inner={rec['inner_classification']} "
              f"exit={rec['actual_exit']} dead_at={rec['dead_observed_at']} "
              f"marker_at={rec['marker_observed_at']}", flush=True)

    # ---------------- Phase 6: line-faithfulness synthetic units ----------
    # (c): the phantom splice + newline-split at unit level with per-stream
    # line-set evidence.
    lf_units = []
    for label, out_t, err_t, allow in [
        ("xstream_phantom", "head ending in ERROR", ": PHANTOM_X\n", ()),
        ("intra_pipe_phantom", "head ending in ERROR: PHANTOM_S\n", "", ()),
        ("newline_split", "clean\nERR\nOR: forged\n", "", ()),
        ("clean_control", "clean\n", "also clean\n", ()),
    ]:
        merged = out_t + err_t
        sig_present = S in merged
        lf_units.append({
            "unit": label,
            "stdout_lines": out_t.splitlines(),
            "stderr_lines": err_t.splitlines(),
            "merged_lines": merged.splitlines(),
            "phantom_in_merged_only": [
                l for l in merged.splitlines()
                if l not in out_t.splitlines() + err_t.splitlines()],
            "verbatim_merged": classify_process(
                0, None, S + "\n" + merged, 0, S, allow)})
        print(f"[lf] {label}: verbatim={lf_units[-1]['verbatim_merged']} "
              f"phantom={lf_units[-1]['phantom_in_merged_only']}", flush=True)
    results["line_faithfulness_units"] = lf_units

    # ---------------- Phase 7: dead-entry / dead-clause census ------------
    census = {"receipt": str(receipt_path)}
    entries_report = []
    rows_by_case = {r.get("case"): r for r in receipt["results"]}
    for name, script, flags, ex, sig in cases_table:
        row = rows_by_case.get(name)
        entries = expected_errors_dict.get(name, ())
        if row is None:
            entries_report.append({"case": name, "entries": list(entries),
                                   "row_present": False})
            continue
        out_lines = row.get("output", [])
        err_lines = [l for l in out_lines if "ERROR:" in l]
        def match_branch(line, ent):
            stripped = line.strip()
            if stripped == ent:
                return "exact"
            if ent.endswith(",") and stripped.startswith(ent) \
                    and stripped.count("ERROR:") == 1:
                return "comma-prefix"
            if ent == CHAIN_ENTRY and allowed_error(line, ent):
                return "structured"
            return None

        entry_status = []
        for ent in entries:
            matched = [l for l in out_lines if allowed_error(l, ent)]
            entry_status.append({
                "entry": ent,
                "form": ("comma-prefix" if ent.endswith(",")
                         else "structured" if ent == CHAIN_ENTRY
                         else "exact"),
                "matched_lines": len(matched),
                "match_branches": sorted({
                    match_branch(l, ent) for l in matched} - {None}),
                "live_on_own_row": bool(matched)})
        unmatched_err = [l for l in err_lines
                         if not any(allowed_error(l, e) for e in entries)]
        entries_report.append({
            "case": name, "entries": entry_status,
            "row_error_lines": len(err_lines),
            "row_unmatched_error_lines": unmatched_err,
            "row_present": True})
    # mutant allowlists (reachable only under --probe-failing)
    for case, (sig, allow) in mutant_allow.items():
        row = rows_by_case.get(case)
        if row:
            out_lines = row.get("output", [])
            entries_report.append({
                "case": case, "entries": [
                    {"entry": e, "form": ("comma-prefix" if e.endswith(",")
                                          else "structured" if e == CHAIN_ENTRY
                                          else "exact"),
                     "matched_lines": sum(
                        1 for l in out_lines if allowed_error(l, e)),
                     "match_branches": sorted({
                        ("exact" if l.strip() == e
                         else "comma-prefix" if e.endswith(",")
                            and l.strip().startswith(e)
                            and l.strip().count("ERROR:") == 1
                         else "structured" if e == CHAIN_ENTRY
                            and allowed_error(l, e)
                         else None)
                        for l in out_lines if allowed_error(l, e)} - {None}),
                     "live_on_own_row": any(
                        allowed_error(l, e) for l in out_lines)}
                    for e in allow],
                "row_error_lines": sum(1 for l in out_lines if "ERROR:" in l),
                "row_present": True})
    census["per_case_entries"] = entries_report
    census["dead_entries"] = [
        {"case": e["case"], "entry": s["entry"], "form": s["form"]}
        for e in entries_report if e.get("row_present")
        for s in e.get("entries", [])
        if not s["live_on_own_row"]]
    census["entries_for_absent_rows"] = [
        e["case"] for e in entries_report if not e.get("row_present")]
    # blob-clause census across every captured output in the receipt
    census["script_error_rows"] = sorted({
        r["case"] for r in receipt["results"]
        if "SCRIPT ERROR:" in "\n".join(r.get("output", []))})
    census["parse_error_rows"] = sorted({
        r["case"] for r in receipt["results"]
        if "Parse Error:" in "\n".join(r.get("output", []))})
    census["rows_with_error_lines"] = sum(
        1 for r in receipt["results"]
        if any("ERROR:" in l for l in r.get("output", [])))
    # classify_streams allowlist call-site census (in-tree callers)
    call_sites = []
    for i, line in enumerate(src.splitlines(), 1):
        if "classify_streams(" in line and "def " not in line:
            call_sites.append({"line": i, "text": line.strip()})
    census["classify_streams_call_sites"] = call_sites
    census["streams_allowlist_always_empty"] = all(
        "allowed_stderr=()" in c["text"] or "allowed_stderr" not in c["text"]
        for c in call_sites)
    # audio leaked-ObjectDB clause census on the audio row
    audio_row = rows_by_case.get("audio_playback")
    census["audio_leak_regex_matches"] = (
        len(re.findall(r"WARNING: [1-9][0-9]* ObjectDB instances were leaked",
                       "\n".join(audio_row["output"]))) if audio_row else None)
    results["dead_entry_census"] = census

    # ---------------- Phase 8: falsifiable-claim synthesis ----------------
    results["claim_synthesis"] = {
        "declared": ("the rejection clause's verdict is a pure function of "
                     "merged-output line presence modulo the allowlist — "
                     "forgeable in both directions (evasion and fabrication) "
                     "by a post-death descendant"),
        "evasion_receipts": {
            "newline_split": "comm_newlinesplit_rerun + comm_bulk_nlsplit",
            "stdout_under_streams": "st_err_stdout",
        },
        "fabrication_receipts": {
            "xstream_splice": "comm_splice_xstream",
            "intra_pipe_splice": "comm_splice_self",
            "negative_row_evidence": "comm_negrow_fabricated",
            "plain_forge": "comm_err_release_control",
        },
        "allowlist_modulo_receipts": {
            "exact": "comm_negrow_fabricated vs comm_negrow_noallow",
            "comma_prefix": "comm_comma_absorbed vs comm_comma_unallowlisted",
            "structured": "comm_chain_absorbed vs comm_chain_escape",
        },
        "scope_limit": ("capture-before-pipe-EOF precondition (r65 critic "
                        "CE-1): the function is over CAPTURED merged lines, "
                        "not over emissions")},
    out_path = EDGE / "surface-verdicts.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n")
    print("wrote", out_path, flush=True)


if __name__ == "__main__":
    sys.exit(main())
