#!/usr/bin/env python3
"""r66-simplifier dead-entry census: replays classify_process.allowed_error
verbatim against captured run rows; reports per-entry trip counts and
allowlist-entry coverage. Literal port of run_battery.py:162-172."""
import json, re, sys
from pathlib import Path

VERDICTS = Path(sys.argv[1])
# Allowlist map copied verbatim from run_battery.py:400-445 (expected_errors)
EXPECTED_ERRORS = {
    "negative_overlap": ("ERROR: negative control: expected collected signal was absent with disabled mask",),
    "negative_transition": ("ERROR: Can't change to a null scene. Use unload_current_scene() if you wish to unload it.",
                          "ERROR: negative control: deliberately invalid scene destination rejected"),
    "negative_signal": ("ERROR: negative control: expected collected signal was absent (dispatch deliberately disabled)",),
    "save_corrupt_negative": ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR",),
    "save_process_missing": ("ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND,",),
    "camera_no_follow": ("ERROR: camera follow assertion failed: target moved but active center did not track",),
    "camera_far_bound": ("ERROR: camera limit assertion failed: expected active center within right boundary and distinct from target",),
    "camera_far_top_bound": ("ERROR: camera limit assertion failed: expected active center within top boundary and distinct from target",),
    "camera_far_left_bound": ("ERROR: camera limit assertion failed: expected active center within left boundary and distinct from target",),
    "camera_far_bottom_bound": ("ERROR: camera limit assertion failed: expected active center within bottom boundary and distinct from target",),
    "ui_signal_disconnected": ("ERROR: UI assertion failed: expected in-tree HUD text=Score: 7",),
    "button_activation_disconnected": ("ERROR: UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1,",),
    "button_activation_unfocused": ("ERROR: UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1,",),
    "checkbox_toggle_disconnected": ("ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []",),
    "button_group_selection_disconnected": ("ERROR: BUTTON_GROUP SIGNAL ASSERTION FAILED: expected transitions [A:false,B:true,B:false,A:true], got []",),
    "button_group_selection_ungroup_b": ("ERROR: BUTTON_GROUP ABSENCE ASSERTION FAILED after B→A: expected exclusive selection, got A=true B=true",),
    "slider_adjust_disconnected": ("ERROR: SLIDER SIGNAL ASSERTION FAILED: expected value_changed receipts [6,5] and Labels [Value 6,Value 5]",),
    "slider_adjust_no_focus": ("ERROR: SLIDER NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,5",),
    "slider_adjust_repeat_right_disconnected": ("ERROR: SLIDER REPEAT SIGNAL ASSERTION FAILED: expected value_changed receipts [6,7,6,5] and Labels [Value 6,Value 7,Value 6,Value 5]",),
    "slider_adjust_repeat_right_no_focus": ("ERROR: SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,7,7,6,6,5,5",),
    "slider_adjust_repeat_right_focus_handoff": ("ERROR: SLIDER REPEAT FOCUS-HANDOFF ASSERTION FAILED: expected post-handoff adjustment after seven checks",),
    "slider_adjust_repeat_right_focus_restore": (),
    "slider_adjust_repeat_right_second_focus_loss": ("ERROR: SLIDER REPEAT SECOND-FOCUS-LOSS ASSERTION FAILED: expected final restored-focus adjustment after seven checks",),
    "slider_adjust_repeat_right_second_focus_restore": (),
    "slider_adjust_repeat_right_second_focus_restore_disconnected": ("ERROR: SLIDER DOUBLE-RESTORE DISCONNECTED ASSERTION FAILED: expected signal-consumer updates",),
    "slider_adjust_repeat_right_second_focus_restore_disconnect_after_first": ("ERROR: SLIDER MID-DISCONNECT ASSERTION FAILED: expected cumulative callback history to stay [6]",),
    "slider_adjust_repeat_right_second_focus_restore_reconnect_after_final_left": ("ERROR: SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks",),
    "slider_adjust_repeat_right_second_focus_restore_press_after_late_reconnect": (),
    "slider_adjust_repeat_right_second_focus_restore_release_after_late_reconnect_press": ("ERROR: SLIDER RELEASE AFTER LATE-RECONNECT PRESS ASSERTION FAILED: expected no new receipt after eleven checks",),
    "slider_adjust_repeat_right_second_focus_restore_observe_parsed_release": ("ERROR: SLIDER PARSED RELEASE OBSERVER ASSERTION FAILED: expected no new receipt after eleven checks",),
    "slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear": ("ERROR: SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks",),
    "slider_adjust_repeat_right_second_focus_restore_clear_then_push_release": ("ERROR: SLIDER CLEAR THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks",),
    "slider_adjust_repeat_right_second_focus_restore_clear_frame_then_push_release": ("ERROR: SLIDER CLEAR FRAME THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks",),
    "slider_adjust_repeat_right_second_focus_restore_push_frame_then_clear_release": ("ERROR: SLIDER PUSH FRAME THEN CLEAR RELEASE ASSERTION FAILED: expected no new receipt after eleven checks",),
    "slider_adjust_repeat_right_second_focus_restore_observe_push_input_release": ("ERROR: SLIDER PUSH INPUT RELEASE ASSERTION FAILED: expected no new receipt after eleven checks",),
    "health_gauge_disconnected": ("ERROR: Health gauge assertion failed: expected in-tree TextureProgressBar value=35 value_changed=1 receipt=35",),
    "animation_stuck": ("ERROR: ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance,",),
    "tween_no_start": ("ERROR: TWEEN ASSERTION FAILED: modulate did not show flash then return to baseline,",),
    "export_preset_missing": ("ERROR: Invalid export preset name: Missing preset.",),
    "contact_no_collision": ("ERROR: CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3,",),
    "audio_no_play": ("ERROR: AUDIO ASSERTION FAILED: expected in-tree player playback to advance,",),
    "audio_bus_route_invalid_control": ("ERROR: AUDIO BUS CONTROL ASSERTION FAILED: requested invalid route silently fell back to Master,",),
    "crash_spontaneous_sigabrt": ("ERROR: r60 spontaneous crash probe",),
}

def allowed_error(line, allowed):
    stripped = line.strip()
    if stripped == allowed:
        return True
    if allowed.endswith(","):
        return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
    if allowed == "ERROR: chain incomplete":
        return (stripped.startswith("ERROR: chain incomplete collections=")
                and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                and stripped.count("ERROR:") == 1)
    return False

data = json.loads(VERDICTS.read_text())
rows = {r["case"]: r for r in data["results"]}
census = {}
for case, entries in EXPECTED_ERRORS.items():
    row = rows.get(case)
    if row is None:
        census[case] = {"status": "NO_ROW", "entries": {}}
        continue
    lines = row.get("output", [])
    per_entry = {}
    for e in entries:
        matched = [ln for ln in lines if allowed_error(ln, e)]
        per_entry[e] = {"matched_lines": len(matched),
                        "shape": ("exact" if not e.endswith(",") and e != "ERROR: chain incomplete"
                                  else "comma-prefix" if e.endswith(",") else "structured")}
    err_lines = [ln for ln in lines if "ERROR:" in ln]
    admitted = [ln for ln in err_lines if any(allowed_error(ln, e) for e in entries)]
    census[case] = {"status": row["verdict"], "entries": per_entry,
                    "error_lines_in_output": len(err_lines),
                    "admitted_lines": len(admitted),
                    "unadmitted_error_lines": len(err_lines) - len(admitted)}
print(json.dumps(census, indent=1))
