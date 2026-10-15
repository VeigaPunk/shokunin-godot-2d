#!/usr/bin/env python3
"""r68 reviewer: independent re-derivation of the r67 divergence map.

Audits COMMITTED code: both classifiers are ast.get_source_segment-extracted
from `git show HEAD:corpus/fixtures/run_battery.py` (never the worktree file),
exec'd, and driven over real subprocess pipes. Arm enumeration mirrors the
committed r67-scribe enumeration (26 synthetic + 2 Godot = 28) plus two
direction-B seam arms added by me to test the adjudicator's "seam is
one-position (stdout-tail|stderr-head)" claim. Synthetic children are real
OS pipes; Godot arms run the shipped fixture in a copied scratch project
(the battery's own copy semantics). Writes only inside corpus/live/r68-reviewer/.
"""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent                      # corpus/live/r68-reviewer
REPO = HERE.parent.parent.parent                            # repo root
GODOT = os.environ.get("GODOT", "/usr/bin/godot")
RAW = HERE / "raw"
PROJ = HERE / "proj"
RAW.mkdir(exist_ok=True)
REPS = 2


def sha(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


# --- verbatim extraction from the COMMITTED blob ------------------------------
head_src = subprocess.run(["git", "-C", str(REPO), "show",
                           "HEAD:corpus/fixtures/run_battery.py"],
                          capture_output=True, text=True, check=True).stdout
tree = ast.parse(head_src)
segments = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in (
            "run_process", "classify_process", "classify_streams"):
        segments[node.name] = ast.get_source_segment(head_src, node)
assert set(segments) == {"run_process", "classify_process", "classify_streams"}
ns = {"subprocess": subprocess}
for n, seg in segments.items():
    exec(compile(seg, n, "exec"), ns)
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]
seg_shas = {n: sha(s) for n, s in segments.items()}

# --- scratch Godot project (mirrors run_battery.py copy semantics) ------------
FIXTURES = REPO / "corpus" / "fixtures"
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
pt = (PROJ / "project.godot").read_text()
(PROJ / "project.godot").write_text(
    pt.replace('config/name="MechanicOneShotTest"',
               'config/name="MechanicOneShotTest-r68-reviewer"', 1))
proj_probe_sha = sha((PROJ / "stream_attribution_probe.gd").read_bytes())


def capture(command, timeout=8):
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate(timeout=timeout)
        return out, err, proc.returncode, None
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate(timeout=3)
        return out, err, proc.returncode, "TIMEOUT"
    except OSError as exc:
        return "", str(exc), None, f"launch error: {exc}"


SIG = "STREAM_STDOUT: expected attribution marker"
SIG_H = len(SIG) // 2


def py(script):
    return [sys.executable, "-c", script]


# Same enumeration as the committed r67-scribe artifact (26 + 2), then my
# direction-B additions (prefix r68_).
ARMS = [
    ("s_clean_sig_stdout",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n')"), 0, SIG, (), ()),
    ("s_stdout_error",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: planted on stdout\\n')"), 0, SIG, (), ()),
    ("s_stderr_error",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('ERROR: planted on stderr\\n')"),
     0, SIG, (), ()),
    ("s_stderr_error_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('ERROR: planted on stderr\\n')"),
     0, SIG, ("ERROR: planted on stderr",), ("ERROR: planted on stderr",)),
    ("s_stdout_error_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: planted on stdout\\n')"),
     0, SIG, ("ERROR: planted on stdout",), ("ERROR: planted on stdout",)),
    ("s_stdout_error_foreign_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: planted on stdout\\n')"),
     0, SIG, ("ERROR: foreign",), ("ERROR: foreign",)),
    ("s_stderr_nonerror_noise",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('WARNING: nondiagnostic noise\\n')"),
     0, SIG, (), ()),
    ("s_stderr_blank",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('\\n')"), 0, SIG, (), ()),
    ("s_sig_on_stderr",
     py(f"import sys; sys.stdout.write('noise on stdout\\n'); sys.stderr.write({SIG!r}+'\\n')"),
     0, SIG, (), ()),
    ("s_sig_seam_out_tail_err_head",
     py(f"import sys; sys.stdout.write({SIG[:SIG_H]!r}); sys.stdout.flush(); "
        f"sys.stderr.write({SIG[SIG_H:]!r}+'\\n')"),
     0, SIG, (), ()),
    ("s_sig_seam_err_tail_out_head",
     py(f"import sys; sys.stdout.write({SIG[:SIG_H]!r}+'\\ntrailer\\n'); sys.stdout.flush(); "
        f"sys.stderr.write('lead\\n'+{SIG[SIG_H:]!r})"),
     0, SIG, (), ()),
    ("s_script_error_stdout",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nSCRIPT ERROR: boom\\n')"), 0, SIG, (), ()),
    ("s_script_error_stderr",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('SCRIPT ERROR: boom\\n')"),
     0, SIG, (), ()),
    ("s_parse_error_stderr",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('Parse Error: boom\\n')"),
     0, SIG, (), ()),
    ("s_error_seam_out_err",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERR'); sys.stdout.flush(); "
        f"sys.stderr.write('OR: seamed at merge\\n')"),
     0, SIG, (), ()),
    ("s_stderr_split_error_evasion",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); sys.stderr.write('ERR\\nOR: split inside stderr\\n')"),
     0, SIG, (), ()),
    ("s_stderr_prefix_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); "
        f"sys.stderr.write('ERROR: PREFIX, tail=anything\\n')"),
     0, SIG, ("ERROR: PREFIX,",), ("ERROR: PREFIX,",)),
    ("s_stdout_prefix_allowed",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: PREFIX, tail=anything\\n')"),
     0, SIG, ("ERROR: PREFIX,",), ("ERROR: PREFIX,",)),
    ("s_wrong_exit",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); raise SystemExit(1)"), 0, SIG, (), ()),
    ("s_both_streams_error",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nERROR: out\\n'); sys.stderr.write('ERROR: err\\n')"),
     0, SIG, (), ()),
    ("s_script_error_seam",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\nSCRIPT ERR'); sys.stdout.flush(); "
        f"sys.stderr.write('OR: blob forged at seam\\n')"),
     0, SIG, (), ()),
    ("s_stderr_allowed_plus_noise",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); "
        f"sys.stderr.write('ERROR: planted on stderr\\nWARNING: extra noise\\n')"),
     0, SIG, ("ERROR: planted on stderr",), ("ERROR: planted on stderr",)),
    ("s_stderr_structured_entry",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\n'); "
        f"sys.stderr.write('ERROR: chain incomplete collections=z scene=SceneB:<Node#9> old_alive=false\\n')"),
     0, SIG, ("ERROR: chain incomplete",), ("ERROR: chain incomplete",)),
    ("s_seam_error_head_allowlisted",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\ntail ends in ERROR'); sys.stdout.flush(); "
        f"sys.stderr.write(': phantom seam line\\n')"),
     0, SIG, (), (": phantom seam line",)),
    ("s_seam_script_head_allowlisted",
     py(f"import sys; sys.stdout.write({SIG!r}+'\\ntail ends in SCRIPT ERR'); sys.stdout.flush(); "
        f"sys.stderr.write('OR: blob\\n')"),
     0, SIG, (), ("OR: blob",)),
    ("s_sig_on_stderr_allowlisted",
     py(f"import sys; sys.stdout.write('noise on stdout\\n'); "
        f"sys.stderr.write({SIG!r}+'\\n')"),
     0, SIG, (), (SIG,)),
    # --- r68 reviewer additions: direction-B seam (stderr tail | stdout head) --
    # Under the runner's fixed stdout+stderr concat these fragments sit at the
    # merged blob's OPPOSITE ends: the 'ERR' tail cannot meet the 'OR:' head.
    ("r68_err_seam_err_tail_out_head",
     py(f"import sys; sys.stdout.write('OR: head frag\\n'+{SIG!r}+'\\n'); sys.stdout.flush(); "
        f"time=__import__('time'); sys.stderr.write('tail ends in ERR'); sys.stderr.flush(); time.sleep(0.05)"),
     0, SIG, (), ()),
    # direction-B signature seam: stderr tail holds sig tail, stdout head holds
    # sig head, separated by other stdout bytes — no contiguity anywhere.
    ("r68_sig_seam_err_tail_out_head",
     py(f"import sys; sys.stdout.write({SIG[:SIG_H]!r}+'\\nmid\\n'); sys.stdout.flush(); "
        f"sys.stderr.write('lead\\n'+{SIG[SIG_H:]!r})"),
     0, SIG, (), ()),
]

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
        rec = {"arm": name, "rep": rep, "expected_exit": expected_exit,
               "actual_exit": code, "error": error,
               "allowed_errors": list(allow_m), "allowed_stderr": list(allow_s),
               "signature_in_stdout": signature in out,
               "signature_in_stderr": signature in err,
               "signature_in_merged": signature in merged,
               "error_token_in_stdout": "ERROR:" in out,
               "error_token_in_stderr": "ERROR:" in err,
               "merged_error_lines": [l for l in merged.splitlines() if "ERROR:" in l],
               "verdict_merged": v_merged, "verdict_streams": v_streams,
               "divergent": v_merged != v_streams}
        records.append(rec)
        print(f"{'DIVERGE' if rec['divergent'] else 'agree  '} rep{rep} {name}: "
              f"merged={v_merged} streams={v_streams} exit={code} err={error}", flush=True)
        (RAW / f"{name}.rep{rep}.stdout").write_text(out)
        (RAW / f"{name}.rep{rep}.stderr").write_text(err)

by_arm = {}
for r in records:
    by_arm.setdefault(r["arm"], []).append((r["verdict_merged"], r["verdict_streams"]))
stable = all(len(set(v)) == 1 for v in by_arm.values())
divergent = sorted(a for a, v in by_arm.items() if len({x != y for x, y in v}) and any(x != y for x, y in v))
divergent = sorted({r["arm"] for r in records if r["divergent"]})

payload = {
    "mode": "r68_reviewer_divergence_rederivation",
    "head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                           capture_output=True, text=True).stdout.strip(),
    "classifier_segment_sha256_from_HEAD_blob": seg_shas,
    "probe_fixture_sha256_worktree_copy": proj_probe_sha,
    "godot": GODOT, "python": sys.version.split()[0],
    "reps": REPS, "arm_count": len(ARMS) + len(GODOT_ARMS),
    "rep_stable": stable,
    "divergent_arms": divergent, "divergent_count": len(divergent),
    "records": records,
}
(HERE / "divergence-rederive.json").write_text(json.dumps(payload, indent=2) + "\n")
print(f"\nwrote {HERE/'divergence-rederive.json'}")
print(f"rep_stable={stable} divergent={len(divergent)} {divergent}")
