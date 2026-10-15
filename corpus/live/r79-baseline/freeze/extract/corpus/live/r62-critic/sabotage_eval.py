#!/usr/bin/env python3
"""r62-critic sabotage evaluation: apply the LANDED meta row's exact
discrimination predicates (run_battery.py working tree, r62 author diff
+142/-0) to my adversarial arm outcomes. Answers per mutant: would
`probe_descendant_pipe_eof` still PASS (slip) or FAIL (reject)?

Predicates mirrored verbatim from the diff:

  hold_timed_out_with_child_dead  = timed_out and child_exit_at_timeout == 0
  hold_post_exit_write_captured   = post_exit_write in captured output
  hold_misattributed_rejects      = inner_classification is False
  hold_descendant_orphaned_alive  = descendant_alive_at_return is True
  detached_case_passes_clean      = control verdict PASS + exit 0 + error None
  detached_lacks_post_exit_write  = post marker absent from control output
  detached_descendant_orphaned_alive = control descendant alive at meta check

child_exit_at_timeout semantics = pipe_proc.poll() inside the TimeoutExpired
handler: 0 iff the direct child was already a reaped-exit-0 zombie at bound,
None if still alive. Mapped from my timeline probe (tl_hold_silent reaped at
0.533s -> poll 0; tl_hang unreaped at bound -> poll None) and per-arm
godot_alive knowledge: clean-mode children exit ~0.4s -> 0; hang arms -> None.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTACKS = json.loads((HERE / "attack-verdicts.json").read_text())["results"]
TIMELINE = json.loads((HERE / "timeline-verdicts.json").read_text())["results"]
EARLY = json.loads((HERE / "early-write.json").read_text())
ARMS = {r["case"]: r for r in ATTACKS}
ARMS["early_write"] = EARLY
TL = {r["case"]: r for r in TIMELINE}

# poll() at TimeoutExpired: 0 if child already exited (all non-hang arms exit
# ~0.4s), None if alive at bound (hang arms). Timeline probe confirms both.
def poll_at_timeout(case):
    if case.startswith("tl_"):
        tl = TL[case]
        return tl["child_returncode"] if tl["child_reaped_at_s"] is not None else None
    arm = ARMS[case]
    return None if "--hang=" in str(arm["command"]) else 0


def eval_hold_arm(arm):
    """Author's 4 hold-side discriminations applied to a mutant hold arm."""
    timed_out = arm["error"] is not None and "TIMEOUT" in arm["error"]
    return {
        "hold_timed_out_with_child_dead": timed_out and poll_at_timeout(arm["case"]) == 0,
        "hold_post_exit_write_captured": arm["desc_post_parent_write_captured"],
        "hold_misattributed_rejects": arm["inner_classification"] is False,
        "hold_descendant_orphaned_alive": any(arm["descendants_alive_at_return"]),
    }


def eval_control(arm, desc_alive_at_meta_check):
    """Author's 3 control-side discriminations applied to a mutant control."""
    return {
        "detached_case_passes_clean": (arm["inner_classification"] is True
                                       and arm["actual_exit"] == 0
                                       and arm["error"] is None),
        "detached_lacks_post_exit_write": not arm["desc_post_parent_write_captured"],
        "detached_descendant_orphaned_alive": desc_alive_at_meta_check is True,
    }


verdicts = []

# ---- HOLD-side mutants -----------------------------------------------------
hold_mutants = {
    # the real arm shape the author drives (post-death write + 7s hold)
    "hold_write_as_authored": "hold_write",
    # S1 SLIP CANDIDATE: same marker written ~0.05s post-spawn = BEFORE the
    # child's ~0.4s exit — evidence claim violated, presence still detected.
    "early_write_sabotage": "early_write",
    # S2: child alive at bound (hang) + holder -> poll() None -> must reject.
    "hang_hold_sabotage": "hang_hold",
    # S3: holder releases at 1.2s < bound -> no timeout -> must reject.
    "early_release_sabotage": "early_release",
    # S4: silent holder (no post-write line) -> disc2 must reject it.
    "silent_hold_sabotage": "hold_silent",
    # S5: single-pipe holds only (no write) -> timeout but disc2 rejects.
    "stderr_only_sabotage": "stderr_only",
    "stdout_only_sabotage": "stdout_only",
    # S6: holder floods 9000 lines post-death but never writes the marker.
    "flood_sabotage": "flood",
    # S7: descendant spoofed the signature post-death, no post-write marker.
    "spoof_hold_sabotage": "spoof_hold",
}
for name, arm_name in hold_mutants.items():
    discs = eval_hold_arm(ARMS[arm_name])
    verdicts.append({"mutant": name, "arm": arm_name, "side": "hold",
                     "discriminations": discs,
                     "meta_hold_side_passes": all(discs.values())})

# ---- CONTROL-side mutants --------------------------------------------------
# real control (detach_alive): descendant alive at meta check -> passes.
verdicts.append({"mutant": "detached_control_as_authored", "arm": "detach_alive",
                 "side": "control",
                 "discriminations": eval_control(ARMS["detach_alive"], True),
                 "meta_control_side_passes": all(eval_control(ARMS["detach_alive"], True).values())})
# mutant: control descendant exits instantly (sleep 0) -> dead at meta check.
verdicts.append({"mutant": "control_descendant_dies_early", "arm": "detach_alive",
                 "side": "control",
                 "discriminations": eval_control(ARMS["detach_alive"], False),
                 "meta_control_side_passes": all(eval_control(ARMS["detach_alive"], False).values())})
# mutant: control row IS a silent holder (fds not detached) -> exit None.
verdicts.append({"mutant": "control_actually_holds_pipes", "arm": "hold_silent",
                 "side": "control",
                 "discriminations": eval_control(ARMS["hold_silent"], True),
                 "meta_control_side_passes": all(eval_control(ARMS["hold_silent"], True).values())})
# mutant: control child also echoes the post-exit marker itself.
spoofed = dict(ARMS["detach_alive"]); spoofed["desc_post_parent_write_captured"] = True
verdicts.append({"mutant": "control_emits_post_exit_marker", "arm": "detach_alive+spoof",
                 "side": "control",
                 "discriminations": eval_control(spoofed, True),
                 "meta_control_side_passes": all(eval_control(spoofed, True).values())})

out = {"mode": "r62_critic_sabotage_eval",
       "note": "predicates mirrored from working-tree run_battery.py r62 meta; "
               "arm outcomes measured by drive_attacks.py / timeline_probe.py "
               "through the verbatim production run_process/classify_process",
       "verdicts": verdicts}
(HERE / "sabotage-eval.json").write_text(json.dumps(out, indent=2) + "\n")
for v in verdicts:
    status = "SLIPS" if v.get("meta_hold_side_passes") or v.get("meta_control_side_passes") else "rejects"
    print(f"{v['mutant']}: {status} {json.dumps(v['discriminations'])}", flush=True)
