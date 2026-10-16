#!/usr/bin/env python3
"""r93-critic seat mutant runner (read-only w.r.t. tracked files).

For each mutant: copy the FROZEN committed fixtures into a scratch project, apply one
textual edit to one fixture, launch the targeted arm in the battery launch shape, and
classify the raw receipt with the COMMITTED classifier (AST-extracted from the frozen
run_battery.py; segment sha256 pinned). Reports the row verdict under the mutant and
under the pristine control.

Every scratch project lives under corpus/live/r93-critic/mutants/<name>/.
"""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEAT = HERE.parent
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
MUTDIR = SEAT / "mutants"
GODOT = "/usr/bin/godot"
BOUND = 25


def load_classifier():
    src = (FROZEN / "run_battery.py").read_text()
    tree = ast.parse(src)
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == "main":
            for sub in ast.walk(n):
                if isinstance(sub, ast.FunctionDef) and sub.name == "classify_process":
                    seg = ast.get_source_segment(src, sub)
                    sha = hashlib.sha256(seg.encode()).hexdigest()
                    ns = {}
                    exec(seg, {"re": __import__("re")}, ns)
                    return ns["classify_process"], sha
    raise SystemExit("classifier not found")


def load_rows():
    return json.loads((HERE / "r93_rows.json").read_text())


def make_project(name):
    proj = MUTDIR / name / "proj"
    if proj.exists():
        shutil.rmtree(proj)
    proj.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FROZEN, proj)
    return proj


def launch(proj, script, flags, tag):
    cmd = [GODOT, "--headless", "--path", str(proj), "--script", f"res://{script}", "--"] + list(flags)
    env = dict(os.environ)
    env["GODOT_SILENCE_ROOT_WARNING"] = "1"
    outdir = MUTDIR / tag
    outdir.mkdir(parents=True, exist_ok=True)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=BOUND, env=env)
        stdout, stderr, code, err = p.stdout, p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        code, err = None, f"TIMEOUT after {BOUND} seconds"
    stem = f"{outdir.name}"
    (outdir / f"{stem}.out").write_text(stdout)
    (outdir / f"{stem}.err").write_text(stderr)
    (outdir / f"{stem}.rc").write_text(str(code) + ("\n" if code is not None else ""))
    return stdout, stderr, code, err


def verdict(classify, stdout, stderr, code, err, row):
    name, script, flags, expected_exit, signature = row[0], row[1], row[2], row[3], row[4]
    return classify(code, err, stdout + stderr, expected_exit, signature, ())


def run_row(classify, proj, row, tag):
    stdout, stderr, code, err = launch(proj, row[1], row[2], tag)
    return verdict(classify, stdout, stderr, code, err, row), (stdout, stderr, code, err)


def main():
    classify, sha = load_classifier()
    rows = {r[0]: r for r in load_rows()}
    print(f"# committed classifier segment sha256 {sha}")
    print(f"# frozen fixtures {FROZEN}")
    print(f"# loadavg {Path('/proc/loadavg').read_text().strip()}")

    # (mutant name, fixture file, old text, new text, rows expected to FLIP to FAIL,
    #  rows expected to STAY PASS)
    MUTANTS = [
        ("back_to_linear", "r93b_anim.gd",
         '.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN_OUT)',
         '.set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_IN_OUT)',
         ["r93_anim_overshoot"], []),
        ("spr_to_linear", "r93b_anim.gd",
         '.set_trans(Tween.TRANS_SPRING).set_ease(Tween.EASE_OUT)',
         '.set_trans(Tween.TRANS_LINEAR).set_ease(Tween.EASE_OUT)',
         ["r93_anim_overshoot"], []),
        ("await_extra_step", "r93b_anim.gd",
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE\n\tplayer.play("move")\n\tvar xs: Array = []',
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE\n\tplayer.play("move")\n\tplayer.advance(0.1)\n\tvar xs: Array = []',
         ["r93_anim_await_offbyone"], ["r93_anim_physics_tick", "r93_anim_phys_delta"]),
        ("frame_idle_to_manual", "r93b_anim.gd",
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE\n\tplayer.play("move")\n\tvar xs: Array = []',
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL\n\tplayer.play("move")\n\tvar xs: Array = []',
         ["r93_anim_physics_tick"], ["r93_anim_await_offbyone"]),
        ("frame_phys_to_manual", "r93b_anim.gd",
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_PHYSICS\n\tplayer.play("move")\n\tvar ys: Array = []',
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL\n\tplayer.play("move")\n\tvar ys: Array = []',
         ["r93_anim_physics_tick"], ["r93_anim_await_offbyone"]),
        ("blend_time_2", "r93b_anim.gd",
         '\tplayer.set_blend_time("a", "b", 1.0)',
         '\tplayer.set_blend_time("a", "b", 2.0)',
         ["r93_anim_blend_interleaved"], []),
        ("deferred_immediate_b", "r93b_anim.gd",
         '\tplayer.stop()\n\tplayer.play("m")\n\tplayer.advance(1.0)\n\tvar b1 := target.calls.duplicate()',
         '\tplayer.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE\n\tplayer.stop()\n\tplayer.play("m")\n\tplayer.advance(1.0)\n\tvar b1 := target.calls.duplicate()',
         ["r93_anim_deferred_flush"], []),
        ("manual_step_05", "r93b_anim.gd",
         '\tt1.custom_step(0.25)\n\tvar a := target.position.x',
         '\tt1.custom_step(0.5)\n\tvar a := target.position.x',
         ["r93_anim_manual_clock_control", "r93_anim_manual_clock_interleaved"], []),
        ("hard_switch_blend", "r93b_anim.gd",
         '\tplayer.play("b", 0.0)\n\tplayer.advance(0.25)',
         '\tplayer.play("b")\n\tplayer.advance(0.25)',
         ["r93_anim_blend_interleaved"], []),
        ("animblend_time_2", "anim_lattice.gd",
         '\tplayer.set_blend_time("a", "b", 1.0)',
         '\tplayer.set_blend_time("a", "b", 2.0)',
         ["r93_anim_blend_finished"], []),
        ("animblend_steps_9", "anim_lattice.gd",
         '\tvar finished_010 := _blend_from_finished(player, target, 10, 0.1)',
         '\tvar finished_010 := _blend_from_finished(player, target, 9, 0.1)',
         ["r93_anim_blend_finished"], []),
        ("tweenproc_paused_advance", "anim_lattice.gd",
         '\tt1.pause()\n\tvar y_paused := target.position.y',
         '\tt1.pause()\n\tt1.custom_step(0.25)\n\tvar y_paused := target.position.y',
         ["r93_tween_process_stable"], []),
        ("tweenval_expo_linear", "anim_lattice.gd",
         '" expo_in_05=", str(Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_EXPO, Tween.EASE_IN)),',
         '" expo_in_05=", str(Tween.interpolate_value(0.0, 10.0, 0.5, 1.0, Tween.TRANS_LINEAR, Tween.EASE_IN)),',
         ["r93_tween_interp_value"], []),
        ("animmethod_deferred_off", "anim_lattice.gd",
         '\tplayer.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_DEFERRED\n\tplayer.play("m")\n\tvar sig_at_play',
         '\tplayer.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE\n\tplayer.play("m")\n\tvar sig_at_play',
         ["r93_anim_method_callback"], []),
    ]

    MUTANTS2 = [
        # fixed batch-1 design error: remove pause() so the tween auto-advances
        ("tweenproc_pause_removed", "anim_lattice.gd",
         '\tt1.pause()\n\tvar y_paused := target.position.y',
         '\tvar y_paused := target.position.y',
         ["r93_tween_process_stable"], []),
        ("tweenval_grid_t", "anim_lattice.gd",
         '\t\t\tfor t in [0.0, 0.25, 0.5, 0.75, 1.0]:',
         '\t\t\tfor t in [0.0, 0.2, 0.5, 0.75, 1.0]:',
         ["r93_tween_interp_grid_a", "r93_tween_interp_grid_b"], []),
        ("census_autocapture", "anim_lattice.gd",
         '",auto_capture=", ap.is_auto_capture(), "]"',
         '",auto_capture=", true, "]"',
         ["r93_tween_census"], []),
        ("animtrack_mid_key", "anim_lattice.gd",
         '\tthree.track_insert_key(t3, 0.5, 10.0)',
         '\tthree.track_insert_key(t3, 0.5, 5.0)',
         ["r93_anim_track_interp"], []),
        ("tweenstep_paused_50", "anim_lattice.gd",
         '\tt2.custom_step(0.25)\n\tvar paused := [target.position.y',
         '\tt2.custom_step(0.5)\n\tvar paused := [target.position.y',
         ["r93_tween_manual_step"], []),
        ("tweenchain_second_leg", "anim_lattice.gd",
         '\tt1.tween_property(target, "position:x", 40.0, 0.5)',
         '\tt1.tween_property(target, "position:x", 30.0, 0.5)',
         ["r93_tween_chain"], []),
        ("animseek_seek_target", "anim_lattice.gd",
         '\tplayer.seek(0.75, true)',
         '\tplayer.seek(0.5, true)',
         ["r93_anim_seek"], []),
        ("animproc_manual_advance", "anim_lattice.gd",
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL\n\tplayer.play("move")\n\tplayer.advance(0.25)',
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_MANUAL\n\tplayer.play("move")\n\tplayer.advance(0.5)',
         ["r93_anim_process_manual", "r93_anim_process_stable"], []),
        ("phys_manual_target", "anim_lattice.gd",
         '\tt3.tween_property(target, "scale:y", 5.0, 1.0)',
         '\tt3.tween_property(target, "scale:y", 10.0, 1.0)',
         ["r93_tween_phys_manual_step"], []),
        ("project_phys_120", "project.godot",
         'config/features=PackedStringArray("4.7")',
         'config/features=PackedStringArray("4.7")\n\n[physics]\ncommon/physics_ticks_per_second=120',
         ["r93_anim_phys_delta", "r93_anim_physics_tick"], ["r93_anim_await_offbyone"]),
        # non-vacuity control for the r93b frame arm: kill the IDLE pose path entirely
        ("frame_idle_stopped", "r93b_anim.gd",
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE\n\tplayer.play("move")\n\tvar xs: Array = []',
         '\tplayer.playback_process_mode = AnimationPlayer.ANIMATION_PROCESS_IDLE\n\tplayer.stop()\n\tvar xs: Array = []',
         ["r93_anim_physics_tick"], ["r93_anim_await_offbyone"]),
        # non-vacuity control for the deferred row: queue nothing at all
        ("deferred_no_queue", "r93b_anim.gd",
         '\tplayer.stop()\n\tplayer.play("m")\n\tplayer.advance(1.0)\n\tvar b1 := target.calls.duplicate()',
         '\tplayer.stop()\n\tvar b1 := target.calls.duplicate()',
         ["r93_anim_deferred_flush"], []),
    ]
    batch = MUTANTS if (len(sys.argv) < 2 or sys.argv[1] == "1") else MUTANTS2
    results = []
    for name, fname, old, new, expect_fail, expect_pass in batch:
        proj = make_project(name)
        target = proj / fname
        text = target.read_text()
        if text.count(old) != 1:
            print(f"SKIP {name}: anchor count={text.count(old)} in {fname}")
            results.append({"mutant": name, "skipped": True, "anchor_count": text.count(old)})
            continue
        target.write_text(text.replace(old, new, 1))
        # control: same rows on the pristine frozen copy
        ctrl = make_project(name + "-ctrl")
        entry = {"mutant": name, "fixture": fname, "rows": {}}
        for row_name in expect_fail + expect_pass:
            row = rows[row_name]
            mv, _ = run_row(classify, proj, row, f"{name}/{row_name}")
            cv, _ = run_row(classify, ctrl, row, f"{name}-ctrl/{row_name}")
            entry["rows"][row_name] = {"mutant_pass": mv, "control_pass": cv,
                                       "expected_mutant": "FAIL" if row_name in expect_fail else "PASS"}
        entry["ok"] = all(
            (v["mutant_pass"] is False) == (v["expected_mutant"] == "FAIL") and v["control_pass"] is True
            for v in entry["rows"].values())
        results.append(entry)
        print(f"{'OK  ' if entry['ok'] else 'BAD '} {name}: " +
              ", ".join(f"{k}={v['mutant_pass']}(ctrl {v['control_pass']})" for k, v in entry["rows"].items()))

    (SEAT / f"mutants{"" if batch is MUTANTS else "2"}.json").write_text(json.dumps(results, indent=1) + "\n")
    bad = [r for r in results if not r.get("ok") and not r.get("skipped")]
    print(f"# {len(results) - len(bad)}/{len(results)} mutants behaved as predicted")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
