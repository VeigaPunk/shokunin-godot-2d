#!/usr/bin/env python3
"""r66 scribe: rejection-clause SURFACE — independent derivation.

Declared falsifiable claim (r66 brief, verbatim): "the rejection clause's
verdict is a pure function of merged-output line presence modulo the
allowlist — forgeable in both directions (evasion and fabrication) by a
post-death descendant."

ast.get_source_segment-extracts run_process / classify_process /
classify_streams / classify_audio_process VERBATIM from the WORKTREE
corpus/fixtures/run_battery.py (the uncommitted r66 author candidate) AND
from the HEAD blob, and execs them — production code path, zero
transcription. Segment shas are compared HEAD-vs-worktree so the
measurements bind to the exact classifier bytes.

Measured surfaces on REAL pipes (subprocess capture, never fed strings):
  (a) allowlist-forge  — ppid-gated post-death descendant writes each
      allowlist SHAPE (exact / `,`-prefix+tail / `,`-prefix+second-ERROR: /
      structured / whitespace-padded exact / foreign) — verdict-inert iff
      the matching entry is given; the count("ERROR:")==1 conjunct shown
      breakable in both directions on captured bytes.
  (c-evade) newline-split — ERR<boundary>OR: post-death across the
      splitlines boundary set (\n, \r, \v), incl. a SCRIPT ERROR: split.
  (c-fab) splice fabrication — concat-seam (stdout tail + stderr head,
      in-life AND post-death), same-fd post-death, SCRIPT ERROR: seam,
      and the ACCEPT-axis dual: a signature fabricated at a seam that no
      process ever emitted -> verdict True.
  (+) midline splice (pre-death descendant inside a halved signature)
      and the decode hole: a post-death \\xff write -> UnicodeDecodeError
      escapes run_process — the verdict is never produced.
  (d) dead-entry census — verbatim allowed_error replay over the r66
      author's own 99-row receipt + static reachability notes.

Synthetic children are /usr/bin/sh; descendant scripts live in desc/
(free of nested-quoting hazards) and use the fixture's own
/proc/self/stat reparenting gate. Real headless Godot children run the
WORKTREE fixture copy in proj/ (carries the author's four --spawn-*forge
arms verbatim).
"""
import ast
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RUNNER = REPO / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
DESC = HERE / "desc"
RAW = HERE / "raw"
GODOT = sys.argv[1] if len(sys.argv) > 1 else "godot"
SIG = "R66_SURFACE_PROBE: expected signature"
GMARK = "DESCENDANT_PIPE_PROBE: expected signature"
BOUND = 3.0
for d in (DESC, RAW):
    d.mkdir(exist_ok=True)

# ---- verbatim extraction: worktree candidate AND committed HEAD ----------
work_src = RUNNER.read_text()
head_src = subprocess.run(["git", "-C", str(REPO), "show",
                           "HEAD:corpus/fixtures/run_battery.py"],
                          capture_output=True, text=True).stdout


def extract(source, names):
    tree = ast.parse(source)
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            out[node.name] = ast.get_source_segment(source, node)
    return out


WANT = ("run_process", "classify_process", "classify_streams",
        "classify_audio_process")
work_funcs = extract(work_src, WANT)
head_funcs = extract(head_src, WANT)
seg_sha = {f"{side}.{name}": hashlib.sha256(seg.encode()).hexdigest()
           for side, funcs in (("worktree", work_funcs), ("head", head_funcs))
           for name, seg in funcs.items()}
seg_equal = {name: work_funcs.get(name) == head_funcs.get(name)
             for name in WANT}

ns = {"subprocess": subprocess, "re": re}
for seg in work_funcs.values():
    exec(seg, ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]

RUNNER_SHA = hashlib.sha256(work_src.encode()).hexdigest()
HEAD_SHA = hashlib.sha256(head_src.encode()).hexdigest()

# Allowlist strings under test (verbatim from worktree expected_errors /
# classify_mutant call sites).
ALLOW_EXACT = ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected "
               "signature=JSON_PARSE_ERROR")             # save_corrupt_negative
ALLOW_COMMA = ("ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file "
               "rejected signature=FILE_NOT_FOUND,")     # save_process_missing
ALLOW_COMMA2 = ("ERROR: UI BUTTON ASSERTION FAILED: expected release1 "
                "text=Activated 1 receipts=1,")          # button_activation_*
ALLOW_CHAIN = "ERROR: chain incomplete"                  # classify_mutant arm
FOREIGN = "ERROR: unrelated different diagnostic"

# ------------------------------------------------------- descendant scripts
GATE = ('while read -r _ _ _ pp _ < /proc/self/stat && [ "$pp" = "$1" ]; '
        'do sleep 0.05; done\n')
DESC_SCRIPTS = {
    # (a) allowlist-forge: each match shape, written post-death
    "R66S_allow_exact": GATE +
        f'echo "{ALLOW_EXACT}"\necho "R66 write_ppid=$pp"\n',
    "R66S_allow_exact_padded": GATE +
        f'echo "   {ALLOW_EXACT}   "\necho "R66 write_ppid=$pp"\n',
    "R66S_allow_twin": GATE +
        'echo "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected '
        'signature=JSON_PARSE_ERR0R"\necho "R66 write_ppid=$pp"\n',
    "R66S_allow_comma_tail": GATE +
        f'echo "{ALLOW_COMMA}forged_tail path=/tmp/x"\n'
        'echo "R66 write_ppid=$pp"\n',
    "R66S_allow_comma_dbl": GATE +
        f'echo "{ALLOW_COMMA}forged ERROR: second tail"\n'
        'echo "R66 write_ppid=$pp"\n',
    "R66S_allow_comma_atcomma": GATE +
        f'echo "{ALLOW_COMMA}"\necho "R66 write_ppid=$pp"\n',
    "R66S_allow_comma2_tail": GATE +
        f'echo "{ALLOW_COMMA2}FORGED_SUFFIX receipts=9"\n'
        'echo "R66 write_ppid=$pp"\n',
    "R66S_allow_structured": GATE +
        'echo "ERROR: chain incomplete collections=9 '
        'scene=SceneB:<Node#9> old_alive=false"\necho "R66 write_ppid=$pp"\n',
    "R66S_allow_structured_missing": GATE +
        'echo "ERROR: chain incomplete collections=9 '
        'scene=SceneB:<Node#9>"\necho "R66 write_ppid=$pp"\n',
    # dormant blob clauses, forged post-death
    "R66S_script_forge": GATE +
        'echo "SCRIPT ERROR: R66 forged script clause"\n'
        'echo "R66 write_ppid=$pp"\n',
    "R66S_parse_forge": GATE +
        'echo "Parse Error: R66 forged parse clause"\n'
        'echo "R66 write_ppid=$pp"\n',
    # (c-evade) newline-split across several splitlines boundaries
    "R66S_nlsplit_lf": GATE +
        "printf 'ERR\\n'; sleep 0.05; "
        "printf 'OR: R66 newline-split diagnostic\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_nlsplit_cr": GATE +
        "printf 'ERR\\rOR: R66 cr-split diagnostic\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_nlsplit_vt": GATE +
        "printf 'ERR\\vOR: R66 vt-split diagnostic\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_nlsplit_script": GATE +
        "printf 'SCRIPT ERR\\nOR: R66 script clause split\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_nosplit_ctrl": GATE +
        "printf 'ERROR: R66 contiguous control\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    # (c-fab) splices, post-death
    "R66S_seam_xfd": GATE +
        "printf 'OR: R66 post-death xfd seam fabricated\\n' >&2\n"
        'echo "R66 write_ppid=$pp" >&2\n',
    "R66S_seam_samefd": GATE +
        "printf 'OR: R66 same-fd seam fabricated\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_seam_sig": GATE +
        "printf 'ture\\n'\necho \"R66 write_ppid=$pp\"\n",
    "R66S_decode": GATE +
        "printf '\\377\\376 R66 post-death undecodable write\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    # midline: UNGATED — fixed-offset pre-death write ($PPID stays child)
    "R66S_midline":
        'sleep 0.3\necho "ERROR: R66 midline forged splice"\n'
        'echo "R66 write_ppid=$PPID"\n',
    # CE-1a: allowlist-absorbed line carrying a blob-clause token in its
    # tail — the scan absorbs it; the blob clause vetoes anyway.
    "R66S_ce1a_parse_tail": GATE +
        f'echo "{ALLOW_COMMA} tail embeds Parse Error: injected"\n'
        'echo "R66 write_ppid=$pp"\n',
    # CE-2 residual-fragment backstops: splits that leave an ERROR:-bearing
    # fragment still reject.
    "R66S_ce2_scr_ipt": GATE +
        "printf 'SCR\\nIPT ERROR: R66 residual fragment\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_ce2_script_sp": GATE +
        "printf 'SCRIPT \\nERROR: R66 residual fragment\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_ce2_parse_split": GATE +
        "printf 'Parse Err\\nor: R66 parse token split\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    "R66S_ce2_error_headsplit": GATE +
        "printf 'ERROR: R66 head line\\nrest of it\\n'\n"
        'echo "R66 write_ppid=$pp"\n',
    # attack-4 composite: ONE descendant evades a real emission (ERR\nOR:)
    # AND fabricates an allowlist-shaped phantom across the concat seam —
    # record twice-forged, verdict PASS under the allowlist.
    "R66S_double_forge": GATE +
        "printf 'ERR\\nOR: R66 real escaped error\\n'\n"
        "printf 'ERROR'\n"
        "printf ': SAVE EXPECTED NEGATIVE: malformed JSON rejected "
        "signature=JSON_PARSE_ERROR\\n' >&2\n"
        'echo "R66 write_ppid=$pp" >&2\n',
}
desc_sha = {}
for name, body in DESC_SCRIPTS.items():
    p = DESC / f"{name}.sh"
    p.write_text("#!/bin/sh\n# r66-scribe descendant arm\n" + body)
    desc_sha[name] = hashlib.sha256(p.read_bytes()).hexdigest()


def proc_state(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return None


def kernel_ppid(pid):
    if pid is None or pid <= 0:
        return None
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return int(fh.read().rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return None


def pid_alive(pid):
    if pid is None or pid <= 0:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def allowed_error(line, allowed):
    """Mirror of the nested helper (line-attribution only; verdicts under
    test are always the exec'd classify_process)."""
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


def clause_table(code, error, text, expected_exit=0, signature=SIG,
                 allowed=()):
    """Explode the classify_process conjunction — read off which conjunct
    fired, never inferred."""
    lines = text.splitlines()
    unrelated = [l for l in lines if "ERROR:" in l
                 and not any(allowed_error(l, a) for a in allowed)]
    return {"code_eq": code == expected_exit,
            "error_none": error is None,
            "sig_present": signature in text,
            "no_unrelated_errors": not unrelated,
            "no_script_error": "SCRIPT ERROR:" not in text,
            "no_parse_error": "Parse Error:" not in text,
            "unrelated_error_lines": [l.strip() for l in unrelated],
            "error_lines": [l.strip() for l in lines if "ERROR:" in l]}


def reap(text, rec):
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"R66 write_ppid=(\d+)|DESCENDANT_PIPE_\w+ write_ppid=(\d+)",
                  text)
    rec["write_ppid"] = (int(m.group(1) or m.group(2))) if m else None
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)|R66 child_pid=(\d+)", text)
    rec["child_pid_seen"] = (int(m.group(1) or m.group(2))) if m else None
    rec["write_post_orphan"] = (rec["write_ppid"] is not None
                              and rec["child_pid_seen"] is not None
                              and rec["write_ppid"] != rec["child_pid_seen"])
    rec["write_pre_death"] = (rec["write_ppid"] is not None
                             and rec["child_pid_seen"] is not None
                             and rec["write_ppid"] == rec["child_pid_seen"])
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(
        rec["descendant_pid"])
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    if pid_alive(rec["descendant_pid"]):
        try:
            with open(f"/proc/{rec['descendant_pid']}/cmdline", "rb") as fh:
                cmdline = fh.read()
            # token-scoped reaper: only this run's tagged descendants
            if b"R66S_" in cmdline or b"DESCENDANT_PIPE" in cmdline:
                os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass


def finalize(rec, code, error, output, signature, allowlists):
    rec["actual_exit"], rec["error"] = code, error
    rec["clauses"] = clause_table(code, error, output,
                                  signature=signature)
    rec["verdicts_by_allowlist"] = {
        (json.dumps(list(a)) if a else "bare()"): classify_process(
            code, error, output, 0, signature, tuple(a))
        for a in allowlists}
    rec["verdict_bare"] = rec["verdicts_by_allowlist"].get(
        "bare()", classify_process(code, error, output, 0, signature, ()))
    stripped = "\n".join(l for l in output.splitlines() if "ERROR:" not in l)
    rec["stripped_verdict"] = classify_process(code, error, stripped, 0,
                                               signature)
    rec["output_lines"] = output.strip().splitlines()
    rec["merged_sha256"] = hashlib.sha256(output.encode()).hexdigest()
    reap(output, rec)
    return rec


def naive_run(command, label, bound=BOUND, allowlists=((),), signature=SIG):
    """The CASES verdict path: verbatim run_process + classify_process."""
    rec = {"label": label, "path": "run_process(verbatim)",
           "command": command, "bound_seconds": bound}
    t0 = time.monotonic()
    try:
        output, code, error = run_process(command, bound)
        rec["run_exception"] = None
    except Exception as exc:  # noqa: BLE001 — record whatever escapes verbatim
        rec["run_exception"] = f"{type(exc).__name__}: {exc}"
        output, code, error = "", None, f"{type(exc).__name__}"
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    return finalize(rec, code, error, output, signature, allowlists)


def split_run(command, label, bound=BOUND, allowlists=((),), signature=SIG):
    """Per-stream capture: proves a fabricated line/signature exists in
    NEITHER stream; the verdict still comes from the verbatim classifier."""
    rec = {"label": label, "path": "split_capture+verbatim classify",
           "command": command, "bound_seconds": bound}
    t0 = time.monotonic()
    stdout_text = stderr_text = ""
    rec["run_exception"] = None
    code, error = None, None
    try:
        proc = subprocess.run(command, capture_output=True, text=True,
                              timeout=bound)
        stdout_text, stderr_text = proc.stdout or "", proc.stderr or ""
        code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout_text = (exc.stdout.decode(errors="replace")
                       if isinstance(exc.stdout, bytes)
                       else (exc.stdout or ""))
        stderr_text = (exc.stderr.decode(errors="replace")
                       if isinstance(exc.stderr, bytes)
                       else (exc.stderr or ""))
        error = f"TIMEOUT after {bound} seconds"
    except Exception as exc:  # noqa: BLE001
        rec["run_exception"] = f"{type(exc).__name__}: {exc}"
        error = f"{type(exc).__name__}"
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    merged = stdout_text + stderr_text
    rec["stdout_lines"] = stdout_text.strip().splitlines()
    rec["stderr_lines"] = stderr_text.strip().splitlines()
    rec["stdout_error_lines"] = [l.strip() for l in rec["stdout_lines"]
                                 if "ERROR:" in l]
    rec["stderr_error_lines"] = [l.strip() for l in rec["stderr_lines"]
                                 if "ERROR:" in l]
    rec["merged_error_lines"] = [l.strip() for l in merged.splitlines()
                                 if "ERROR:" in l]
    rec["sig_in_stdout"] = signature in stdout_text
    rec["sig_in_stderr"] = signature in stderr_text
    rec["sig_in_merged"] = signature in merged
    return finalize(rec, code, error, merged, signature, allowlists)


def sh_child(body, desc=None):
    """Child sh: prints R66 child_pid, spawns desc script (reparenting-
    gated unless the script opts out), runs body, exits 0. Descendant is
    spawned BEFORE body so a body's unterminated tail stays last."""
    pre = 'echo R66 child_pid=$$; '
    spawn = ""
    if desc:
        spawn = (f'sh "{DESC}/{desc}.sh" $$ & '
                 'echo DESCENDANT_PIPE spawned_pid=$!; ')
    return ["/usr/bin/sh", "-c", pre + spawn + body + '; exit 0']


def godot_cmd(*flags):
    return [GODOT, "--headless", "--path", str(PROJ), "--script",
            "res://descendant_pipe_probe.gd", "--", *flags]


ARMS = {
    # ---- controls ----
    "syn_genuine": (naive_run, sh_child(f'echo "{SIG}"')),
    "syn_self_error": (naive_run, sh_child(
        f'echo "{SIG}"; echo "ERROR: child self diagnostic"')),
    # ---- (a) allowlist-forge, all shapes, post-death ----
    "syn_allowforge_exact": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_exact")),
    "syn_allowforge_exact_padded": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_exact_padded")),
    "syn_allowforge_twin": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_twin")),
    "syn_allowforge_comma_tail": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_comma_tail")),
    "syn_allowforge_comma_dbl": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_comma_dbl")),
    "syn_allowforge_comma_atcomma": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_comma_atcomma")),
    "syn_allowforge_comma2_tail": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_comma2_tail")),
    "syn_allowforge_structured": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_structured")),
    "syn_allowforge_structured_missing": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_allow_structured_missing")),
    "syn_script_forge": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_script_forge")),
    "syn_parse_forge": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_parse_forge")),
    # ---- (c) newline-split evasion, post-death ----
    "syn_nlsplit_lf": (naive_run, sh_child(f'echo "{SIG}"',
                                           "R66S_nlsplit_lf")),
    "syn_nlsplit_cr": (naive_run, sh_child(f'echo "{SIG}"',
                                           "R66S_nlsplit_cr")),
    "syn_nlsplit_vt": (naive_run, sh_child(f'echo "{SIG}"',
                                           "R66S_nlsplit_vt")),
    "syn_nlsplit_script": (naive_run, sh_child(f'echo "{SIG}"',
                                               "R66S_nlsplit_script")),
    "syn_nosplit_ctrl": (naive_run, sh_child(f'echo "{SIG}"',
                                             "R66S_nosplit_ctrl")),
    # ---- (c) splice fabrication ----
    # in-life concat seam: child's OWN unterminated stdout tail + its OWN
    # stderr head — fabrication is merge-order, not provenance.
    "syn_seam_inlife": (split_run, ["/usr/bin/sh", "-c",
        'echo R66 child_pid=$$; '
        f'printf "{SIG}\\nSEAM_ERR"; '
        'printf "OR: R66 in-life seam fabricated\\n" >&2; exit 0']),
    # post-death cross-fd: child unterminated stdout tail, exits; gated
    # descendant writes the completing head to stderr after death.
    "syn_seam_postdeath_xfd": (split_run, sh_child(
        f'printf "{SIG}\\nSEAM_ERR"', "R66S_seam_xfd")),
    # post-death same-fd: descendant continues the child's unterminated
    # stdout line inside a SINGLE captured stream.
    "syn_seam_postdeath_samefd": (split_run, sh_child(
        f'printf "{SIG}\\nSFD_ERR"', "R66S_seam_samefd")),
    # accept-axis dual: signature completed across the concat seam — no
    # process ever emits the full marker.
    "syn_seam_sig_inlife": (split_run, ["/usr/bin/sh", "-c",
        'echo R66 child_pid=$$; printf "R66_SURFACE_PROBE: expected signa"; '
        'printf "ture\\n" >&2; exit 0']),
    # post-death same-fd signature completion: descendant appends the last
    # token to the child's unterminated stdout tail after death.
    "syn_seam_sig_postdeath": (split_run, sh_child(
        'printf "R66_SURFACE_PROBE: expected signa"', "R66S_seam_sig")),
    # SCRIPT ERROR: blob clause fabricated at the concat seam.
    "syn_seam_script": (split_run, ["/usr/bin/sh", "-c",
        'echo R66 child_pid=$$; '
        f'printf "{SIG}\\nTAIL_SCRIPT "; '
        'printf "ERROR: R66 seam script clause\\n" >&2; exit 0']),
    # mid-signature splice, pre-death descendant (author's arm in syn):
    "syn_midline": (split_run, sh_child(
        'printf "R66_SURFACE_PROBE: expected "; sleep 0.8; '
        'printf "signature\\n"', "R66S_midline")),
    # ---- decode hole: invalid UTF-8 -> UnicodeDecodeError escapes ----
    "syn_decode_inlife": (naive_run, sh_child(
        f'echo "{SIG}"; printf "\\377\\376\\n"')),
    "syn_decode_postdeath": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_decode")),
    # ---- critic-bound reproductions on real pipes ----
    # CE-1a: line-scan-absorbed line carrying a Parse Error: blob token.
    "syn_ce1a_parse_tail": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_ce1a_parse_tail")),
    # CE-1b: Parse Error: fabricated at the seam — zero ERROR: lines yet
    # the record rejects (blob channel independent of the line scan).
    "syn_ce1b_parse_seam": (split_run, ["/usr/bin/sh", "-c",
        'echo R66 child_pid=$$; '
        f'printf "{SIG}\\nends in Parse Err"; '
        'printf "or: R66 spliced parse clause\\n" >&2; exit 0']),
    # CE-2 residual-fragment matrix cells.
    "syn_ce2_scr_ipt": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_ce2_scr_ipt")),
    "syn_ce2_script_sp": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_ce2_script_sp")),
    "syn_ce2_parse_split": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_ce2_parse_split")),
    "syn_ce2_error_headsplit": (naive_run, sh_child(
        f'echo "{SIG}"', "R66S_ce2_error_headsplit")),
    # attack-4 composite: evasion + allowlisted fabrication in one record.
    "syn_double_forge": (split_run, sh_child(
        f'echo "{SIG}"', "R66S_double_forge")),
    # ---- real Godot children: author's worktree fixture arms ----
    "g_genuine": (naive_run, godot_cmd()),
    "g_errforge_release": (naive_run, godot_cmd("--spawn-errforge-release")),
    "g_emit_errforge": (naive_run, godot_cmd("--emit-errforge")),
    "g_allowforge": (naive_run, godot_cmd("--spawn-allowforge")),
    "g_splitforge": (naive_run, godot_cmd("--spawn-splitforge")),
    "g_seamforge": (split_run, godot_cmd("--spawn-seamforge")),
    "g_midlineforge": (naive_run, godot_cmd("--spawn-midlineforge")),
}

ARM_ALLOWLISTS = {
    "syn_allowforge_exact": ((), (ALLOW_EXACT,), (FOREIGN,)),
    "syn_allowforge_exact_padded": ((), (ALLOW_EXACT,), (FOREIGN,)),
    "syn_allowforge_twin": ((), (ALLOW_EXACT,), (FOREIGN,)),
    "syn_allowforge_comma_tail": ((), (ALLOW_COMMA,), (FOREIGN,)),
    "syn_allowforge_comma_dbl": ((), (ALLOW_COMMA,), (FOREIGN,)),
    "syn_allowforge_comma_atcomma": ((), (ALLOW_COMMA,), (FOREIGN,)),
    "syn_allowforge_comma2_tail": ((), (ALLOW_COMMA2,), (FOREIGN,)),
    "syn_allowforge_structured": ((), (ALLOW_CHAIN,), (FOREIGN,)),
    "syn_allowforge_structured_missing": ((), (ALLOW_CHAIN,), (FOREIGN,)),
    "syn_ce1a_parse_tail": ((), (ALLOW_COMMA,), (FOREIGN,)),
    "syn_double_forge": ((), (ALLOW_EXACT,), (FOREIGN,)),
    "g_allowforge": ((), (ALLOW_EXACT,), (FOREIGN,)),
}
ARM_SIG = {a: GMARK for a in ARMS if a.startswith("g_")}

REPS_SYN = 3
REPS_GODOT = 3

# ------------------------------------------------------------------ census
AUTHOR_RECEIPT = (REPO / "live" / "r66-author" / "runs" /
                  "20261014T051301624764Z" / "verdicts.json")


def census():
    """Dead-entry census, independently replayed: verbatim allowed_error
    over the r66 author's own 99-row captured outputs (records now carry
    expected_errors). Also blob-clause hit counts."""
    payload = {"receipt": str(AUTHOR_RECEIPT), "rows_seen": 0,
               "entry_rows": [], "dead_entries_in_run": [],
               "clause_line_counts": {"SCRIPT ERROR:": 0, "Parse Error:": 0,
                                      "ERROR:_lines": 0,
                                      "objectdb_leak": 0},
               "notes": []}
    if not AUTHOR_RECEIPT.is_file():
        payload["notes"].append("author receipt missing")
        return payload
    data = json.loads(AUTHOR_RECEIPT.read_text())
    payload["receipt_verdict"] = data.get("verdict")
    for row in data["results"]:
        payload["rows_seen"] += 1
        out = row.get("output") or []
        for line in out:
            if "SCRIPT ERROR:" in line:
                payload["clause_line_counts"]["SCRIPT ERROR:"] += 1
            if "Parse Error:" in line:
                payload["clause_line_counts"]["Parse Error:"] += 1
            if "ERROR:" in line:
                payload["clause_line_counts"]["ERROR:_lines"] += 1
            if re.fullmatch(
                    r"WARNING: [1-9][0-9]* ObjectDB instances were leaked"
                    r" at exit(?: \(run with `--verbose` for details\)\.)?",
                    line.strip()):
                payload["clause_line_counts"]["objectdb_leak"] += 1
        entries = row.get("expected_errors") or []
        if not entries or not isinstance(out, list):
            continue
        text = "\n".join(out)
        recs = []
        for entry in entries:
            matched = [l.strip() for l in out if allowed_error(l, entry)]
            shape = ("structured" if entry == "ERROR: chain incomplete"
                     else "comma_prefix" if entry.endswith(",") else "exact")
            via = None
            if matched:
                s = matched[0]
                via = ("exact" if s == entry else
                       "comma_prefix" if entry.endswith(",") else
                       "structured")
            recs.append({"entry": entry, "shape": shape,
                         "matched_lines": len(matched),
                         "first_match": matched[0] if matched else None,
                         "match_branch": via,
                         "dead_in_run": not matched})
        bare = not classify_process(row["actual_exit"], row["error"], text,
                                    row["expected_exit"], row["signature"],
                                    ())
        listed = classify_process(row["actual_exit"], row["error"], text,
                                  row["expected_exit"], row["signature"],
                                  tuple(entries))
        payload["entry_rows"].append({
            "case": row["case"], "verdict": row["verdict"],
            "entries": recs,
            "any_entry_matched": any(not e["dead_in_run"] for e in recs),
            "bare_classification_rejects": bare,
            "allowlisted_classification_passes": listed})
        for e in recs:
            if e["dead_in_run"]:
                payload["dead_entries_in_run"].append(
                    {"case": row["case"], "entry": e["entry"],
                     "shape": e["shape"]})
    return payload


def boundary_units():
    """Cheap synthetic geometry probes through the verbatim classifier —
    documents the clause alphabet the real-pipe arms exercise."""
    base = f"{SIG}\n"
    bounds = ["\n", "\r", "\r\n", "\v", "\f", "\x1c", "\x1d", "\x1e",
              "\x85", "\u2028", "\u2029"]
    rows = []
    for b in bounds:
        text = base + "ERR" + b + "OR: unit boundary probe\n"
        rows.append({"boundary": b.encode("unicode_escape").decode(),
                     "line_count": len(text.splitlines()),
                     "no_error_line": not any(
                         "ERROR:" in l for l in text.splitlines()),
                     "halves_captured": ("ERR" in text
                                         and "OR:" in text),
                     "verdict": classify_process(0, None, text, 0, SIG)})
    # \x1f (unit separator) is NOT a splitlines boundary but still breaks
    # the substring contiguity — evasion without a split.
    text = base + "ERR\x1fOR: unit-separator probe\n"
    rows.append({"boundary": "\\x1f", "line_count": len(text.splitlines()),
                 "no_error_line": not any(
                     "ERROR:" in l for l in text.splitlines()),
                 "halves_captured": ("ERR" in text and "OR:" in text),
                 "verdict": classify_process(0, None, text, 0, SIG)})
    # blob-clause geometry: for newline-free patterns `p in blob` is
    # equivalent to `any(p in line)` — verified identity holds here.
    for p in ("SCRIPT ERROR:", "Parse Error:"):
        blob = base + "noise " + p + " tail\nsecond line\n"
        rows.append({"boundary": f"blob_equiv:{p}",
                     "in_blob": p in blob,
                     "in_some_line": any(p in l for l in
                                         blob.splitlines()),
                     "verdict": classify_process(0, None, blob, 0, SIG)})
    return rows


def main():
    records = []
    for arm, (fn, cmd) in ARMS.items():
        reps = REPS_GODOT if arm.startswith("g_") else REPS_SYN
        allowlists = ARM_ALLOWLISTS.get(arm, ((),))
        signature = ARM_SIG.get(arm, SIG)
        for rep in range(reps):
            rec = fn(cmd, f"{arm}#{rep}", allowlists=allowlists,
                     signature=signature)
            rec["arm"], rec["rep"] = arm, rep
            print(f"{arm:36s} rep={rep} exit={rec['actual_exit']} "
                  f"exc={str(rec['run_exception'])[:28]:28s} "
                  f"sig={rec['clauses']['sig_present']!s:5s} "
                  f"errln={len(rec['clauses']['error_lines'])} "
                  f"v={ {k[:18]: v for k, v in rec['verdicts_by_allowlist'].items()} } "
                  f"wppid={rec.get('write_ppid')}", flush=True)
            records.append(rec)
            (RAW / f"{arm}-{rep}.stdout").write_text(
                "\n".join(rec["output_lines"]) + "\n")
    payload = {
        "runner": str(RUNNER), "runner_sha256_worktree": RUNNER_SHA,
        "runner_sha256_head_blob": HEAD_SHA,
        "segment_sha256": seg_sha,
        "segment_equal_head_vs_worktree": seg_equal,
        "extraction": "ast.get_source_segment verbatim exec of "
                      "run_process/classify_process/classify_streams/"
                      "classify_audio_process",
        "signature_syn": SIG, "signature_godot": GMARK,
        "godot": GODOT, "proj": str(PROJ),
        "fixture_sha256": hashlib.sha256(
            (PROJ / "descendant_pipe_probe.gd").read_bytes()).hexdigest(),
        "desc_script_sha256": desc_sha,
        "allowlists_under_test": {"exact": ALLOW_EXACT,
                                  "comma": ALLOW_COMMA,
                                  "comma2": ALLOW_COMMA2,
                                  "structured": ALLOW_CHAIN,
                                  "foreign": FOREIGN},
        "records": records,
        "boundary_units": boundary_units(),
        "census": census()}
    out = HERE / "surface-verdicts.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {out} ({len(records)} runs)")


if __name__ == "__main__":
    main()
