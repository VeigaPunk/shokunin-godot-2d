#!/usr/bin/env python3
"""r67 scribe: independent classify_streams-vs-classify_process divergence map.

Drives the VERBATIM production classifiers (ast.get_source_segment-extracted
from the worktree run_battery.py, sha-pinned against the HEAD blob) over real
captured per-stream pipe bytes — synthetic python children plus real Godot
runs of the shipped stream_attribution_probe.gd. Every record stores raw
stdout/stderr captures and BOTH verdicts. Never feeds the classifiers strings.
"""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                      # corpus/live/r67-scribe
REPO = HERE.parent.parent.parent                            # repo root
RUNNER = REPO / "corpus" / "fixtures" / "run_battery.py"
FIXTURES = REPO / "corpus" / "fixtures"
GODOT = os.environ.get("GODOT", "/usr/bin/godot")
RAW = HERE / "raw"
PROJ = HERE / "proj"
REPS = 2


def sha(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def extract_segment(tree_source, func_name):
    tree = ast.parse(tree_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.get_source_segment(tree_source, node)
    raise KeyError(func_name)


# --- verbatim classifier extraction: worktree bytes + HEAD blob ---------------
wt_src = RUNNER.read_text()
head_src = subprocess.run(["git", "-C", str(REPO), "show",
                           "HEAD:corpus/fixtures/run_battery.py"],
                          capture_output=True, text=True, check=True).stdout
names = ["run_process", "classify_process", "classify_streams", "classify_audio_process"]
segments = {}
for n in names:
    seg_wt = extract_segment(wt_src, n)
    seg_head = extract_segment(head_src, n)
    segments[n] = {"worktree_sha256": sha(seg_wt), "head_sha256": sha(seg_head),
                   "identical": seg_wt == seg_head}
ns = {"subprocess": subprocess}
for n in names:
    exec(compile(extract_segment(wt_src, n), n, "exec"), ns)
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]

runner_sha = sha(RUNNER.read_bytes())
head_runner_sha = sha(head_src)

# --- scratch project for Godot arms (mirrors run_battery.py copy semantics) ---
if PROJ.exists():
    shutil.rmtree(PROJ)
PROJ.mkdir()
for item in FIXTURES.iterdir():
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, PROJ / item.name)
    else:
        shutil.copy2(item, PROJ / item.name)
proj_text = (PROJ / "project.godot").read_text()
proj_text = proj_text.replace('config/name="MechanicOneShotTest"',
                              'config/name="MechanicOneShotTest-r67-scribe"', 1)
(PROJ / "project.godot").write_text(proj_text)
proj_sha = sha(PROJ.joinpath("stream_attribution_probe.gd").read_bytes())


# --- real-pipe per-stream capture ----------------------------------------------
def capture(command, timeout=8, env=None):
    """Real subprocess, separate pipes; returns (stdout, stderr, code, error)."""
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, env=env)
        out, err = proc.communicate(timeout=timeout)
        return out, err, proc.returncode, None
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=3)
        return out, err, proc.returncode, "TIMEOUT"
    except OSError as exc:
        return "", str(exc), None, f"launch error: {exc}"


SIG = "STREAM_STDOUT: expected attribution marker"
SIG_H = len(SIG) // 2  # seam split point for the signature token


def py(script):
    return [sys.executable, "-c", script]


# Synthetic arms: controlled per-stream bytes on real OS pipes.
# Each arm: (name, command, expected_exit, signature, allowed_errors, allowed_stderr)
ARMS = [
    # control: clean single-stream signature
    ("s_clean_sig_stdout",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n')"), 0, SIG, (), ()),
    # headline: stdout-carried ERROR: — merged rejects, streams absorbs
    ("s_stdout_error",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: planted on stdout\\n')"), 0, SIG, (), ()),
    # stderr-carried ERROR: — both reject
    ("s_stderr_error",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('ERROR: planted on stderr\\n')"),
     0, SIG, (), ()),
    # stderr ERROR: under matching allowlists — both absorb
    ("s_stderr_error_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('ERROR: planted on stderr\\n')"),
     0, SIG, ("ERROR: planted on stderr",), ("ERROR: planted on stderr",)),
    # stdout ERROR: under a stderr-only allowlist — streams absorbs w/o consulting
    ("s_stdout_error_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: planted on stdout\\n')"),
     0, SIG, ("ERROR: planted on stdout",), ("ERROR: planted on stdout",)),
    # stdout ERROR: w/ foreign allowlist — still absorbed by streams
    ("s_stdout_error_foreign_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: planted on stdout\\n')"),
     0, SIG, ("ERROR: foreign",), ("ERROR: foreign",)),
    # stderr NON-ERROR noise — merged ignores (no ERROR: token), streams rejects
    ("s_stderr_nonerror_noise",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('WARNING: nondiagnostic noise\\n')"),
     0, SIG, (), ()),
    # stderr blank line only — both pass (streams skips empty lines)
    ("s_stderr_blank",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('\\n')"), 0, SIG, (), ()),
    # signature on STDERR only — merged sees it (concat), streams blind
    ("s_sig_on_stderr",
     py(f"import sys; sys.stdout.write('noise on stdout\\n'); sys.stderr.write({SIG!r}+'\\n')"),
     0, SIG, (), ()),
    # signature split across the merge seam: stdout tail + stderr head
    ("s_sig_seam_out_tail_err_head",
     py(f"import sys; sys.stdout.write({SIG[:SIG_H]!r}); sys.stdout.flush(); "
        f"sys.stderr.write({SIG[SIG_H:]!r}+'\\n')"),
     0, SIG, (), ()),
    # signature split stdout-head...stderr-tail — order broken in merged too
    ("s_sig_seam_err_tail_out_head",
     py(f"import sys; sys.stdout.write({SIG[:SIG_H]!r}+'\\ntrailer\\n'); sys.stdout.flush(); "
        f"sys.stderr.write('lead\\n'+{SIG[SIG_H:]!r})"),
     0, SIG, (), ()),
    # SCRIPT ERROR: on each channel — both reject (streams scans both streams)
    ("s_script_error_stdout",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nSCRIPT ERROR: boom\\n')"), 0, SIG, (), ()),
    ("s_script_error_stderr",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('SCRIPT ERROR: boom\\n')"),
     0, SIG, (), ()),
    ("s_parse_error_stderr",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('Parse Error: boom\\n')"),
     0, SIG, (), ()),
    # ERROR: fabricated at the merge seam (stdout tail 'ERR' + stderr head 'OR: ...')
    ("s_error_seam_out_err",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERR'); sys.stdout.flush(); "
        f"sys.stderr.write('OR: seamed at merge\\n')"),
     0, SIG, (), ()),
    # streams-side evasion probe: 'ERR\nOR:' inside stderr only — streams rejects
    # ANY non-allowlisted stderr line, evasion is moot
    ("s_stderr_split_error_evasion",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('ERR\\nOR: split inside stderr\\n')"),
     0, SIG, (), ()),
    # comma-prefix allowlist on stderr — both absorb tailed line
    ("s_stderr_prefix_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); "
        f"sys.stderr.write('ERROR: PREFIX, tail=anything\\n')"),
     0, SIG, ("ERROR: PREFIX,",), ("ERROR: PREFIX,",)),
    # comma-prefix allowlist entry vs matching line on STDOUT — merged absorbs,
    # streams never consults the list (stdout unscanned)
    ("s_stdout_prefix_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: PREFIX, tail=anything\\n')"),
     0, SIG, ("ERROR: PREFIX,",), ("ERROR: PREFIX,",)),
    # exit-code mismatch — both reject
    ("s_wrong_exit",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); raise SystemExit(1)"), 0, SIG, (), ()),
    # ERROR: on BOTH streams
    ("s_both_streams_error",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: out\\n'); sys.stderr.write('ERROR: err\\n')"),
     0, SIG, (), ()),
    # SCRIPT ERROR: blob clause fabricated at the merge seam — streams scans
    # each stream separately so the fabricated token exists in NEITHER
    ("s_script_error_seam",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nSCRIPT ERR'); sys.stdout.flush(); "
        f"sys.stderr.write('OR: blob forged at seam\\n')"),
     0, SIG, (), ()),
    # stderr mix: one allowlisted line + one unallowlisted — merged absorbs
    # the ERROR: line and ignores the noise; streams rejects the noise
    ("s_stderr_allowed_plus_noise",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); "
        f"sys.stderr.write('ERROR: planted on stderr\\nWARNING: extra noise\\n')"),
     0, SIG, ("ERROR: planted on stderr",), ("ERROR: planted on stderr",)),
    # structured allowlist entry — merged-only shape: classify_process's
    # allowed_error has the 'chain incomplete' special case (:168-171);
    # classify_streams' line_allowed implements exact + ','-prefix ONLY
    ("s_stderr_structured_entry",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); "
        f"sys.stderr.write('ERROR: chain incomplete collections=z scene=SceneB:<Node#9> old_alive=false\\n')"),
     0, SIG, ("ERROR: chain incomplete",), ("ERROR: chain incomplete",)),
    # allowlisted stderr fragment completes a fabricated ERROR: seam line —
    # merged rejects the phantom line; streams accepts the exempted stderr line
    ("s_seam_error_head_allowlisted",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\ntail ends in ERROR'); sys.stdout.flush(); "
        f"sys.stderr.write(': phantom seam line\\n')"),
     0, SIG, (), (": phantom seam line",)),
    # same geometry with the SCRIPT ERROR: blob token
    ("s_seam_script_head_allowlisted",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\ntail ends in SCRIPT ERR'); sys.stdout.flush(); "
        f"sys.stderr.write('OR: blob\\n')"),
     0, SIG, (), ("OR: blob",)),
    # stderr-carried signature under an allowlist that exempts it — the
    # exemption clears the stderr gate but cannot move the signature to stdout
    ("s_sig_on_stderr_allowlisted",
     py(f"import sys; sys.stdout.write('noise on stdout\\n'); "
        f"sys.stderr.write({SIG!r}+'\\n')"),
     0, SIG, (), (SIG,)),
]

# Godot arms: the shipped fixture, real engine bytes.
GODOT_SCRIPT = "res://stream_attribution_probe.gd"
GODOT_ARMS = [
    ("g_stream_accept", [GODOT, "--headless", "--path", str(PROJ),
                         "--script", GODOT_SCRIPT, "--"], 0, SIG, (), ()),
    ("g_stream_reject", [GODOT, "--headless", "--path", str(PROJ),
                         "--script", GODOT_SCRIPT, "--", "--stderr-unrelated"],
     0, SIG, (), ()),
]

records = []
for rep in range(REPS):
    for name, command, expected_exit, signature, allow_m, allow_s in ARMS + GODOT_ARMS:
        out, err, code, error = capture(command)
        merged = out + err
        v_merged = classify_process(code, error, merged, expected_exit, signature, allow_m)
        v_streams = classify_streams(code, error, out, err, expected_exit, signature,
                                     allowed_stderr=allow_s)
        rec = {"arm": name, "rep": rep, "command": command,
               "expected_exit": expected_exit, "actual_exit": code, "error": error,
               "signature": signature,
               "allowed_errors": list(allow_m), "allowed_stderr": list(allow_s),
               "raw_stdout": out, "raw_stderr": err,
               "stdout_lines": out.splitlines(), "stderr_lines": err.splitlines(),
               "merged_len": len(merged),
               "signature_in_stdout": signature in out,
               "signature_in_stderr": signature in err,
               "signature_in_merged": signature in merged,
               "error_token_in_stdout": "ERROR:" in out,
               "error_token_in_stderr": "ERROR:" in err,
               "verdict_merged": v_merged, "verdict_streams": v_streams,
               "divergent": v_merged != v_streams}
        records.append(rec)
        tag = "DIVERGE" if rec["divergent"] else "agree  "
        print(f"{tag} rep{rep} {name}: merged={v_merged} streams={v_streams} "
              f"exit={code} sig(out/err/mer)={rec['signature_in_stdout']}/"
              f"{rec['signature_in_stderr']}/{rec['signature_in_merged']}", flush=True)
        (RAW / f"{name}.rep{rep}.stdout").write_text(out)
        (RAW / f"{name}.rep{rep}.stderr").write_text(err)

# Rep-stability check
by_arm = {}
for r in records:
    by_arm.setdefault(r["arm"], []).append((r["verdict_merged"], r["verdict_streams"]))
stable = all(len(set(v)) == 1 for v in by_arm.values())

divergent_arms = sorted({r["arm"] for r in records if r["divergent"]})
payload = {
    "mode": "r67_scribe_stream_divergence",
    "runner_sha256": runner_sha, "head_runner_sha256": head_runner_sha,
    "runner_worktree_eq_head": runner_sha == head_runner_sha,
    "classifier_segments": segments,
    "fixture_probe_sha256": proj_sha, "godot": GODOT, "python": sys.version.split()[0],
    "reps": REPS, "arm_count": len(ARMS) + len(GODOT_ARMS),
    "rep_stable": stable,
    "divergent_arms": divergent_arms,
    "divergent_count": len(divergent_arms),
    "records": records,
}
out_path = HERE / "stream-verdicts.json"
out_path.write_text(json.dumps(payload, indent=2) + "\n")
print(f"\nwrote {out_path}")
print(f"rep_stable={stable} divergent_arms={divergent_arms}")
