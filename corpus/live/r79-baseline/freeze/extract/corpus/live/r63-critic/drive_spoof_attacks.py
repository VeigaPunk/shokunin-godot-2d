#!/usr/bin/env python3
"""r63-critic adversarial driver (scratch-only; independent reproduction).

Verbatim-extracts run_process + classify_process + classify_streams from the
tracked corpus/fixtures/run_battery.py (WORKTREE = the landed r63 diff) via
ast.get_source_segment and attacks the claimed signature-spoof boundary:

  attack (a) - does the release-before-bound arm really classify True, or is
      there a hidden liveness guard?  Also: does the forged marker still
      accept when written to stderr only, at mid-hold release, or against a
      nonzero expected-exit (negative-signature) tuple?
  attack (b) - merged vs split streams: classify_process judges
      stdout+stderr concatenated; classify_streams requires stdout. Mutants
      write the forged signature to fd2 to test which check matters.
  attack (c) - ordering/buffering: an UNGATED descendant writes the marker
      ~0.05s post-spawn (pre-death) with the HONEST ppid, and a LYING
      variant prints write_ppid=1 — is the write_ppid discrimination
      self-reported and slip-able?
  attack (d) - forgeability of the discriminating fields: a live-child arm
      tries to produce timed_out + child_exit_at_timeout==0 (kernel poll —
      expected reject), a GENUINE-marker hold arm tests whether
      timed_out/child_exit_at_timeout separate forged from genuine at all,
      and a double-write arm tests whether "descendant-authored" is
      record-provable.

Meta arms replicate the author's bounded-Popen block verbatim (Popen +
communicate(timeout); on TimeoutExpired: poll() -> child_exit_at_timeout,
close streams, wait/kill) and evaluate the eight landed spoof
discriminations verbatim per arm.
"""
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = (HERE.parent.parent / "fixtures" / "run_battery.py").resolve()
GODOT = "godot"
PROJ = HERE / "proj"
RAW = HERE / "raw"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
PPID_RE = r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)"
BOUND = 3.0          # meta bound
CASES_BOUND = 8.0    # CASES bound used by execute()


def extract_runner_functions(runner_path):
    src = runner_path.read_text()
    tree = ast.parse(src)
    want = ("run_process", "classify_process", "classify_streams")
    segs = {}

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef) and child.name in want:
                seg = ast.get_source_segment(src, child)
                assert seg, f"no source segment for {child.name}"
                segs[child.name] = seg
            walk(child)

    walk(tree)
    assert set(segs) == set(want), segs.keys()
    ns = {"subprocess": subprocess}
    for n in want:
        exec(segs[n], ns)
    return ns["run_process"], ns["classify_process"], ns["classify_streams"], segs


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


def proc_stat(pid):
    """(state, ppid) from /proc, comm-safe."""
    if pid is None or pid <= 0:
        return (None, None)
    try:
        text = Path(f"/proc/{pid}/stat").read_text()
        rest = text[text.rindex(")") + 2:].split()
        return (rest[0], int(rest[1]))
    except (OSError, ValueError, IndexError):
        return (None, None)


def parse_ids(output):
    godot = re.search(r"(?:DESCENDANT_PIPE|SIG_SPOOF) godot_pid= *(\d+)", output or "")
    spawned = re.search(r"(?:DESCENDANT_PIPE|SIG_SPOOF) spawned_pid= *(\d+)", output or "")
    wpp = re.search(PPID_RE, output or "")
    return (int(godot.group(1)) if godot else None,
            int(spawned.group(1)) if spawned else None,
            int(wpp.group(1)) if wpp else None)


def output_shape(output):
    """Line list plus marker position evidence — the output-content
    discriminators the claim ignores."""
    lines = (output or "").strip().splitlines()
    return {"lines": lines,
            "marker_index": next((i for i, l in enumerate(lines) if MARKER in l), None),
            "line_count": len(lines),
            "withheld_banner": "child_signature=withheld" in (output or "")}


def run_cases_arm(run_process, classify_process, classify_streams, name, script,
                  flags, bound, expected_exit=0, signature=MARKER, allowed=()):
    """CASES-path arm: verbatim subprocess.run shape + verbatim classify."""
    command = [GODOT, "--headless", "--path", str(PROJ), "--script",
               "res://" + script, "--", *flags]
    started = time.monotonic()
    output, code, error = run_process(command, bound)
    elapsed = time.monotonic() - started
    (RAW / f"{name}.stdout").write_text(output or "")
    godot_pid, desc_pid, wpp = parse_ids(output)
    # stream view: rerun is NOT possible for the same process; instead note
    # that run_process merges stdout+stderr — see meta arms for split view.
    rec = {
        "case": name, "command": command, "bound_seconds": bound,
        "expected_exit": expected_exit, "actual_exit": code, "error": error,
        "elapsed_seconds": round(elapsed, 3),
        "signature": signature, "marker_observed": signature in (output or ""),
        "write_ppid": wpp, "godot_pid": godot_pid, "descendant_pid": desc_pid,
        "inner_classification": classify_process(code, error, output or "",
                                                 expected_exit, signature, allowed),
        "shape": output_shape(output),
        "godot_alive_at_return": pid_alive(godot_pid),
        "descendant_alive_at_return": pid_alive(desc_pid),
        "descendant_ppid_at_return": proc_stat(desc_pid)[1],
        "godot_state_at_return": proc_stat(godot_pid)[0],
    }
    print(f"{name}: exit={code} err={error!r} t={rec['elapsed_seconds']}s "
          f"classify={rec['inner_classification']} marker={rec['marker_observed']} "
          f"wpp={wpp} godot={godot_pid}", flush=True)
    return rec


def run_meta_arm(name, script, flags, bound=BOUND):
    """Verbatim replica of the landed probe_descendant_signature_spoof
    bounded-Popen block (same field names as the landed hold_arm record)."""
    command = [GODOT, "--headless", "--path", str(PROJ), "--script",
               "res://" + script, "--", *flags]
    rec = {"case": name, "bound_seconds": bound, "timed_out": False,
           "child_exit_at_timeout": None, "actual_exit": None, "error": None,
           "marker_observed": False, "write_ppid": None, "godot_pid": None,
           "descendant_pid": None, "godot_alive_at_return": None,
           "descendant_alive_at_return": None, "inner_classification": False}
    proc = None
    started = time.monotonic()
    text = ""
    out = err = ""
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            out, err = proc.communicate(timeout=bound)
            text = (out or "") + (err or "")
            rec["actual_exit"] = proc.returncode
        except subprocess.TimeoutExpired as exc:
            rec["timed_out"] = True
            rec["child_exit_at_timeout"] = proc.poll()
            out = (exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes)
                   else (exc.stdout or ""))
            err = (exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes)
                   else (exc.stderr or ""))
            text = out + err
            rec["error"] = f"TIMEOUT after {bound} seconds"
            for stream in (proc.stdout, proc.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    rec["error"] += "; post-kill wait timed out"
    except (OSError, ValueError) as exc:
        rec["error"] = f"launch/read error: {exc}"
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] = (rec["error"] or "") + "; forced cleanup timed out"
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["stdout_text"] = out or ""
    rec["stderr_text"] = err or ""
    rec["marker_on_stdout"] = MARKER in (out or "")
    rec["marker_on_stderr"] = MARKER in (err or "")
    rec["marker_observed"] = MARKER in text
    rec["shape"] = output_shape(text)
    godot_pid, desc_pid, wpp = parse_ids(text)
    rec["godot_pid"] = godot_pid
    rec["descendant_pid"] = desc_pid
    rec["write_ppid"] = wpp
    rec["godot_alive_at_return"] = pid_alive(godot_pid)
    rec["descendant_alive_at_return"] = pid_alive(desc_pid)
    # Kernel-side ppid of the (possibly live) descendant at return — the
    # check the landed meta does NOT perform (it trusts the printed line).
    rec["descendant_ppid_at_return"] = proc_stat(desc_pid)[1]
    rec["godot_state_at_return"] = proc_stat(godot_pid)[0]
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, MARKER)
    (RAW / f"{name}.merged").write_text(text)
    # hygiene: reap bounded orphaned descendants like the landed meta does
    if pid_alive(desc_pid):
        try:
            os.kill(desc_pid, 9)
        except OSError:
            pass
    print(f"{name}: timed_out={rec['timed_out']} child_exit={rec['child_exit_at_timeout']} "
          f"exit={rec['actual_exit']} marker={rec['marker_observed']} "
          f"(stdout={rec['marker_on_stdout']}/stderr={rec['marker_on_stderr']}) "
          f"wpp={wpp} inner={rec['inner_classification']}", flush=True)
    return rec


def eval_landed_discriminations(hold, forged, detached):
    """The eight landed spoof discriminations, verbatim, applied to given
    hold-arm / forged-release / detached-control records."""
    forged_output = "\n".join(forged["shape"]["lines"]) if forged else ""
    detached_output = "\n".join(detached["shape"]["lines"]) if detached else ""
    forged_godot = forged["godot_pid"] if forged else None
    forged_wpp = forged["write_ppid"] if forged else None
    return {
        "hold_timed_out_with_child_dead": (hold["timed_out"]
                                         and hold["child_exit_at_timeout"] == 0),
        "hold_forged_signature_captured": hold["marker_observed"],
        "hold_write_post_orphan": (hold["write_ppid"] is not None
                                   and hold["godot_pid"] is not None
                                   and hold["write_ppid"] != hold["godot_pid"]),
        "hold_rejects_via_timeout_axis_only": hold["inner_classification"] is False,
        "hold_descendant_orphaned_alive": hold["descendant_alive_at_return"] is True,
        "release_row_passes_on_forged_signature": (forged is not None
            and forged["inner_classification"] and forged["actual_exit"] == 0
            and forged["error"] is None and MARKER in forged_output),
        "release_write_post_orphan": (forged_wpp is not None
                                      and forged_godot is not None
                                      and forged_wpp != forged_godot),
        "release_shape_matches_genuine": (
            forged is not None and detached is not None
            and bool(forged["inner_classification"]) == bool(detached["inner_classification"])
            and forged["actual_exit"] == detached["actual_exit"] == 0
            and forged["error"] is None and detached["error"] is None
            and (MARKER in forged_output) == (MARKER in detached_output)),
    }


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    (run_process, classify_process, classify_streams, segs) = extract_runner_functions(RUNNER)
    # expose to run_meta_arm
    globals()["classify_process"] = classify_process
    env = {
        "godot_version": subprocess.run([GODOT, "--version"], capture_output=True,
                                        text=True).stdout.strip(),
        "python": sys.version.split()[0],
        "platform": subprocess.run(["uname", "-srvm"], capture_output=True,
                                   text=True).stdout.strip(),
        "runner": str(RUNNER),
        "runner_sha256_worktree": runner_sha,
        "sh": subprocess.run(["readlink", "-f", "/usr/bin/sh"], capture_output=True,
                             text=True).stdout.strip(),
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(env, indent=2), flush=True)

    results = {"cases_arms": [], "meta_arms": [], "discrimination_evals": {}}
    FIX = "descendant_pipe_probe.gd"
    MUT = "sig_spoof_probe.gd"

    # ---- reproduction: author's landed arms through the verbatim path ------
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "auth_forge_release_b8", FIX, ["--spawn-forge-release"], CASES_BOUND))
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "auth_forge_release_b3", FIX, ["--spawn-forge-release"], BOUND))
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "auth_detached_control", FIX, ["--spawn-detach"], CASES_BOUND))
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "auth_hold_as_cases_b8", FIX, ["--spawn-forge-hold"], CASES_BOUND))

    # ---- attack (a): hidden guards on the release-before-bound arm ---------
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "mut_forge_midhold_b8", MUT, ["--forge-midhold=1.2"], CASES_BOUND))
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "mut_forge_neg_exit_b8", MUT, ["--forge-neg-exit"], CASES_BOUND,
        expected_exit=2,
        signature="ERROR: SPOOFED NEGATIVE DIAGNOSTIC forged by descendant",
        allowed=("ERROR: SPOOFED NEGATIVE DIAGNOSTIC forged by descendant",)))

    # ---- attack (b): which stream does the forged write need? --------------
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "mut_forge_release_stderr_b8", MUT, ["--forge-release-stderr"], CASES_BOUND))

    # ---- attack (c): pre-death write ordering / self-reported ppid ---------
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "mut_forge_ungated_honest_b8", MUT, ["--forge-ungated-honest"], CASES_BOUND))
    results["cases_arms"].append(run_cases_arm(
        run_process, classify_process, classify_streams,
        "mut_forge_lying_ppid_b8", MUT, ["--forge-lying-ppid"], CASES_BOUND))

    # ---- meta-path arms (bounded Popen replica, author field names) --------
    meta_arms = {}
    meta_arms["auth_forge_hold"] = run_meta_arm(
        "auth_forge_hold", FIX, ["--spawn-forge-hold"])
    meta_arms["mut_genuine_hold"] = run_meta_arm(
        "mut_genuine_hold", MUT, ["--child-prints-marker", "--genuine-hold=6"])
    meta_arms["mut_double_forge_hold"] = run_meta_arm(
        "mut_double_forge_hold", MUT, ["--child-prints-marker", "--double-forge-hold=6"])
    meta_arms["mut_forge_livechild"] = run_meta_arm(
        "mut_forge_livechild", MUT, ["--forge-livechild", "--hang=30"])
    meta_arms["mut_stderr_hold"] = run_meta_arm(
        "mut_stderr_hold", MUT, ["--forge-stderr-hold=6"])
    meta_arms["mut_genuine_silent_hold"] = run_meta_arm(
        "mut_genuine_silent_hold", FIX, ["--spawn-hold"])
    results["meta_arms"] = meta_arms

    # Evaluate the eight landed discriminations against each hold-arm paired
    # with (i) the author's forged-release record and (ii) my release mutants.
    forged_rec = next(r for r in results["cases_arms"] if r["case"] == "auth_forge_release_b8")
    detached_rec = next(r for r in results["cases_arms"] if r["case"] == "auth_detached_control")
    for arm_name, hold_rec in meta_arms.items():
        results["discrimination_evals"][f"{arm_name}__x__forged_release"] = \
            eval_landed_discriminations(hold_rec, forged_rec, detached_rec)
    for rel_name in ("mut_forge_ungated_honest_b8", "mut_forge_lying_ppid_b8",
                     "mut_forge_release_stderr_b8"):
        rel_rec = next(r for r in results["cases_arms"] if r["case"] == rel_name)
        results["discrimination_evals"][f"auth_forge_hold__x__{rel_name}"] = \
            eval_landed_discriminations(meta_arms["auth_forge_hold"], rel_rec, detached_rec)

    payload = {"mode": "r63_critic_signature_spoof_attacks",
               "environment": env, "marker": MARKER, **results}
    out = HERE / "spoof-attack-verdicts.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
