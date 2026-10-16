#!/usr/bin/env python3
"""Run the read-only Godot fixtures serially in an isolated scratch project."""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import selectors
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = [
    ("mechanic", "controls/mechanic_test.gd", [], 0, "PASS first=true"),
    ("scene_signal", "controls/test_scene_signal.gd", [], 0, "PASS scene_loaded=true"),
    ("input_route", "controls/input_route.gd", [], 0, "PASS route=parse_input_event-to-Node._input"),
    ("route_toggle", "controls/input_route_toggle.gd", [], 0, "PASS toggle=disabled-to-inherit"),
    ("overlap", "controls/overlap_probe.gd", [], 0, "PASS packed_scene=true"),
    ("transition", "controls/scene_transition_probe.gd", [], 0, "PASS valid_transition=true"),
    ("causal", "causal_chain.gd", [], 0, "PASS positive input=1"),
    ("wrong_key", "causal_chain.gd", ["--wrong-key-negative"], 1, "PASS wrong_key=F"),
    ("release", "causal_chain.gd", ["--release-test"], 0, "PASS release press_receipts=1"),
    ("keyup", "causal_chain.gd", ["--keyup-test"], 0, "PASS keyup E_press_receipts=1"),
    ("negative_route", "controls/input_route_negative.gd", [], 1, "PASS negative_route=disabled_node"),
    ("negative_overlap", "controls/overlap_negative.gd", [], 1, "negative control: expected collected signal was absent"),
    ("negative_transition", "controls/scene_transition_negative.gd", [], 1, "PASS invalid_destination_rejected=true"),
    ("negative_signal", "controls/test_scene_signal_negative.gd", [], 1, "negative control: expected collected signal was absent"),
    ("camera_follow", "camera_follow.gd", [], 0, "PASS camera_follow moved=true current=true center_matches_target=true"),
    ("camera_no_follow", "camera_follow.gd", ["--no-follow"], 2, "camera follow assertion failed: target moved but active center did not track"),
    ("camera_limit", "camera_limit.gd", [], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true far_bound=false"),
    ("camera_far_bound", "camera_limit.gd", ["--far-bound"], 2, "camera limit assertion failed: expected active center within right boundary and distinct from target"),
    ("camera_top_limit", "camera_limit.gd", ["--top-bound"], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true"),
    ("camera_far_top_bound", "camera_limit.gd", ["--far-top-bound"], 2, "camera limit assertion failed: expected active center within top boundary and distinct from target"),
    ("camera_left_limit", "camera_limit.gd", ["--left-bound"], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true"),
    ("camera_far_left_bound", "camera_limit.gd", ["--far-left-bound"], 2, "camera limit assertion failed: expected active center within left boundary and distinct from target"),
    ("camera_bottom_limit", "camera_limit.gd", ["--bottom-bound"], 0, "PASS camera_limit moved=true current=true center_at_viewport_adjusted_clamp=true center_differs_from_target=true"),
    ("camera_far_bottom_bound", "camera_limit.gd", ["--far-bottom-bound"], 2, "camera limit assertion failed: expected active center within bottom boundary and distinct from target"),
    ("ui_signal_hud", "ui_signal_hud.gd", [], 0, "PASS ui_signal connected=true hud_in_tree=true initial=Score: 0 hud_text=Score: 7"),
    ("ui_signal_disconnected", "ui_signal_hud.gd", ["--disconnect-signal"], 2, "UI assertion failed: expected in-tree HUD text=Score: 7"),
    ("health_gauge", "health_gauge.gd", [], 0, "PASS health_gauge in_tree=true range=0..100 values=35,0.0,100.0,100.0 receipts=35,0,100"),
    ("health_gauge_disconnected", "health_gauge.gd", ["--disconnect-signal"], 2, "Health gauge assertion failed: expected in-tree TextureProgressBar value=35 value_changed=1 receipt=35"),
    ("level_collision", "level_collision/level_probe.gd", [], 0, "PASS level_packed_scene=true cell=2,3 collision_vertices=4"),
    ("contact_runtime", "contact_probe.gd", [], 0, "PASS runtime_tile_contact=true cell=2,3,"),
    ("contact_no_collision", "contact_probe.gd", ["--no-collision"], 2, "CONTACT ASSERTION FAILED: body motion did not contact level tile at cell=2,3"),
    ("animation_property", "animation_property.gd", [], 0, "PASS animation_property_changed=true started=true"),
    ("animation_stuck", "animation_property.gd", ["--stuck"], 2, "ANIMATION ASSERTION FAILED: expected animated property x=60 after bounded advance"),
    ("tween_flash", "tween_flash.gd", [], 0, "PASS tween_flash transient_modulate="),
    ("tween_no_start", "tween_flash.gd", ["--no-tween"], 2, "TWEEN ASSERTION FAILED: modulate did not show flash then return to baseline,"),
    ("audio_playback", "audio_playback.gd", [], 0, "PASS audio_playback in_tree=true playing=true position_advanced=true"),
    ("audio_no_play", "audio_playback.gd", ["--no-play"], 2, "AUDIO ASSERTION FAILED: expected in-tree player playback to advance"),
    ("audio_bus_route", "audio_bus_route.gd", [], 0, "PASS audio_bus_route in_tree=true requested=FixtureBus resolved_index=1 resolved_bus=FixtureBus playing=true position_advanced=true"),
    ("audio_bus_route_invalid_control", "audio_bus_route.gd", ["--invalid"], 2, "AUDIO BUS CONTROL ASSERTION FAILED: requested invalid route silently fell back to Master"),
    ("export_readiness", "__godot_export__", [], 0, "EXPORT PASS preset=Linux/X11 executable=nonempty"),
    ("export_preset_missing", "__godot_export_missing__", [], 1, "No export preset 'Missing preset' found"),
    ("button_activation", "button_activation.gd", [], 0, "PASS button_activation in_tree=true initial=Ready edge_texts=[Ready,Activated 1,Activated 1,Activated 2] receipts=[0,1,1,2]"),
    ("button_activation_disconnected", "button_activation.gd", ["--disconnect-signal"], 2, "UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1"),
    ("button_activation_unfocused", "button_activation.gd", ["--no-focus"], 2, "UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1"),
    ("button_activation_focus_loss", "button_activation.gd", ["--lose-focus-after-first"], 0, "PASS button_activation_focus_loss initial=focused release1=Activated1 mid_sequence=no_focus release2=Activated1 receipts=1"),
    ("checkbox_toggle", "checkbox_toggle.gd", [], 0, "PASS checkbox_toggle edge_states=[false,true,true,false] toggled=[true,false] labels=[On,Off]"),
    ("checkbox_toggle_disconnected", "checkbox_toggle.gd", ["--disconnect-signal"], 2, "ERROR: CHECKBOX SIGNAL ASSERTION FAILED: expected toggled sequence [true,false], got []"),
    ("button_group_selection", "button_group_selection.gd", [], 0, "PASS button_group_selection exclusive=true toggled=[A:false,B:true,B:false,A:true] labels=[B,A]"),
    ("button_group_selection_disconnected", "button_group_selection.gd", ["--disconnect-signal"], 2, "ERROR: BUTTON_GROUP SIGNAL ASSERTION FAILED: expected transitions [A:false,B:true,B:false,A:true], got []"),
    ("button_group_selection_ungroup_b", "button_group_selection.gd", ["--ungroup-b"], 2, "BUTTON_GROUP ABSENCE ASSERTION FAILED after B→A: expected exclusive selection, got A=true B=true"),
    ("slider_adjust", "slider_adjust.gd", [], 0, "PASS slider_adjust focused=true range=0..10 step=1 values=6,5 receipts=6,5 Labels=Value 6,Value 5"),
    ("slider_adjust_disconnected", "slider_adjust.gd", ["--disconnect-signal"], 2, "SLIDER SIGNAL ASSERTION FAILED: expected value_changed receipts [6,5] and Labels [Value 6,Value 5]"),
    ("slider_adjust_no_focus", "slider_adjust.gd", ["--no-focus"], 2, "SLIDER NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,5"),
    ("slider_adjust_repeat_right", "slider_adjust.gd", ["--repeat-right"], 0, "PASS slider_adjust_repeat focused=true range=0..10 step=1 values=6,7,7,6,6,5,5 receipts=6,7,6,5 Labels=Value 6,Value 7,Value 6,Value 5"),
    ("slider_adjust_repeat_right_disconnected", "slider_adjust.gd", ["--repeat-right", "--disconnect-signal"], 2, "SLIDER REPEAT SIGNAL ASSERTION FAILED: expected value_changed receipts [6,7,6,5] and Labels [Value 6,Value 7,Value 6,Value 5]"),
    ("slider_adjust_repeat_right_no_focus", "slider_adjust.gd", ["--repeat-right", "--no-focus"], 2, "SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,7,7,6,6,5,5"),
    ("slider_adjust_repeat_right_focus_handoff", "slider_adjust.gd", ["--repeat-right", "--focus-handoff"], 2, "SLIDER REPEAT FOCUS-HANDOFF ASSERTION FAILED: expected post-handoff adjustment after seven checks"),
    ("slider_adjust_repeat_right_focus_restore", "slider_adjust.gd", ["--repeat-right", "--focus-restore"], 0, "PASS slider_adjust_repeat_focus_restore focused=true range=0..10 step=1 values=6,6,6,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4"),
    ("slider_adjust_repeat_right_second_focus_loss", "slider_adjust.gd", ["--repeat-right", "--second-focus-loss"], 2, "SLIDER REPEAT SECOND-FOCUS-LOSS ASSERTION FAILED: expected final restored-focus adjustment after seven checks"),
    ("slider_adjust_repeat_right_second_focus_restore", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore"], 0, "PASS slider_adjust_repeat_second_focus_restore focused=true values=6,6,6,5,5,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4"),
    ("slider_adjust_repeat_right_second_focus_restore_disconnected", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--disconnect-signal"], 2, "SLIDER DOUBLE-RESTORE DISCONNECTED ASSERTION FAILED: expected signal-consumer updates"),
    ("slider_adjust_repeat_right_second_focus_restore_reconnect_after_first_left", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--reconnect-after-first-left"], 0, "PASS slider_adjust_repeat_second_focus_restore_reconnect values=6,6,6,5,5,5,5,4,4 receipts=6,4 Labels=Value 6,Value 4"),
    ("slider_adjust_repeat_right_second_focus_restore_release_after_late_reconnect_press", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--release-after-late-reconnect-press"], 2, "SLIDER RELEASE AFTER LATE-RECONNECT PRESS ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_observe_parsed_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--observe-parsed-release"], 2, "SLIDER PARSED RELEASE OBSERVER ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--composite-push-and-clear"], 2, "SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_clear_then_push_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--clear-then-push-release"], 2, "SLIDER CLEAR THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_clear_frame_then_push_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--clear-frame-then-push-release"], 2, "SLIDER CLEAR FRAME THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_push_frame_then_clear_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--push-frame-then-clear-release"], 2, "SLIDER PUSH FRAME THEN CLEAR RELEASE ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_observe_push_input_release", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--observe-push-input-release"], 2, "SLIDER PUSH INPUT RELEASE ASSERTION FAILED: expected no new receipt after eleven checks"),
    ("slider_adjust_repeat_right_second_focus_restore_press_after_late_reconnect", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--press-after-late-reconnect"], 0, "PASS slider_adjust_repeat_second_focus_restore_press_after_late_reconnect values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3"),
    ("slider_adjust_repeat_right_second_focus_restore_reconnect_after_final_left", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--reconnect-after-final-left"], 2, "SLIDER LATE-RECONNECT ASSERTION FAILED: expected no retroactive receipt after nine checks"),
    ("slider_adjust_repeat_right_second_focus_restore_disconnect_after_first", "slider_adjust.gd", ["--repeat-right", "--second-focus-restore", "--disconnect-after-first"], 2, "SLIDER MID-DISCONNECT ASSERTION FAILED: expected cumulative callback history to stay [6]"),
    ("save_roundtrip", "save_roundtrip.gd", [], 0, "PASS save_roundtrip structured=true reopened=true values_match=true user_path="),
    ("save_corrupt_negative", "save_roundtrip.gd", ["--corrupt-negative"], 2, "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR"),
    ("save_process_writer", "__save_process_writer__", [], 0, "PASS save_process writer=true pid="),
    ("save_process_reader", "__save_process_reader__", [], 0, "PASS save_process reader=true pid="),
    ("save_process_missing", "__save_process_missing__", [], 2, "ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND"),
    # r79: PhysicsServer2D interior-window lattice — the contact_monitor
    # RigidBody2D window vs the monitoring Area2D window on the same scene.
    # Pinned from r79-scout §1.4 (23 arms, measured x3 byte-stable).
    # Inserted ahead of the crash/descendant tail, not appended at the end:
    # probe_descendant_pipe_eof requires detached_descendant_orphaned_alive
    # within the descendant's `sleep 8` lifetime, so no CASES rows may sit
    # between descendant_pipe_detached_control and the meta probes.
    ("phys2d_events_edge_srv", "phys2d_events.gd", ["--arm=edge_srv"], 0,
     'PASS phys2d_events edge_srv q_before=1 srv_before=(100.0, 0.0) srv_after=(200.0, 0.0) q_new=1 q_old=0 q_new_n1=1 q_old_n1=0'),
    ("phys2d_events_edge_node_srv", "phys2d_events.gd", ["--arm=edge_node_srv"], 0,
     'PASS phys2d_events edge_node_srv q_before=1 srv_after=(200.0, 0.0) q_new=1 q_old=0 node_prop_in_cb=(300.0, 0.0) srv_n1=(200.0, 0.0) node_prop_n1=(300.0, 0.0) q_new_n1=1 q_old_n1=0'),
    ("phys2d_events_edge_node", "phys2d_events.gd", ["--arm=edge_node"], 0,
     'PASS phys2d_events edge_node node_prop_in_cb=(400.0, 0.0) srv_in_cb=(300.0, 0.0) q_new=0 q_old=1 srv_n1=(400.0, 0.0) q_new_n1=1 q_old_n1=0'),
    ("phys2d_events_edge_revert", "phys2d_events.gd", ["--arm=edge_revert"], 0,
     'PASS phys2d_events edge_revert q_srv_w0=1 srv_after_node_w0=(200.0, 0.0) q_srv_after_node_w0=1 q_node_after_node_w0=0 srv_n1=(400.0, 0.0) q_srv_n1=0 q_node_n1=1 node_prop_n1=(400.0, 0.0)'),
    ("phys2d_events_area_edge", "phys2d_events.gd", ["--arm=area_edge"], 0,
     'PASS phys2d_events area_edge q_before=1 node_prop_in_cb=(100.0, 0.0) srv_in_cb=(0.0, 0.0) q_new=0 q_old=1 srv_n1=(100.0, 0.0) q_new_n1=1 q_old_n1=0 node_prop_n1=(100.0, 0.0) srv_direct_in_cb=(200.0, 0.0) q_direct=1 node_prop_direct_in_cb=(100.0, 0.0) srv_direct_n2=(200.0, 0.0) node_prop_direct_n2=(100.0, 0.0)'),
    ("phys2d_events_cm_on", "phys2d_events.gd", ["--arm=cm_on"], 0,
     'PASS phys2d_events cm_on entered=2 exited=1 entry1_frame=1 entry2_frame=20 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 valid=true exit1_frame=7'),
    ("phys2d_events_cm_off", "phys2d_events.gd", ["--arm=cm_off"], 0,
     'PASS phys2d_events cm_off entered=0 exited=0 entry1_frame=-1 entry2_frame=-1 cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- post_monitor=false post_max=4 valid=true exit1_frame=-1'),
    ("phys2d_events_cm_max0", "phys2d_events.gd", ["--arm=cm_max0"], 0,
     'PASS phys2d_events cm_max0 entered=0 exited=0 entry1_frame=-1 entry2_frame=-1 cb_fired=false cb_count=- cb_colliders=- cb_monitor=- cb_max=- post_monitor=true post_max=0 valid=true exit1_frame=-1'),
    ("phys2d_events_cm_toggle_cb", "phys2d_events.gd", ["--arm=cm_toggle_cb"], 0,
     'PASS phys2d_events cm_toggle_cb entered=2 exited=1 entry1_frame=1 entry2_frame=20 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=true post_monitor=true post_count=2 valid=true exit1_frame=7'),
    ("phys2d_events_cm_deferred_cb", "phys2d_events.gd", ["--arm=cm_deferred_cb"], 0,
     'PASS phys2d_events cm_deferred_cb entered=1 exited=0 entry1_frame=1 entry2_frame=-1 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=true post_monitor=false valid=true exit1_frame=-1'),
    ("phys2d_events_cm_max0_cb", "phys2d_events.gd", ["--arm=cm_max0_cb"], 0,
     'PASS phys2d_events cm_max0_cb entered=1 exited=1 entry1_frame=1 entry2_frame=-1 cb_fired=true cb_count=2 cb_colliders=1 cb_monitor=true cb_max=4 cb_readback=0 post_max=0 valid=true exit1_frame=1'),
    ("phys2d_events_rb_srv_set_state", "phys2d_events.gd", ["--arm=rb_srv_set_state"], 0,
     'PASS phys2d_events rb_srv_set_state entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=(500.0, 500.0) cb_node_unchanged=true cb_node_read=- cb_srv_before=- next_node=(500.0001, 501.0889) next_srv=(500.0001, 501.0889) late_node=(500.0006, 516.297) node_write_stuck=false node_follows_srv=true valid_after=true'),
    ("phys2d_events_rb_node_position", "phys2d_events.gd", ["--arm=rb_node_position"], 0,
     'PASS phys2d_events rb_node_position entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=(600.0, 600.0) cb_srv_before=(0.000128, -4.56002) next_node=(0.000128, -4.672004) next_srv=(0.000128, -4.672004) late_node=(0.000128, -4.699955) node_write_stuck=false node_follows_srv=false valid_after=true'),
    ("phys2d_events_rb_queue_free", "phys2d_events.gd", ["--arm=rb_queue_free"], 0,
     'PASS phys2d_events rb_queue_free entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=<dead> next_srv=<dead> late_node=<dead> node_write_stuck=false node_follows_srv=false valid_after=false cb_queued=true'),
    ("phys2d_events_rb_free_rid", "phys2d_events.gd", ["--arm=rb_free_rid"], 0,
     'PASS phys2d_events rb_free_rid entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=(0.000128, -4.56002) next_srv=<null> late_node=(0.000128, -4.56002) node_write_stuck=false node_follows_srv=false valid_after=true cb_freed=true'),
    ("phys2d_events_rb_dss_in_cb", "phys2d_events.gd", ["--arm=rb_dss_in_cb"], 0,
     'PASS phys2d_events rb_dss_in_cb entry1_frame=1 cb_count=2 cb_colliders=1 cb_srv_read=- cb_node_unchanged=- cb_node_read=- cb_srv_before=- next_node=(0.000128, -4.672004) next_srv=(0.000128, -4.672004) late_node=(0.000128, -4.699955) node_write_stuck=false node_follows_srv=false valid_after=true cb_dss_null=false cb_q_hits=1'),
    ("phys2d_events_area_monitoring_direct", "phys2d_events.gd", ["--arm=area_monitoring_direct"], 0,
     'PASS phys2d_events area_monitoring_direct entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=true cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0'),
    ("phys2d_events_area_monitoring_deferred", "phys2d_events.gd", ["--arm=area_monitoring_deferred"], 0,
     'PASS phys2d_events area_monitoring_deferred entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=true cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=false entries=1 exits=1'),
    ("phys2d_events_area_free_rid", "phys2d_events.gd", ["--arm=area_free_rid"], 0,
     'PASS phys2d_events area_free_rid entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=true cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -2.911111) next_srv=<null> late_node=(0.0, -2.911111) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=1'),
    ("phys2d_events_area_queue_free", "phys2d_events.gd", ["--arm=area_queue_free"], 0,
     'PASS phys2d_events area_queue_free entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=true cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=<dead> next_srv=<dead> late_node=<dead> node_write_stuck=false node_follows_srv=false valid_after=false post_monitoring=true entries=1 exits=1'),
    ("phys2d_events_area_srv_set_state", "phys2d_events.gd", ["--arm=area_srv_set_state"], 0,
     'PASS phys2d_events area_srv_set_state entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=(0.0, -2.911111) cb_srv_read=(500.0, 500.0) cb_node_read=- next_node=(500.0, 502.176) next_srv=(500.0, 502.176) late_node=(500.0, 521.7144) node_write_stuck=false node_follows_srv=true valid_after=true post_monitoring=true entries=1 exits=1'),
    ("phys2d_events_area_node_position", "phys2d_events.gd", ["--arm=area_node_position"], 0,
     'PASS phys2d_events area_node_position entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=(600.0, 600.0) next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0'),
    ("phys2d_events_area_dss_in_cb", "phys2d_events.gd", ["--arm=area_dss_in_cb"], 0,
     'PASS phys2d_events area_dss_in_cb entry1_frame=1 cb_cls=RigidBody2D cb_monitoring=true cb_readback=- cb_queued=- cb_freed=- cb_srv_before=- cb_srv_read=- cb_node_read=- next_node=(0.0, -0.735148) next_srv=(0.0, -0.735148) late_node=(0.0, 18.80326) node_write_stuck=false node_follows_srv=false valid_after=true post_monitoring=true entries=1 exits=0 cb_dss_null=false cb_q_hits=1'),
    # r80: RigidBody2D CCD + the motion-query family — continuous_cd
    # {disabled,cast_ray,cast_shape} tunneling lattice, body_test_motion /
    # move_and_collide / test_move, direct-space-state sweep-vs-pose split,
    # and contact-materialization / body-state windows.
    # Pinned from r80-scout §1.4 (28 arms, measured x3 byte-stable).
    # Same ordering constraint as the r79 block above: inserted ahead of the
    # crash/descendant tail — probe_descendant_pipe_eof requires
    # detached_descendant_orphaned_alive within the descendant's `sleep 8`
    # lifetime, so no CASES rows may sit between
    # descendant_pipe_detached_control and the meta probes.
    ("phys2d_motion_ccd_ladder", "phys2d_motion.gd", ["--arm=ccd_ladder"], 0,
     "PASS phys2d_motion ccd_ladder vels=[600.0, 1150.0, 1200.0, 2000.0, 2400.0, 3000.0, 3600.0] entries=17 d_cross=[0, 0, 0, 0, 1, 0, 1] d_x=[90.3, 90.3, 90.3, 90.3, 1169.494, 90.3, 1754.241] d_vx=[0.0, 0.0, 0.0, 0.0, 2282.856, 0.0, 3424.283] d_ccd=0 r_cross=[0, 0, 0, 0, 0, 0, 0] r_x=[90.16, 90.16, 90.16, 90.16, 90.16, 90.16, 90.16] r_vx=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] r_ccd=1 s_cross=[0, 0, 0, 0, 1, 0, 1] s_x=[90.3, 90.3, 90.3, 90.3, 1169.494, 90.3, 1754.241] s_vx=[0.0, 0.0, 0.0, 0.0, 2282.856, 0.0, 3424.283] s_ccd=2"),
    ("phys2d_motion_ccd_gap", "phys2d_motion.gd", ["--arm=ccd_gap"], 0,
     "PASS phys2d_motion ccd_gap v=2400 box16x16 gap12 d_cross=1 d_hit=0 d_x=1169.494 r_cross=0 r_hit=2 r_x=90.157 s_cross=1 s_hit=0 s_x=1169.494"),
    ("phys2d_motion_ccd_spin", "phys2d_motion.gd", ["--arm=ccd_spin"], 0,
     "PASS phys2d_motion ccd_spin w=90deg_per_step bar8x128 wall20x4@(40,+40) d_hit=0 d_rot=308.05 d_ccd=0 r_hit=0 r_rot=308.05 r_ccd=1 s_hit=0 s_rot=308.05 s_ccd=2 endposes=[308.05, 308.05, 308.05] endpose_overlap=[1, 1, 1]"),
    ("phys2d_motion_ccd_edge", "phys2d_motion.gd", ["--arm=ccd_edge"], 0,
     "PASS phys2d_motion ccd_edge v=2400 circle8@y14 wall4x10@[0,10] d_cross=1 d_hit=0 d_pos=(1169.4938,814.0000) r_cross=1 r_hit=0 r_pos=(1169.4938,1614.0000) s_cross=1 s_hit=0 s_pos=(1169.4938,2414.0000) w[hit=true travel=(1.9531,0.0000) rem=(18.0469,0.0000) pt=(98.0000,805.0000) n=(-1.0000,0.0000) depth=0.0704 sf=0.0977 uf=0.1035 cv=(0.0000,0.0000) cls=StaticBody2D]"),
    ("phys2d_motion_btm_from", "phys2d_motion.gd", ["--arm=btm_from"], 0,
     "PASS phys2d_motion btm_from body@(0,1000) wall@200 no_from[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] with_from[hit=false travel=(400.0000,0.0000) rem=(0.0000,0.0000)] bodypos=(0.0000,1000.0000)"),
    ("phys2d_motion_btm_hit", "phys2d_motion.gd", ["--arm=btm_hit"], 0,
     "PASS phys2d_motion btm_hit hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(0.0000,0.0000)"),
    ("phys2d_motion_btm_embed", "phys2d_motion.gd", ["--arm=btm_embed"], 0,
     "PASS phys2d_motion btm_embed rec_off[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] rec_on[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] rec_on_sepray[hit=true travel=(-6.9633,0.0000) rem=(50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] away_off[hit=true travel=(-6.9633,0.0000) rem=(-50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] away_on[hit=true travel=(-6.9633,0.0000) rem=(-50.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D]"),
    ("phys2d_motion_btm_margin", "phys2d_motion.gd", ["--arm=btm_margin"], 0,
     "PASS phys2d_motion btm_margin m0.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m0.08[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m1.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D] m4.0[hit=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=4.2813 sf=0.4375 uf=0.4414 cv=(0.0000,0.0000) cls=StaticBody2D]"),
    ("phys2d_motion_btm_from2", "phys2d_motion.gd", ["--arm=btm_from2"], 0,
     "PASS phys2d_motion btm_from2 n1[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] n2[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] srv_tele[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] ident_from[hit=true travel=(187.5000,0.0000) rem=(212.5000,0.0000) pt=(198.0000,0.0000) n=(-1.0000,0.0000) depth=1.0626 sf=0.4688 uf=0.4727 cv=(0.0000,0.0000) cls=StaticBody2D] with_from3600[hit=false travel=(400.0000,0.0000) rem=(0.0000,0.0000)] b1pos=(0.0000,3000.0000) b3pos=(0.0000,0.0000)"),
    ("phys2d_motion_btm_recflag", "phys2d_motion.gd", ["--arm=btm_recflag"], 0,
     "PASS phys2d_motion btm_recflag zero_off[hit=true travel=(-6.9633,0.0000) rem=(0.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] zero_on[hit=true travel=(-6.9633,0.0000) rem=(0.0000,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] tiny_off[hit=true travel=(-6.9633,0.0000) rem=(0.0100,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D] tiny_on[hit=true travel=(-6.9633,0.0000) rem=(0.0100,0.0000) pt=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0368 sf=0.0 uf=0.0 cv=(0.0000,0.0000) cls=StaticBody2D]"),
    ("phys2d_motion_mac_hit", "phys2d_motion.gd", ["--arm=mac_hit"], 0,
     "PASS phys2d_motion mac_hit travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(87.5000,0.0000)"),
    ("phys2d_motion_mac_miss", "phys2d_motion.gd", ["--arm=mac_miss"], 0,
     "PASS phys2d_motion mac_miss col=null bodypos=(60.0000,0.0000)"),
    ("phys2d_motion_tm_hit", "phys2d_motion.gd", ["--arm=tm_hit"], 0,
     "PASS phys2d_motion tm_hit ret=true travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(0.0000,0.0000)"),
    ("phys2d_motion_mac_test_only", "phys2d_motion.gd", ["--arm=mac_test_only"], 0,
     "PASS phys2d_motion mac_test_only col1=travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos_after_test=(0.0000,0.0000) srv_after_test=(0.0000,0.0000) col2=hit pos_after_real=(87.5000,0.0000)"),
    ("phys2d_motion_mac_nodecomp", "phys2d_motion.gd", ["--arm=mac_nodecomp"], 0,
     "PASS phys2d_motion mac_nodecomp travel=(87.5000,-87.5000) rem=(112.5000,-112.5000) pos=(98.0000,-88.2812) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D bodypos=(87.5000,-87.5000)"),
    ("phys2d_motion_mac_chain", "phys2d_motion.gd", ["--arm=mac_chain"], 0,
     "PASS phys2d_motion mac_chain h0[t=(87.5000,-87.5000) r=(112.5000,-112.5000) n=(-1.0000,0.0000) pos=(87.5000,-87.5000)] h1[t=(0.0000,-10.3271) r=(0.0000,-102.1729) n=(0.0000,1.0000) pos=(87.5000,-97.8271)] n2=null pos=(87.5014,-97.8271)"),
    ("phys2d_motion_mac_maxcol", "phys2d_motion.gd", ["--arm=mac_maxcol"], 0,
     "PASS phys2d_motion mac_maxcol callv5=null bodypos=(0.0000,0.0000)"),
    ("phys2d_motion_mac_rigid", "phys2d_motion.gd", ["--arm=mac_rigid"], 0,
     "PASS phys2d_motion mac_rigid col=null pos_now=(60.0000,0.0000) pos_late=(60.0000,0.0000) srv_late=(60.0000,0.0000) hitcol=travel=(87.5000,0.0000) rem=(112.5000,0.0000) pos=(98.0000,900.0000) n=(-1.0000,0.0000) depth=0.3613 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D hpos_now=(87.5000,900.0000) hpos_late=(87.5000,900.0000) hsrv_late=(87.5000,900.0000)"),
    ("phys2d_motion_mac_embed", "phys2d_motion.gd", ["--arm=mac_embed"], 0,
     "PASS phys2d_motion mac_embed rec_off[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,0.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,0.0000)] rec_on[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,600.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,600.0000)] prop5_argdefault[travel=(-7.0294,0.0000) rem=(50.0000,0.0000) pos=(98.0000,1200.0000) n=(-1.0000,0.0000) depth=1.0507 angle=1.5708 cv=(0.0000,0.0000) cls=StaticBody2D pos=(88.9706,1200.0000)]"),
    ("phys2d_motion_dss_motion", "phys2d_motion.gd", ["--arm=dss_motion"], 0,
     "PASS phys2d_motion dss_motion cm=[0.44921875, 0.453125] cm_away=[1.0, 1.0] cm_zero=[1.0, 1.0] cs_n=2 is_n=1 ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(98.0000,0.0000) n=(-1.0000,0.0000) lv=(0.0000,0.0000) cls=null} ri_zero={}"),
    ("phys2d_motion_dss_embed", "phys2d_motion.gd", ["--arm=dss_embed"], 0,
     "PASS phys2d_motion dss_embed cm_toward=[1.0, 1.0] cm_away=[1.0, 1.0] cs_n=2 cs_pts=[(88.0, 0.0), (102.0, 0.0)] is_n=1 ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(102.0000,0.0000) n=(1.0000,0.0000) lv=(0.0000,0.0000) cls=null}"),
    ("phys2d_motion_dss_shapes", "phys2d_motion.gd", ["--arm=dss_shapes"], 0,
     "PASS phys2d_motion dss_shapes ray_hit={keys=[\"collider\", \"collider_id\", \"normal\", \"position\", \"rid\", \"shape\"] cls=StaticBody2D pos=(98.0000,0.0000) n=(-1.0000,0.0000)} ray_miss={} ri={keys=[\"collider_id\", \"linear_velocity\", \"normal\", \"point\", \"rid\", \"shape\"] pt=(303.9900,-8.0000) n=(0.0000,-1.0000) lv=(119.6003,0.0000) cls=null} is_n=1 is0={keys=[\"collider\", \"collider_id\", \"rid\", \"shape\"] cls=RigidBody2D} cs_full=2 cs_cap1=2"),
    ("phys2d_motion_dss_purity", "phys2d_motion.gd", ["--arm=dss_purity"], 0,
     "PASS phys2d_motion dss_purity equal=true before=[[X: (0.955337, 0.29552), Y: (-0.29552, 0.955337), O: (5.0, 7.0)], (150.0, -40.0), 0.5, 4294967295, true, false, []] after=[[X: (0.955337, 0.29552), Y: (-0.29552, 0.955337), O: (5.0, 7.0)], (150.0, -40.0), 0.5, 4294967295, true, false, []]"),
    ("phys2d_motion_dss_wrongarg", "phys2d_motion.gd", ["--arm=dss_wrongarg"], 0,
     "PASS phys2d_motion dss_wrongarg is=0 cm=[] ri={  } cs=0 is_null=0 ray_null={  } pt_null=0"),
    ("phys2d_motion_cont_windows", "phys2d_motion.gd", ["--arm=cont_windows"], 0,
     "PASS phys2d_motion cont_windows entry_f=4 exit_f=6 in_cb=[2, 1] pp_entry=[2, 1] proc_entry=[2, 1] in_exit_cb=[0, 1] pp_exit=[0, 0] proc_exit=[0, 0]"),
    ("phys2d_motion_cont_cap", "phys2d_motion.gd", ["--arm=cont_cap"], 0,
     "PASS phys2d_motion cont_cap capped=[count=1 arr=1] uncapped=[count=4 arr=2 cls=StaticBody2D,StaticBody2D]"),
    ("phys2d_motion_bds_windows", "phys2d_motion.gd", ["--arm=bds_windows"], 0,
     "PASS phys2d_motion bds_windows oop=obj cnt=0 in_cb={ \"obj\": true, \"count\": 2 } in_phase=obj cnt=2 proc=obj cnt=2 integ_first={ \"count\": 0, \"lv\": (0.0, 65.33334) } integ_last={ \"count\": 2, \"lv\": (0.0383, -0.006104) }"),
    ("phys2d_motion_cont_persist", "phys2d_motion.gd", ["--arm=cont_persist"], 0,
     "PASS phys2d_motion cont_persist entry_f=4 exit_f=5 seq[frame,size]=[[5, 1], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [11, 0]]"),
    # r81: Godot-4 2D joint lattice + collision layer/mask lattice — the
    # Joint2D/Joint server family, the layer/mask detection-vs-response split,
    # and the Area2D gates. Pinned from r81-scout §1.1-1.3 (20 arms, measured x3
    # byte-stable); fixture `phys2d_joints.gd` is the scout probe
    # (`corpus/live/r81-scout/proj/phys2d_jl.gd`, sha256 50da7ae5…) with the
    # comment header conformed and the family token renamed to the assigned
    # fixture name; every measured value is verbatim (see r81-author report).
    # Same ordering constraint as the r79/r80 blocks above: inserted ahead of the
    # crash/descendant tail — probe_descendant_pipe_eof requires
    # detached_descendant_orphaned_alive within the descendant's `sleep 8`
    # lifetime, so no CASES rows may sit between
    # descendant_pipe_detached_control and the meta probes.
    ("phys2d_joints_joint_census", "phys2d_joints.gd", ["--arm=joint_census"], 0,
     'PASS phys2d_joints joint_census cls=["Joint2D[\\"bias\\", \\"disable_collision\\", \\"node_a\\", \\"node_b\\"]", "PinJoint2D[\\"Angular Limit\\", \\"Motor\\", \\"angular_limit_enabled\\", \\"angular_limit_lower\\", \\"angular_limit_upper\\", \\"motor_enabled\\", \\"motor_target_velocity\\", \\"softness\\"]", "GrooveJoint2D[\\"initial_offset\\", \\"length\\"]", "DampedSpringJoint2D[\\"damping\\", \\"length\\", \\"rest_length\\", \\"stiffness\\"]"] srv=["damped_spring_joint_get_param(joint,param)", "damped_spring_joint_set_param(joint,param,value)", "joint_clear(joint)", "joint_create()", "joint_disable_collisions_between_bodies(joint,disable)", "joint_get_param(joint,param)", "joint_get_type(joint)", "joint_is_disabled_collisions_between_bodies(joint)", "joint_make_damped_spring(joint,anchor_a,anchor_b,body_a,body_b)", "joint_make_groove(joint,groove1_a,groove2_a,anchor_b,body_a,body_b)", "joint_make_pin(joint,anchor,body_a,body_b)", "joint_set_param(joint,param,value)", "pin_joint_get_flag(joint,flag)", "pin_joint_get_param(joint,param)", "pin_joint_set_flag(joint,flag,enabled)", "pin_joint_set_param(joint,param,value)"] consts=["DAMPED_SPRING_DAMPING=2", "DAMPED_SPRING_REST_LENGTH=0", "DAMPED_SPRING_STIFFNESS=1", "JOINT_PARAM_BIAS=0", "JOINT_PARAM_MAX_BIAS=1", "JOINT_PARAM_MAX_FORCE=2", "JOINT_TYPE_DAMPED_SPRING=2", "JOINT_TYPE_GROOVE=1", "JOINT_TYPE_MAX=3", "JOINT_TYPE_PIN=0", "PIN_JOINT_FLAG_ANGULAR_LIMIT_ENABLED=0", "PIN_JOINT_FLAG_MOTOR_ENABLED=1", "PIN_JOINT_LIMIT_LOWER=2", "PIN_JOINT_LIMIT_UPPER=1", "PIN_JOINT_MOTOR_TARGET_VELOCITY=3", "PIN_JOINT_SOFTNESS=0"] live=["unset_type=3", "unset_dis=true", "unset_bias=0.0000", "max_bias=340282001837565597733306976381245063168.0", "max_force=340282001837565597733306976381245063168.0", "pin_type=0", "pin_soft=0.0000", "pin_lu=0.0000", "pin_ll=0.0000", "pin_mtv=0.0000", "pin_flag_ang=false", "pin_flag_motor=false", "pin_bias=0.0000", "pin_dis=true", "groove_type=1", "groove_bias=0.0000", "spring_type=2", "spring_rest=200.0000", "spring_stiff=20.0000", "spring_damp=1.5000", "spring_dis=true"]'),
    ("phys2d_joints_joint_unset_refusal", "phys2d_joints.gd", ["--arm=joint_unset_refusal"], 0,
     "PASS phys2d_joints joint_unset_refusal before=[0.0, 0.0, 0.0, 0.0, false, false, 0.0, 0.0, 0.0] type_pin=0 after=[0.0, 0.0, 0.0, 0.0, false, false, 0.0, 0.0, 0.0] cleared_type=3 spring_after=[200.0, 20.0, 1.5]"),
    ("phys2d_joints_joint_pin_tiers", "phys2d_joints.gd", ["--arm=joint_pin_tiers"], 0,
     "PASS phys2d_joints joint_pin_tiers n_rel=(114.5184,164.2985) s_rel=(114.5184,164.2983) n_dist=200.2710 s_dist=200.2708 n2_dist=200.2708 n_type=0 s_type=0 n_np=/root/PA n_bias_prop=0.0000 n_bias_srv=0.0000 s_bias_srv=0.0000 n_soft_prop=0.0000 n_soft_srv=0.0000 s_soft_srv=0.0000 n_dis=true s_dis=true n_flag_ang=false n_flag_motor=false"),
    ("phys2d_joints_joint_pin_clear", "phys2d_joints.gd", ["--arm=joint_pin_clear"], 0,
     "PASS phys2d_joints joint_pin_clear pre=(176.7844,94.1389) pre_dist=200.2869 pre_vel=(-132.8277,256.8133) type_pre=0 type_post=3 bias_post=0.0000 soft_post=0.0000 post=(112.0589,219.2813) post_dist=246.2549 post_vel=(-126.3444,244.2782) type_rearm=0 end=(7.4813,246.2695) end_dist=246.3831"),
    ("phys2d_joints_joint_node_clear", "phys2d_joints.gd", ["--arm=joint_node_clear"], 0,
     "PASS phys2d_joints joint_node_clear pre=(176.7844,94.1389) type_pre=0 nudge_type=0 nudge_pos=(0.0000,100.0000) after_nudge=(110.6721,166.9125) dn_old=200.2710 dn_new=131.3346 dn_old2=200.2701 dn_new2=129.3275 type_post=3 post=(35.0778,218.2878) nudge2_type=3 end=(-38.0363,267.9774) end_d_old=270.6633 end_d_new=172.2300 valid=true na=true nb=true"),
    ("phys2d_joints_joint_freed_rid", "phys2d_joints.gd", ["--arm=joint_freed_rid"], 0,
     "PASS phys2d_joints joint_freed_rid pre=(176.7844,94.1389) type_freed=0 bias_freed=-1.0000 soft_freed=0.0000 type_remade=0 bias_remade=-1.0000 post=(112.0589,219.2813) late=(91.1935,259.6230) b_frozen=false b_valid=true"),
    ("phys2d_joints_joint_node_freed_rid", "phys2d_joints.gd", ["--arm=joint_node_freed_rid"], 0,
     "PASS phys2d_joints joint_node_freed_rid pre=(176.7844,94.1389) type_freed=0 rid_same=true type_again=0 valid=true post=(112.0589,219.2813) type_nudge=0 end=(50.4926,338.3154) end_dist=342.0626 b_frozen=false"),
    ("phys2d_joints_joint_spring_env", "phys2d_joints.gd", ["--arm=joint_spring_env"], 0,
     "PASS phys2d_joints joint_spring_env s0d0=(100.00,-58.47) s0d1=(90.11,-56.02) s0d4=(85.67,-55.37) s4d0=(75.96,-53.84) s4d1=(80.94,-54.93) s4d4=(83.18,-55.18) s16d0=(24.36,-45.70) s16d1=(58.15,-52.89) s16d4=(76.15,-54.72) s64d0=(-59.85,-63.83) s64d1=(8.37,-55.40) s64d4=(53.55,-53.88) nojoint=(100.00,-58.47) rb_s0d0=[50.0000,0.0000,0.0000] rb_s64d4=[50.0000,64.0000,4.0000] node_props=[l=100.0,r=50.0,s=64.0,d=1.0] node_srv=[50.0000,64.0000,1.0000] node_type=2 node_pos=(0.00,42.92)"),
    ("phys2d_joints_joint_pin_params", "phys2d_joints.gd", ["--arm=joint_pin_params"], 0,
     "PASS phys2d_joints joint_pin_params soft0[pos=(114.52,164.30) dist=200.2710 rot=0.9622 rb=[0.0000,0.0000,false,0.0000,0.0000,false,0.0000]] soft1[pos=(115.62,164.18) dist=200.8065 rot=0.9577 rb=[1.0000,0.0000,false,0.0000,0.0000,false,0.0000]] soft4[pos=(118.79,163.79) dist=202.3308 rot=0.9446 rb=[4.0000,0.0000,false,0.0000,0.0000,false,0.0000]] motor[pos=(113.18,165.18) dist=200.2333 rot=0.9722 rb=[0.0000,3.0000,true,0.0000,0.0000,false,0.0000]] limit[pos=(119.57,161.60) dist=201.0246 rot=0.8871 rb=[0.0000,0.0000,false,-0.5000,0.5000,true,0.0000]] bias1[pos=(114.08,164.34) dist=200.0545 rot=0.9640 rb=[0.0000,0.0000,false,0.0000,0.0000,false,1.0000]] motor_spin[pos=(200.00,0.00) dist=200.0000 rot=1.7255 rb=[0.0000,3.0000,true,0.0000,0.0000,false,0.0000]] limit_spin[pos=(200.00,0.00) dist=200.0000 rot=0.1694 rb=[0.0000,0.0000,false,-0.5000,0.5000,true,0.0000]]"),
    ("phys2d_joints_joint_node_anchor", "phys2d_joints.gd", ["--arm=joint_node_anchor"], 0,
     "PASS phys2d_joints joint_node_anchor created_at_100[d0=271.3221 d0b=272.7762 d100=223.8021 d100b=223.8015] moved_before_step[d0=200.2708 d0b=200.2699 d100=131.3344 d100b=129.3274] p2_pos=(0.0000,2100.0000)"),
    ("phys2d_joints_joint_groove", "phys2d_joints.gd", ["--arm=joint_groove"], 0,
     "PASS phys2d_joints joint_groove gst_node=(50.00,50.00) gst_srv_center=(0.01,50.00) gst_srv_jpos=(50.00,50.00) gnode=(-48.41,21.88) gsmallA=(-63.01,92.61) gsmallB=(-57.68,-40.85) gend_far=(0.00,5.99) gend_far_vel=(0.00,16.06) gend_near=(0.00,19.70) gend_near_vel=(-0.00,0.00) gnode_props=[l=100.0,off=0.0] gnode_type=1 j3_type=1 gnode_a_dis=true gsrv_a_dis=true"),
    ("phys2d_joints_joint_disable_coll", "phys2d_joints.gd", ["--arm=joint_disable_coll"], 0,
     "PASS phys2d_joints joint_disable_coll dis_true[acnt=0 bcnt=0 d=10.0000 a_pos=(0.00,0.00) b_pos=(10.00,0.00) rb=true] dis_false[acnt=1 bcnt=1 d=17.0493 a_pos=(-3.40,-1.45) b_pos=(13.40,1.45) rb=false] groove_default[rb=[true, true, true] acnt=0 bcnt=0 d=10.0000 a_pos=(0.00,0.00) b_pos=(10.00,0.00)] node_prop_default=[true, true, true] node_prop_false=[false, false, false] node_pos=[(-3.40,-1.45),(13.40,1.45)] static_default[rb=true dcnt=1 d_pos=(17.43,0.24)] static_enabled[rb=false dcnt=1 d_pos=(17.43,0.24)]"),
    ("phys2d_joints_layer_or_table", "phys2d_joints.gd", ["--arm=layer_or_table"], 0,
     "PASS phys2d_joints layer_or_table ctl_both[wl=1 wm=2 bl=2 bm=1]ent=46 ext=-1 x=88.2989 cross=0 cnt=2 body_only[wl=1 wm=0 bl=2 bm=1]ent=46 ext=-1 x=88.2989 cross=0 cnt=2 wall_only[wl=1 wm=2 bl=2 bm=0]ent=46 ext=59 x=114.0952 cross=1 cnt=0 neither[wl=1 wm=0 bl=2 bm=0]ent=-1 ext=-1 x=114.0952 cross=1 cnt=0"),
    ("phys2d_joints_layer_zero_table", "phys2d_joints.gd", ["--arm=layer_zero_table"], 0,
     "PASS phys2d_joints layer_zero_table z_body_l0[wl=1 wm=1 bl=0 bm=1]ent=46 ext=-1 x=88.2989 cross=0 cnt=2 z_body_m0[wl=1 wm=1 bl=1 bm=0]ent=46 ext=59 x=114.0952 cross=1 cnt=0 z_wall_l0m0[wl=0 wm=0 bl=1 bm=1]ent=-1 ext=-1 x=114.0952 cross=1 cnt=0 z_wall_l0m1[wl=0 wm=1 bl=1 bm=1]ent=46 ext=59 x=114.0952 cross=1 cnt=0"),
    ("phys2d_joints_layer_dyn_pair", "phys2d_joints.gd", ["--arm=layer_dyn_pair"], 0,
     "PASS phys2d_joints layer_dyn_pair a_scans_only[va=(-112.2546,0.0000) vb=(-112.2546,0.0000) xa=-37.02 xb=-17.32 crossed=0 acnt=2 bcnt=2 ent_a=11 ent_b=11] b_scans_only[va=(112.2546,0.0000) vb=(112.2546,0.0000) xa=77.32 xb=97.02 crossed=0 acnt=2 bcnt=2 ent_a=11 ent_b=11] both_scan[va=(0.0000,0.0000) vb=(0.0000,0.0000) xa=20.15 xb=39.85 crossed=0 acnt=2 bcnt=2 ent_a=11 ent_b=11] neither[va=(112.2546,0.0000) vb=(-112.2546,0.0000) xa=77.32 xb=-17.32 crossed=1 acnt=0 bcnt=0 ent_a=-1 ent_b=-1]"),
    ("phys2d_joints_layer_flip_mid", "phys2d_joints.gd", ["--arm=layer_flip_mid"], 0,
     "PASS phys2d_joints layer_flip_mid body_mask_off flip_f=40 x_at=88.2972 m_pre=1 wl_pre=1 cnt=[2,2,2] ent=23 ext=-1 x_end=88.2882 vx_end=-0.01 mask=0 wl=1 | wall_layer_off flip_f=40 x_at=88.2972 m_pre=1 wl_pre=1 cnt=[2,2,2] ent=23 ext=-1 x_end=88.2882 vx_end=-0.01 mask=1 wl=0 | mask_off_move flip_f=40 x_at=88.2972 m_pre=1 wl_pre=1 cnt=[2,2,2] ent=23 ext=46 x_end=242.9471 vx_end=224.51 mask=0 wl=1 | body_mask_on flip_f=10 x_at=39.6352 m_pre=0 wl_pre=1 cnt=[0,0,0] ent=23 ext=-1 x_end=88.2882 vx_end=-0.01 mask=1 wl=1 | wall_layer_on flip_f=10 x_at=39.6352 m_pre=1 wl_pre=0 cnt=[0,0,0] ent=23 ext=-1 x_end=88.2882 vx_end=-0.01 mask=1 wl=1"),
    ("phys2d_joints_layer_flip_cb", "phys2d_joints.gd", ["--arm=layer_flip_cb"], 0,
     "PASS phys2d_joints layer_flip_cb direct ent=23 ext=-1 cb_cnt=2 after_write=0 x_end=88.6725 mask=0 | deferred ent=23 ext=-1 cb_cnt=2 after_write=1 x_end=88.6725 mask=0"),
    ("phys2d_joints_area_lattice", "phys2d_joints.gd", ["--arm=area_lattice"], 0,
     "PASS phys2d_joints area_lattice mon_a_only[am=true amab=false bm=false bmab=true a_ent=1 b_ent=0] mon_b_only[am=true amab=true bm=true bmab=false a_ent=0 b_ent=1] neither_mon[am=false amab=true bm=false bmab=true a_ent=0 b_ent=0] neither_mable[am=true amab=false bm=true bmab=false a_ent=0 b_ent=0] both_mutual[am=true amab=true bm=true bmab=true a_ent=1 b_ent=1] layer_off[am=true amab=true bm=true bmab=true a_ent=0 b_ent=0] a_scans_b[am=true amab=true bm=true bmab=true a_ent=1 b_ent=0] b_scans_a[am=true amab=true bm=true bmab=true a_ent=0 b_ent=1]"),
    ("phys2d_joints_area_body_gate", "phys2d_joints.gd", ["--arm=area_body_gate"], 0,
     "PASS phys2d_joints area_body_gate area_scans[am=true al=1 amask=2 bl=2 bm=0 ent=0] area_blind[am=true al=1 amask=1 bl=2 bm=0 ent=-1] area_scans_bmask[am=true al=1 amask=2 bl=2 bm=1 ent=0] area_blind_bmask[am=true al=1 amask=1 bl=2 bm=1 ent=-1]"),
    ("phys2d_joints_area_entry_order", "phys2d_joints.gd", ["--arm=area_entry_order"], 0,
     'PASS phys2d_joints area_entry_order created1=["o", "i", "b"] areas_first=["ob@0", "oa@0", "ib@0", "ia@0"] created2=["b", "o", "i"] body_first=["ob@0", "oa@0", "ib@0", "ia@0"]'),
    # r85: CanvasLayer / Viewport / Camera2D transform lattice — 15 arms,
    # measured x3 byte-stable (r85-scout). Insert ahead of the crash/descendant tail:
    # probe_descendant_pipe_eof requires detached_descendant_orphaned_alive within the
    # descendant's `sleep 8` lifetime, so no CASES rows may sit between
    # descendant_pipe_detached_control and the meta probes.
    # Signature literals are repr()-generated: several arms carry quote-heavy
    # payloads (dict/list renderings) that a hand-quoted literal would corrupt.
    ('camera_proc_cam_comp', 'camera_proc.gd', ['--arm=cam_comp'], 0,
     'PASS camera_proc cam_comp vp2=(64.0, 64.0) nocam=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) s0=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) s1=(1.0000,-0.0000;-0.0000,1.0000;-68.0000,-18.0000) s2=(2.0000,-0.0000;-0.0000,2.0000;-168.0000,-68.0000) s3=(2.0000,-0.0000;-0.0000,2.0000;-188.0000,-108.0000) s4=(2.0000,-0.0000;-0.0000,2.0000;-220.0000,-140.0000) s5=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) n3=(2.0000,0.0000;-0.0000,2.0000;412.0000,292.0000) comp=(2.0000,0.0000;-0.0000,2.0000;412.0000,292.0000) n4=(2.0000,0.0000;-0.0000,2.0000;380.0000,260.0000) comp4=(2.0000,0.0000;-0.0000,2.0000;380.0000,260.0000) t0=0.0000,0.0000 c0=0.0000,0.0000 t3=100.0000,50.0000 c3=110.0000,70.0000 t4=100.0000,50.0000 c4=126.0000,86.0000 eq[cam_vp=1 screen=1 comp=1 comp4=1 inv=1] probe=32.0000,32.0000'),
    ('camera_proc_cam_zoom_center', 'camera_proc.gd', ['--arm=cam_zoom_center'], 0,
     'PASS camera_proc cam_zoom_center zoom=1.5 pos=10.5,-3.25 ct=(1.5000,-0.0000;-0.0000,1.5000;16.2500,36.8750) screens=[16.2500,36.8750|32.0000,32.0000|166.2500,186.8750|5.3750,42.5000] center_world=10.5000,-3.2500 anchor_ok=1 dx=1.5000,0.0000 dy=0.0000,1.5000 sub60=-0.0250,0.0000 sub_dev=0.000001526 sub_ok=1 ct2=(1.5000,-0.0000;-0.0000,1.5000;16.2250,36.8750)'),
    ('camera_proc_cam_phase', 'camera_proc.gd', ['--arm=cam_phase'], 0,
     'PASS camera_proc cam_phase pc_idle=1 prio[o=100] A.w1[32.0000,32.0000>32.0000,32.0000] A.i1[22.0000,32.0000] A.w2[22.0000,32.0000>22.0000,32.0000] A.i2[12.0000,32.0000] A.w3[12.0000,32.0000>12.0000,32.0000] A.i3[2.0000,32.0000] A.next[2.0000,32.0000] B.w1[32.0000,32.0000>12.0000,32.0000] B.i1[12.0000,32.0000] B.w2[12.0000,32.0000>-8.0000,32.0000] B.i2[-8.0000,32.0000] B.w3[-8.0000,32.0000>-28.0000,32.0000] B.i3[-28.0000,32.0000] B.next[-28.0000,32.0000] C.w1[32.0000,32.0000>32.0000,32.0000] C.i1[2.0000,32.0000] C.w2[2.0000,32.0000>2.0000,32.0000] C.i2[-28.0000,32.0000] C.w3[-28.0000,32.0000>-28.0000,32.0000] C.i3[-58.0000,32.0000] C.next[-58.0000,32.0000] D.p1[32.0000,32.0000] D.w1[after=32.0000,32.0000] D.i1[-8.0000,32.0000] D.p2[-8.0000,32.0000] D.w2[after=-8.0000,32.0000] D.i2[-48.0000,32.0000] D.p3[-48.0000,32.0000] D.w3[after=-48.0000,32.0000] D.i3[-88.0000,32.0000] E.w1[after=32.0000,32.0000] E.o1[sees=32.0000,32.0000] E.i1[-18.0000,32.0000] E.w2[after=-18.0000,32.0000] E.o2[sees=-18.0000,32.0000] E.i2[-68.0000,32.0000] E.next[-68.0000,32.0000]'),
    ('camera_proc_cam_subpixel', 'camera_proc.gd', ['--arm=cam_subpixel'], 0,
     'PASS camera_proc cam_subpixel n=12 distinct=12 samples=[32.0000,32.0000|31.9833,31.9917|31.9667,31.9833|31.9500,31.9750|31.9333,31.9667|31.9167,31.9583|31.9000,31.9500|31.8833,31.9417|31.8667,31.9333|31.8500,31.9250|31.8333,31.9167|31.8167,31.9083] eq_exact=111111111111 eq_close=111111111111 zoom15=31.7000,31.8500 want15=31.7000,31.8500 z15_ok=1 zoom05=31.9000,31.9500 want05=31.9000,31.9500 z05_ok=1'),
    ('camera_proc_cam_space', 'camera_proc.gd', ['--arm=cam_space'], 0,
     'PASS camera_proc cam_space vpr=[P: (0.0, 0.0), S: (64.0, 64.0)] g0=(1.0000,0.0000;-0.0000,1.0000;300.0000,200.0000) g1=(1.0000,0.0000;-0.0000,1.0000;300.0000,200.0000) g_indep=1 ct0=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) ct1=(2.0000,-0.0000;-0.0000,2.0000;-168.0000,-68.0000) wc0=(1.0000,0.0000;-0.0000,1.0000;332.0000,232.0000) wc1=(2.0000,0.0000;-0.0000,2.0000;432.0000,332.0000) sc0=(1.0000,0.0000;0.0000,1.0000;332.0000,232.0000) sc1=(2.0000,0.0000;0.0000,2.0000;432.0000,332.0000) vx0=(1.0000,0.0000;0.0000,1.0000;32.0000,32.0000) vx1=(2.0000,0.0000;0.0000,2.0000;-168.0000,-68.0000) wc_eq=1 screen_eq=1 vp_eq=1 cl[has_final=1 final=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) lwc=(1.0000,0.0000;0.0000,1.0000;300.0000,200.0000) lsc=(1.0000,0.0000;0.0000,1.0000;300.0000,200.0000) lvx=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) l_indep=1] stretch[f2_final=(2.0000,0.0000;0.0000,2.0000;0.0000,0.0000) f2_ct=(2.0000,-0.0000;-0.0000,2.0000;-184.0000,-84.0000) f2_wc=(2.0000,0.0000;-0.0000,2.0000;416.0000,316.0000) f2_sc=(2.0000,0.0000;0.0000,2.0000;416.0000,316.0000) f2_vx=(4.0000,0.0000;0.0000,4.0000;-368.0000,-168.0000) vx_final_ct=1 sc_wc=1 layer_unscaled=1 half=16.0000,16.0000 restored=1]'),
    ('camera_proc_cl_stack', 'camera_proc.gd', ['--arm=cl_stack'], 0,
     'PASS camera_proc cl_stack cam=50.0000,0.0000 root_wc=82.0000,32.0000 layers=[L-1[in=1 wc=100.0000,0.0000 vx=0.0000,0.0000 fin=0.0000,0.0000]|L0[in=1 wc=100.0000,0.0000 vx=0.0000,0.0000 fin=0.0000,0.0000]|L7[in=1 wc=100.0000,0.0000 vx=0.0000,0.0000 fin=0.0000,0.0000]] t1[off=10.0000,20.0000 rot=0.5000 scale=1.0000,1.0000 xf=(0.8776,0.4794;-0.4794,0.8776;10.0000,20.0000)] t2[off=5.0000,5.0000 rot=0.5000 scale=1.0000,1.0000 xf=(0.8776,0.4794;-0.4794,0.8776;5.0000,5.0000)] t3[off=5.0000,5.0000 rot=0.5000 scale=2.0000,2.0000 xf=(1.7552,0.9589;-0.9589,1.7552;5.0000,5.0000)] wc7=(1.7552,0.9589;-0.9589,1.7552;180.5165,100.8851) expect7=(1.7552,0.9589;-0.9589,1.7552;180.5165,100.8851) comp7=1 nested[wc=100.0000,0.0000 isolated=1]'),
    ('camera_proc_cl_follow', 'camera_proc.gd', ['--arm=cl_follow'], 0,
     'PASS camera_proc cl_follow ct=(2.0000,-0.0000;-0.0000,2.0000;-168.0000,-68.0000) rows=[F0[en=0 in=1 sc=1.0 wc=100.0000,0.0000 fin=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000)]|F1[en=1 in=1 sc=1.0 wc=32.0000,-68.0000 fin=(2.0000,0.0000;0.0000,2.0000;-168.0000,-68.0000)]|F2[en=1 in=1 sc=0.5 wc=-68.0000,-68.0000 fin=(1.0000,0.0000;0.0000,1.0000;-168.0000,-68.0000)]|F3[en=1 in=1 sc=2.0 wc=232.0000,-68.0000 fin=(4.0000,0.0000;0.0000,4.0000;-168.0000,-68.0000)]] f2b[wc=52.0000,-28.0000 fin=(2.0000,0.0000;0.0000,2.0000;-148.0000,-28.0000)] moved[ct=(2.0000,-0.0000;-0.0000,2.0000;-568.0000,32.0000) wc=-348.0000,72.0000 fin=(2.0000,0.0000;0.0000,2.0000;-548.0000,72.0000)]'),
    ('camera_proc_cl_phase', 'camera_proc.gd', ['--arm=cl_phase'], 0,
     'PASS camera_proc cl_phase A.w1[cl=100.0000,0.0000 vp=32.0000,32.0000>cl=110.0000,0.0000 vp=32.0000,32.0000]A.i1[cl=110.0000,0.0000 vp=32.0000,32.0000]A.w2[cl=110.0000,0.0000 vp=32.0000,32.0000>cl=120.0000,0.0000 vp=32.0000,32.0000]A.i2[cl=120.0000,0.0000 vp=32.0000,32.0000]A.w3[cl=120.0000,0.0000 vp=32.0000,32.0000>cl=130.0000,0.0000 vp=32.0000,32.0000]A.i3[cl=130.0000,0.0000 vp=32.0000,32.0000]A.next[cl=130.0000,0.0000 vp=32.0000,32.0000]B.w1[cl=100.0000,0.0000>cl=105.0000,0.0000]B.i1[cl=105.0000,0.0000]B.w2[cl=105.0000,0.0000>cl=110.0000,0.0000]B.i2[cl=110.0000,0.0000]B.w3[cl=110.0000,0.0000>cl=115.0000,0.0000]B.i3[cl=115.0000,0.0000]B.next[cl=115.0000,0.0000] inv[wc=100.0000,0.0000 vp=32.0000,32.0000]'),
    ('camera_proc_cl_draworder', 'camera_proc.gd', ['--arm=cl_draworder'], 0,
     'PASS camera_proc cl_draworder seq=L7@pf1|L-1@pf1|L0@pf1|LR@pf1|LR@pf2|L7@pf2|L-1@pf2|L0@pf2|LR@pf3|L7@pf3|L-1@pf3|L0@pf3|LR@pf4|L7@pf4|L-1@pf4|L0@pf4 n=16 counts={ "L7": 4, "L-1": 4, "L0": 4, "LR": 4 } first=[L7,L-1,L0,LR] later=[LR,L7,L-1,L0] hidden_draws=0 hidden[in=1 vis=0 queued=3] creation_order=1 layer_sorted=0'),
    ('camera_proc_vp_worlds', 'camera_proc.gd', ['--arm=vp_worlds'], 0,
     'PASS camera_proc vp_worlds share[d_own=1 d_shares=0 s_shares=1 o_shares=0] pos[br=0.0007,76.3000 bs=40.0007,76.3000 bo=0.0000,207.9190 bd=0.0007,76.3000] contacts[br=0 bs=0 bo=0 bd=0] same_rest=1 shared_floor=1 own_fall=1'),
    ('camera_proc_vp_render_indep', 'camera_proc.gd', ['--arm=vp_render_indep'], 0,
     'PASS camera_proc vp_render_indep names=V0|V1|V2|ROOT pos=[0.0007,76.3003|0.0007,76.3003|0.0007,76.3003|0.0007,76.3003] eq_exact=1 eq_4dp=1 root_ct=30.8158,32.0000 v2cam[pos=0.4833,0.2417 zoom=2.4500,2.4500] cloff=29.0000,0.0000'),
    ('camera_proc_vp_subcam', 'camera_proc.gd', ['--arm=vp_subcam'], 0,
     'PASS camera_proc vp_subcam root_vpr=(64.0, 64.0) sub_vpr=(320.0, 180.0) r0=(1.0000,-0.0000;-0.0000,1.0000;32.0000,32.0000) s0=(1.0000,-0.0000;-0.0000,1.0000;120.0000,90.0000) r1=(1.0000,-0.0000;-0.0000,1.0000;-68.0000,32.0000) s1=(1.0000,-0.0000;-0.0000,1.0000;120.0000,90.0000) r2=(1.0000,-0.0000;-0.0000,1.0000;-68.0000,32.0000) s2=(1.0000,-0.0000;-0.0000,1.0000;80.0000,70.0000) cams[sv=1 root=1] iso[sub_only=1 root_only=1]'),
    ('camera_proc_par_layer', 'camera_proc.gd', ['--arm=par_layer'], 0,
     'PASS camera_proc par_layer cam=128.0000,0.0000 ms=0.5000,0.5000 mm=0.0000,0.0000 mo=0.0000,0.0000 rows=[p0[wc=32.0000,32.0000]|ms05[cam0 wc=32.0000,32.0000 lp=0.0000,0.0000]|cam64[wc=-32.0000,32.0000 lp=0.0000,0.0000]|cam128[wc=-96.0000,32.0000 lp=0.0000,0.0000]|mirror100[mm=100.0000,0.0000 cam128 wc=-96.0000,32.0000 lp=0.0000,0.0000]|cam150mirror[wc=-118.0000,32.0000 lp=0.0000,0.0000]|moff10[mo=10.0000,0.0000 wc=-118.0000,32.0000 lp=0.0000,0.0000]|has_pbg=1|pbg0[follow=0 wc=16.0000,16.0000 lp=16.0000,16.0000]|pbg64[wc=-16.0000,16.0000 lp=-16.0000,16.0000 fin=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000)]|pbg128[wc=-48.0000,16.0000 lp=-48.0000,16.0000]|pbgmirror[mm=100.0000,0.0000 wc=-48.0000,16.0000 lp=-48.0000,16.0000]|pbgmoff[mo=10.0000,0.0000 wc=-38.0000,16.0000 lp=-38.0000,16.0000]|pbgms1[wc=-96.0000,32.0000 lp=-96.0000,32.0000]|pbgms0[wc=0.0000,0.0000 lp=0.0000,0.0000]|pbgz2[ct=-224.0000,32.0000 wc=-112.0000,16.0000 lp=-112.0000,16.0000 ign=0]|cl_follow[wc=-96.0000,32.0000 lp=0.0000,0.0000]|cl_nofollow[wc=0.0000,0.0000 lp=0.0000,0.0000]]'),
    ('camera_proc_par_2d', 'camera_proc.gd', ['--arm=par_2d'], 0,
     'PASS camera_proc par_2d cam=150.0000,0.0000 rep=100.0000,0.0000x3 fv=1 so=118.0000,-32.0000 ign=0 rows=[d0[off=0.0000,0.0000 wc=16.0000,16.0000]|cam64[off=0.0000,0.0000 wc=-16.0000,16.0000]|ignore[off=0.0000,0.0000 wc=-16.0000,16.0000]|rep100x3[off=0.0000,0.0000 wc=-16.0000,16.0000]|cam150rep[off=0.0000,0.0000 wc=-59.0000,16.0000]|follow[off=0.0000,0.0000 wc=-59.0000,16.0000]|screen_off[off=0.0000,0.0000 wc=-59.0000,16.0000]]'),
    ('camera_proc_par_phase', 'camera_proc.gd', ['--arm=par_phase'], 0,
     'PASS camera_proc par_phase PL.w1[cam=32.0000,32.0000 pl=32.0000,32.0000 p2=16.0000,16.0000 pbl=16.0000,16.0000 pbc=16.0000,16.0000>cam=32.0000,32.0000 pl=32.0000,32.0000 p2=16.0000,16.0000 pbl=16.0000,16.0000 pbc=16.0000,16.0000]PL.i1[cam=-32.0000,32.0000 pl=-32.0000,32.0000 p2=-16.0000,16.0000 pbl=-16.0000,16.0000 pbc=-16.0000,16.0000]PL.w2[cam=-32.0000,32.0000 pl=-32.0000,32.0000 p2=-16.0000,16.0000 pbl=-16.0000,16.0000 pbc=-16.0000,16.0000>cam=-32.0000,32.0000 pl=-32.0000,32.0000 p2=-16.0000,16.0000 pbl=-16.0000,16.0000 pbc=-16.0000,16.0000]PL.i2[cam=-96.0000,32.0000 pl=-96.0000,32.0000 p2=-48.0000,16.0000 pbl=-48.0000,16.0000 pbc=-48.0000,16.0000]PL.next[cam=-96.0000,32.0000 pl=-96.0000,32.0000 p2=-48.0000,16.0000 pbl=-48.0000,16.0000 pbc=-48.0000,16.0000]'),
    ('phys2d_backends_census', 'phys2d_backends.gd', ['--arm=census'], 0,
     'PASS phys2d_backends census census self_cfg=[DEFAULT] hint2d=[DEFAULT,GodotPhysics2D,Dummy] hint3d=[DEFAULT,Jolt Physics,GodotPhysics3D,Dummy] jolt2d_ns=0 jolt3d_ns=32 PhysicsServer2DManager={own=[register_server,set_default_server],enum5=0} PhysicsServer3DManager={own=[register_server,set_default_server],enum5=0} ce=[GodotPhysicsServer2D=true,JoltPhysicsServer2D=false,GodotPhysicsServer3D=true,JoltPhysicsServer3D=false,JoltPhysicsDirectSpaceState2D=false]'),
    ('phys2d_backends_lattice', 'phys2d_backends.gd', ['--arm=lattice'], 0,
     'PASS phys2d_backends lattice lattice default{stored=[DEFAULT],has=true,dss=GodotPhysicsDirectSpaceState2D,valid=true,mv=pos,rc=0,errB=0} gp2d{stored=[GodotPhysics2D],has=true,dss=GodotPhysicsDirectSpaceState2D,valid=true,mv=pos,rc=0,errB=0} dummy{stored=[Dummy],has=true,dss=PhysicsDirectSpaceState2DDummy,valid=false,mv=zero,rc=0,errB=0} jolt{stored=[Jolt Physics],has=true,dss=GodotPhysicsDirectSpaceState2D,valid=true,mv=pos,rc=0,errB=0} garbage{stored=[garbage_xyz],has=true,dss=GodotPhysicsDirectSpaceState2D,valid=true,mv=pos,rc=0,errB=0} empty{stored=[],has=true,dss=GodotPhysicsDirectSpaceState2D,valid=true,mv=pos,rc=0,errB=0}'),
    ('phys2d_backends_jolt3d_live', 'phys2d_backends.gd', ['--arm=jolt3d_live'], 0,
     'PASS phys2d_backends jolt3d_live jolt3d_live jolt{stored3d=[Jolt Physics],dss3=JoltPhysicsDirectSpaceState3D,valid3=true,rc=0,errB=0} default{stored3d=[DEFAULT],dss3=GodotPhysicsDirectSpaceState3D,valid3=true,rc=0,errB=0}'),
    ('phys2d_backends_xcheck', 'phys2d_backends.gd', ['--arm=xcheck'], 0,
     'PASS phys2d_backends xcheck xcheck offered2d=[GodotPhysics2D,Dummy,Jolt Physics,garbage_xyz,] errs2d=[0,0,1,1,1] offered3d=[Jolt Physics,GodotPhysics3D,Dummy,garbage_xyz] errs3d=[0,0,0,1] at2d=set_default_server (servers/physics_2d/physics_server_2d.cpp:959) at3d=set_default_server (servers/physics_3d/physics_server_3d.cpp:1193) rc=0 errs_total=4'),
    ('phys2d_backends_gate_matrix', 'phys2d_backends.gd', ['--arm=gate_matrix'], 0,
     'PASS phys2d_backends gate_matrix gate_matrix thr_ok=1 def[A=ok,B=ok,C=ok,D=ok,E=ok,F=ok,G=ok,loud=ok,errs=0,df=] nofetch[thr=true,errs=0] rc=[0,0,0] errB=[0,0] at=space_get_direct_state (modules/godot_physics_2d/godot_physics_server_2d.cpp:281)'),
    ('phys2d_backends_gate_duality', 'phys2d_backends.gd', ['--arm=gate_duality'], 0,
     'PASS phys2d_backends gate_duality gate_duality dual_ok=1'),
    ('phys2d_backends_dummy_degenerate', 'phys2d_backends.gd', ['--arm=dummy_degenerate'], 0,
     'PASS phys2d_backends dummy_degenerate dummy_degenerate dummy{valid=false,dss=PhysicsDirectSpaceState2DDummy,mv=zero,ray_keys=[],ray_pos=<absent>,is_n=0,cm0=-1.0000,cm1=-1.0000,rc=0,errB=0} control{valid=true,dss=GodotPhysicsDirectSpaceState2D,mv=pos,ray_keys=["collider", "collider_id", "normal", "position", "rid", "shape"],ray_pos=(98.0, 0.0),is_n=1,cm0=0.4688,cm1=0.4727,rc=0,errB=0}'),
    ('phys2d_backends_dummy_timeout', 'phys2d_backends.gd', ['--arm=dummy_timeout'], 0,
     'PASS phys2d_backends dummy_timeout dummy_timeout rc=124 bound_s=3 dur_ge=1 hang_begin=1 collider_sig=1 errs=1'),
    # r87: input event/action lattice — 20 stable arms of 23, plus three
    # bimodal mode-envelope cells and two deterministic edge cells
    # (r87-scout; probe = input_lattice.gd sha256 2b68531d…, verbatim;
    # r87-simplifier SP1–SP7 later removed 21 dead lines -> 7624aa97…,
    # proven byte-identical outputs — pinned strings unchanged).
    # Signatures are repr()-generated byte-pinned PASS lines; envelope
    # rows carry a TUPLE of the two measured payloads — execute() treats
    # a tuple signature as 'any listed payload whitelisted'.
    # jmode deliberately NOT authored: its histogram is the interleave
    # mode itself (r87-scout §6), not a pinnable byte sequence.
    ('input_lattice_census', 'input_lattice.gd', ['--arm=census'], 0, 'PASS input_lattice census imap=[_get,_get_property_list,_init,_iter_get,_iter_init,_iter_next,_notification,_property_can_revert,_property_get_revert,_set,_to_string,_validate_property,action_add_event,action_erase_event,action_erase_events,action_get_deadzone,action_get_events,action_has_event,action_set_deadzone,add_action,add_user_signal,call,call_deferred,callv,can_translate_messages,cancel_free,connect,disconnect,emit_signal,erase_action,event_is_action,free,get,get_action_description,get_actions,get_class,get_incoming_connections,get_indexed,get_instance_id,get_meta,get_meta_list,get_method_argument_count,get_method_list,get_property_list,get_script,get_signal_connection_list,get_signal_list,get_translation_domain,has_action,has_connections,has_meta,has_method,has_signal,has_user_signal,is_blocking_signals,is_class,is_connected,is_queued_for_deletion,load_from_project_settings,notification,notify_property_list_changed,property_can_revert,property_get_revert,remove_meta,remove_user_signal,set,set_block_signals,set_deferred,set_indexed,set_message_translation,set_meta,set_script,set_translation_domain,to_string,tr,tr_n] input=[action_press,action_release,add_joy_mapping,clear_joy_motion_sensors_calibration,flush_buffered_events,get_action_raw_strength,get_action_strength,get_connected_joypads,get_joy_accelerometer,get_joy_axis,get_joy_gravity,get_joy_guid,get_joy_gyroscope,get_joy_info,get_joy_motion_sensors_calibration,get_joy_motion_sensors_rate,get_joy_name,get_joy_vibration_duration,get_joy_vibration_remaining_duration,get_joy_vibration_strength,get_last_mouse_screen_velocity,get_last_mouse_velocity,get_mouse_button_mask,get_mouse_mode,has_joy_light,has_joy_motion_sensors,has_joy_vibration,is_action_just_pressed,is_action_just_pressed_by_event,is_action_just_released,is_action_just_released_by_event,is_action_pressed,is_anything_pressed,is_emulating_mouse_from_touch,is_emulating_touch_from_mouse,is_ignoring_joypad_on_unfocused_application,is_joy_button_pressed,is_joy_known,is_joy_motion_sensors_calibrated,is_joy_motion_sensors_calibrating,is_joy_motion_sensors_enabled,is_joy_vibrating,is_key_label_pressed,is_key_pressed,is_mouse_button_pressed,is_physical_key_pressed,is_using_accumulated_input,parse_input_event,remove_joy_mapping,set_custom_mouse_cursor,set_emulate_mouse_from_touch,set_emulate_touch_from_mouse,set_ignore_joypad_on_unfocused_application,set_joy_light,set_joy_motion_sensors_calibration,set_joy_motion_sensors_enabled,set_mouse_mode,set_use_accumulated_input,start_joy_motion_sensors_calibration,start_joy_vibration,stop_joy_motion_sensors_calibration,stop_joy_vibration,warp_mouse] evact=[device,action,pressed,strength,event_index] evkey=[device,window_id,command_or_control_autoremap,alt_pressed,shift_pressed,ctrl_pressed,meta_pressed,pressed,keycode,physical_keycode,key_label,unicode,location,echo] ui_builtins=[ui_accept,ui_accessibility_drag_and_drop,ui_cancel,ui_close_dialog,ui_close_dialog.macos,ui_colorpicker_delete_preset,ui_copy,ui_cut,ui_down,ui_end,ui_filedialog_delete,ui_filedialog_find,ui_filedialog_focus_path,ui_filedialog_focus_path.macos,ui_filedialog_refresh,ui_filedialog_show_hidden,ui_filedialog_up_one_level,ui_focus_mode,ui_focus_next,ui_focus_prev,ui_graph_delete,ui_graph_duplicate,ui_graph_follow_left,ui_graph_follow_left.macos,ui_graph_follow_right,ui_graph_follow_right.macos,ui_home,ui_left,ui_menu,ui_page_down,ui_page_up,ui_paste,ui_redo,ui_right,ui_select,ui_swap_input_direction,ui_text_add_selection_for_next_occurrence,ui_text_backspace,ui_text_backspace_all_to_left,ui_text_backspace_all_to_left.macos,ui_text_backspace_word,ui_text_backspace_word.macos,ui_text_caret_add_above,ui_text_caret_add_above.macos,ui_text_caret_add_below,ui_text_caret_add_below.macos,ui_text_caret_document_end,ui_text_caret_document_end.macos,ui_text_caret_document_start,ui_text_caret_document_start.macos,ui_text_caret_down,ui_text_caret_left,ui_text_caret_line_end,ui_text_caret_line_end.macos,ui_text_caret_line_start,ui_text_caret_line_start.macos,ui_text_caret_page_down,ui_text_caret_page_up,ui_text_caret_right,ui_text_caret_up,ui_text_caret_word_left,ui_text_caret_word_left.macos,ui_text_caret_word_right,ui_text_caret_word_right.macos,ui_text_clear_carets_and_selection,ui_text_completion_accept,ui_text_completion_query,ui_text_completion_replace,ui_text_dedent,ui_text_delete,ui_text_delete_all_to_right,ui_text_delete_all_to_right.macos,ui_text_delete_word,ui_text_delete_word.macos,ui_text_indent,ui_text_newline,ui_text_newline_above,ui_text_newline_blank,ui_text_scroll_down,ui_text_scroll_down.macos,ui_text_scroll_up,ui_text_scroll_up.macos,ui_text_select_all,ui_text_select_word_under_caret,ui_text_select_word_under_caret.macos,ui_text_skip_selection_for_next_occurrence,ui_text_submit,ui_text_toggle_insert_mode,ui_undo,ui_unicode_start,ui_up] ui_accept_ev=[K4194309,K4194310,K32] dz_ui=0.50 ps_acc=<missing> ps_agile=false acc_wback=false eng=0/1 joys=0 sink=true'),
    ('input_lattice_press_idle', 'input_lattice.gd', ['--arm=press_idle'], 0, 'PASS input_lattice press_idle imm[0/0.00/0/0] pl=[] recv=[1:ins0@pr+0/ph+0:A(pi,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pi:1/0|I1/1/0] echo0 2:uhs0@pr+0/ph+0:A(pi,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pi:1/0|I1/1/0] echo0] ticks=pre=pr{pi=0/0.00/0/0} post_ph=[ph+0{pi=1/1.00/1/0} ph+1{pi=1/1.00/0/0} ph+2{pi=1/1.00/0/0}] post_pr=[pr+0{pi=1/1.00/1/0} pr+1{pi=1/1.00/0/0} pr+2{pi=1/1.00/0/0}]'),
    ('input_lattice_acc_off', 'input_lattice.gd', ['--arm=acc_off'], 0, 'PASS input_lattice acc_off acc=false inline_receipts=2 imm[1/1.00/1/0] recv=[1:ins0@pr+0/ph+0:A(ao,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[ao:1/0|I1/1/0] echo0 2:uhs0@pr+0/ph+0:A(ao,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[ao:1/0|I1/1/0] echo0] ticks=pre= post_ph=[ph+0{ao=1/1.00/1/0} ph+1{ao=1/1.00/0/0}] post_pr=[pr+0{ao=1/1.00/1/0} pr+1{ao=1/1.00/0/0}]'),
    ('input_lattice_acc_flush', 'input_lattice.gd', ['--arm=acc_flush'], 0, 'PASS input_lattice acc_flush mid[0/0.00/0/0] mid_len=0 post[1/1.00/1/0] post_len=2 recv=[1:ins0@pr+0/ph+0:A(af,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[af:1/0|I1/1/0] echo0 2:uhs0@pr+0/ph+0:A(af,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[af:1/0|I1/1/0] echo0]'),
    # pre_frame carries the latent press_phys shape (ph-count inside a
    # process_frame window): scout flagged it, battery rep1 empirically
    # produced post_ph=[]. Census 24/24 on this host = exactly the two
    # payloads whitelisted below (23x one-tick, 1x empty).
    ('input_lattice_pre_frame', 'input_lattice.gd', ['--arm=pre_frame'], 0,
     ('PASS input_lattice pre_frame imm0[0/0.00/0/0] recv=[1:ins0@pr+1/ph~:A(pf0,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pf0:1/0|I1/1/0] echo0 2:uhs0@pr+1/ph~:A(pf0,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pf0:1/0|I1/1/0] echo0] ticks=pre=pr{pf0=0/0.00/0/0} post_ph=[ph+0{pf0=1/1.00/1/0}] post_pr=[pr+0{pf0=1/1.00/1/0}]',
      'PASS input_lattice pre_frame imm0[0/0.00/0/0] recv=[1:ins0@pr+1/ph~:A(pf0,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pf0:1/0|I1/1/0] echo0 2:uhs0@pr+1/ph~:A(pf0,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pf0:1/0|I1/1/0] echo0] ticks=pre=pr{pf0=0/0.00/0/0} post_ph=[] post_pr=[pr+0{pf0=1/1.00/1/0}]')),
    # api_press is bimodal per the boundary pulse law (inter==0 <=> jp==1):
    # the release->idle-frame->press gap admits an interposed physics step
    # that consumes the release pulse, flipping ph1's jr field 1->0.
    # r87 critic F1: alt mode observed 27/30 under CPU load.
    ('input_lattice_api_press', 'input_lattice.gd', ['--arm=api_press'], 0,
     ('PASS input_lattice api_press imm[1/0.70/1/0] raw=0.70 pl=["ap"] recv=[] pr=["pr0{ap=1/0.70/1/0}", "pr1{ap=1/0.70/0/0}", "pr2{ap=0/0.00/0/1}"] ph=["ph1{ap=1/0.70/1/1}", "ph2{ap=0/0.00/0/0}", "ph3{ap=0/0.00/0/1}"]',
      'PASS input_lattice api_press imm[1/0.70/1/0] raw=0.70 pl=["ap"] recv=[] pr=["pr0{ap=1/0.70/1/0}", "pr1{ap=1/0.70/0/0}", "pr2{ap=0/0.00/0/1}"] ph=["ph1{ap=1/0.70/1/0}", "ph2{ap=0/0.00/0/0}", "ph3{ap=0/0.00/0/1}"]')),
    ('input_lattice_burst', 'input_lattice.gd', ['--arm=burst'], 0, 'PASS input_lattice burst imm[0/0.00/0/0] recv=[1:ins0@pr+0/ph+0:A(bu,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[bu:1/0|I1/1/0] echo0 2:uhs0@pr+0/ph+0:A(bu,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[bu:1/0|I1/1/0] echo0 3:ins0@pr+0/ph+0:A(bu,p=0,s=1.00,d=-1,ai=<null>,ei=-1) m[bu:0/1|I0/1/1] echo0 4:uhs0@pr+0/ph+0:A(bu,p=0,s=1.00,d=-1,ai=<null>,ei=-1) m[bu:0/1|I0/1/1] echo0] ticks=pre=pr{bu=0/0.00/0/0} post_ph=[ph+0{bu=0/0.00/1/1} ph+1{bu=0/0.00/0/0} ph+2{bu=0/0.00/0/0}] post_pr=[pr+0{bu=0/0.00/1/1} pr+1{bu=0/0.00/0/0}]'),
    ('input_lattice_dz_ladder', 'input_lattice.gd', ['--arm=dz_ladder'], 0, 'PASS input_lattice dz_ladder dz50=[s0.00[1/0.00/1/0] s0.30[1/0.30/0/0] s0.49[1/0.49/0/0] s0.50[1/0.50/0/0] s0.51[1/0.51/0/0] s0.70[1/0.70/0/0] s1.00[1/1.00/0/0]] dz20=[s0.00[1/0.00/0/0] s0.30[1/0.30/0/0] s0.49[1/0.49/0/0] s0.50[1/0.50/0/0] s0.51[1/0.51/0/0] s0.70[1/0.70/0/0] s1.00[1/1.00/0/0]] api50=[s0.00[1/0.00/1/0|raw 0.00] s0.30[1/0.30/1/0|raw 0.30] s0.49[1/0.49/1/0|raw 0.49] s0.50[1/0.50/1/0|raw 0.50] s0.51[1/0.51/1/0|raw 0.51] s0.70[1/0.70/1/0|raw 0.70] s1.00[1/1.00/1/0|raw 1.00]]'),
    ('input_lattice_joy_axis', 'input_lattice.gd', ['--arm=joy_axis'], 0, 'PASS input_lattice joy_axis v0.00[0/0.00/0/0|0/0.00/0/0|raw 0.00/0.00] v0.20[0/0.00/0/0|0/0.00/0/0|raw 0.20/0.00] v0.21[0/0.00/0/0|0/0.00/0/0|raw 0.21/0.00] v0.49[0/0.00/0/0|0/0.00/0/0|raw 0.49/0.00] v0.50[1/0.00/0/0|0/0.00/0/0|raw 0.50/0.00] v0.51[1/0.02/0/0|0/0.00/0/0|raw 0.51/0.00] v0.70[1/0.40/0/0|0/0.00/0/0|raw 0.70/0.00] v1.00[1/1.00/0/0|0/0.00/0/0|raw 1.00/0.00] v-0.20[0/0.00/0/0|1/0.00/0/0|raw 0.00/0.20] v-0.21[0/0.00/0/0|1/0.01/0/0|raw 0.00/0.21] v-0.70[0/0.00/0/0|1/0.62/0/0|raw 0.00/0.70]'),
    ('input_lattice_echo_edge', 'input_lattice.gd', ['--arm=echo_edge'], 0, 'PASS input_lattice echo_edge after_echo[1/1.00/0/0] first_echo[1/1.00/0/0] recv=[1:ins0@pr+0/ph~:K(kc=69,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ek:1/0|I1/1/0] echo0 2:scs0@pr+0/ph~:K(kc=69,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ek:1/0|I1/1/0] echo0 3:uks0@pr+0/ph~:K(kc=69,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ek:1/0|I1/1/0] echo0 4:uhs0@pr+0/ph~:K(kc=69,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ek:1/0|I1/1/0] echo0 5:ins0@pr+2/ph~:K(kc=69,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I1/0/0] echo1 6:scs0@pr+2/ph~:K(kc=69,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I1/0/0] echo1 7:uks0@pr+2/ph~:K(kc=69,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I1/0/0] echo1 8:uhs0@pr+2/ph~:K(kc=69,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I1/0/0] echo1 9:ins0@pr+4/ph~:K(kc=69,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ek:0/1|I0/0/1] echo0 10:scs0@pr+4/ph~:K(kc=69,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ek:0/1|I0/0/1] echo0 11:uks0@pr+4/ph~:K(kc=69,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ek:0/1|I0/0/1] echo0 12:uhs0@pr+4/ph~:K(kc=69,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ek:0/1|I0/0/1] echo0 13:ins0@pr+6/ph~:K(kc=82,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I0/0/0] echo1 14:scs0@pr+6/ph~:K(kc=82,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I0/0/0] echo1 15:uks0@pr+6/ph~:K(kc=82,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I0/0/0] echo1 16:uhs0@pr+6/ph~:K(kc=82,ph=0,pr=1,echo=1,dev=16,u=0,sh=0) m[ek:0/0|I0/0/0] echo1]'),
    ('input_lattice_key_map', 'input_lattice.gd', ['--arm=key_map'], 0, 'PASS input_lattice key_map after_q[1/1.00/0/0|0/0.00/0/0 keyq=1 phq=0 phw=0] after_qphysw[1/1.00/0/0|1/1.00/0/0 phw=1] tail[0/0.00/0/0|0/0.00/0/0] recv=[1:ins0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/1/0,kp:0/0|I0/0/0] echo0 2:scs0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/1/0,kp:0/0|I0/0/0] echo0 3:uks0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/1/0,kp:0/0|I0/0/0] echo0 4:uhs0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/1/0,kp:0/0|I0/0/0] echo0 5:ins0@pr+2/ph~:K(kc=81,ph=87,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/0/0,kp:1/0|I1/1/0] echo0 6:scs0@pr+2/ph~:K(kc=81,ph=87,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/0/0,kp:1/0|I1/1/0] echo0 7:uks0@pr+2/ph~:K(kc=81,ph=87,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/0/0,kp:1/0|I1/1/0] echo0 8:uhs0@pr+2/ph~:K(kc=81,ph=87,pr=1,echo=0,dev=16,u=0,sh=0) m[ka:1/0|I1/0/0,kp:1/0|I1/1/0] echo0 9:ins0@pr+4/ph~:K(kc=81,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/1|I0/0/1,kp:0/0|I1/0/0] echo0 10:scs0@pr+4/ph~:K(kc=81,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/1|I0/0/1,kp:0/0|I1/0/0] echo0 11:uks0@pr+4/ph~:K(kc=81,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/1|I0/0/1,kp:0/0|I1/0/0] echo0 12:uhs0@pr+4/ph~:K(kc=81,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/1|I0/0/1,kp:0/0|I1/0/0] echo0 13:ins0@pr+4/ph~:K(kc=0,ph=87,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/0|I0/0/1,kp:0/1|I0/0/1] echo0 14:scs0@pr+4/ph~:K(kc=0,ph=87,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/0|I0/0/1,kp:0/1|I0/0/1] echo0 15:uks0@pr+4/ph~:K(kc=0,ph=87,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/0|I0/0/1,kp:0/1|I0/0/1] echo0 16:uhs0@pr+4/ph~:K(kc=0,ph=87,pr=0,echo=0,dev=16,u=0,sh=0) m[ka:0/0|I0/0/1,kp:0/1|I0/0/1] echo0]'),
    ('input_lattice_imap_erase', 'input_lattice.gd', ['--arm=imap_erase'], 0, 'PASS input_lattice imap_erase while[1/1.00/0/0] pl1=["er"] has=false pl2=[] readd=true pl3=["er"] buf_erase_recv=4 recv=["K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "K(kc=90,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)"]'),
    ('input_lattice_imap_mid_cb', 'input_lattice.gd', ['--arm=imap_mid_cb'], 0, 'PASS input_lattice imap_mid_cb erased_in_cb=true b_has=false pl=["cb_a", "ui_filedialog_refresh"] b_rearmed[1/1.00/0/0] recv=["ins0:K(kc=4194336,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "scs0:K(kc=4194336,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "uks0:K(kc=4194336,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "uhs0:K(kc=4194336,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "ins0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "scs0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "uks0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "uhs0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "ins0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "scs0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "uks0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)", "uhs0:K(kc=4194337,ph=0,pr=1,echo=0,dev=16,u=0,sh=0)"]'),
    ('input_lattice_conflict', 'input_lattice.gd', ['--arm=conflict'], 0, 'PASS input_lattice conflict both[1/1.00/0/0|1/1.00/0/0 pl=["ck_a", "ck_b"]] exact[ck_s[1/1.00/0/0] a_exact=1 a_plain=1 s_exact=1] recv=[1:ins0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ck_a:1/0|I1/1/0,ck_b:1/0|I1/1/0,ck_s:0/0|I0/0/0] echo0 2:scs0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ck_a:1/0|I1/1/0,ck_b:1/0|I1/1/0,ck_s:0/0|I0/0/0] echo0 3:uks0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ck_a:1/0|I1/1/0,ck_b:1/0|I1/1/0,ck_s:0/0|I0/0/0] echo0 4:uhs0@pr+0/ph~:K(kc=81,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ck_a:1/0|I1/1/0,ck_b:1/0|I1/1/0,ck_s:0/0|I0/0/0] echo0 5:ins0@pr+2/ph~:K(kc=87,ph=0,pr=1,echo=0,dev=16,u=0,sh=1) m[ck_a:0/0|I1/0/0,ck_b:0/0|I1/0/0,ck_s:1/0|I1/1/0] echo0 6:scs0@pr+2/ph~:K(kc=87,ph=0,pr=1,echo=0,dev=16,u=0,sh=1) m[ck_a:0/0|I1/0/0,ck_b:0/0|I1/0/0,ck_s:1/0|I1/1/0] echo0 7:uks0@pr+2/ph~:K(kc=87,ph=0,pr=1,echo=0,dev=16,u=0,sh=1) m[ck_a:0/0|I1/0/0,ck_b:0/0|I1/0/0,ck_s:1/0|I1/1/0] echo0 8:uhs0@pr+2/ph~:K(kc=87,ph=0,pr=1,echo=0,dev=16,u=0,sh=1) m[ck_a:0/0|I1/0/0,ck_b:0/0|I1/0/0,ck_s:1/0|I1/1/0] echo0]'),
    ('input_lattice_dev_joy', 'input_lattice.gd', ['--arm=dev_joy'], 0, 'PASS input_lattice dev_joy joys=0 d0[1/1.00/0/0] j0=1 j5=0 d5[0/0.00/0/0] j0=0 j5=1 d-1[0/0.00/0/0] j0=0 j5=0 recv=[1:ins0@pr+0/ph~:JB(b=0,p=1,dev=0) m[jb:1/0|I1/1/0] echo0 2:scs0@pr+0/ph~:JB(b=0,p=1,dev=0) m[jb:1/0|I1/1/0] echo0 3:uhs0@pr+0/ph~:JB(b=0,p=1,dev=0) m[jb:1/0|I1/1/0] echo0 4:ins0@pr+2/ph~:JB(b=0,p=0,dev=0) m[jb:0/1|I0/0/1] echo0 5:scs0@pr+2/ph~:JB(b=0,p=0,dev=0) m[jb:0/1|I0/0/1] echo0 6:uhs0@pr+2/ph~:JB(b=0,p=0,dev=0) m[jb:0/1|I0/0/1] echo0 7:ins0@pr+3/ph~:JB(b=0,p=1,dev=5) m[jb:0/0|I0/0/0] echo0 8:scs0@pr+3/ph~:JB(b=0,p=1,dev=5) m[jb:0/0|I0/0/0] echo0 9:uhs0@pr+3/ph~:JB(b=0,p=1,dev=5) m[jb:0/0|I0/0/0] echo0 10:ins0@pr+5/ph~:JB(b=0,p=0,dev=5) m[jb:0/0|I0/0/0] echo0 11:scs0@pr+5/ph~:JB(b=0,p=0,dev=5) m[jb:0/0|I0/0/0] echo0 12:uhs0@pr+5/ph~:JB(b=0,p=0,dev=5) m[jb:0/0|I0/0/0] echo0 13:ins0@pr+6/ph~:JB(b=0,p=1,dev=-1) m[jb:0/0|I0/0/0] echo0 14:scs0@pr+6/ph~:JB(b=0,p=1,dev=-1) m[jb:0/0|I0/0/0] echo0 15:uhs0@pr+6/ph~:JB(b=0,p=1,dev=-1) m[jb:0/0|I0/0/0] echo0 16:ins0@pr+8/ph~:JB(b=0,p=0,dev=-1) m[jb:0/0|I0/0/0] echo0 17:scs0@pr+8/ph~:JB(b=0,p=0,dev=-1) m[jb:0/0|I0/0/0] echo0 18:uhs0@pr+8/ph~:JB(b=0,p=0,dev=-1) m[jb:0/0|I0/0/0] echo0]'),
    ('input_lattice_mouse_hdls', 'input_lattice.gd', ['--arm=mouse_hdls'], 0, 'PASS input_lattice mouse_hdls ml=1 pos=(0,0) pos2=(0,0) recv=[1:ins0@pr+0/ph~:MB(b=1,p=1,pos=(7,9)) m[mh:0/0|I0/0/0] echo0 2:uhs0@pr+0/ph~:MB(b=1,p=1,pos=(7,9)) m[mh:0/0|I0/0/0] echo0 3:ins0@pr+2/ph~:MM(pos=(30,40),rel=(23,31)) m[mh:0/0|I0/0/0] echo0 4:uhs0@pr+2/ph~:MM(pos=(30,40),rel=(23,31)) m[mh:0/0|I0/0/0] echo0]'),
    ('input_lattice_null_edge', 'input_lattice.gd', ['--arm=null_edge'], 0, 'PASS input_lattice null_edge rel_first[0/0.00/0/0] base_recv=7 miss_p=false miss_jp=false recv=["ins0:A(ne,p=0,s=1.00,d=-1,ai=<null>,ei=-1)", "uhs0:A(ne,p=0,s=1.00,d=-1,ai=<null>,ei=-1)", "ins0:InputEventShortcut", "scs0:InputEventShortcut", "uhs0:InputEventShortcut", "ins0:A(,p=1,s=1.00,d=-1,ai=<null>,ei=-1)", "uhs0:A(,p=1,s=1.00,d=-1,ai=<null>,ei=-1)"]'),
    ('input_lattice_dispatch_order', 'input_lattice.gd', ['--arm=dispatch_order'], 0, 'PASS input_lattice dispatch_order recv=["1:ins1", "2:ins0", "3:scs1", "4:scs0", "5:uks1", "6:uks0", "7:uhs1", "8:uhs0", "9:ins1", "10:ins0", "11:ins1", "12:ins0"]'),
    ('input_lattice_reentrant', 'input_lattice.gd', ['--arm=reentrant'], 0, 'PASS input_lattice reentrant acc=["1:ins0:A(ra,p=1,s=1.00,d=-1,ai=<null>,ei=-1)", "2:uhs0:A(ra,p=1,s=1.00,d=-1,ai=<null>,ei=-1)", "3:ins0:A(rb,p=1,s=1.00,d=-1,ai=<null>,ei=-1)", "4:uhs0:A(rb,p=1,s=1.00,d=-1,ai=<null>,ei=-1)"] off=["5:ins0:A(ra,p=0,s=1.00,d=-1,ai=<null>,ei=-1)", "6:uhs0:A(ra,p=0,s=1.00,d=-1,ai=<null>,ei=-1)", "7:ins0:A(ra,p=1,s=1.00,d=-1,ai=<null>,ei=-1)", "8:ins0:A(rb,p=1,s=1.00,d=-1,ai=<null>,ei=-1)", "9:uhs0:A(rb,p=1,s=1.00,d=-1,ai=<null>,ei=-1)", "10:uhs0:A(ra,p=1,s=1.00,d=-1,ai=<null>,ei=-1)"]'),
    # phys_peer is the same interposed-step class as api_press (r87): under
    # CPU oversubscription the press receipt lands 1+ ph steps after the
    # pinned parse step, shifting the px=1 cell right; delta>=4 pushes it
    # past the recorded d-1..d+4 window entirely (all cells px=0, only the
    # delta digit differs). r88 critic F5 measured {0:29, 1:15, 2:8, 3:6,
    # 4:2} over 60 hogged reps at 12-way concurrency; the r88 fold's 150
    # hogged reps measured {0:98, 1:19, 2:6, 3:8, 4:4, 5:15} — the envelope
    # covers all six observed verbatim payloads. delta>=6 is theoretically
    # reachable (bounded by max_physics_steps_per_frame) but unobserved in
    # 210 reps; it would fail loudly, a flake — never a silent wrong answer.
    ('input_lattice_phys_peer', 'input_lattice.gd', ['--arm=phys_peer'], 0,
     ('PASS input_lattice phys_peer same_tick[0/0.00/0/0] ev_step_delta=0 cells=d-1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+0{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+1{s1=px=1/1.00/1/0,s0=px=1/1.00/1/0} d+2{s1=px=1/1.00/0/0,s0=px=1/1.00/0/0} d+3{s1=px=1/1.00/0/0,s0=px=1/1.00/0/0} d+4{s1=px=1/1.00/0/0,s0=px=1/1.00/0/0}',
      'PASS input_lattice phys_peer same_tick[0/0.00/0/0] ev_step_delta=1 cells=d-1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+0{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+2{s1=px=1/1.00/1/0,s0=px=1/1.00/1/0} d+3{s1=px=1/1.00/0/0,s0=px=1/1.00/0/0} d+4{s1=px=1/1.00/0/0,s0=px=1/1.00/0/0}',
      'PASS input_lattice phys_peer same_tick[0/0.00/0/0] ev_step_delta=2 cells=d-1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+0{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+2{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+3{s1=px=1/1.00/1/0,s0=px=1/1.00/1/0} d+4{s1=px=1/1.00/0/0,s0=px=1/1.00/0/0}',
      'PASS input_lattice phys_peer same_tick[0/0.00/0/0] ev_step_delta=3 cells=d-1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+0{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+2{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+3{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+4{s1=px=1/1.00/1/0,s0=px=1/1.00/1/0}',
      'PASS input_lattice phys_peer same_tick[0/0.00/0/0] ev_step_delta=4 cells=d-1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+0{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+2{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+3{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+4{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0}',
      'PASS input_lattice phys_peer same_tick[0/0.00/0/0] ev_step_delta=5 cells=d-1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+0{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+1{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+2{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+3{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0} d+4{s1=px=0/0.00/0/0,s0=px=0/0.00/0/0}')),
    ('input_lattice_press_phys', 'input_lattice.gd', ['--arm=press_phys'], 0,
     ('PASS input_lattice press_phys imm[0/0.00/0/0] recv=[1:ins0@pr+1/ph~:A(pp,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pp:1/0|I1/1/0] echo0 2:uhs0@pr+1/ph~:A(pp,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pp:1/0|I1/1/0] echo0] ticks=pre=pr{pp=0/0.00/0/0} post_ph=[ph+0{pp=1/1.00/1/0} ph+1{pp=1/1.00/0/0} ph+2{pp=1/1.00/0/0}] post_pr=[pr+0{pp=1/1.00/1/0} pr+1{pp=1/1.00/0/0}]',
      'PASS input_lattice press_phys imm[0/0.00/0/0] recv=[1:ins0@pr+1/ph~:A(pp,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pp:1/0|I1/1/0] echo0 2:uhs0@pr+1/ph~:A(pp,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[pp:1/0|I1/1/0] echo0] ticks=pre=pr{pp=0/0.00/0/0} post_ph=[ph+0{pp=1/1.00/1/0} ph+1{pp=1/1.00/0/0}] post_pr=[pr+0{pp=1/1.00/1/0} pr+1{pp=1/1.00/0/0}]')),
    ('input_lattice_release_edge', 'input_lattice.gd', ['--arm=release_edge'], 0,
     ('PASS input_lattice release_edge imm[1/1.00/0/0] recv=[1:ins0@pr+0/ph~:A(re,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[re:1/0|I1/1/0] echo0 2:uhs0@pr+0/ph~:A(re,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[re:1/0|I1/1/0] echo0 3:ins0@pr+2/ph~:A(re,p=0,s=1.00,d=-1,ai=<null>,ei=-1) m[re:0/1|I0/0/1] echo0 4:uhs0@pr+2/ph~:A(re,p=0,s=1.00,d=-1,ai=<null>,ei=-1) m[re:0/1|I0/0/1] echo0] ticks=pre=pr{re=1/1.00/0/0} post_ph=[ph+0{re=0/0.00/1/1} ph+1{re=0/0.00/0/0} ph+2{re=0/0.00/0/0}] post_pr=[pr+0{re=0/0.00/0/1} pr+1{re=0/0.00/0/0}]',
      'PASS input_lattice release_edge imm[1/1.00/0/0] recv=[1:ins0@pr+0/ph~:A(re,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[re:1/0|I1/1/0] echo0 2:uhs0@pr+0/ph~:A(re,p=1,s=1.00,d=-1,ai=<null>,ei=-1) m[re:1/0|I1/1/0] echo0 3:ins0@pr+2/ph~:A(re,p=0,s=1.00,d=-1,ai=<null>,ei=-1) m[re:0/1|I0/0/1] echo0 4:uhs0@pr+2/ph~:A(re,p=0,s=1.00,d=-1,ai=<null>,ei=-1) m[re:0/1|I0/0/1] echo0] ticks=pre=pr{re=1/1.00/0/0} post_ph=[ph+0{re=0/0.00/0/1} ph+1{re=0/0.00/0/0} ph+2{re=0/0.00/0/0}] post_pr=[pr+0{re=0/0.00/0/1} pr+1{re=0/0.00/0/0}]')),
    ('input_lattice_ui_ns', 'input_lattice.gd', ['--arm=ui_ns'], 0,
     ('PASS input_lattice ui_ns ua_ev=3 during[1/1.00/0/0|1/1.00/0/0] pl=["cx", "ui_accept", "ui_text_completion_accept", "ui_text_newline", "ui_text_submit"] ua_has_after=false cx_after[0/0.00/0/0] recv=[1:ins0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 2:scs0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 3:uks0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 4:uhs0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 5:ins0@pr+2/ph+0:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0 6:scs0@pr+2/ph+0:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0 7:uks0@pr+2/ph+0:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0 8:uhs0@pr+2/ph+0:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0]',
      'PASS input_lattice ui_ns ua_ev=3 during[1/1.00/0/0|1/1.00/0/0] pl=["cx", "ui_accept", "ui_text_completion_accept", "ui_text_newline", "ui_text_submit"] ua_has_after=false cx_after[0/0.00/0/0] recv=[1:ins0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 2:scs0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 3:uks0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 4:uhs0@pr+0/ph+0:K(kc=4194309,ph=0,pr=1,echo=0,dev=16,u=0,sh=0) m[ui_accept:1/0|I1/1/0,cx:1/0|I1/1/0] echo0 5:ins0@pr+2/ph+1:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0 6:scs0@pr+2/ph+1:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0 7:uks0@pr+2/ph+1:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0 8:uhs0@pr+2/ph+1:K(kc=4194309,ph=0,pr=0,echo=0,dev=16,u=0,sh=0) m[ui_accept:gone|Igone,cx:0/1|I0/0/1] echo0]')),
    ('r87_edge_jpbe', 'r87_edge.gd', ['--arm=jpbe'], 0, 'PASS r87_edge jpbe imm[0/0.00/0/0] post[1/1.00/1/0] jpbe[j=1 wrong=0 other=0 rel_on_press=0 ex=1] eia[hit=1 miss=0 ex=1] shift[s_ex=1 s_plain=1 p_ex=0 p_plain=0] act[pre=0/0.00/0/0 imm=1/1.00/1/0 jpbe=1 eia=1 ei=-1 ai=<null> bad_st=0/0.00/0/0] rel[st=0/0.00/0/1 jrbe=1 jpbe=0] recv_n=3'),
    ('ei_bound_refusal', 'ei_bound.gd', [], 0, 'ei=-2 -> pressed=1\nei=-1 -> pressed=1\nei=0 -> pressed=1\nei=1 -> pressed=0\nei=31 -> pressed=0\nei=32 -> pressed=0\nei=33 -> pressed=0\nei=42 -> pressed=0\nei=100 -> pressed=0'),
    # r88: the r88 census's remaining measured surfaces — Offline/ENet
    # loopback multiplayer incl. spawner/synchronizer controls, 2D
    # light/occluder props (with the scout-documented height fix), sprite
    # metadata vs physics, and the headless-null audio/visibility surfaces
    # (negative pins only — positive rows are structurally impossible on
    # this host). Probe r88_surfaces.gd is an r88-author fixture adapting
    # the dead seat's measured arms (r88-scout §3, directives 4-7); every
    # payload measured x4 byte-stable. Inserted ahead of the
    # crash/descendant tail — probe_descendant_pipe_eof requires
    # detached_descendant_orphaned_alive within the descendant's `sleep 8`
    # lifetime, so no CASES rows may sit between
    # descendant_pipe_detached_control and the meta probes.
    ('r88_surfaces_mp_offline', 'r88_surfaces.gd', ['--arm=mp_offline'], 0,
     'PASS r88_surfaces mp_offline status=2 uid=1 mode=2 chan=0 tree_uid=1 is_server=true tree_status=2'),
    ('r88_surfaces_mp_loopback', 'r88_surfaces.gd', ['--arm=mp_loopback'], 0,
     'PASS r88_surfaces mp_loopback rc=[0,0] uid_s=1 uid_after_dyn=true order=["c_on_srv", "c_conn1", "s_conn<C>", "c_srvdisc", "s_disc<C>"] limb_s=["ping7:c2s", "ping5:call_local_c"] limb_c=["ping5:call_local_c", "ping9:s2c"]'),
    ('r88_surfaces_mp_spawner', 'r88_surfaces.gd', ['--arm=mp_spawner'], 0,
     'PASS r88_surfaces mp_spawner neg[c_children=0 srv_children=4 bound_hit=300] pos[added=SpawnableOne c_got=SpawnableOne c_pos=33.0000,44.0000] sync[pos=111.0000,222.0000]'),
    ('r88_surfaces_light_props', 'r88_surfaces.gd', ['--arm=light_props'], 0,
     'PASS r88_surfaces light_props pl=[en=true sh=true en2=2.500 ts=1.500 h=42.000 col=(0.5, 0.25, 0.125, 1.0) mask=4 mo=1] dl=[en=0.750 mask=1] occ=[closed=true cull=0 mask=2 sdf=true n=3] cm=[col=(0.2, 0.2, 0.4, 1.0)] body_y=118.4614 ray_through_occluder=true occ_cls=LightOccluder2D occ_is_co=false'),
    ('r88_surfaces_sprite_meta', 'r88_surfaces.gd', ['--arm=sprite_meta'], 0,
     'PASS r88_surfaces sprite_meta readback=[re=true rr=[P: (4.0, 4.0), S: (8.0, 8.0)] hf=4 vf=2 f=5 fc=(1, 1) fh=true fv=true off=(3.0, -2.0) cen=false] xf=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (0.0, 0.0)] signals=["fc"] sneg_xf=[X: (-1.0, 0.0), Y: (0.0, 1.0), O: (0.0, 0.0)] get_rect=[P: (3.0, -2.0), S: (2.0, 4.0)] s2_rect=[P: (-16.0, -8.0), S: (32.0, 16.0)]'),
    ('r88_surfaces_sprite_phys', 'r88_surfaces.gd', ['--arm=sprite_phys'], 0,
     'PASS r88_surfaces sprite_phys [pos=250.0000,74.5675 spr_gt=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (250.0, 74.56753)] spr_rel=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (0.0, 0.0)]|pos=350.0000,74.5675 spr_gt=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (350.0, 74.56753)] spr_rel=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (0.0, 0.0)]|pos=400.0000,74.5675 spr_gt=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (400.0, 74.56753)] spr_rel=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (0.0, 0.0)]|pos=500.0000,74.5675 spr_gt=[X: (-1.0, 0.0), Y: (0.0, -1.0), O: (500.0, 74.56753)] spr_rel=[X: (-1.0, 0.0), Y: (0.0, -1.0), O: (0.0, 0.0)]]'),
    ('r88_surfaces_audio_pos', 'r88_surfaces.gd', ['--arm=audio_pos'], 0,
     'PASS r88_surfaces audio_pos playing=false pos=0.000 peaks_near=[-200.00,-200.00,-200.00,-200.00] peaks_far=[-200.00,-200.00,-200.00,-200.00] listen_pos=0.0000,0.0000 listener_current=true'),
    ('r88_surfaces_vis_not', 'r88_surfaces.gd', ['--arm=vis_not'], 0,
     'PASS r88_surfaces vis_not on_screen0=false en_onscreen=false events=[] on_screen_end=false enabler_proc=false'),
    # r89: the Geometry2D authorability lattice (r88-census top-ranked
    # surface) + two r87 input leftovers closed as a bounded secondary
    # split (r89-scout; probes = geo2d_lattice.gd sha256 dcce4c74… —
    # r89-fold variant of scout sha256 9784716b…: dead `names`
    # accumulator removed (simplifier SP1) + dead receipt-only arms
    # bridge_hole/bridge_hole2 deleted with their falsified merge-hole
    # comment (critic F5; merge collapses containment to k=1 — clip is
    # the hole-producer). input89_edges.gd sha256 601c223e…, landed
    # verbatim — arm parse is
    # already the battery convention and every arm prints its own name).
    # Signatures are measured PASS lines byte-pinned x6 fresh by the r89
    # author (corpus/live/r89-author/runs/) on top of the scout's 24-cell
    # x3/x6 lattice and the boundary's 6x-under-load replay (19/20 stable).
    # input89_edges_exact is the boundary's ONE unstable row: its
    # just_after_flush token is LOAD-BIMODAL (w_jp[ex=false inex=true]
    # quiet / inex=false loaded — observed live: 6/6 Q quiet, 12/12 L
    # under 16 hogs), so it carries the 2-payload tuple envelope per the
    # r87 mode-envelope precedent (payload[0] = quiet/pinned mode).
    # geo2d_lattice_lineempty is a dedicated single-call crash row:
    # offset_polyline(empty,...) hits an uncatchable Clipper2 vector
    # assert -> SIGABRT -6 (signature is the pre-call R89 diagnostic
    # line; the PASS line is never reached). r89-fold (critic F1): the
    # row also carries a required_stderr pin — the Clipper2 assert
    # fragments must appear on stderr and the signature on stdout, so a
    # foreign SIGABRT on the merged blob can no longer classify PASS.
    # Inserted ahead of the
    # crash/descendant tail — see the r88 note above: no CASES rows may
    # sit between descendant_pipe_detached_control and the meta probes.
    ('geo2d_lattice_census', 'geo2d_lattice.gd', ['--arm=census'], 0,
     'PASS geo2d_lattice census sig=[clip_polygons(polygon_a,polygon_b)|convex_hull(points)|decompose_polygon_in_convex(polygon)|make_atlas(sizes)|merge_polygons(polygon_a,polygon_b)|offset_polygon(polygon,delta,join_type)|offset_polyline(polyline,delta,join_type,end_type)|triangulate_polygon(polygon)] join=SQ=0,RD=1,MT=2 end=POLY=0,JOINED=1,BUTT=2,SQUARE=3,ROUND=4 op=UNION=0,DIFF=1,INTER=2,XOR=3 nmethods=86 default_join_polygon=k=1{n8[12.0000,-10.8284;12.0000,10.8284;10.8284,12.0000;-10.8284,12.0000;-12.0000,10.8284;-12.0000,-10.8284;-10.8284,-12.0000;10.8284,-12.0000]} match=[sq,] default_polyline=k=1{n7[22.0000,-0.8284;22.0000,22.0000;18.0000,22.0000;18.0000,2.0000;-2.0000,2.0000;-2.0000,-2.0000;20.8284,-2.0000]} match=[sq/square,]'),
    ('geo2d_lattice_ops', 'geo2d_lattice.gd', ['--arm=ops'], 0,
     'PASS geo2d_lattice ops clip=k=1{n4[-2.0000,-10.0000;-2.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000]} merge=k=1{n4[18.0000,-10.0000;18.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000]} inter=k=1{n4[10.0000,10.0000;-2.0000,10.0000;-2.0000,-10.0000;10.0000,-10.0000]} excl=k=2{n4[-2.0000,-10.0000;-2.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000] a=160.0000|n4[18.0000,10.0000;10.0000,10.0000;10.0000,-10.0000;18.0000,-10.0000] a=160.0000} tri_idx=[3, 0, 1, 1, 2, 3] tri_area=400.0000 poly_area=400.0000 off_p2_sq=k=1{n8[12.0000,-10.8284;12.0000,10.8284;10.8284,12.0000;-10.8284,12.0000;-12.0000,10.8284;-12.0000,-10.8284;-10.8284,-12.0000;10.8284,-12.0000] a=573.2548} off_p2_rd=k=1{n12[11.6944,-11.0625;12.0000,-10.0000;12.0000,10.0000;11.0625,11.6944;10.0000,12.0000;-10.0000,12.0000;-11.6944,11.0625;-12.0000,10.0000;-12.0000,-10.0000;-11.0625,-11.6944;-10.0000,-12.0000;10.0000,-12.0000] a=571.0277} off_p2_mt=k=1{n4[12.0000,12.0000;-12.0000,12.0000;-12.0000,-12.0000;12.0000,-12.0000] a=576.0000} off_m2_sq=k=1{n4[8.0000,-8.0000;8.0000,8.0000;-8.0000,8.0000;-8.0000,-8.0000] a=256.0000} off_m2_rd=k=1{n4[8.0000,-8.0000;8.0000,8.0000;-8.0000,8.0000;-8.0000,-8.0000] a=256.0000} off_m2_mt=k=1{n4[8.0000,-8.0000;8.0000,8.0000;-8.0000,8.0000;-8.0000,-8.0000] a=256.0000}'),
    ('geo2d_lattice_contain', 'geo2d_lattice.gd', ['--arm=contain'], 0,
     'PASS geo2d_lattice contain merge_bs=k=1{n4[20.0000,20.0000;-20.0000,20.0000;-20.0000,-20.0000;20.0000,-20.0000] a=1600.0000} merge_sb=k=1{n4[20.0000,20.0000;-20.0000,20.0000;-20.0000,-20.0000;20.0000,-20.0000] a=1600.0000} clip_bs=k=2{n4[20.0000,20.0000;-20.0000,20.0000;-20.0000,-20.0000;20.0000,-20.0000] a=1600.0000|n4[-5.0000,-5.0000;-5.0000,5.0000;5.0000,5.0000;5.0000,-5.0000] a=-100.0000} clip_sb=k=0{} inter_bs=k=1{n4[5.0000,5.0000;-5.0000,5.0000;-5.0000,-5.0000;5.0000,-5.0000] a=100.0000} inter_sb=k=1{n4[5.0000,5.0000;-5.0000,5.0000;-5.0000,-5.0000;5.0000,-5.0000] a=100.0000} excl_bs=k=2{n4[20.0000,20.0000;-20.0000,20.0000;-20.0000,-20.0000;20.0000,-20.0000] a=1600.0000|n4[-5.0000,-5.0000;-5.0000,5.0000;5.0000,5.0000;5.0000,-5.0000] a=-100.0000} excl_sb=k=2{n4[20.0000,20.0000;-20.0000,20.0000;-20.0000,-20.0000;20.0000,-20.0000] a=1600.0000|n4[-5.0000,-5.0000;-5.0000,5.0000;5.0000,5.0000;5.0000,-5.0000] a=-100.0000} adj_merge=k=1{n4[30.0000,-10.0000;30.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000] a=800.0000} adj_clip=k=1{n4[10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000] a=400.0000} adj_inter=k=0{} ovl_excl=k=2{n6[16.0000,16.0000;-4.0000,16.0000;-4.0000,10.0000;10.0000,10.0000;10.0000,-4.0000;16.0000,-4.0000] a=204.0000|n6[10.0000,-4.0000;-4.0000,-4.0000;-4.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000] a=204.0000} ovl_clip=k=1{n6[10.0000,-4.0000;-4.0000,-4.0000;-4.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000] a=204.0000} ovl_inter=k=1{n4[10.0000,10.0000;-4.0000,10.0000;-4.0000,-4.0000;10.0000,-4.0000] a=196.0000}'),
    ('geo2d_lattice_joins', 'geo2d_lattice.gd', ['--arm=joins'], 0,
     'PASS geo2d_lattice joins poly_p2_sq=k=1{n8[12.0000,-10.8284;12.0000,10.8284;10.8284,12.0000;-10.8284,12.0000;-12.0000,10.8284;-12.0000,-10.8284;-10.8284,-12.0000;10.8284,-12.0000] a=573.2548} poly_p2_rd=k=1{n12[11.6944,-11.0625;12.0000,-10.0000;12.0000,10.0000;11.0625,11.6944;10.0000,12.0000;-10.0000,12.0000;-11.6944,11.0625;-12.0000,10.0000;-12.0000,-10.0000;-11.0625,-11.6944;-10.0000,-12.0000;10.0000,-12.0000] a=571.0277} poly_p2_mt=k=1{n4[12.0000,12.0000;-12.0000,12.0000;-12.0000,-12.0000;12.0000,-12.0000] a=576.0000} poly_m2_sq=k=1{n4[8.0000,-8.0000;8.0000,8.0000;-8.0000,8.0000;-8.0000,-8.0000] a=256.0000} poly_m2_rd=k=1{n4[8.0000,-8.0000;8.0000,8.0000;-8.0000,8.0000;-8.0000,-8.0000] a=256.0000} poly_m2_mt=k=1{n4[8.0000,-8.0000;8.0000,8.0000;-8.0000,8.0000;-8.0000,-8.0000] a=256.0000} poly_zero=k=1{n4[-10.0000,-10.0000;10.0000,-10.0000;10.0000,10.0000;-10.0000,10.0000] a=400.0000} poly_collapse=k=0{} line_rd_joined=k=2{n11[21.6944,-1.0625;22.0000,0.0000;22.0000,20.0000;21.0625,21.6944;19.1289,21.8003;18.5858,21.4142;-1.4142,1.4142;-1.9494,-0.4468;-0.6571,-1.8890;0.0000,-2.0000;20.0000,-2.0000] a=347.4172|n3[4.8284,2.0000;18.0000,15.1716;18.0000,2.0000] a=-86.7453} line_sq_joined=k=2{n6[22.0000,-0.8284;22.0000,21.3364;19.5307,22.3592;-2.3592,0.4693;-1.3364,-2.0000;20.8284,-2.0000] a=350.5732|n3[4.8284,2.0000;18.0000,15.1716;18.0000,2.0000] a=-86.7453} line_mt_joined=k=2{n5[22.0000,21.3364;19.5307,22.3592;-2.3592,0.4693;-1.3364,-2.0000;22.0000,-2.0000] a=351.2595|n3[4.8284,2.0000;18.0000,15.1716;18.0000,2.0000] a=-86.7453} line_rd_butt=k=1{n8[21.6944,-1.0625;22.0000,0.0000;22.0000,20.0000;18.0000,20.0000;18.0000,2.0000;0.0000,2.0000;0.0000,-2.0000;20.0000,-2.0000] a=158.7569} line_rd_square=k=1{n8[21.6944,-1.0625;22.0000,0.0000;22.0000,22.0000;18.0000,22.0000;18.0000,2.0000;-2.0000,2.0000;-2.0000,-2.0000;20.0000,-2.0000] a=174.7569} line_rd_round=k=1{n14[21.6944,-1.0625;22.0000,0.0000;22.0000,20.0000;21.0625,21.6944;19.1289,21.8003;18.0120,20.2184;18.0000,20.0000;18.0000,2.0000;0.0000,2.0000;-1.6944,1.0625;-1.8003,-0.8711;-0.2184,-1.9880;0.0000,-2.0000;20.0000,-2.0000] a=169.3603} line_m2_joined=k=2{n11[21.6944,-1.0625;22.0000,0.0000;22.0000,20.0000;21.0625,21.6944;19.1289,21.8003;18.5858,21.4142;-1.4142,1.4142;-1.9494,-0.4468;-0.6571,-1.8890;0.0000,-2.0000;20.0000,-2.0000] a=347.4172|n3[4.8284,2.0000;18.0000,15.1716;18.0000,2.0000] a=-86.7453} line_default=k=1{n7[22.0000,-0.8284;22.0000,22.0000;18.0000,22.0000;18.0000,2.0000;-2.0000,2.0000;-2.0000,-2.0000;20.8284,-2.0000] a=175.3137}'),
    ('geo2d_lattice_trig', 'geo2d_lattice.gd', ['--arm=trig'], 0,
     'PASS geo2d_lattice trig hull=k=1{n5[0.0000,0.0000;20.0000,0.0000;20.0000,20.0000;0.0000,20.0000;0.0000,0.0000]} tri_idx=[1, 2, 3, 3, 4, 0, 0, 1, 3] tri_area=280.0000 poly_area=280.0000 decomp=k=3{n3[20.0000,0.0000;20.0000,20.0000;10.0000,8.0000]|n3[0.0000,0.0000;20.0000,0.0000;10.0000,8.0000]|n3[0.0000,20.0000;0.0000,0.0000;10.0000,8.0000]} dec_area=280.0000 delaunay=[0, 1, 3, 0, 2, 3, 1, 2, 4, 2, 3, 4, 1, 3, 4] atlas3=points=[(0.0000,0.0000),(20.0000,0.0000),(20.0000,5.0000)] size=(25.0000,10.0000) atlas1=points=[(0.0000,0.0000)] size=(4.0000,4.0000) atlas_sq=points=[(0.0000,0.0000),(0.0000,3.0000)] size=(7.0000,6.0000)'),
    ('geo2d_lattice_pred', 'geo2d_lattice.gd', ['--arm=pred'], 0,
     'PASS geo2d_lattice pred pip=in=true out=false edge=true corner=true outside_corner=true pic=on=true out=false center=true isect=line=(2.0, 0.0) seg=(2.0, 0.0) miss=<null> closest=cap=(3.0, 0.0) uncap=(13.0, 0.0) segseg=[(5.0, 0.0), (5.0, 0.0)] degenerate=(2.0, 2.0) tri=in=true out=false edge=false vertex=false bresenham=fwd=[(0, 0), (1, 1), (2, 1), (3, 2), (4, 2), (5, 3)] rev=[(5, 3), (4, 2), (3, 2), (2, 1), (1, 1), (0, 0)] diag=[(0, 0), (1, 1), (2, 2), (3, 3)] sic=fwd=0.2500 rev=0.2500 miss=-1.0000 inside=-1.0000 startinside=0.5000 tangent=0.5000'),
    ('geo2d_lattice_pipedges', 'geo2d_lattice.gd', ['--arm=pipedges'], 0,
     'PASS geo2d_lattice pipedges pip_right=[0:true,1e-6:true,1e-4:true,1e-3:false,1e-2:false,0.1:false,1.0:false] pip_right_cw=[0:true,1e-4:true,1e-2:false,0.1:false] pip_corner=on=true e4=true e2=false d1=false tri_ladder=[0:false,1e-6:true,1e-4:true,1e-2:true,0.1:true] circle_ladder=on=true in=true out=false'),
    ('geo2d_lattice_edge', 'geo2d_lattice.gd', ['--arm=edge'], 0,
     'PASS geo2d_lattice edge clip_emptyR=k=1{n4[10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000]} merge_emptyR=k=1{n4[10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000]} inter_emptyR=k=0{} excl_emptyR=k=1{n4[10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000]} clip_emptyL=k=0{} merge_emptyL=k=1{n4[10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000]} inter_emptyL=k=0{} clip_self=k=0{} merge_self=k=1{n4[10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000]} inter_self=k=1{n4[10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000;10.0000,-10.0000]} excl_self=k=0{} clip_one=k=0{} clip_two=k=0{} tri=one=[] two=[] dup=[0, 3, 2, 2, 1, 0] col=[0, 2, 1] bow=[] sq=[3, 0, 1, 1, 2, 3] cw=sq=false rev=true one=false two=false col=false bow=false pip_degen=bow=true col=false one=false clip_bow=k=0{} clip_rev=k=1{n4[-2.0000,-10.0000;-2.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000]} hull_degen=one=k=1{n1[1.0000,1.0000]} col=k=1{n3[0.0000,0.0000;2.0000,0.0000;0.0000,0.0000]} sq=k=1{n5[-10.0000,-10.0000;10.0000,-10.0000;10.0000,10.0000;-10.0000,10.0000;-10.0000,-10.0000]}'),
    ('geo2d_lattice_offempty', 'geo2d_lattice.gd', ['--arm=offempty'], 0,
     'PASS geo2d_lattice offempty call=offset_polygon(empty,2.0,JOIN_ROUND) result=k=0{}'),
    ('geo2d_lattice_offdeg', 'geo2d_lattice.gd', ['--arm=offdeg'], 0,
     'PASS geo2d_lattice offdeg col3=k=1{n10[3.6944,-1.0625;3.8003,0.8711;2.2184,1.9880;2.0000,2.0000;0.0000,2.0000;-1.6944,1.0625;-1.8003,-0.8711;-0.2184,-1.9880;0.0000,-2.0000;2.0000,-2.0000]} two=k=1{n10[5.6944,-1.0625;5.8003,0.8711;4.2184,1.9880;4.0000,2.0000;0.0000,2.0000;-1.6944,1.0625;-1.8003,-0.8711;-0.2184,-1.9880;0.0000,-2.0000;4.0000,-2.0000]} one=k=1{n7[2.2470,-0.5637;3.0000,1.0000;2.2470,2.5637;0.5550,2.9499;-0.8019,1.8678;-0.8019,0.1322;0.5550,-0.9499]}'),
    ('geo2d_lattice_atlasempty', 'geo2d_lattice.gd', ['--arm=atlasempty'], 0,
     'PASS geo2d_lattice atlasempty call=make_atlas(empty) result=points=[] size=(0.0000,0.0000)'),
    ('geo2d_lattice_polyendpoly', 'geo2d_lattice.gd', ['--arm=polyendpoly'], 0,
     'PASS geo2d_lattice polyendpoly open_endpolygon=k=0{} closed_endpolygon=k=0{} closed_endjoined=k=2{n12[21.6944,-1.0625;22.0000,0.0000;22.0000,20.0000;21.0625,21.6944;20.0000,22.0000;0.0000,22.0000;-1.6944,21.0625;-2.0000,20.0000;-2.0000,0.0000;-1.0625,-1.6944;0.0000,-2.0000;20.0000,-2.0000] a=571.0277|n4[2.0000,2.0000;2.0000,18.0000;18.0000,18.0000;18.0000,2.0000] a=-256.0000} closed_endbutt=k=1{n12[21.6944,-1.0625;22.0000,0.0000;22.0000,20.0000;21.0625,21.6944;20.0000,22.0000;0.0000,22.0000;0.0000,18.0000;18.0000,18.0000;18.0000,2.0000;0.0000,2.0000;0.0000,-2.0000;20.0000,-2.0000] a=237.5139}'),
    ('geo2d_lattice_bridge', 'geo2d_lattice.gd', ['--arm=bridge'], 0,
     'PASS geo2d_lattice bridge wall=k=1{n4[60.0000,60.0000;-60.0000,60.0000;-60.0000,30.0000;60.0000,30.0000]} tps=60 frames=60 rest=y=82.3000 vel=0.0000,0.0000 self_hit=1'),
    ('geo2d_lattice_ring', 'geo2d_lattice.gd', ['--arm=ring'], 0,
     'PASS geo2d_lattice ring ring=k=2{n4[40.0000,40.0000;-40.0000,40.0000;-40.0000,-40.0000;40.0000,-40.0000] a=6400.0000|n4[-10.0000,-10.0000;-10.0000,10.0000;10.0000,10.0000;10.0000,-10.0000] a=-400.0000} colliders=n=1 contour0_only drop_center=y=-47.8043 vel=0.0000,0.0000 hits=1 tps=60 frames=60'),
    ('geo2d_lattice_ring2', 'geo2d_lattice.gd', ['--arm=ring2'], 0,
     'PASS geo2d_lattice ring2 ring=k=2{n4[40.0000,40.0000;-40.0000,40.0000;-40.0000,-40.0000;40.0000,-40.0000] a=6400.0000|n4[-10.0000,-10.0000;-10.0000,10.0000;10.0000,10.0000;10.0000,-10.0000] a=-400.0000} colliders=n=2 all_contours drop_center=y=-47.8043 vel=0.0000,0.0000 hits=1 tps=60 frames=60'),
    ('geo2d_lattice_ring4', 'geo2d_lattice.gd', ['--arm=ring4'], 0,
     'PASS geo2d_lattice ring4 slabs=4 drop_center=y=-47.8043 vel=0.0000,0.0000 hits=1 tps=60 frames=60'),
    ('geo2d_lattice_ringhits', 'geo2d_lattice.gd', ['--arm=ringhits'], 0,
     'PASS geo2d_lattice ringhits hits=[A_contour0[centre:1,top:1,right:1,bottom:1,left:1]|B_both[centre:2,top:1,right:1,bottom:1,left:1]|C_slabs[centre:0,top:1,right:1,bottom:1,left:1]] ring=k=2{n4[40.0000,40.0000;-40.0000,40.0000;-40.0000,-40.0000;40.0000,-40.0000] a=6400.0000|n4[-10.0000,-10.0000;-10.0000,10.0000;10.0000,10.0000;10.0000,-10.0000] a=-400.0000} tps=60'),
    ('input89_edges_exact', 'input89_edges.gd', ['--arm=exact'], 0,
     ('PASS input89_edges exact control=wW_eia_ex=1_actual=1 sW_eia_ex=1_actual=1 eia_wW=ex=1 inex=1 eia_sW_vs_wW=ex=0 inex=1 eia_wW_vs_sW=ex=0 inex=0 eia_sW=ex=1 inex=1 eia_both=plainW[ex=1 inex=1] shiftW[ex=1 inex=1] poll_shiftW_on_plainW_binding=w[ex=false inex=true] sw[ex=true inex=true] poll_after_shiftW_release=w[ex=false inex=false] sw[ex=false inex=false] poll_plainW=w[ex=true inex=true] sw[ex=false inex=false] both[ex=true inex=true] poll_plainW_released=w[ex=false inex=false] both[ex=false inex=false] just_after_flush=w_jp[ex=false inex=true]',
      'PASS input89_edges exact control=wW_eia_ex=1_actual=1 sW_eia_ex=1_actual=1 eia_wW=ex=1 inex=1 eia_sW_vs_wW=ex=0 inex=1 eia_wW_vs_sW=ex=0 inex=0 eia_sW=ex=1 inex=1 eia_both=plainW[ex=1 inex=1] shiftW[ex=1 inex=1] poll_shiftW_on_plainW_binding=w[ex=false inex=true] sw[ex=true inex=true] poll_after_shiftW_release=w[ex=false inex=false] sw[ex=false inex=false] poll_plainW=w[ex=true inex=true] sw[ex=false inex=false] both[ex=true inex=true] poll_plainW_released=w[ex=false inex=false] both[ex=false inex=false] just_after_flush=w_jp[ex=false inex=false]')),
    ('input89_edges_axisdev', 'input89_edges.gd', ['--arm=axisdev'], 0,
     'PASS input89_edges axisdev census=joys=0 eia_avail=true dz_ax0=0.2000 dz_ui_accept=0.5000 eia_dev0=ax0[ex=1 inex=1] axany[ex=1 inex=1] eia_dev5=ax0[ex=0 inex=0] axany[ex=1 inex=1] eia_dev-1=ax0[ex=0 inex=0] axany[ex=1 inex=1] poll_dev5=ax0=false axany=true axis5=1.0000 axis0=0.0000 strength0=0.0000 poll_dev0=ax0=true axany=true axis0=1.0000 strength0=1.0000 raw0=1.0000 poll_dev0_06=ax0=true axis0=0.6000 strength0=0.5000 raw0=0.6000 poll_dev0_neg=ax0=false axany=true axis0=-1.0000 poll_release=ax0=false axany=true axis0=0.0000'),
    ('geo2d_lattice_lineempty', 'geo2d_lattice.gd', ['--arm=lineempty'], -6,
     'R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)'),
    # r90: the RigidBody2D authorability lattice (r88-census top-ranked
    # REMAINING PINNABLE family) — gravity_scale/COM/integrator ordering +
    # impulse/freeze/contact extras. Probe rb_lattice.gd sha256 10da2291…
    # (folded variant of scout sha256 4f201e85…) + rb_watch.gd sha256
    # e349faa0… (verbatim — the _integrate_forces forwarder; BOTH files are
    # required). Boundary folds landed, all mandatory:
    #   * engine precondition — every arm emits eng=<live PhysicsServer2D
    #     class> FIRST on the PASS line: under a Dummy boot the family is
    #     silently vacuous (ncb=0, tld=-1, no motion, 0B stderr — boundary
    #     §3), so eng=PhysicsServer2DDummy mismatches loudly instead of
    #     passing vacuously;
    #   * tps qualification — every motion row pins tps=60 plus step
    #     accounting pf_delta/tick_dh (await↔step 1:1); the damped fall is
    #     NOT tps-invariant at equal duration (scout §3.11) and the 30 tps
    #     late_body pairing (ncb=frames-1) is never pinned;
    #   * pairing key — cb0≡f1 is pinned only with cb0_rel=1/obs0_rel=1
    #     (boundary §8.1); lag's exp=N= derives n from the callback count,
    #     never from --frames;
    #   * impulse oracle bound — pinned lanes stay in the resolvable band
    #     (iI>=0.024; at inertia>=~1e9 the 6-dp iI oracle collapses and the
    #     row would stop discriminating — boundary §8.5, no extreme lanes
    #     authored); impedge pins only the typed refusals
    #     (set_inertia:334 / set_mass:324 — a DIFFERENT error path than
    #     comrefuse's :376) and the AUTO-sentinel lane (inertia=0.0).
    # Signatures byte-pinned from 6 fresh reps each
    # (corpus/live/r90-author/runs/, out_uniq=err_uniq=1). Rows inserted
    # ahead of the crash/descendant tail — descendant_pipe_detached_control's
    # sleep-8 gap stays adjacent to the meta probes.
    ('r90_lattice_props', 'rb_lattice.gd', ['--arm=props'], 0,
     'PASS r90_lattice props eng=PhysicsServer2D tps=60 nprops=88 props=[mass|physics_material_override|gravity_scale|Mass Distribution|center_of_mass_mode|center_of_mass|inertia|Deactivation|sleeping|can_sleep|lock_rotation|freeze|freeze_mode|Solver|custom_integrator|continuous_cd|contact_monitor|max_contacts_reported|Linear|linear_velocity|linear_damp_mode|linear_damp|Angular|angular_velocity|angular_damp_mode|angular_damp|Constant Forces|constant_force|constant_torque|disable_mode|Collision|collision_layer|collision_mask|collision_priority|Input|input_pickable|Transform|position|rotation|rotation_degrees|scale|skew|transform|global_position|global_rotation|global_rotation_degrees|global_scale|global_skew|global_transform|Visibility|visible|modulate|self_modulate|show_behind_parent|top_level|clip_children|oversampling_with_scale|light_mask|visibility_layer|Ordering|z_index|z_as_relative|y_sort_enabled|Texture|texture_filter|texture_repeat|Material|material|use_parent_material|name|unique_name_in_owner|scene_file_path|owner|multiplayer|Process|process_mode|process_priority|process_physics_priority|Thread Group|process_thread_group|process_thread_group_order|process_thread_messages|Physics Interpolation|physics_interpolation_mode|Auto Translate|auto_translate_mode|Editor Description|editor_description] u_center_of_mass=6 u_center_of_mass_local=-1 u_inertia=6 u_linear_damp=6 u_angular_damp=6 u_constant_force=6 u_constant_torque=6 u_freeze_mode=6 u_sleeping=6 methods=[_edit_get_state|_edit_set_state|_integrate_forces|add_constant_central_force|add_constant_force|add_constant_torque|apply_central_force|apply_central_impulse|apply_force|apply_impulse|apply_torque|apply_torque_impulse|force_update_transform|get_angular_damp|get_angular_damp_mode|get_constant_force|get_constant_torque|get_gravity|get_gravity_scale|get_linear_damp|get_linear_damp_mode|set_angular_damp|set_angular_damp_mode|set_constant_force|set_constant_torque|set_gravity_scale|set_linear_damp|set_linear_damp_mode] enum=COM_AUTO=0,COM_CUSTOM=1,FM_STATIC=0,FM_KINEMATIC=1,CCD_OFF=0,CCD_RAY=1,CCD_SHAPE=2,DAMP_COMBINE=0,DAMP_REPLACE=1 ps_gravity=980.0000 ps_ldamp=0.1000 ps_adamp=1.0000 ps_tps=60 d_mass=1.0000 d_inertia=0.0000 d_center_of_mass=0.0000,0.0000 d_center_of_mass_local=<null> d_center_of_mass_mode=0 d_gravity_scale=1.0000 d_custom_integrator=false d_freeze=false d_freeze_mode=0 d_lock_rotation=false d_can_sleep=true d_sleeping=false d_continuous_cd=0 d_max_contacts_reported=0 d_contact_monitor=false d_linear_damp=0.0000 d_linear_damp_mode=0 d_angular_damp=0.0000 d_angular_damp_mode=0 d_constant_force=0.0000,0.0000 d_constant_torque=0.0000'),
    ('r90_lattice_comread', 'rb_lattice.gd', ['--arm=comread'], 0,
     'PASS r90_lattice comread eng=PhysicsServer2D tps=60 auto_com=0.0000,0.0000 auto_mode=0 coml_prop=<null> custom_mode=1 custom_com=4.0000,0.0000 rot_com=4.0000,0.0000 inertia5=5.0000 inertia0=0.0000 inertia33_mass4=33.0000 inertia33_mass1=33.0000 gscale_neg=-1.5000 gscale0=0.0000'),
    ('r90_lattice_comrefuse', 'rb_lattice.gd', ['--arm=comrefuse'], 0,
     'PASS r90_lattice comrefuse eng=PhysicsServer2D tps=60 auto_set4=com=0.0000,0.0000 mode=0 auto_set0=com=0.0000,0.0000 mode=0 custom_set4=com=4.0000,0.0000 mode=1 custom_set0=com=0.0000,0.0000 mode=1 back_auto=com=0.0000,0.0000 mode=0'),
    ('r90_lattice_gravity', 'rb_lattice.gd', ['--arm=gravity'], 0,
     'PASS r90_lattice gravity eng=PhysicsServer2D tps=60 f30=g0[y=0.0000,vy=0.0000]|g05[y=62.2838,vy=239.1703]|g1[y=124.5675,vy=478.3405]|g2[y=249.1351,vy=956.6811]|gm1[y=-124.5675,vy=-478.3405]|zv[y=-14.6187,vy=-28.5357]|zv0[y=-15.0000,vy=-30.0000]|cf[y=124.5675,vy=478.3405] f60=g0[y=0.0000,vy=0.0000]|g05[y=241.1125,vy=466.6662]|g1[y=482.2250,vy=933.3325]|g2[y=964.4500,vy=1866.6649]|gm1[y=-482.2250,vy=-933.3325]|zv[y=-28.5238,vy=-27.1429]|zv0[y=-30.0000,vy=-30.0000]|cf[y=482.2250,vy=933.3325] ncb=60 cb0_rel=1 obs0_rel=1 pf_delta=60 tick_dh=1:59'),
    ('r90_lattice_damp', 'rb_lattice.gd', ['--arm=damp'], 0,
     'PASS r90_lattice damp eng=PhysicsServer2D tps=60 f30=default[y=124.5675,vy=478.3405]|rep0[y=126.5834,vy=490.0001]|rep05[y=116.9554,vy=435.1487]|comb05[y=115.1592,vy=425.1562] f60=default[y=482.2250,vy=933.3325]|rep0[y=498.1666,vy=979.9996]|rep05[y=425.5192,vy=773.6876]|comb05[y=412.9205,vy=739.6441] tld=default=0.1000|rep0=0.0000|rep05=0.5000|comb05=0.6000 ncb=default=60|rep0=60|rep05=60|comb05=60 cb0_rel=1 obs0_rel=1 pf_delta=60 tick_dh=1:59'),
    ('r90_lattice_order', 'rb_lattice.gd', ['--arm=order'], 0,
     'PASS r90_lattice order eng=PhysicsServer2D tps=60 ncb=60 cb0=st=0.016667 ty=0.2722 vy=16.3333 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb1=st=0.016667 ty=0.8162 vy=32.6394 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb2=st=0.016667 ty=1.6315 vy=48.9184 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb3=st=0.016667 ty=2.7177 vy=65.1702 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cb4=st=0.016667 ty=4.0743 vy=81.3949 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 cblast=st=0.016667 ty=482.2250 vy=933.3325 g=980.0000 tld=0.1000 im=1.0000 iI=0.031250 f1=y=0.2722,vy=16.3333 f2=y=0.8162,vy=32.6394 f3=y=1.6315,vy=48.9184 f60=y=482.2250,vy=933.3325 cb0_rel=1 obs0_rel=1 pf_delta=60 tick_dh=1:59 cbpf_dh=1:59'),
    ('r90_lattice_write', 'rb_lattice.gd', ['--arm=write'], 0,
     'PASS r90_lattice write eng=PhysicsServer2D tps=60 step=0.016667 f30=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=118.4167,vy=490.0001] f60=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=481.8333,vy=979.9996] ncb=60 cb0_rel=1 obs0_rel=1 pf_delta=60 tick_dh=1:59'),
    ('r90_lattice_impulse', 'rb_lattice.gd', ['--arm=impulse'], 0,
     'PASS r90_lattice impulse eng=PhysicsServer2D tps=60 post=c_central[v=0.0000,-60.0000,w=0.0000,iI=0.031250,im=1.0000]|c_off[v=0.0000,-60.0000,w=-15.0000,iI=0.031250,im=1.0000]|c_tq[v=0.0000,0.0000,w=15.0000,iI=0.031250,im=1.0000]|r_tq[v=0.0000,0.0000,w=11.5200,iI=0.024000,im=1.0000]|r_off[v=0.0000,-60.0000,w=-11.5200,iI=0.024000,im=1.0000] ncb=c_central=4|c_off=4|c_tq=4|r_tq=4|r_off=4 cb0_rel=1 obs0_rel=1 pf_delta=4 tick_dh=1:3'),
    ('r90_lattice_impedge', 'rb_lattice.gd', ['--arm=impedge'], 0,
     'PASS r90_lattice impedge eng=PhysicsServer2D tps=60 set=neg_i[i=0.0000,m=1.0000]|zero_i[i=0.0000,m=1.0000]|mass0[i=0.0000,m=1.0000]|massneg[i=0.0000,m=1.0000] post=neg_i[v=0.0000,0.0000,w=15.0000,iI=0.031250,im=1.0000]|zero_i[v=0.0000,0.0000,w=15.0000,iI=0.031250,im=1.0000]|mass0[v=0.0000,0.0000,w=15.0000,iI=0.031250,im=1.0000]|massneg[v=0.0000,0.0000,w=15.0000,iI=0.031250,im=1.0000] ncb=neg_i=4|zero_i=4|mass0=4|massneg=4 cb0_rel=1 obs0_rel=1 pf_delta=4 tick_dh=1:3'),
    ('r90_lattice_freezelock', 'rb_lattice.gd', ['--arm=freezelock', '--frames=120'], 0,
     'PASS r90_lattice freezelock eng=PhysicsServer2D tps=60 f30=f_normal[y=-7.6969,vy=0.0000,w=0.0000,fz=false]|f_static[y=-100.0000,vy=0.0000,w=0.0000,fz=true]|f_kin[y=-100.0000,vy=-30.0000,w=0.0000,fz=true]|f_kin2[y=-100.0000,vy=-30.0000,w=0.0000,fz=true]|f_lock[y=-128.0000,vy=-60.0000,w=0.0000,fz=false] sleep=s_off[sl=false,y=-7.7000,vy=0.0000] s_on[sl=true,y=-7.7000,vy=0.0000] ncb=120 cb0_rel=1 obs0_rel=1 pf_delta=120 tick_dh=1:119'),
    ('r90_lattice_contacts', 'rb_lattice.gd', ['--arm=contacts'], 0,
     'PASS r90_lattice contacts eng=PhysicsServer2D tps=60 rest=y=-7.7000,vy=0.0000 cb=count=1 y=-7.7000 pos=0.0000,0.3000 cvel=0.0000,16.3333 entered=1 ncb=45 cb0_rel=1 obs0_rel=1 pf_delta=60 tick_dh=1:59'),
    ('r90_lattice_lag', 'rb_lattice.gd', ['--arm=lag', '--frames=30'], 0,
     'PASS r90_lattice lag eng=PhysicsServer2D tps=60 a=y=126.5834,vy=490.0001 b=y=118.4167,vy=490.0001 c=y=124.5675,vy=478.3405 d=dy=8.1667,dvy=0.0000 step=0.016667 gdt=16.3333 gdt2=0.272222 exp=N=30 exp_dy=8.1667 exp_dvy_gdt=16.3333 acc=an=30,bn=30,apre=490.0001,bpre=473.6668,bpost=490.0001 cb0_rel=1 obs0_rel=1 pf_delta=30 tick_dh=1:29'),
    # r91: the Navigation2D authorability lattice — NavigationServer2D
    # map/region/link lifecycle + map-sync gating, exact path/query geometry,
    # region steering, NavigationAgent2D, agent avoidance, headless baking,
    # and the avoidance-callback teardown crash class. Probe nav_lattice.gd
    # (folded variant of r91-scout's frozen probe sha256 efb496e5…).
    # Boundary folds (r91-boundary 93ce7c4) applied — all measured:
    #   * every scheduler/rate field (settle/iter/ladder/first_reach*/
    #     walk_steps/reached_at/first_reachable/iter_b/link_iter/gate) is a
    #     trailing diagnostic tail, NEVER inside the pin — the sync ladder is
    #     not constant (4..10 at 60 tps under ambient load, 43 at ff30, never
    #     at ff120); no universal frame counts are pinned anywhere below.
    #   * _await_sync polls iteration_id>=2 AND reach (necessary + sufficient
    #     gate, boundary attack 1) with a 48-frame bound; exhaustion emits a
    #     `STALE nav_lattice <arm>` line + exit 2 — a sync stall fails loudly
    #     instead of printing a PASS-shaped payload off an unsynced map.
    #   * same-frame OLD-answer reads are race fields, unpinned (boundary §3:
    #     invalidation can land in frame 0, 1/5 at 60 tps under load): dis_same
    #     and fwd_disabled_same sit in the tails. chg_same=false stays pinned
    #     (new answer never live same-frame, 100% of 60-tps runs).
    #   * agent reads is_navigation_finished() BEFORE is_target_reached()
    #     (boundary §6: scout's reached_at=-1 was a query-order artifact; the
    #     pin carries the order-independent final state only).
    #   * avoid pins the boundary-confirmed invariants probe-side
    #     (sum_bound_ok = every measured frame |a|+|b| <= 20.001 — the ORCA
    #     bound, never above 20.0000 in 100 samples; dirs_ok = a.x>0 & b.x<0),
    #     never the process-dependent split digits.
    #   * nav_lattice_teardown_crash arms the teardown-crash negative control:
    #     exit with a live avoidance callback -> deterministic double-free
    #     (rc=-6; 51/51 boundary + 9/9 scout-discovery repro), stderr fragment
    #     bound via required_stderr. teardown_clean pins the discipline
    #     control (clear + >=1 frame + free -> exit 0).
    # Signatures verified substring-stable across fresh reps on this loaded
    # host. Rows inserted ahead of the crash/descendant tail —
    # descendant_pipe_detached_control's sleep-8 gap stays adjacent to the
    # meta probes.
    ('nav_lattice_census', 'nav_lattice.gd', ['--arm=census'], 0,
     'PASS nav_lattice census srv_methods=199 poly_methods=134 srv_info=[0,1,2,3,9,4,5,7,6,8] pgt=[0,1,2,3] sgm=[0,1,2,3] sp=[0,1,2] pp=[2,0,1] md=[0,2,1,4,7] alg=0 poly_defaults=agent_r=10.0000,cell=1.0000,border=0.0000,pgt=2,sgm=0,sp=0,cmask=4294967295,brect=[P: (0.0, 0.0), S: (0.0, 0.0)],boff=(0.0, 0.0),polys=0 reg_defaults=cost=1.0000,enter=0.0000,en=true,edge=true agent_defaults=r=10.0000,path_d=20.0000,tgt_d=10.0000,maxspeed=100.0000,nd=500.0000,mn=10,tha=1.0000,tho=0.0000,avoid=false,prio=1.0000,layers=1,pp=0,simpl=false,eps=0.0000 qp_defaults=pp=0,md=7,layers=1,maxlen=0.0000,maxrad=0.0000,maxdist=0.0000,maxpolys=4096,simpl=false,eps=0.0000'),
    ('nav_lattice_path', 'nav_lattice.gd', ['--arm=path'], 0,
     'PASS nav_lattice path diag=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)] diag_raw=[(20.0000,180.0000),(40.0000,20.0000),(180.0000,20.0000)] same=[(20.0000,20.0000),(20.0000,20.0000)] out_start=[(0.0000,0.0000),(40.0000,8.8889),(90.0000,20.0000)] out_target=[(20.0000,20.0000),(40.0000,22.2222),(200.0000,40.0000)] gap=[(20.0000,20.0000),(40.0000,20.0000),(200.0000,20.0000)] closest_in=(20.0000,20.0000) closest_out=(0.0000,0.0000) owner_in_is_rv=true owner_out_is_rv=true gap20=[(20.0000,20.0000),(40.0000,20.0000),(205.0000,20.0000),(250.0000,20.0000)] gap20_reach=true gap20_margin=20.0000'),
    ('nav_lattice_query', 'nav_lattice.gd', ['--arm=query'], 0,
     'PASS nav_lattice query postproc=[pp2=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)],pp0=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)],pp1=[(20.0000,180.0000),(40.0000,20.0000),(180.0000,20.0000)]] metadata=[md0:[]|n0|n0,md2:[]|n3|n0,md1:[0,0,0]|n0|n0,md4:[]|n0|n3,md7:[0,0,0]|n3|n3] maxlen=[(20.0000,180.0000),(24.2426,150.3015)] maxrad=[(20.0000,180.0000),(20.0814,179.4301)] maxdist=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)] maxpolys=[(20.0000,180.0000),(40.0000,20.0000)] simplify=[(20.0000,180.0000),(40.0000,40.0000),(180.0000,20.0000)] layers0=[] length=282.8427'),
    ('nav_lattice_sync', 'nav_lattice.gd', ['--arm=sync'], 0,
     'PASS nav_lattice sync pre_iter=0 pre_regions=0 pre_path=[] pre_closest=(0.0000,0.0000) cellsize=1.0000 edgemargin=1.0000 linkradius=4.0000 merge_scale=0.1000 useedge=true async=true active_after=true chg_same=false chg_settled=true dis_settled=false'),
    ('nav_lattice_region', 'nav_lattice.gd', ['--arm=region'], 0,
     'PASS nav_lattice region base=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] top_cost1=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] bot_cost1=[(10.0000,50.0000),(20.0000,40.0000),(80.0000,40.0000),(90.0000,50.0000)] enter500=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] l1=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] l2=[(20.0000,40.0000),(80.0000,40.0000)] l3=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] dis_settled=[(10.0000,50.0000),(20.0000,40.0000),(80.0000,40.0000),(90.0000,50.0000)] reenabled=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] swapped=[(10.0000,50.0000),(20.0000,40.0000),(80.0000,40.0000),(90.0000,50.0000)] restored=[(10.0000,50.0000),(20.0000,60.0000),(80.0000,60.0000),(90.0000,50.0000)] counts=regs=4,cost_a=1.0,cost_b=1.0,en_a=true,en_b=true'),
    ('nav_lattice_agent', 'nav_lattice.gd', ['--arm=agent'], 0,
     'PASS nav_lattice agent settled=(180.0000,180.0000)/false/true/false/226.27/226.27/1 fin=true reached=true reachable=true dist=2.2741 final_pos=(178.3920,178.3920) final_target=(180.0000,180.0000) path=[(20.0000,20.0000),(180.0000,180.0000)] desired=4.0 target_desired=8.0'),
    ('nav_lattice_avoid', 'nav_lattice.gd', ['--arm=avoid'], 0,
     'PASS nav_lattice avoid pa=(150.0000,150.0000) pb=(190.0000,150.0000) warm_n_a=16 n_a=21 n_b=21 sum_bound_ok=true dirs_ok=true has_cb_a=true radius_a=10.0 maxspeed_a=50.0 obs_pos=(170.0000,150.0000) obs_en=false'),
    ('nav_lattice_bake', 'nav_lattice.gd', ['--arm=bake'], 0,
     'PASS nav_lattice bake outline_polys=4 outline_verts=8 hole_across=[(100.0000,20.0000),(140.0000,60.0000),(140.0000,140.0000),(100.0000,180.0000)] hole_straight=[(20.0000,100.0000),(60.0000,60.0000),(140.0000,60.0000),(180.0000,100.0000)] parse_obs=1 parse_trav=0 parse_has=false baked_polys=4 baked_verts=8 collider_only_polys=0 through=[(-100.0000,0.0000),(-55.0000,55.0000),(55.0000,55.0000),(100.0000,-0.0000)] around=[(-100.0000,-100.0000),(-55.0000,55.0000),(100.0000,100.0000)] outside=[(-145.0000,-145.0000),(-55.0000,55.0000),(100.0000,100.0000)]'),
    ('nav_lattice_link', 'nav_lattice.gd', ['--arm=link'], 0,
     'PASS nav_lattice link bidir_default=true en_default=true fwd_default=[(10.0000,50.0000),(100.0000,50.0000),(400.0000,50.0000),(490.0000,50.0000)] rev_default=[(490.0000,50.0000),(400.0000,50.0000),(100.0000,50.0000),(10.0000,50.0000)] rev_bidir=[(490.0000,50.0000),(400.0000,50.0000),(100.0000,50.0000),(10.0000,50.0000)] fwd_disabled_settled=[(10.0000,50.0000),(100.0000,50.0000)] cost300=[(10.0000,50.0000),(100.0000,50.0000),(400.0000,50.0000),(490.0000,50.0000)] layer1=[(10.0000,50.0000),(100.0000,50.0000)] layer2=[] start=(100.0000,50.0000) end=(400.0000,50.0000) bidir=false en=true cost=1.0 enter=0.0 layers=2'),
    # Teardown-crash negative control: exit with a live avoidance callback ->
    # double-free at server teardown (SIGABRT). Signature on stdout, the
    # `double free or corruption` glibc fragment pinned on stderr via
    # required_stderr (same shape as geo2d_lattice_lineempty).
    ('nav_lattice_teardown_crash', 'nav_lattice.gd', ['--arm=teardown_crash'], -6,
     'NAV_LATTICE_TEARDOWN_CRASH armed=live_cb has_cb=true'),
    ('nav_lattice_teardown_clean', 'nav_lattice.gd', ['--arm=teardown_clean'], 0,
     'PASS nav_lattice teardown_clean survived=true has_cb=false'),
    # r92: the TileMapLayer/TileSet authorability lattice — cell
    # set/erase/readback, atlas-source and alternative-tile management,
    # custom data layers, terrain connect/path placement, TileMapPattern
    # get/set/map_pattern, the tile_map_data byte encoding (header +
    # 12-byte records, in-place tombstones), fix_invalid_tiles repair,
    # source-id allocation, the physics quadrant and per-tile collision
    # polygons, navigation region registration, the one-physics-step
    # update-timing law with update_internals as the only synchronous
    # lever, and the null-TileSet get_cell_tile_data SIGSEGV hazard.
    # Probe tilemap_lattice.gd sha256 a699138945ec7c1c… — BYTE-COPY of
    # the frozen r92-scout probe (no fixture folds; every boundary fold
    # lands row-side in the signatures below).
    # Boundary folds (r92-boundary 7a45a60) applied:
    #   * r92_tilemap_nav carries a 2-payload envelope on regions_f1 —
    #     the cold cell-write's region registration flushes through the
    #     idle/process pass, not the physics step, so the first-step
    #     read is scheduler-mode-sensitive: regions_f1=1 at
    #     idle:physics <= 2 (the production harness — default scheduler
    #     20/20 + all 65 quiet/load matrix receipts, and the 120-tps
    #     project; boundary §3/§4.1) and regions_f1=0 at ratio >= 2.5
    #     (--fixed-fps >= 150 at 60 tps, ff480 at 120 tps; ff150 0/10,
    #     ff600 0/10). payload[0] is the production/pinned mode. The
    #     settled form regions_f2=1 is single-valued across all 126
    #     boundary nav receipts and stays pinned in BOTH payloads —
    #     the envelope moves the frame-counted read, never the law.
    #   * update_internals()/map_force_update() are NOT synchronous nav
    #     levers (boundary F7: n_upd=0 n_force=0; one await
    #     process_frame flushes the pending region, n_proc1=1) — no
    #     claim about them is pinned on the nav path; the physics-path
    #     update_internals pins live only in r92_tilemap_timing, where
    #     the synchronous apply was measured (update_set_same_frame=hit
    #     / update_erase_same_frame=null).
    #   * r92_tilemap_nullts_crash arms the null-TileSet SIGSEGV hazard
    #     (scout §4.7/§5.1): null tile_set + set_cell +
    #     get_cell_tile_data -> the engine's signal-11 handler prints
    #     the crash dump then abort()s — subprocess returncode -6
    #     (SIGABRT), measured 3/3 fresh reps in this launch shape (the
    #     scout's bash `timeout` wrapper reported the same exit as
    #     134 = 128+6). The signature is the last pre-crash diagnostic
    #     on stdout — the PASS line is never reached — and
    #     required_stderr pins the signal-11 crash-handler header AND
    #     the _nullts backtrace site, so the row is bound to THIS
    #     null-deref, not merely to the -6 signal class (same shape as
    #     geo2d_lattice_lineempty / nav_lattice_teardown_crash). The
    #     halves alone are both safe: only the pair crashes (scout §5.1
    #     isolation).
    #   * Tombstone encoding pinned verbatim (scout §4.4): a 2-byte
    #     header + 12-byte little-endian cell records; erase_cell
    #     rewrites a record to 0xFF tombstones in place and clear()
    #     tombstones every record — the buffer is a high-water mark,
    #     never a live-cell count.
    # Signatures byte-pinned from the scout's 51 canonical runs (all 13
    # cells out_uniq=1 err_uniq=1 under loadavg 118.85 and the 120-tps
    # project) and re-confirmed on 432 boundary scout-arm receipts (the
    # only 2 mismatches are the nav regions_f1 flips the envelope now
    # covers). Nine rows emit deterministic engine ERROR refusals —
    # allowlisted below; census/timing/quadrant/nav are ERROR:-clean
    # (nav's deprecation WARNING carries no ERROR: substring).
    # Rows inserted ahead of the crash/descendant tail —
    # descendant_pipe_detached_control's sleep-8 gap stays adjacent to
    # the meta probes.
    ('r92_tilemap_census', 'tilemap_lattice.gd', ['--arm=census'], 0,
     'PASS tilemap_lattice census layer_defaults=enabled=1 collision_enabled=1 nav_enabled=1 use_kinematic=0 phys_quad=16 rend_quad=16 col_vis=0 nav_vis=0 y_sort_origin=0 x_draw_rev=0 occl=1 layer_props=n16[collision_enabled,collision_visibility_mode,enabled,navigation_enabled,navigation_visibility_mode,occlusion_enabled,physics_quadrant_size,rendering_quadrant_size,tile_map_data,tile_set,use_kinematic_bodies,x_draw_order_reversed,y_sort_origin] layer_no_collision_priority=1 ts_defaults=tile_size=16,16 physics_layers=0 nav_layers=0 custom_data_layers=0 terrain_sets=0 occlusion_layers=0 sources=0 tile_shape=0 tile_layout=0 tile_offset_axis=0 uv_clipping=0 atlas_defaults=region=16,16 margins=0,0 separation=0,0 tiles=0 padding=1 enum_terrainset=MATCH_CORNERS_AND_SIDES=0 MATCH_CORNERS=1 MATCH_SIDES=2 enum_tileshape=SQUARE=0 ISOMETRIC=1 HALF_OFFSET_SQUARE=2 HEXAGON=3 enum_neighbor=RIGHT_SIDE=0 RIGHT_CORNER=1 BOTTOM_RIGHT_SIDE=2 BOTTOM_RIGHT_CORNER=3 BOTTOM_SIDE=4 TOP_RIGHT_CORNER=15 invalid_source=-1 class_method_counts=TileMapLayer=58 TileSet=90 TileSetAtlasSource=41 TileData=54 TileMapPattern=10'),
    ('r92_tilemap_atlas', 'tilemap_lattice.gd', ['--arm=atlas'], 0,
     'PASS tilemap_lattice atlas sid_first=0 count_1=1 has_source_0=1 src_class=TileSetAtlasSource tiles_after_2=2 has_tile_00=1 has_tile_11=0 tiles_list=n2[0,0;1,0] tiles_after_dup=2 alt_id=1 alt_count=2 alt_list=n2[0;1] has_alt_0=1 has_alt_1=1 has_alt_7=0 td_class=TileData td_alt_distinct=1 td_missing=null tiles_after_remove=1 has_tile_10_after=0 sid_explicit_7=7 ids=n2[0;7] next_source_id=1 grid_size=2,2 tile_size_in_atlas=1,1 tex_region=[P: (0, 0), S: (16, 16)]'),
    ('r92_tilemap_cells', 'tilemap_lattice.gd', ['--arm=cells'], 0,
     'PASS tilemap_lattice cells empty_used=n0[] empty_rect=[P: (0, 0), S: (0, 0)] empty_source=-1 empty_atlas=-1,-1 empty_alt=-1 empty_td=null used_after_3=n3[0,0;3,2;-2,-1] rect_after_3=[P: (-2, -1), S: (6, 4)] src_3_2=0 atlas_3_2=1,0 td_3_2=obj same_frame_td=obj same_frame_used_has=1 erase_src=-1 erase_used_n=3 erase_used_n2=2 erase_absent_ok=1 bad_src_readback=42 bad_src_in_used=1 bad_atlas_readback=9,9 bad_atlas_td=null used_by_id_src=n3[-2,-1;9,9;6,6] used_by_id_bad=n1[5,5] clear_used_n=0 clear_rect=[P: (0, 0), S: (0, 0)] map_to_local_1_1=24.0000,24.0000 map_to_local_neg=-8.0000,-8.0000 local_to_map_16_16=1,1 local_to_map_8_8=0,0 local_to_map_neg=-1,-1 surrounding=n4[1,0;0,1;-1,0;0,-1] neighbors_valid8=BOTTOM_LEFT_CORNER:-1,1|BOTTOM_RIGHT_CORNER:1,1|BOTTOM_SIDE:0,1|LEFT_SIDE:-1,0|RIGHT_SIDE:1,0|TOP_LEFT_CORNER:-1,-1|TOP_RIGHT_CORNER:1,-1|TOP_SIDE:0,-1 neighbors_invalid4=BOTTOM_CORNER:0,0|BOTTOM_RIGHT_SIDE:0,0|RIGHT_CORNER:0,0|TOP_RIGHT_SIDE:0,0 empty_flip_h=1 empty_flip_v=1 empty_transpose=1 set_flip_h=0 set_flip_v=0 set_transpose=0'),
    ('r92_tilemap_custom', 'tilemap_lattice.gd', ['--arm=custom'], 0,
     'PASS tilemap_lattice custom layers_0=0 layers_2=2 name_0=hp type_0=2 index_of_hp=0 index_of_missing=-1 has_layer_hp=1 default_hp=0 default_tag= has_hp=1 hp_7=7 tag_alpha=alpha by_index_0=7 by_index_1=alpha hp_wrongtype=not-an-int hp_wrongtype_still=not-an-int layer_hp=not-an-int layer_tag=alpha ghost=<null> missing=<null> layers_after_remove=1 tag_after_remove=<null> hp_after_remove=not-an-int dup_layers=1 dup_hp=0 dup_is_distinct=1'),
    ('r92_tilemap_terrain', 'tilemap_lattice.gd', ['--arm=terrain'], 0,
     'PASS tilemap_lattice terrain sets_0=0 sets_1=1 mode_default=0 mode_set=0 terrains_0=0 terrains_2=2 names=grass,dirt color_0=(0.0, 1.0, 0.0, 1.0) td_terrain_set_default=-1 td_terrain_default=-1 td_terrain_set=0 td_terrain=0 peering_right=1 peering_left=-1 peering_right_valid=1 peering_right_corner_valid=0 connect_used=n2[1,0;0,0] connect_src_0_0=0 connect_atlas_0_0=0,0 connect_atlas_1_0=0,0 connect_atlas_2_0=-1,-1 connect_dirt_used=n3[1,0;0,0;2,0] connect_dirt_atlas_0_0=1,0 path_used=n2[1,0;0,0] bad_set_used=n0[] bad_terrain_used=n0[] no_terrain_used=n0[]'),
    ('r92_tilemap_pattern', 'tilemap_lattice.gd', ['--arm=pattern'], 0,
     'PASS tilemap_lattice pattern class=TileMapPattern size=2,2 used=n3[0,0;1,0;0,1] src_0_0=0 atlas_1_0=1,0 has_cell_0_0=1 empty_at_1_1=-1 is_empty=0 empty_size=0,0 empty_used=n0[] empty_is_empty=1 set_used=n3[4,4;5,4;4,5] set_rect=[P: (4, 4), S: (2, 2)] set_atlas_5_4=1,0 sparse_size=5,5 sparse_used=n2[0,0;4,4] sparse_hole_src=-1 map_pattern_10_10_1_0=11,10 map_pattern_0_0_0_0=0,0 cross_layer_used=n1[-2,-2] cross_layer_atlas=0,0'),
    ('r92_tilemap_encoding', 'tilemap_lattice.gd', ['--arm=encoding'], 0,
     'PASS tilemap_lattice encoding empty_bytes_len=0 empty_arr_len=0 one_bytes_len=14 one_bytes=[0,0,3,0,4,0,0,0,1,0,0,0,0,0] two_bytes_len=26 two_bytes=[0,0,3,0,4,0,0,0,1,0,0,0,0,0,7,0,254,255,0,0,0,0,1,0,0,0] two_arr_len=26 two_arr_equals_bytes=1 stride=12 alt_bytes=[0,0,3,0,4,0,0,0,1,0,0,0,1,0,7,0,254,255,255,255,255,255,255,255,255,255] alt_id_created=1 tomb_set_bytes=[0,0,1,0,1,0,0,0,0,0,0,0,0,0] tomb_erase_len=14 tomb_erase_bytes=[0,0,1,0,1,0,255,255,255,255,255,255,255,255] tomb_erase_used=n0[] tomb_reset_len=14 tomb_reset_bytes=[0,0,1,0,1,0,0,0,0,0,0,0,0,0] tomb_clear_len=14 tomb_clear_bytes=[0,0,1,0,1,0,255,255,255,255,255,255,255,255] tomb_clear_set_len=26 tomb_clear_set_bytes=[0,0,1,0,1,0,255,255,255,255,255,255,255,255,5,0,5,0,0,0,0,0,0,0,0,0] arr_roundtrip_used=n2[3,4;7,-2] arr_roundtrip_src=0 arr_roundtrip_atlas=0,1 short_arr_used=n0[] short_arr_len=0 truncated_used=n1[3,4] truncated_len=14'),
    ('r92_tilemap_fixinvalid', 'tilemap_lattice.gd', ['--arm=fixinvalid'], 0,
     'PASS tilemap_lattice fixinvalid before_used=n3[0,0;1,0;2,0] after_used=n1[0,0] after_src_1_0=-1 after_src_2_0=-1 removed_used=n1[0,0] removed_fixed_used=n0[]'),
    ('r92_tilemap_srcids', 'tilemap_lattice.gd', ['--arm=srcids'], 0,
     'PASS tilemap_lattice srcids auto_id=0 next_after_auto=1 explicit_5=5 next_after_explicit=1 ids=n2[0;5] id_index_0=0 id_index_1=5 moved_ids=n2[0;2] has_2=1 has_5=0 removed_ids=n1[0] count=1 add_null=-1 count_after_null=1 add_colliding=-1 count_after_colliding=1 add_negative=-1 ids_after_refusals=n1[0]'),
    ('r92_tilemap_physics', 'tilemap_lattice.gd', ['--arm=physics'], 0,
     'PASS tilemap_lattice physics phys_layers=1 layer_defaults=cl=1 cm=1 prio=1.0000 mat_null=1 polys_0=0 polys_1=1 poly_pt0=-8.0000,-8.0000 poly_oneway=0 poly_oneway_set=1 m=4.0000 tile0=hit tile1_no_polygon=null tile0_again=hit disabled_same_frame=hit disabled_f1=null enabled_same_frame=null enabled_f1=hit erase_same_frame=hit erase_f1=null collider=class=TileMapLayer travel=0.0000,1.9531 normal=0.0000,-1.0000 is_layer=1 shape=true coords_for_untracked_body=0,0 has_body_rid=0 kinematic_use=1 kinematic_body_tracked=0 kinematic_coords=0,0'),
    ('r92_tilemap_timing', 'tilemap_lattice.gd', ['--arm=timing'], 0,
     'PASS tilemap_lattice timing empty=null set_same_frame_physics=null set_same_frame_td=obj set_same_frame_used=1 set_f1=hit set_f2=hit move_same_frame=hit move_f1=null move_f2=null moved_back=hit erase_same_frame=hit erase_f1=null notify_same_frame=null notify_f1=hit update_erase_same_frame=null update_erase_f1=null update_set_same_frame=hit data_immediate_control=1'),
    ('r92_tilemap_quadrant', 'tilemap_lattice.gd', ['--arm=quadrant'], 0,
     'PASS tilemap_lattice quadrant default_quad=16 quad16_near=hit quad16_far=hit quad_set=2 quad2_same_frame_far=hit quad2_f1_far=hit quad2_near=hit quad2_spread=0,0:hit|15,0:hit|16,0:hit|40,0:hit quad16_spread=0,0:hit|15,0:hit|16,0:hit|40,0:hit quad_restored=16 rendering_quad_untouched=16'),
    ('r92_tilemap_nav', 'tilemap_lattice.gd', ['--arm=nav'], 0,
     ('PASS tilemap_lattice nav nav_layers=1 nav_layer_defaults=layers=1 value1=1 nav_layer_set=3 nav_poly_default=null nav_poly_set=obj layer_nav_enabled=1 layer_nav_vis=0 nav_map_valid=1 regions_empty=0 regions_same_frame=0 regions_f1=1 regions_f2=1 regions_after_plain_cell=1 regions_disabled_same_frame=1 regions_disabled_f1=0 regions_reenabled=1 regions_erased_same_frame=1 regions_erased_f1=0',
      'PASS tilemap_lattice nav nav_layers=1 nav_layer_defaults=layers=1 value1=1 nav_layer_set=3 nav_poly_default=null nav_poly_set=obj layer_nav_enabled=1 layer_nav_vis=0 nav_map_valid=1 regions_empty=0 regions_same_frame=0 regions_f1=0 regions_f2=1 regions_after_plain_cell=1 regions_disabled_same_frame=1 regions_disabled_f1=0 regions_reenabled=1 regions_erased_same_frame=1 regions_erased_f1=0')),
    # Null-TileSet SIGSEGV negative control: null tile_set + a written
    # cell + get_cell_tile_data -> signal 11, and the engine crash
    # handler's abort() exits the process -6 (measured 3/3 fresh reps in
    # this launch shape). The signature is the last pre-crash diagnostic
    # on stdout (the PASS line is never reached); required_stderr binds
    # the crash to the signal-11 handler header and the _nullts site in
    # this probe — a foreign SIGSEGV/SIGABRT or a stderr-only signature
    # still fails.
    ('r92_tilemap_nullts_crash', 'tilemap_lattice.gd', ['--arm=nullts'], -6,
     'R92 nullts about_to_call_tile_data=1'),
    # --- r93 block: AnimationPlayer + Tween authorability lattice ---------
    # Probe anim_lattice.gd sha256 6a919ae04d4e754953b9f8067c49b74c46cf5f3bdc1dce76d4e29597faa2cd4a
    # — BYTE-COPY of the frozen r93-scout probe (689 lines). Probe r93b_anim.gd
    # sha256 3c8dd8f10d6888e120c2420a3dcfc8c0867372ad0907d99d88b1eb98f1efd966
    # — BYTE-COPY of the frozen r93-boundary attack probe. No fixture folds;
    # every boundary fold lands row-side in the signatures below.
    #
    # Boundary-validated laws pinned (r93-scout 54 canonical + 24 loadtest
    # reps; r93-boundary 258 canonical + 16 purity reps across quiet,
    # 16/32-hog and --fixed-fps 30/60/120 launches; all signatures
    # byte-verified against every committed receipt of their arm):
    #   * The manual clock is exact and frame-independent: Tween pause() +
    #     custom_step(delta) and AnimationPlayer MANUAL + advance()/seek()
    #     are byte-stable under loadavg 118 and 32 hogs, and remain exact
    #     with awaited process/physics frames interleaved between steps.
    #   * await N process_frame => N-1 applied steps (boundary §9): pinned
    #     as idle=[x1=0.0 (the first awaited frame still reads the pre-play
    #     value) in 258/258 frame runs; reads past the first await are
    #     modes (their value is rate x sum of observed deltas).
    #   * Runtime tweens OVERSHOOT — no clamp on either side (boundary §7,
    #     falsifying the scout's "runtime clamps" parenthetical):
    #     BACK/EASE_IN_OUT reads 0.1029 BELOW the start value at t=0.25 and
    #     SPRING/EASE_OUT reads 10.5102 ABOVE the end value at t=0.5;
    #     endpoints are guaranteed only at t=0 and t>=duration. The static
    #     interpolate_value also extrapolates (clamp_neg=-5.0,
    #     clamp_over=15.0) and the expo curve is offset by exactly 0.001
    #     (EASE_IN: 2^(10(t-1))-0.001 -> t=1 yields 0.999*delta; EASE_OUT:
    #     1.001*(1-2^(-10t)), endpoint special-cased).
    #   * Crossfade weight law w_i=(i-1)/(N-1) for N uniform manual steps
    #     of dt=blend_time/N — w=0 on the first step, w=1 at t=blend_time;
    #     mid-blend values are STEP-GRANULARITY dependent (finished_010 /
    #     finished_005 / finished_020 pin the same blend at three Ns) and
    #     the lattice is await-immune (interleaved == plain byte-for-byte);
    #     never pin a mid-blend value outside its N.
    #   * DEFERRED method-track callbacks flush on the next process frame
    #     AND on a physics frame (boundary §8, new route); IMMEDIATE calls
    #     land inside advance(); a disabled track calls nothing.
    #   * Completion signals fire synchronously inside custom_step/advance.
    #   * Frame-coupled counters (unpaused auto-advance sums, frames-to-
    #     finish, tweenproc.phys, proc_frames_during_6phys, idle_lag) are
    #     modes — only the stable=[...] clauses / manual sub-lattices are
    #     pinned. --fixed-fps is a STABILIZER for these cells (collapses
    #     each to a single byte-stable value), not a destabilizer.
    # Negative controls carried inside the rows: clamp_neg/clamp_over prove
    #   interpolate_value does NOT clamp; deferred_adv=[] and
    #   disabled_track=[] pin absent callbacks; manual_frames=[0.0,0.0]
    #   pins a MANUAL player never advancing on awaits; idle=[x1=0.0 pins
    #   zero applied steps after one await; unpaused_moved=true proves the
    #   frame path is live (non-vacuity control); kill=[...] and
    #   node_free pin immediate vs lazy invalidation; at_play=[7.0,...]
    #   pins play() not applying a pose.
    # All 23 rows are ERROR:-clean (0 B stderr in every committed receipt)
    # — no expected_errors entries. Rows inserted ahead of the
    # crash/descendant tail — descendant_pipe_detached_control's sleep-8
    # gap stays adjacent to the meta probes.
    ('r93_tween_census', 'anim_lattice.gd', ['--arm=census'], 0,
     'PASS anim_lattice census ap_is_mixer=true ap_is_node=true tw_is_ref=true anim_is_res=true anim_consts=[TYPE_VALUE=0,TYPE_POSITION_3D=1,TYPE_ROTATION_3D=2,TYPE_SCALE_3D=3,TYPE_BLEND_SHAPE=4,TYPE_METHOD=5,TYPE_BEZIER=6,TYPE_AUDIO=7,TYPE_ANIMATION=8,INTERPOLATION_NEAREST=0,INTERPOLATION_LINEAR=1,INTERPOLATION_CUBIC=2,INTERPOLATION_LINEAR_ANGLE=3,INTERPOLATION_CUBIC_ANGLE=4,UPDATE_CONTINUOUS=0,UPDATE_DISCRETE=1,UPDATE_CAPTURE=2,LOOP_NONE=0,LOOP_LINEAR=1,LOOP_PINGPONG=2,LOOPED_FLAG_NONE=0,LOOPED_FLAG_END=1,LOOPED_FLAG_START=2,FIND_MODE_NEAREST=0,FIND_MODE_APPROX=1,FIND_MODE_EXACT=2] mixer_consts=[ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS=0,ANIMATION_CALLBACK_MODE_PROCESS_IDLE=1,ANIMATION_CALLBACK_MODE_PROCESS_MANUAL=2,ANIMATION_CALLBACK_MODE_METHOD_DEFERRED=0,ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE=1,ANIMATION_CALLBACK_MODE_DISCRETE_DOMINANT=0,ANIMATION_CALLBACK_MODE_DISCRETE_RECESSIVE=1,ANIMATION_CALLBACK_MODE_DISCRETE_FORCE_CONTINUOUS=2] player_consts=[ANIMATION_PROCESS_PHYSICS=0,ANIMATION_PROCESS_IDLE=1,ANIMATION_PROCESS_MANUAL=2,ANIMATION_METHOD_CALL_DEFERRED=0,ANIMATION_METHOD_CALL_IMMEDIATE=1] tween_consts=[TWEEN_PROCESS_PHYSICS=0,TWEEN_PROCESS_IDLE=1,TWEEN_PAUSE_BOUND=0,TWEEN_PAUSE_STOP=1,TWEEN_PAUSE_PROCESS=2,TRANS_LINEAR=0,TRANS_SINE=1,TRANS_QUINT=2,TRANS_QUART=3,TRANS_QUAD=4,TRANS_EXPO=5,TRANS_ELASTIC=6,TRANS_CUBIC=7,TRANS_CIRC=8,TRANS_BOUNCE=9,TRANS_BACK=10,TRANS_SPRING=11,EASE_IN=0,EASE_OUT=1,EASE_IN_OUT=2,EASE_OUT_IN=3] ap_defaults=[proc=1,cbm=0,cbp=1,cbd=1,root=..,active=true,speed=1.0,default_blend=0.0,auto_capture=true] anim_defaults=[len=1.0,loop=0,step=0.0333333350718,tracks=0] ap_signals=[script_changed,property_list_changed,ready,renamed,tree_entered,tree_exiting,tree_exited,child_entered_tree,child_exiting_tree,child_order_changed,replacing_by,editor_description_changed,editor_state_changed,animation_list_changed,animation_libraries_updated,animation_finished,animation_started,caches_cleared,mixer_applied,mixer_updated,current_animation_changed,animation_changed] tw_signals=[script_changed,property_list_changed,step_finished,loop_finished,finished] an_m_count=177 tw_m_count=94 ap_m_count=293 cache_methods=[clear_caches] capture_methods=[set_auto_capture,is_auto_capture,set_auto_capture_duration,get_auto_capture_duration,set_auto_capture_transition_type,get_auto_capture_transition_type,set_auto_capture_ease_type,get_auto_capture_ease_type,play_with_capture,capture] blend_methods=[set_blend_time,get_blend_time,set_default_blend_time,get_default_blend_time] an_sample_methods=[position_track_interpolate,rotation_track_interpolate,scale_track_interpolate,blend_shape_track_interpolate,value_track_interpolate,bezier_track_interpolate] tw_step_methods=[custom_step]'),
    ('r93_tween_interp_value', 'anim_lattice.gd', ['--arm=tweenval'], 0,
     'PASS anim_lattice tweenval r91_exact=9.69718754291534 expo_in_05=0.30249999836087 expo_in_10=9.99000012874603 expo_out_05=9.69718754291534 expo_out_10=10.0 clamp_neg=-5.0 clamp_over=15.0 int_025=3 int_050=5 int_075=8 vec_025=(2.0, 4.0) color_050=(0.5, 0.25, 0.0, 1.0) form_in_err=0.00000000016391 form_out_err=0.00000000429153'),
    ('r93_tween_interp_grid_a', 'anim_lattice.gd', ['--arm=tweenval_grid'], 0,
     'lin in=0.0,2.5,5.0,7.5,10.0 out=0.0,2.5,5.0,7.5,10.0 io=0.0,2.5,5.0,7.5,10.0 oi=0.0,2.5,5.0,7.5,10.0 sin in=0.0,0.76120465993881,2.9289323091507,6.17316544055939,10.0 out=0.0,3.82683426141739,7.0710676908493,9.23879504203796,10.0 io=0.0,1.46446615457535,5.0,8.53553414344788,10.0 oi=0.0,3.53553384542465,5.0,6.46446585655212,10.0 qui in=0.0,0.009765625,0.3125,2.373046875,10.0 out=0.0,7.626953125,9.6875,9.990234375,10.0 io=0.0,0.15625,5.0,9.84375,10.0 oi=0.0,4.84375,5.0,5.15625,10.0 qua in=0.0,0.0390625,0.625,3.1640625,10.0 out=0.0,6.8359375,9.375,9.9609375,10.0 io=0.0,0.3125,5.0,9.6875,10.0 oi=0.0,4.6875,5.0,5.3125,10.0 qad in=0.0,0.625,2.5,5.625,10.0 out=0.0,4.375,7.5,9.375,10.0 io=0.0,1.25,5.0,8.75,10.0 oi=0.0,3.75,5.0,6.25,10.0'),
    ('r93_tween_interp_grid_b', 'anim_lattice.gd', ['--arm=tweenval_grid'], 0,
     'expo in=0.0,0.04524271469563,0.30249999836087,1.75776690244675,9.99000012874603 out=0.0,8.24046492576599,9.69718754291534,9.95470225811005,10.0 io=0.0,0.15124999918044,5.00249981880188,9.84867215156555,10.0 oi=0.0,4.84859377145767,5.0,5.15124976634979,9.99499976634979 ela in=0.0,-0.05524271633476,-0.15625020489097,0.8838826417923,10.0 out=0.0,9.11611676216125,10.15625,10.0552427768707,10.0 io=0.0,0.11969446204603,5.0,9.88030552864075,10.0 oi=0.0,5.078125,5.0,4.921875,10.0 cub in=0.0,0.15625,1.25,4.21875,10.0 out=0.0,5.78125,8.75,9.84375,10.0 io=0.0,0.625,5.0,9.375,10.0 oi=0.0,4.375,5.0,5.625,10.0 cir in=0.0,0.3175413608551,1.33974611759186,3.38562190532684,10.0 out=0.0,6.61437809467316,8.66025388240814,9.6824586391449,10.0 io=0.0,0.66987305879593,5.0,9.33012723922729,10.0 oi=0.0,4.33012694120407,5.0,5.66987276077271,10.0 bou in=0.0,0.2734375,2.34375,5.2734375,10.0 out=0.0,4.7265625,7.65625,9.7265625,10.0 io=0.0,1.171875,5.0,8.828125,10.0 oi=0.0,3.828125,5.0,6.171875,10.0 bac in=0.0,-0.64136564731598,-0.87697505950928,1.82590305805206,10.0 out=0.0,8.17409694194794,10.8769750595093,10.6413650512695,10.0 io=0.0,-0.99681839346886,5.0,10.9968185424805,10.0 oi=0.0,5.43848752975464,5.0,4.56151247024536,10.0 spr in=0.0,0.13654887676239,-0.51015734672546,3.3666330575943,10.0 out=0.0,6.6333669424057,10.5101573467255,9.86345112323761,10.0 io=0.0,-0.25507867336273,5.0,10.2550792694092,10.0 oi=0.0,5.25507867336273,5.0,4.74492132663727,10.0'),
    ('r93_anim_track_interp', 'anim_lattice.gd', ['--arm=animtrack'], 0,
     'PASS anim_lattice animtrack two_key=[it0=[t05=0.0,t09=0.0,t10=10.0],it1=[t05=5.0,t09=8.99999976158142,t10=10.0],it2=[t05=5.0,t09=9.71999987125395,t10=10.0]] three_key=[it0=[t025=0.0,t075=10.0],it1=[t025=5.0,t075=5.0],it2=[t025=5.0,t075=5.0]] two_default_interp=1 three_key_count=3 k0=0.0 kt1=0.5 k1=10.0 bezier=[1.05892944335938,5.0,8.94107055664062] bezier_key_count=2 track_enabled=true track_type=0 track_path=.:position:x'),
    ('r93_tween_manual_step', 'anim_lattice.gd', ['--arm=tweenstep'], 0,
     'PASS anim_lattice tweenstep created=[true,true,0.0,0.0] step05=[5.0,true,0.5,0,0] step10=[10.0,false,1.0,1,1] step_again=[10.0,false,1.0,1,1] paused=[5.0,false,true,0.25,0] paused_done=[20.0,false,1.0,1] loop1=[2.0,1,0,1] loop2=[2.0,0,1,1]'),
    ('r93_tween_chain', 'anim_lattice.gd', ['--arm=tweenchain'], 0,
     'PASS anim_lattice tweenchain seq=[20.0,30.0,40.0] par=[30.0,2.0] interval=[cb_at_050=0,mvals_at_050=[],cb_at_100=1,mvals_at_100=[5.0],cb_after_extra=1] node_free=[before=[true,true],right_after=[true,true],stepped_after_free=[true,true],after_frame=[false,true]] kill=[before=[true,false],after=[false,false]]'),
    ('r93_tween_process_stable', 'anim_lattice.gd', ['--arm=tweenproc'], 0,
     'stable=[auto_advanced=true,paused_frozen=true,phys_advanced=true,manual_exact=true]'),
    ('r93_tween_phys_manual_step', 'anim_lattice.gd', ['--arm=tweenproc'], 0,
     'phys_manual=[before=1.0,after_step025=2.0]'),
    ('r93_anim_seek', 'anim_lattice.gd', ['--arm=animseek'], 0,
     'PASS anim_lattice animseek at_play=[7.0,true,0.0,move] adv025=[25.0,0.25] seek_up=[75.0,0.75] seek_noup=[75.0,0.5] cross=[100.0,1.0,false,1] after_frame=[100.0,1] before_stop=50.0 after_stop=[0.0,false,,move] speed2=[50.0,0.5] speed0=[50.0,0.5] replay_before=[50.0,0.5] replay_same=[50.0,0.5] play_other=[50.0,0.0,loop] back_other=[50.0,0.0] paused_adv=[50.0,false] looped=[25.0,0.25,0] seek_over=[100.0,1.0,true] manual_frames=[0.0,0.0]'),
    ('r93_anim_method_callback', 'anim_lattice.gd', ['--arm=animmethod'], 0,
     'PASS anim_lattice animmethod sig_at_play=[1,0,1] deferred_adv=[] deferred_frame=[7,8] sig_after_frame=[1,0,2] immediate_adv=[7,8] immediate_frame=[7,8] disabled_track=[] started_names=[m,m,m] changed=[] cur_changed=[m,,,,,]'),
    ('r93_anim_blend_finished', 'anim_lattice.gd', ['--arm=animblend'], 0,
     'finished_010=[100.0,144.444442749023,188.888900756836,233.333343505859,277.777801513672,322.222229003906,366.666687011719,411.111114501953,455.555572509766,500.0] finished_005=[100.0,121.052627563477,142.105255126953,163.15788269043,184.210525512695,205.263168334961,226.315795898438,247.368408203125,268.421051025391,289.473663330078,310.526336669922,331.578948974609,352.631561279297,373.684204101562,394.736846923828,415.789489746094,436.842071533203,457.894714355469,478.947357177734,500.0] finished_020=[100.0,200.0,300.0,400.0,500.0]'),
    ('r93_anim_blend_running', 'anim_lattice.gd', ['--arm=animblend'], 0,
     'running_from_50=[60.0000038146973,117.777778625488,173.333343505859,226.66667175293,277.777801513672,322.222229003906,366.666687011719,411.111114501953,455.555572509766,500.0] hard=[at_play=100.0,after_025=500.0] default_blend_mid=100.0 capture=[before=50.0,seq=60.0000038146973,117.777778625488,173.333343505859,226.66667175293,277.777801513672,322.222229003906,366.666687011719,411.111114501953,455.555572509766,500.0]'),
    ('r93_anim_process_manual', 'anim_lattice.gd', ['--arm=animproc'], 0,
     'manual=[x=25.0,after3frames=25.0] frozen=[0.0,true,0.0] inactive=[50.0,true]'),
    ('r93_anim_process_stable', 'anim_lattice.gd', ['--arm=animproc'], 0,
     'stable=[manual_frame_frozen=true,manual_exact=true,speed0_frozen=true,inactive_advance=true,fin_fired=true,caches_once=true,mixer_updated_zero=true]'),
    ('r93_anim_overshoot', 'r93b_anim.gd', ['--arm=purity'], 0,
     'PASS r93b_anim purity expo=[out05=9.69718754291534,in05=0.30249999836087,in10=9.99000012874603,out10=10.0] clamp=[neg=-5.0,over=15.0] int050=5 vec025=(2.0, 4.0) col050=(0.5, 0.25, 0.0, 1.0) track=[it0=[t05=0.0,t09=0.0,t10=10.0],it1=[t05=5.0,t09=8.99999976158142,t10=10.0],it2=[t05=5.0,t09=9.71999987125395,t10=10.0]] deltas=[tiny=0.00000001,mid=2.5,huge=10.0,huge_running=false,neg=0.0,neg_elapsed=-0.5] overshoot=[back025=0.10286344587803,back050=5.5] overshoot2=[spr050=10.510157585144,spr100=10.0,ela025=9.11611652374268] accum1000=1.0'),
    ('r93_anim_manual_clock_interleaved', 'r93b_anim.gd', ['--arm=manual_inv'], 0,
     'PASS r93b_anim manual_inv paused=[a=2.5,b=2.5,c=5.0,d=5.0,e=10.0] manual=[f=25.0,g=25.0,h=50.0,k=50.0,m=100.0]'),
    ('r93_anim_manual_clock_control', 'r93b_anim.gd', ['--arm=manual_inv'], 0,
     'inv=[paused_proc=true,paused_phys=true,manual_proc=true,manual_phys=true] step_exact=[paused025=true,paused_done=true,manual025=true,manual_done=true] unpaused_moved=true'),
    ('r93_anim_deferred_flush', 'r93b_anim.gd', ['--arm=deferred'], 0,
     'PASS r93b_anim deferred manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]] manual_def_phys=[after_adv=[],after_phys=[7,8]] two_adv=[after=[],flush=[7,8]] immediate=[after_adv=[7,8],after_frame=[7,8]]'),
    ('r93_anim_await_offbyone', 'r93b_anim.gd', ['--arm=frame'], 0,
     'PASS r93b_anim frame idle=[x1=0.0'),
    ('r93_anim_physics_tick', 'r93b_anim.gd', ['--arm=frame'], 0,
     'mixer_applied_10=10 phys=[y1=0.0,y2=0.0,y3=1.66666674613953,y6=6.66666698455811]'),
    ('r93_anim_phys_delta', 'r93b_anim.gd', ['--arm=frame'], 0,
     'phys_delta=0.01666666666667'),
    ('r93_anim_blend_interleaved', 'r93b_anim.gd', ['--arm=blend'], 0,
     'PASS r93b_anim blend finished_010=[100.0,144.444442749023,188.888900756836,233.333343505859,277.777801513672,322.222229003906,366.666687011719,411.111114501953,455.555572509766,500.0] finished_020=[100.0,200.0,300.0,400.0,500.0] interleaved=[100.0,144.444442749023,188.888900756836,233.333343505859,277.777801513672,322.222229003906,366.666687011719,411.111114501953,455.555572509766,500.0] interleaved_eq_plain=true hard_after_frame=500.0'),
    # --- r94 block: CPUParticles2D + GPUParticles2D emission lattice -----
    # Probe particles_lattice.gd sha256 0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9
    # — folded variant of the frozen r94-scout probe
    # (corpus/live/r94-scout/probes/particles_lattice.gd sha256
    # e6a2e0f55c6bbeaa…, 741 lines). Fixture folds (r94-boundary e741cf8
    # §10 applied — the row-side signature text is unchanged by them):
    #   * cpu_pause widens the three fin_after_* resume windows from
    #     [4,7] to [1,7] — the ONLY behavioral fold. Boundary §4.2/§10:
    #     the frozen windows reject 3/3 under --fixed-fps 30 (vis_parent
    #     and pm_disabled land on 2 — the same freeze+resume law through
    #     a different frame-quantization ratio; [1,7] covers every
    #     condition measured: 4-5 quiet/load, 2 at ff30).
    #   * Comment-only corrections carry the other boundary falsifications
    #     (no emitted byte changes): contamination is the add_pf>=1
    #     first-idle-frame rule, NOT process-global state (§8 — cpu_never
    #     is created inside _initialize i.e. add_pf=0, cpu_contam's nevers
    #     are later-added i.e. add_pf>=1; both arms still pin the same
    #     booleans); the request lattice closed form is floor(L/step)+1
    #     not round (§6 — the emitted expected= values are unchanged:
    #     floor(0.5/0.10)=5->6, floor(0.5/0.05)=10->11); fixed_fps shifts
    #     the end time by up to one quantum and fixed_fps<=5 is a stall
    #     hazard, never authored (§5); the amount setter ARMS the spurious
    #     finished which fires on the node's next _process same-frame —
    #     fin_after_set=0 is a frame-order fact, not setter-synchronous
    #     (§7); gpu flip_after is [1,7] not 3-7 and stays unpinned (§9).
    #   * Deliberately NOT authored: the continuous-emitter amount
    #     coupling (boundary §7.3 — unstable [U], set-tick and node-order
    #     dependent); any tick-count tail after " | " (±1 modes, wider
    #     under ff30); seed (random per instantiation); particle
    #     positions/colors (no headless readback); GPU signals (headless
    #     inert by law); fixed_fps<=5 (stall).
    # Signatures are the gating boolean-block prefixes before " | " —
    # byte-stable over 143 scout receipts and all 6 boundary conditions
    # (quiet/load/ff30/ff60/ff120/ff120load: the ONLY rejection was the
    # cpu_pause window now folded). The ladder/stream/pause ok=_ok
    # booleans internally window fin_delta at the pinned 60-tps launch
    # project (no physics_ticks_per_second override) — the law, not the
    # ±1 measured tail, is pinned. 19 rows, all ERROR:-clean (0 B stderr
    # on every receipt incl. this seat's smoke pass) — EXPECTED_ERRORS={}.
    # Rows inserted ahead of the crash/descendant tail —
    # descendant_pipe_detached_control's sleep-8 gap stays adjacent to
    # the meta probes.
    ('r94_particles_census', 'particles_lattice.gd', ['--arm=census'], 0,
     'PASS particles_lattice census cpu_consts=DRAW_ORDER_INDEX=0,DRAW_ORDER_LIFETIME=1,PARAM_INITIAL_LINEAR_VELOCITY=0,PARAM_ANGULAR_VELOCITY=1,PARAM_ORBIT_VELOCITY=2,PARAM_LINEAR_ACCEL=3,PARAM_RADIAL_ACCEL=4,PARAM_TANGENTIAL_ACCEL=5,PARAM_DAMPING=6,PARAM_ANGLE=7,PARAM_SCALE=8,PARAM_HUE_VARIATION=9,PARAM_ANIM_SPEED=10,PARAM_ANIM_OFFSET=11,PARAM_MAX=12,PARTICLE_FLAG_ALIGN_Y_TO_VELOCITY=0,PARTICLE_FLAG_ROTATE_Y=1,PARTICLE_FLAG_DISABLE_Z=2,PARTICLE_FLAG_MAX=3,EMISSION_SHAPE_POINT=0,EMISSION_SHAPE_SPHERE=1,EMISSION_SHAPE_SPHERE_SURFACE=2,EMISSION_SHAPE_RECTANGLE=3,EMISSION_SHAPE_POINTS=4,EMISSION_SHAPE_DIRECTED_POINTS=5,EMISSION_SHAPE_RING=6,EMISSION_SHAPE_MAX=7 gpu_consts=DRAW_ORDER_INDEX=0,DRAW_ORDER_LIFETIME=1,DRAW_ORDER_REVERSE_LIFETIME=2,EMIT_FLAG_POSITION=1,EMIT_FLAG_ROTATION_SCALE=2,EMIT_FLAG_VELOCITY=4,EMIT_FLAG_COLOR=8,EMIT_FLAG_CUSTOM=16 ppm_consts=PARAM_INITIAL_LINEAR_VELOCITY=0,PARAM_ANGULAR_VELOCITY=1,PARAM_ORBIT_VELOCITY=2,PARAM_LINEAR_ACCEL=3,PARAM_RADIAL_ACCEL=4,PARAM_TANGENTIAL_ACCEL=5,PARAM_DAMPING=6,PARAM_ANGLE=7,PARAM_SCALE=8,PARAM_HUE_VARIATION=9,PARAM_ANIM_SPEED=10,PARAM_ANIM_OFFSET=11,PARAM_RADIAL_VELOCITY=15,PARAM_DIRECTIONAL_VELOCITY=16,PARAM_SCALE_OVER_VELOCITY=17,PARAM_MAX=18,PARTICLE_FLAG_ALIGN_Y_TO_VELOCITY=0,PARTICLE_FLAG_ROTATE_Y=1,PARTICLE_FLAG_DISABLE_Z=2,PARTICLE_FLAG_DAMPING_AS_FRICTION=3,PARTICLE_FLAG_INHERIT_EMITTER_SCALE=4,PARTICLE_FLAG_MAX=5,EMISSION_SHAPE_POINT=0,EMISSION_SHAPE_SPHERE=1,EMISSION_SHAPE_SPHERE_SURFACE=2,EMISSION_SHAPE_BOX=3,EMISSION_SHAPE_POINTS=4,EMISSION_SHAPE_DIRECTED_POINTS=5,EMISSION_SHAPE_RING=6,EMISSION_SHAPE_MAX=7,PARAM_TURB_VEL_INFLUENCE=13,PARAM_TURB_INIT_DISPLACEMENT=14,PARAM_TURB_INFLUENCE_OVER_LIFE=12,SUB_EMITTER_DISABLED=0,SUB_EMITTER_CONSTANT=1,SUB_EMITTER_AT_END=2,SUB_EMITTER_AT_COLLISION=3,SUB_EMITTER_AT_START=4,SUB_EMITTER_MAX=5,COLLISION_DISABLED=0,COLLISION_RIGID=1,COLLISION_HIDE_ON_CONTACT=2,COLLISION_MAX=3 cpu_props=unique_name_in_owner=false,process_mode=0,process_priority=0,process_physics_priority=0,process_thread_group=0,physics_interpolation_mode=2,auto_translate_mode=0,editor_description=,visible=true,modulate=1.000/1.000/1.000/1.000,self_modulate=1.000/1.000/1.000/1.000,show_behind_parent=false,top_level=false,clip_children=0,oversampling_with_scale=0,light_mask=1,visibility_layer=1,z_index=0,z_as_relative=true,y_sort_enabled=false,texture_filter=0,texture_repeat=0,material=<null>,use_parent_material=false,position=(0.0000,0.0000),rotation=0.0000,scale=(1.0000,1.0000),skew=0.0000,emitting=true,amount=8,texture=<null>,lifetime=1.0000,one_shot=false,preprocess=0.0000,speed_scale=1.0000,explosiveness=0.0000,randomness=0.0000,use_fixed_seed=false,lifetime_randomness=0.0000,fixed_fps=0,fract_delta=true,local_coords=false,draw_order=0,emission_shape=0,particle_flag_align_y=false,direction=(1.0000,0.0000),spread=45.0000,gravity=(0.0000,980.0000),initial_velocity_min=0.0000,initial_velocity_max=0.0000,angular_velocity_min=0.0000,angular_velocity_max=0.0000,angular_velocity_curve=<null>,orbit_velocity_min=0.0000,orbit_velocity_max=0.0000,orbit_velocity_curve=<null>,linear_accel_min=0.0000,linear_accel_max=0.0000,linear_accel_curve=<null>,radial_accel_min=0.0000,radial_accel_max=0.0000,radial_accel_curve=<null>,tangential_accel_min=0.0000,tangential_accel_max=0.0000,tangential_accel_curve=<null>,damping_min=0.0000,damping_max=0.0000,damping_curve=<null>,angle_min=0.0000,angle_max=0.0000,angle_curve=<null>,scale_amount_min=1.0000,scale_amount_max=1.0000,scale_amount_curve=<null>,split_scale=false,color=1.000/1.000/1.000/1.000,color_ramp=<null>,color_initial_ramp=<null>,hue_variation_min=0.0000,hue_variation_max=0.0000,hue_variation_curve=<null>,anim_speed_min=0.0000,anim_speed_max=0.0000,anim_speed_curve=<null>,anim_offset_min=0.0000,anim_offset_max=0.0000,anim_offset_curve=<null> gpu_props=unique_name_in_owner=false,process_mode=0,process_priority=0,process_physics_priority=0,process_thread_group=0,physics_interpolation_mode=0,auto_translate_mode=0,editor_description=,visible=true,modulate=1.000/1.000/1.000/1.000,self_modulate=1.000/1.000/1.000/1.000,show_behind_parent=false,top_level=false,clip_children=0,oversampling_with_scale=0,light_mask=1,visibility_layer=1,z_index=0,z_as_relative=true,y_sort_enabled=false,texture_filter=0,texture_repeat=0,material=<null>,use_parent_material=false,position=(0.0000,0.0000),rotation=0.0000,scale=(1.0000,1.0000),skew=0.0000,emitting=true,amount=8,amount_ratio=1.0000,sub_emitter=,texture=<null>,lifetime=1.0000,interp_to_end=0.0000,one_shot=false,preprocess=0.0000,speed_scale=1.0000,explosiveness=0.0000,randomness=0.0000,use_fixed_seed=false,fixed_fps=30,interpolate=true,fract_delta=true,collision_base_size=1.0000,visibility_rect=[P: (-100.0, -100.0), S: (200.0, 200.0)],local_coords=false,draw_order=1,trail_enabled=false,trail_lifetime=0.3000,trail_sections=8,trail_section_subdivisions=4,process_material=<null> ppm_props=lifetime_randomness=0.0000,particle_flag_align_y=false,particle_flag_rotate_y=false,particle_flag_disable_z=false,particle_flag_damping_as_friction=false,particle_flag_inherit_emitter_scale=false,emission_shape_offset=(0.0, 0.0, 0.0),emission_shape_scale=(1.0, 1.0, 1.0),emission_shape=0,angle=(0.0000,0.0000),angle_min=0.0000,angle_max=0.0000,angle_curve=<null>,use_rotation_3d=false,rotation_3d_min=(0.0, 0.0, 0.0),rotation_3d_max=(0.0, 0.0, 0.0),inherit_velocity_ratio=0.0000,velocity_pivot=(0.0, 0.0, 0.0),direction=(1.0, 0.0, 0.0),spread=45.0000,flatness=0.0000,initial_velocity=(0.0000,0.0000),initial_velocity_min=0.0000,initial_velocity_max=0.0000,angular_velocity=(0.0000,0.0000),angular_velocity_min=0.0000,angular_velocity_max=0.0000,angular_velocity_curve=<null>,directional_velocity=(1.0000,1.0000),directional_velocity_curve=<null>,orbit_velocity=(0.0000,0.0000),orbit_velocity_min=0.0000,orbit_velocity_max=0.0000,orbit_velocity_curve=<null>,radial_velocity=(0.0000,0.0000),radial_velocity_min=0.0000,radial_velocity_max=0.0000,radial_velocity_curve=<null>,velocity_limit_curve=<null>,use_rotation_velocity_3d=false,gravity=(0.0, -9.8, 0.0),linear_accel=(0.0000,0.0000),linear_accel_min=0.0000,linear_accel_max=0.0000,linear_accel_curve=<null>,radial_accel=(0.0000,0.0000),radial_accel_min=0.0000,radial_accel_max=0.0000,radial_accel_curve=<null>,tangential_accel=(0.0000,0.0000),tangential_accel_min=0.0000,tangential_accel_max=0.0000,tangential_accel_curve=<null>,damping=(0.0000,0.0000),damping_min=0.0000,damping_max=0.0000,damping_curve=<null>,attractor_interaction_enabled=true,use_scale_3d=false,scale_3d_min=(1.0, 1.0, 1.0),scale_3d_max=(1.0, 1.0, 1.0),scale=(1.0000,1.0000),scale_min=1.0000,scale_max=1.0000,scale_curve=<null>,scale_over_velocity=(0.0000,0.0000),scale_over_velocity_min=0.0000,scale_over_velocity_max=0.0000,scale_over_velocity_curve=<null>,color=1.000/1.000/1.000/1.000,color_ramp=<null>,color_initial_ramp=<null>,alpha_curve=<null>,emission_curve=<null>,hue_variation=(0.0000,0.0000),hue_variation_min=0.0000,hue_variation_max=0.0000,hue_variation_curve=<null>,anim_speed=(0.0000,0.0000),anim_speed_min=0.0000,anim_speed_max=0.0000,anim_speed_curve=<null>,anim_offset=(0.0000,0.0000),anim_offset_min=0.0000,anim_offset_max=0.0000,anim_offset_curve=<null>,turbulence_enabled=false,turbulence_noise_strength=1.0000,turbulence_noise_scale=9.0000,turbulence_noise_speed=(0.0, 0.0, 0.0),turbulence_noise_speed_random=0.2000,turbulence_influence=(0.1000,0.1000),turbulence_influence_min=0.1000,turbulence_influence_max=0.1000,turbulence_initial_displacement=(0.0000,0.0000),turbulence_initial_displacement_min=0.0000,turbulence_initial_displacement_max=0.0000,turbulence_influence_over_life=<null>,collision_mode=0,collision_use_scale=false,sub_emitter_mode=0,sub_emitter_keep_velocity=false ppm_curve_types=alpha:24,angle:24,angular_velocity:24,anim_offset:24,anim_speed:24,damping:24,directional_velocity:24,emission:24,hue_variation:24,linear_accel:24,orbit_velocity:24,radial_accel:24,radial_velocity:24,rotation_velocity_3d:24,scale:24,scale_over_velocity:24,tangential_accel:24,velocity_limit:24 cpu_sig=convert_from_particles(particles:24)->0|is_emitting()->1|request_particles_process(process_time:3,process_time_residual:3)->0|restart(keep_seed:1)->0 gpu_sig=capture_rect()->7|convert_from_particles(particles:24)->0|emit_particle(xform:11,velocity:5,color:20,custom:20,flags:2)->0|is_emitting()->1|request_particles_process(process_time:3,process_time_residual:3)->0|restart(keep_seed:1)->0 ppm_sig=get_param(param:2)->5|get_param_max(param:2)->3|get_param_min(param:2)->3|get_param_texture(param:2)->24|get_particle_flag(particle_flag:2)->1|set_param(param:2,value:5)->0|set_param_max(param:2,value:3)->0|set_param_min(param:2,value:3)->0|set_param_texture(param:2,texture:24)->0|set_particle_flag(particle_flag:2,enable:1)->0'),
    ('r94_particles_ppm', 'particles_lattice.gd', ['--arm=ppm'], 0,
     'PASS particles_lattice ppm iv_min=7.0000 iv_max=9.0000 scale=(2.0000,3.0000) tex_same=true curve_same=true flags=truetrue sub_mode=3 sub_amt=3 coll=2 turb=true turb_n=1'),
    ('r94_particles_convert', 'particles_lattice.gd', ['--arm=convert'], 0,
     'PASS particles_lattice convert g2c[amount=12 lifetime=0.7000 os=true expl=0.2500 rand=0.5000 ss=2.0000 ffps=0 pre=0.1250 local=true draw=2] g2c_dir=(0.5000,0.5000) spread=30.0000 grav=(0.0000,98.0000) iv=10.0000..20.0000 scale=2.0000..3.0000 g2c_col=0.250/0.500/0.750/0.500 shape=1 sph=5.0000 c2g[amount=5 lifetime=0.4000 os=false expl=0.5000 pm_null=false dir=(0.0000,-1.0000,0.0000) spread=10.0000 grav=(0.0000,30.0000,0.0000) iv=3.0000..4.0000 col=0.100/0.200/0.300/0.400]'),
    ('r94_particles_cpu_lifetime', 'particles_lattice.gd', ['--arm=cpu_lifetime'], 0,
     'PASS particles_lattice cpu_lifetime ok=true l01_ok=true l025_ok=true l05_ok=true l1_ok=true'),
    ('r94_particles_cpu_expl', 'particles_lattice.gd', ['--arm=cpu_expl'], 0,
     'PASS particles_lattice cpu_expl ok=true e1_ok=true e05_ok=true e0_ok=true'),
    ('r94_particles_cpu_speed_pre', 'particles_lattice.gd', ['--arm=cpu_speed_pre'], 0,
     'PASS particles_lattice cpu_speed_pre ok=true ss2_ok=true ss05_ok=true pre25_ok=true ff30_ok=true'),
    ('r94_particles_cpu_stop', 'particles_lattice.gd', ['--arm=cpu_stop'], 0,
     'PASS particles_lattice cpu_stop ok=true stop10_ok=true stop40_ok=true'),
    ('r94_particles_cpu_never', 'particles_lattice.gd', ['--arm=cpu_never'], 0,
     'PASS particles_lattice cpu_never ok=true never_fired=true n_fin=0'),
    ('r94_particles_cpu_contam', 'particles_lattice.gd', ['--arm=cpu_contam'], 0,
     'PASS particles_lattice cpu_contam ok=true n_never=2'),
    ('r94_particles_cpu_oneshot_off', 'particles_lattice.gd', ['--arm=cpu_oneshot_off'], 0,
     'PASS particles_lattice cpu_oneshot_off ok=true fin_ok=true em_after=false os_after=true'),
    ('r94_particles_cpu_oneshot_flag', 'particles_lattice.gd', ['--arm=cpu_oneshot_flag'], 0,
     'PASS particles_lattice cpu_oneshot_flag ok=true never_fired=true em_after=true os_after=false'),
    ('r94_particles_cpu_pause', 'particles_lattice.gd', ['--arm=cpu_pause'], 0,
     'PASS particles_lattice cpu_pause ok=true vis_ok=true vis_parent_ok=true pm_disabled_ok=true ts0_ok=true'),
    ('r94_particles_cpu_restart', 'particles_lattice.gd', ['--arm=cpu_restart'], 0,
     'PASS particles_lattice cpu_restart ok=true first_ok=true second_ok=true first_em=false first_ise=false em_after_restart=true ise_after_restart=true em_after=false'),
    ('r94_particles_cpu_retrigger', 'particles_lattice.gd', ['--arm=cpu_retrigger'], 0,
     'PASS particles_lattice cpu_retrigger ok=true first_ok=true second_ok=true em_set=true ise_set=true'),
    ('r94_particles_cpu_lt_mid', 'particles_lattice.gd', ['--arm=cpu_lt_mid'], 0,
     'PASS particles_lattice cpu_lt_mid ok=true fin_ok=true em_after=false'),
    ('r94_particles_cpu_speed_mid', 'particles_lattice.gd', ['--arm=cpu_speed_mid'], 0,
     'PASS particles_lattice cpu_speed_mid ok=true fin_ok=true em_after=false'),
    ('r94_particles_cpu_amount_mid', 'particles_lattice.gd', ['--arm=cpu_amount_mid'], 0,
     'PASS particles_lattice cpu_amount_mid ok=true em_at_set=true spurious_finish=true'),
    ('r94_particles_cpu_request', 'particles_lattice.gd', ['--arm=cpu_request'], 0,
     'PASS particles_lattice cpu_request ok=true step010_ok=true step005_ok=true'),
    ('r94_particles_gpu_headless', 'particles_lattice.gd', ['--arm=gpu_headless'], 0,
     'PASS particles_lattice gpu_headless ok=true os_ok=true cont_ok=true manual_ok=true capture_ok=true'),
    # --- r95 block: PhysicsDirectSpaceState2D query lattice + the
    # multi-hit order k(k-1) cycle law -----------------------------------
    # Two probes, both byte-copies of the frozen lane artifacts:
    #   dss_lattice.gd sha256
    #   77ae4adb8a47ccf50b5da345720247c035418e31872a117d17cd98913f479627
    #   (corpus/live/r95-scout/probes/dss_lattice.gd, identical bytes)
    #   r95b_order.gd sha256
    #   4f7e945e1b16f241d510e1b1aa7c7fc1aafca6369626e3910bb36cf62d9e2490
    #   (corpus/live/r95-boundary/probes/r95b_order.gd, identical bytes)
    # Boundary-surviving encoding (r95-boundary verdicts applied):
    #   * The 13 non-order-vector dss_lattice rows pin their full PASS
    #     lines; the four order-vector cells (point_cap, point_cap_rev,
    #     order_core, order_core_rev) pin only the order-free head — the
    #     scout's ROWS_PREFIX form. The vectors are the t=2 phase of a
    #     k(k-1)-tick broadphase cycle (boundary §2) and the full
    #     order_core line carries the refuted layout_changes_order key
    #     (§4: co-presence, not translation) — both excluded from the
    #     signatures (the bytes still print as data).
    #   * The ordering law is pinned phase-resolved by the r95b rows:
    #     canon dense ladder (t0=insertion, t20==t0), periodx k=2..10
    #     (cycle_len = k(k-1)), period_k5 (the ff/thr/load-covered k=5
    #     cell), perm0..7 (creation-order permutations under a fixed
    #     tag->position map — the insertion-order evidence the scout's
    #     label-only --rev could not be), scoutrev (the label-mirror
    #     counter-pin), celloff (translation invariance — refutes
    #     "layout dependent"), twopiles + warm_keep8 (co-presence
    #     perturbation — the true attribution), warm_k32 (freed
    #     allocation history is inert), free_ab/ba + readd_a (mutation
    #     coordinates), cap40_p0..p2 (n0/n32/n64 counts and
    #     set32_distinct=5 — the set is NOT invariant above the cap),
    #     layers_k0/k1 (point/shape order agreement is
    #     canvas-layer-conditional), rigid (solver positions
    #     byte-deterministic).
    #   * Deliberately NOT authored: procwait (boundary §9 [U] — a
    #     process-frame await lands on a different tick phase per rep;
    #     8 distinct payloads across 16 receipts), env (frame counters,
    #     2 distinct payloads), every full-line multi-hit order vector,
    #     every instance_id/RID (warm_k1 proves ids change while the
    #     ladder holds — ids are never semantic).
    # Signatures verified fresh-process on the fixture bytes: 52/52
    # arms rc=0, 0 B stderr, signature substring-matched — the
    # dss_lattice 17 are the scout's verify_rows-accepted ROWS_PREFIX
    # set (150/150 receipts); the r95b 35 are canonical PASS lines
    # byte-identical across the boundary's 261-run matrix (pass_uniq=1
    # per authored cell). EXPECTED_ERRORS={} — every arm is
    # ERROR:-clean. Rows inserted ahead of the crash/descendant tail —
    # descendant_pipe_detached_control's sleep-8 gap stays adjacent to
    # the meta probes.
    ('dss_lattice_census', 'dss_lattice.gd', ["--arm=census"], 0,
     'PASS dss_lattice census dss_methods=n6[cast_motion,collide_shape,get_rest_info,intersect_point,intersect_ray,intersect_shape] dss_sigs=[cast_motion(parameters:24)|collide_shape(parameters:24,max_results:2)|get_rest_info(parameters:24)|intersect_point(parameters:24,max_results:2)|intersect_ray(parameters:24)|intersect_shape(parameters:24,max_results:2)] ray=props=[collide_with_areas,collide_with_bodies,collision_mask,exclude,from,hit_from_inside,to] defaults=[collide_with_areas=false,collide_with_bodies=true,collision_mask=4294967295,exclude=n0,from=(0.0000,0.0000),hit_from_inside=false,to=(0.0000,0.0000)] pt=props=[canvas_instance_id,collide_with_areas,collide_with_bodies,collision_mask,exclude,position] defaults=[canvas_instance_id=0,collide_with_areas=false,collide_with_bodies=true,collision_mask=4294967295,exclude=n0,position=(0.0000,0.0000)] sh=props=[collide_with_areas,collide_with_bodies,collision_mask,exclude,margin,motion,shape,shape_rid,transform] defaults=[collide_with_areas=false,collide_with_bodies=true,collision_mask=4294967295,exclude=n0,margin=0.0000,motion=(0.0000,0.0000),shape=<Object#null>,shape_rid=RID(0),transform=[X: (1.0, 0.0), Y: (0.0, 1.0), O: (0.0, 0.0)]] ray_backface=has=false pt_canvas=has=true ray_create=from=(1.0000,2.0000) to=(3.0000,4.0000) mask=4294967295 excl=0 bodies=true areas=false inside=false dss_cls=cls=GodotPhysicsDirectSpaceState2D dss_identity=same_across_calls=true'),
    ('dss_lattice_ray_flags', 'dss_lattice.gd', ["--arm=ray_flags"], 0,
     'PASS dss_lattice ray_flags base=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)} mask2=r={} mask0=r={} nobodies=r={} areas_on=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)} areas_only=r={w2 pos=(298.0000,0.0000) n=(-1.0000,0.0000)} excl_wall=r={} excl_area=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)} inside_off=r={} inside_on=r={w pos=(100.0000,0.0000) n=(0.0000,0.0000)} inside_area_on=r={w2 pos=(300.0000,0.0000) n=(0.0000,0.0000)} outside_on=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)} keys=["collider", "collider_id", "normal", "position", "rid", "shape"]'),
    ('dss_lattice_ray_geom', 'dss_lattice.gd', ["--arm=ray_geom"], 0,
     'PASS dss_lattice ray_geom end_at_face=r={w pos=(98.0000,0.0000) n=(-1.0000,0.0000)} end_eps_before=r={} graze_top=r={w pos=(98.0000,-200.0000) n=(-1.0000,0.0000)} graze_inside=r={w pos=(98.0000,-199.9990) n=(-1.0000,0.0000)} corner_diag=r={c pos=(180.0000,-20.0000) n=(-1.0000,0.0000)} zero_len_face=r={} zero_len_out=r={} reverse=r={c pos=(220.0000,0.0000) n=(1.0000,0.0000)} from_left_away=r={} from_left_through=r={c pos=(180.0000,0.0000) n=(-1.0000,0.0000)} from_right_away=r={w pos=(102.0000,0.0000) n=(0.0000,0.0000)} from_right_through=r={w pos=(102.0000,0.0000) n=(0.0000,0.0000)} corner_start_away=r={}'),
    ('dss_lattice_ray_order', 'dss_lattice.gd', ["--arm=ray_order"], 0,
     'PASS dss_lattice ray_order nearest=r={near pos=(98.0000,0.0000) n=(-1.0000,0.0000)} tie=r={tie_b pos=(298.0000,0.0000) n=(-1.0000,0.0000)} tie_minus_first=r={tie_b pos=(298.0000,0.0000) n=(-1.0000,0.0000)} tie_minus_second=r={tie_a pos=(298.0000,0.0000) n=(-1.0000,0.0000)} tie_add_order=[tie_a,tie_b] last_added_wins=true rev=false'),
    ('dss_lattice_ray_order_rev', 'dss_lattice.gd', ["--arm=ray_order", "--rev"], 0,
     'PASS dss_lattice ray_order nearest=r={near pos=(98.0000,0.0000) n=(-1.0000,0.0000)} tie=r={tie_a pos=(298.0000,0.0000) n=(-1.0000,0.0000)} tie_minus_first=r={tie_a pos=(298.0000,0.0000) n=(-1.0000,0.0000)} tie_minus_second=r={tie_b pos=(298.0000,0.0000) n=(-1.0000,0.0000)} tie_add_order=[tie_b,tie_a] last_added_wins=true rev=true'),
    ('dss_lattice_point_cap', 'dss_lattice.gd', ["--arm=point_cap"], 0,
     'PASS dss_lattice point_cap add_order=[a,b,c,d,e] cap0=[]'),
    ('dss_lattice_point_cap_rev', 'dss_lattice.gd', ["--arm=point_cap", "--rev"], 0,
     'PASS dss_lattice point_cap add_order=[e,d,c,b,a] cap0=[]'),
    ('dss_lattice_point_edge', 'dss_lattice.gd', ["--arm=point_edge"], 0,
     'PASS dss_lattice point_edge box_left=[box#0] box_right=[] box_top=[box#0] box_bottom=[] box_left_in=[box#0] box_right_in=[box#0] circ_left=[] circ_left_in=[circ#0] circ_top=[] circ_center=[circ#0] rot_left=[] rot_right=[] rot_top=[rot#0] s_box_right=[box#0] s_box_bottom=[box#0] s_circ_top=[circ#0] s_rot_right=[rot#0] point_half_open=left=true right=false top=true bottom=false'),
    ('dss_lattice_point_canvas', 'dss_lattice.gd', ["--arm=point_canvas"], 0,
     'PASS dss_lattice point_canvas default_q=[def#0] layer_q=[clb#0] layer_q_at_default_spot=[clb#0] layer_scoped=true shifted_default_q=[def#0] shifted_layer_q=[clb#0] layer_offset_ignored=true ray_sees_default=r={def pos=(80.0000,0.0000) n=(-1.0000,0.0000)} shape_sees_both=[def#0,clb#0] shape_layer_agnostic=true rev=false'),
    ('dss_lattice_shape', 'dss_lattice.gd', ["--arm=shape_lattice"], 0,
     'PASS dss_lattice shape_lattice cap0=n0 cap1=n1 cap3=n3 cap5=n5 cap_default=n5 keys=["collider", "collider_id", "rid", "shape"] set=[a#0,b#0,c#0,d#0,e#0] touch=[e#0] touch_in=[e#0] touch_out=[] multi_c0=[m#0] multi_c1=[m#1] multi_c2=[m#2] multi_set=[m#0,m#1,m#2] shape_rid=[m#1] empty=n0 rev=false'),
    ('dss_lattice_shape_rev', 'dss_lattice.gd', ["--arm=shape_lattice", "--rev"], 0,
     'PASS dss_lattice shape_lattice cap0=n0 cap1=n1 cap3=n3 cap5=n5 cap_default=n5 keys=["collider", "collider_id", "rid", "shape"] set=[a#0,b#0,c#0,d#0,e#0] touch=[a#0] touch_in=[a#0] touch_out=[] multi_c0=[m#0] multi_c1=[m#1] multi_c2=[m#2] multi_set=[m#0,m#1,m#2] shape_rid=[m#1] empty=n0 rev=true'),
    ('dss_lattice_order_core', 'dss_lattice.gd', ["--arm=order_core"], 0,
     'PASS dss_lattice order_core add_order=[a,b,c,d,e]'),
    ('dss_lattice_order_core_rev', 'dss_lattice.gd', ["--arm=order_core", "--rev"], 0,
     'PASS dss_lattice order_core add_order=[e,d,c,b,a]'),
    ('dss_lattice_layer_forms', 'dss_lattice.gd', ["--arm=layer_forms"], 0,
     'PASS dss_lattice layer_forms point_vis=[sb:body1/areas1/only0,ar:body0/areas1/only1,rb:body1/areas1/only0,cb:body1/areas1/only0,srv:body1/areas1/only0,canvas:body0/areas0/only0] ray_sb=r={sb pos=(80.0000,0.0000) n=(-1.0000,0.0000)} ray_srv=r={? pos=(860.0000,0.0000) n=(-1.0000,0.0000)} ray_area_off=r={} ray_area_on=r={ar pos=(280.0000,0.0000) n=(-1.0000,0.0000)} shape_srv=[?#0] shape_area_off=[] shape_area_on=[ar#0] cast_srv_ignored=[1.0, 1.0] server_tier_visible=true canvas_absent=true'),
    ('dss_lattice_cast_rest', 'dss_lattice.gd', ["--arm=cast_rest"], 0,
     'PASS dss_lattice cast_rest cm_base=[0.220703125, 0.2265625] cm_to_wall1=[0.59765625, 0.6015625] cm_mask2=[1.0, 1.0] cm_excl_w1=[0.72265625, 0.7265625] cm_excl_both=[1.0, 1.0] cm_areas_on=[0.220703125, 0.2265625] cm_zero=[1.0, 1.0] cm_negative=[1.0, 1.0] cm_from_inside=[0.47265625, 0.4765625] cm_inside_skips_overlap=true cm_inside_matches_later_wall=true ri_m50={} ri_m200={w1 pt=(98.0000,0.0000) n=(-1.0000,0.0000) shape=0} ri_m290={w1 pt=(102.0000,0.0000) n=(1.0000,0.0000) shape=0} ri_m300={w1 pt=(102.0000,0.0000) n=(1.0000,0.0000) shape=0} ri_m400={w1 pt=(102.0000,0.0000) n=(1.0000,0.0000) shape=0} ri_m600={w2 pt=(298.0000,200.0000) n=(0.0000,1.0000) shape=0} ri_m200_excl_w1={} ri_m400_excl_w1={w2 pt=(298.0000,0.0000) n=(-1.0000,0.0000) shape=0} ri_mask2={} ri_empty={} ri_offaxis={} ri_keys=["collider_id", "linear_velocity", "normal", "point", "rid", "shape"] ri_zero_motion={w1 pt=(98.0000,0.0000) n=(-1.0000,0.0000) shape=0} cs_n=6 cs_pts=[(98.0000,0.0000),(102.0000,0.0000),(114.0000,0.0000),(110.0000,0.0000),(98.0000,0.0000),(102.0000,0.0000)] cs_cap1=n2 cs_cap2=n4 cs_excl_b1=n4 cs_mask2=n0 cs_rep=n6 cs_empty=n0'),
    ('dss_lattice_excl_space', 'dss_lattice.gd', ["--arm=excl_space"], 0,
     'PASS dss_lattice excl_space baseline=[a#0] body_rid=[] shape_rid_inert=true null_rid_inert=true dup_rid=[] ray_shape_rid_inert=r={a pos=(80.0000,0.0000) n=(-1.0000,0.0000)} shape_rid_is_body_rid=false same_space=false root_view=[root_body#0] sv_view=[sv_body#0] space_scoped=true dss_identity=same_across_calls=true node_world_ok=true'),
    ('dss_lattice_fresh', 'dss_lattice.gd', ["--arm=fresh"], 0,
     'PASS dss_lattice fresh add_t0_point=[f#0] add_t0_ray=r={f pos=(80.0000,0.0000) n=(-1.0000,0.0000)} add_t0_shape=[f#0] add_same_frame=true node_move_t0_old=[f#0] node_move_t0_new=[] node_move_deferred=true node_move_t1_old=[] node_move_t1_new=[f#0] server_tele_t0_old=[] server_tele_t0_new=[f#0] server_write_live=true pre_free=[c#0] free_t0=[c#0] free_deferred=true free_t1=[] vis_off=[d#0] visible_irrelevant=true layer_change_t0=[e#0] layer_change_t1=[e#0]'),
    ('r95b_order_canon', 'r95b_order.gd', ["--arm=canon"], 0,
     'PASS r95b_order canon add_order=[a,b,c,d,e] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:0,1,2,3,4;t1:4,1,2,3,0;t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t5:3,0,1,2,4;t6:3,4,1,2,0;t7:3,4,0,2,1;t8:3,4,0,1,2;t9:2,4,0,1,3;t10:2,3,0,1,4;t11:2,3,4,1,0;t12:2,3,4,0,1;t13:1,3,4,0,2;t14:1,2,4,0,3;t15:1,2,3,0,4;t16:1,2,3,4,0;t17:0,2,3,4,1;t18:0,1,3,4,2;t19:0,1,2,4,3;t20:0,1,2,3,4;t21:4,1,2,3,0;t22:4,0,2,3,1;t23:4,0,1,3,2;t24:4,0,1,2,3;t25:3,0,1,2,4;t26:3,4,1,2,0;t27:3,4,0,2,1;t28:3,4,0,1,2;t29:2,4,0,1,3;t30:2,3,0,1,4;t32:2,3,4,0,1;t36:1,2,3,4,0;t40:0,1,2,3,4;t48:3,4,0,1,2;t56:1,2,3,4,0;t64:4,0,1,2,3] distinct_ticks=20 last_change_tick=64 cycle_len_dense=20 t0_pidx=0,1,2,3,4 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t2_sh_vec=[e#0,a#0,c#0,d#0,b#0] t2_pt_eq_sh=true t64_vec=[e#0,a#0,b#0,c#0,d#0] end_sh_vec=[e#0,a#0,b#0,c#0,d#0] end_pt_eq_sh=true pt_stable_interleaved=true'),
    ('r95b_order_periodx_k2', 'r95b_order.gd', ["--arm=periodx", "--k=2"], 0,
     'PASS r95b_order periodx k=2 spacing=4.0 cycle_len=2 expected_kk1=2 distinct_ticks=2 n_ticks=5 t0_vec=[p0#0,p1#0] t2_vec=[p0#0,p1#0] t3_vec=[p1#0,p0#0]'),
    ('r95b_order_periodx_k3', 'r95b_order.gd', ["--arm=periodx", "--k=3"], 0,
     'PASS r95b_order periodx k=3 spacing=4.0 cycle_len=6 expected_kk1=6 distinct_ticks=6 n_ticks=9 t0_vec=[p0#0,p1#0,p2#0] t2_vec=[p2#0,p0#0,p1#0] t3_vec=[p1#0,p0#0,p2#0]'),
    ('r95b_order_periodx_k4', 'r95b_order.gd', ["--arm=periodx", "--k=4"], 0,
     'PASS r95b_order periodx k=4 spacing=4.0 cycle_len=12 expected_kk1=12 distinct_ticks=12 n_ticks=15 t0_vec=[p0#0,p1#0,p2#0,p3#0] t2_vec=[p3#0,p0#0,p2#0,p1#0] t3_vec=[p3#0,p0#0,p1#0,p2#0]'),
    ('r95b_order_periodx_k5', 'r95b_order.gd', ["--arm=periodx", "--k=5"], 0,
     'PASS r95b_order periodx k=5 spacing=4.0 cycle_len=20 expected_kk1=20 distinct_ticks=20 n_ticks=23 t0_vec=[p0#0,p1#0,p2#0,p3#0,p4#0] t2_vec=[p4#0,p0#0,p2#0,p3#0,p1#0] t3_vec=[p4#0,p0#0,p1#0,p3#0,p2#0]'),
    ('r95b_order_periodx_k5s8', 'r95b_order.gd', ["--arm=periodx", "--k=5", "--spacing=8"], 0,
     'PASS r95b_order periodx k=5 spacing=8.0 cycle_len=20 expected_kk1=20 distinct_ticks=20 n_ticks=23 t0_vec=[p0#0,p1#0,p2#0,p3#0,p4#0] t2_vec=[p4#0,p0#0,p2#0,p3#0,p1#0] t3_vec=[p4#0,p0#0,p1#0,p3#0,p2#0]'),
    ('r95b_order_periodx_k6', 'r95b_order.gd', ["--arm=periodx", "--k=6"], 0,
     'PASS r95b_order periodx k=6 spacing=4.0 cycle_len=30 expected_kk1=30 distinct_ticks=30 n_ticks=33 t0_vec=[p0#0,p1#0,p2#0,p3#0,p4#0,p5#0] t2_vec=[p5#0,p0#0,p2#0,p3#0,p4#0,p1#0] t3_vec=[p5#0,p0#0,p1#0,p3#0,p4#0,p2#0]'),
    ('r95b_order_periodx_k7', 'r95b_order.gd', ["--arm=periodx", "--k=7"], 0,
     'PASS r95b_order periodx k=7 spacing=4.0 cycle_len=42 expected_kk1=42 distinct_ticks=42 n_ticks=45 t0_vec=[p0#0,p1#0,p2#0,p3#0,p4#0,p5#0,p6#0] t2_vec=[p6#0,p0#0,p2#0,p3#0,p4#0,p5#0,p1#0] t3_vec=[p6#0,p0#0,p1#0,p3#0,p4#0,p5#0,p2#0]'),
    ('r95b_order_periodx_k8', 'r95b_order.gd', ["--arm=periodx", "--k=8"], 0,
     'PASS r95b_order periodx k=8 spacing=4.0 cycle_len=56 expected_kk1=56 distinct_ticks=56 n_ticks=59 t0_vec=[p0#0,p1#0,p2#0,p3#0,p4#0,p5#0,p6#0,p7#0] t2_vec=[p7#0,p0#0,p2#0,p3#0,p4#0,p5#0,p6#0,p1#0] t3_vec=[p7#0,p0#0,p1#0,p3#0,p4#0,p5#0,p6#0,p2#0]'),
    ('r95b_order_periodx_k10', 'r95b_order.gd', ["--arm=periodx", "--k=10"], 0,
     'PASS r95b_order periodx k=10 spacing=4.0 cycle_len=90 expected_kk1=90 distinct_ticks=90 n_ticks=93 t0_vec=[p0#0,p1#0,p2#0,p3#0,p4#0,p5#0,p6#0,p7#0,p8#0,p9#0] t2_vec=[p9#0,p0#0,p2#0,p3#0,p4#0,p5#0,p6#0,p7#0,p8#0,p1#0] t3_vec=[p9#0,p0#0,p1#0,p3#0,p4#0,p5#0,p6#0,p7#0,p8#0,p2#0]'),
    ('r95b_order_period_k5', 'r95b_order.gd', ["--arm=period", "--k=5"], 0,
     'PASS r95b_order period k=5 cycle_len=20 distinct_ticks=20 t0_vec=[p0#0,p1#0,p2#0,p3#0,p4#0] t2_vec=[p4#0,p0#0,p2#0,p3#0,p1#0] t_last_vec=[p3#0,p4#0,p0#0,p2#0,p1#0]'),
    ('r95b_order_perm0', 'r95b_order.gd', ["--arm=perm", "--perm=0"], 0,
     'PASS r95b_order perm perm=0 add_order=[a,b,c,d,e] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:0,1,2,3,4;t1:4,1,2,3,0;t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t5:3,0,1,2,4;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1] distinct_ticks=9 last_change_tick=32 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000]'),
    ('r95b_order_perm1', 'r95b_order.gd', ["--arm=perm", "--perm=1"], 0,
     'PASS r95b_order perm perm=1 add_order=[e,d,c,b,a] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:4,3,2,1,0;t1:0,3,2,1,4;t2:0,4,2,1,3;t3:0,4,3,1,2;t4:0,4,3,2,1;t5:1,4,3,2,0;t8:1,0,4,3,2;t16:3,2,1,0,4;t32:2,1,0,4,3] distinct_ticks=9 last_change_tick=32 t2_vec=[a#0,e#0,c#0,b#0,d#0] t2_relpos=[0.0000,0.0000|32.0000,0.0000|16.0000,0.0000|8.0000,0.0000|24.0000,0.0000]'),
    ('r95b_order_perm2', 'r95b_order.gd', ["--arm=perm", "--perm=2"], 0,
     'PASS r95b_order perm perm=2 add_order=[b,c,a,e,d] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:1,2,0,4,3;t1:0,2,4,3,1;t2:0,1,4,3,2;t3:2,1,4,3,0;t4:2,1,0,3,4;t5:2,1,0,4,3;t8:1,3,2,4,0;t16:4,0,3,2,1;t32:3,4,1,0,2] distinct_ticks=9 last_change_tick=32 t2_vec=[a#0,b#0,e#0,d#0,c#0] t2_relpos=[0.0000,0.0000|8.0000,0.0000|32.0000,0.0000|24.0000,0.0000|16.0000,0.0000]'),
    ('r95b_order_perm3', 'r95b_order.gd', ["--arm=perm", "--perm=3"], 0,
     'PASS r95b_order perm perm=3 add_order=[c,a,e,d,b] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:2,0,4,3,1;t1:0,4,1,3,2;t2:2,4,1,3,0;t3:2,0,1,3,4;t4:2,0,1,4,3;t5:2,0,3,4,1;t8:1,2,3,0,4;t16:4,3,0,1,2;t32:3,1,4,2,0] distinct_ticks=9 last_change_tick=32 t2_vec=[c#0,e#0,b#0,d#0,a#0] t2_relpos=[16.0000,0.0000|32.0000,0.0000|8.0000,0.0000|24.0000,0.0000|0.0000,0.0000]'),
    ('r95b_order_perm4', 'r95b_order.gd', ["--arm=perm", "--perm=4"], 0,
     'PASS r95b_order perm perm=4 add_order=[a,c,b,e,d] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:0,2,1,4,3;t1:4,2,1,3,0;t2:4,0,1,3,2;t3:4,0,2,3,1;t4:1,0,2,3,4;t5:1,0,2,4,3;t8:2,3,0,4,1;t16:3,1,4,2,0;t32:0,4,3,1,2] distinct_ticks=9 last_change_tick=32 t2_vec=[e#0,a#0,b#0,d#0,c#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|24.0000,0.0000|16.0000,0.0000]'),
    ('r95b_order_perm5', 'r95b_order.gd', ["--arm=perm", "--perm=5"], 0,
     'PASS r95b_order perm perm=5 add_order=[d,a,b,e,c] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:3,0,1,4,2;t1:0,4,1,2,3;t2:3,4,1,2,0;t3:3,4,0,2,1;t4:3,1,0,2,4;t5:3,1,0,4,2;t8:2,0,3,4,1;t16:1,2,4,0,3;t32:4,3,2,1,0] distinct_ticks=9 last_change_tick=32 t2_vec=[d#0,e#0,b#0,c#0,a#0] t2_relpos=[24.0000,0.0000|32.0000,0.0000|8.0000,0.0000|16.0000,0.0000|0.0000,0.0000]'),
    ('r95b_order_perm6', 'r95b_order.gd', ["--arm=perm", "--perm=6"], 0,
     'PASS r95b_order perm perm=6 add_order=[e,a,c,d,b] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:4,0,2,3,1;t1:0,1,2,3,4;t2:4,1,2,3,0;t3:4,1,0,3,2;t4:4,1,0,2,3;t5:4,3,0,2,1;t8:1,3,4,0,2;t16:2,0,3,1,4;t32:3,2,1,4,0] distinct_ticks=9 last_change_tick=32 t2_vec=[e#0,b#0,c#0,d#0,a#0] t2_relpos=[32.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000|0.0000,0.0000]'),
    ('r95b_order_perm7', 'r95b_order.gd', ["--arm=perm", "--perm=7"], 0,
     'PASS r95b_order perm perm=7 add_order=[b,a,d,c,e] map=[a@0,b@8,c@16,d@24,e@32] ladder=[t0:1,0,3,2,4;t1:0,4,3,2,1;t2:1,4,3,2,0;t3:1,4,0,2,3;t4:1,4,0,3,2;t5:1,2,0,3,4;t8:4,2,1,0,3;t16:3,0,2,4,1;t32:2,3,4,1,0] distinct_ticks=9 last_change_tick=32 t2_vec=[b#0,e#0,d#0,c#0,a#0] t2_relpos=[8.0000,0.0000|32.0000,0.0000|24.0000,0.0000|16.0000,0.0000|0.0000,0.0000]'),
    ('r95b_order_scoutrev', 'r95b_order.gd', ["--arm=scoutrev"], 0,
     'PASS r95b_order scoutrev add_order=[e,d,c,b,a] map=[e@0,d@8,c@16,b@24,a@32] ladder=[t0:4,3,2,1,0;t1:0,3,2,1,4;t2:0,4,2,1,3;t3:0,4,3,1,2;t4:0,4,3,2,1;t5:1,4,3,2,0;t8:1,0,4,3,2;t16:3,2,1,0,4;t32:2,1,0,4,3] distinct_ticks=9 t2_vec=[a#0,e#0,c#0,b#0,d#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] scout_row_rev_t2_vec=[a#0,e#0,c#0,b#0,d#0] t2_vec_matches_scout_row=true t2_relpos_equals_canon=true'),
    ('r95b_order_celloff_x0', 'r95b_order.gd', ["--arm=celloff", "--off=0"], 0,
     'PASS r95b_order celloff off=0.0000 add_order=[a,b,c,d,e] ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3] distinct_ticks=7 last_change_tick=64 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t64_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000]'),
    ('r95b_order_celloff_x1000', 'r95b_order.gd', ["--arm=celloff", "--off=1000"], 0,
     'PASS r95b_order celloff off=1000.0000 add_order=[a,b,c,d,e] ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3] distinct_ticks=7 last_change_tick=64 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t64_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000]'),
    ('r95b_order_celloff_y1000', 'r95b_order.gd', ["--arm=celloff", "--off=0", "--offy=1000"], 0,
     'PASS r95b_order celloff off=0.0000 add_order=[a,b,c,d,e] ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1;t64:4,0,1,2,3] distinct_ticks=7 last_change_tick=64 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t64_relpos=[32.0000,0.0000|0.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000]'),
    ('r95b_order_twopiles', 'r95b_order.gd', ["--arm=twopiles"], 0,
     'PASS r95b_order twopiles a_t2_vec=[e#0,a#0,c#0,d#0,b#0] a_t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] a_t4_with_b_vec=[e#0,a#0,c#0,b#0,d#0] a_t4_with_b_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|8.0000,0.0000|24.0000,0.0000] b_t2_vec=[e2#0,a2#0,b2#0,c2#0,d2#0] b_t2_relpos=[32.0000,1000.0000|0.0000,1000.0000|8.0000,1000.0000|16.0000,1000.0000|24.0000,1000.0000] a_t6_with_b_vec=[d#0,a#0,c#0,b#0,e#0] b_t4_vec=[e2#0,b2#0,c2#0,d2#0,a2#0]'),
    ('r95b_order_warm_k32', 'r95b_order.gd', ["--arm=warm", "--k=32", "--keep=0"], 0,
     'PASS r95b_order warm k=32 keep=0 add_order=[a,b,c,d,e] ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1] distinct_ticks=7 t2_vec=[e#0,a#0,c#0,d#0,b#0] t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] t32_vec=[c#0,d#0,e#0,a#0,b#0]'),
    ('r95b_order_warm_keep8', 'r95b_order.gd', ["--arm=warm", "--k=8", "--keep=1"], 0,
     'PASS r95b_order warm k=8 keep=1 add_order=[a,b,c,d,e] ladder=[t2:0,4,1,2,3;t3:0,4,1,2,3;t4:0,4,1,2,3;t6:0,4,1,2,3;t8:4,1,2,3,0;t16:4,3,0,1,2;t32:4,3,2,0,1] distinct_ticks=4 t2_vec=[a#0,e#0,b#0,c#0,d#0] t2_relpos=[0.0000,0.0000|32.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000] t32_vec=[e#0,d#0,c#0,a#0,b#0]'),
    ('r95b_order_free_ab', 'r95b_order.gd', ["--arm=free", "--order=ab"], 0,
     'PASS r95b_order free freed=[a,b] add_order=[a,b,c,d,e] ladder=[t1:4,3,2;t2:2,3,4;t3:2,4,3;t4:3,4,2;t6:4,2,3;t8:2,3,4;t16:3,4,2] distinct_ticks=5 last_change_tick=16 t1_vec=[e#0,d#0,c#0] t1_relpos=[32.0000,0.0000|24.0000,0.0000|16.0000,0.0000] t16_vec=[d#0,e#0,c#0] set=[c#0,d#0,e#0]'),
    ('r95b_order_free_ba', 'r95b_order.gd', ["--arm=free", "--order=ba"], 0,
     'PASS r95b_order free freed=[b,a] add_order=[a,b,c,d,e] ladder=[t1:3,4,2;t2:2,4,3;t3:2,3,4;t4:4,3,2;t6:3,2,4;t8:2,4,3;t16:4,3,2] distinct_ticks=5 last_change_tick=16 t1_vec=[d#0,e#0,c#0] t1_relpos=[24.0000,0.0000|32.0000,0.0000|16.0000,0.0000] t16_vec=[e#0,d#0,c#0] set=[c#0,d#0,e#0]'),
    ('r95b_order_readd_a', 'r95b_order.gd', ["--arm=readd", "--which=a"], 0,
     'PASS r95b_order readd which=a add_order=[a,b,c,d,e] ladder=[t1:4,1,2,3,f;t2:f,1,2,3,4;t3:f,4,2,3,1;t4:f,4,1,3,2;t6:3,4,1,2,f;t8:3,f,4,2,1;t16:1,2,3,4,f] distinct_ticks=7 t1_vec=[e#0,b#0,c#0,d#0,f#0] t1_relpos=[32.0000,0.0000|8.0000,0.0000|16.0000,0.0000|24.0000,0.0000|0.0000,0.0000] t16_vec=[b#0,c#0,d#0,e#0,f#0] set=[b#0,c#0,d#0,e#0,f#0]'),
    ('r95b_order_cap40_p0', 'r95b_order.gd', ["--arm=cap40", "--perm=0"], 0,
     'PASS r95b_order cap40 perm=0 add_order_head=[t0,t1,t2,t3,t4,t5,t6,t7] set32_ladder=[t2:[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t31#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0];t4:[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0];t8:[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t31#0,t39#0,t4#0,t5#0,t6#0,t8#0,t9#0];t16:[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t31#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0];t32:[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0]] set32_distinct=5 set32_t2=[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t31#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0] n32=32 n64=40 n0=0 set32_t32=[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0] relpos32_t32=[0.0000,0.0000|2.0000,0.0000|78.0000,0.0000|4.0000,0.0000|6.0000,0.0000|8.0000,0.0000|10.0000,0.0000|12.0000,0.0000|14.0000,0.0000|16.0000,0.0000|18.0000,0.0000|20.0000,0.0000|22.0000,0.0000|24.0000,0.0000|26.0000,0.0000|28.0000,0.0000|30.0000,0.0000|32.0000,0.0000|34.0000,0.0000|36.0000,0.0000|38.0000,0.0000|40.0000,0.0000|42.0000,0.0000|44.0000,0.0000|46.0000,0.0000|48.0000,0.0000|50.0000,0.0000|52.0000,0.0000|54.0000,0.0000|56.0000,0.0000|58.0000,0.0000|60.0000,0.0000] set64=[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t38#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0] relpos64_head=[0.0000,0.0000|2.0000,0.0000|78.0000,0.0000|4.0000,0.0000|6.0000,0.0000|8.0000,0.0000|10.0000,0.0000|12.0000,0.0000]'),
    ('r95b_order_cap40_p1', 'r95b_order.gd', ["--arm=cap40", "--perm=1"], 0,
     'PASS r95b_order cap40 perm=1 add_order_head=[t39,t38,t37,t36,t35,t34,t33,t32] set32_ladder=[t2:[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t39#0,t8#0,t9#0];t4:[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t37#0,t38#0,t39#0,t8#0,t9#0];t8:[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t33#0,t34#0,t35#0,t36#0,t37#0,t38#0,t39#0,t8#0,t9#0];t16:[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t20#0,t21#0,t22#0,t23#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t38#0,t39#0,t8#0,t9#0];t32:[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t38#0,t39#0,t9#0]] set32_distinct=5 set32_t2=[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t39#0,t8#0,t9#0] n32=32 n64=40 n0=0 set32_t32=[t0#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t38#0,t39#0,t9#0] relpos32_t32=[78.0000,0.0000|76.0000,0.0000|0.0000,0.0000|74.0000,0.0000|72.0000,0.0000|70.0000,0.0000|68.0000,0.0000|66.0000,0.0000|64.0000,0.0000|62.0000,0.0000|60.0000,0.0000|58.0000,0.0000|56.0000,0.0000|54.0000,0.0000|52.0000,0.0000|50.0000,0.0000|48.0000,0.0000|46.0000,0.0000|44.0000,0.0000|42.0000,0.0000|40.0000,0.0000|38.0000,0.0000|36.0000,0.0000|34.0000,0.0000|32.0000,0.0000|30.0000,0.0000|28.0000,0.0000|26.0000,0.0000|24.0000,0.0000|22.0000,0.0000|20.0000,0.0000|18.0000,0.0000] set64=[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t38#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0] relpos64_head=[78.0000,0.0000|76.0000,0.0000|0.0000,0.0000|74.0000,0.0000|72.0000,0.0000|70.0000,0.0000|68.0000,0.0000|66.0000,0.0000]'),
    ('r95b_order_cap40_p2', 'r95b_order.gd', ["--arm=cap40", "--perm=2"], 0,
     'PASS r95b_order cap40 perm=2 add_order_head=[t3,t10,t17,t24,t31,t38,t5,t12] set32_ladder=[t2:[t0#0,t1#0,t11#0,t12#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t23#0,t24#0,t25#0,t26#0,t28#0,t3#0,t30#0,t31#0,t32#0,t33#0,t35#0,t36#0,t37#0,t38#0,t4#0,t5#0,t6#0,t7#0,t9#0];t4:[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t23#0,t25#0,t26#0,t28#0,t3#0,t30#0,t31#0,t32#0,t33#0,t35#0,t36#0,t37#0,t38#0,t4#0,t5#0,t6#0,t7#0,t9#0];t8:[t0#0,t1#0,t10#0,t11#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t23#0,t24#0,t25#0,t26#0,t28#0,t3#0,t30#0,t31#0,t32#0,t33#0,t35#0,t36#0,t37#0,t38#0,t4#0,t5#0,t6#0,t7#0,t9#0];t16:[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t23#0,t24#0,t25#0,t26#0,t3#0,t30#0,t31#0,t32#0,t33#0,t35#0,t36#0,t37#0,t38#0,t4#0,t5#0,t6#0,t7#0,t9#0];t32:[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t21#0,t23#0,t24#0,t25#0,t26#0,t28#0,t3#0,t30#0,t31#0,t33#0,t35#0,t36#0,t37#0,t38#0,t39#0,t4#0,t5#0,t6#0,t7#0,t9#0]] set32_distinct=5 set32_t2=[t0#0,t1#0,t11#0,t12#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t23#0,t24#0,t25#0,t26#0,t28#0,t3#0,t30#0,t31#0,t32#0,t33#0,t35#0,t36#0,t37#0,t38#0,t4#0,t5#0,t6#0,t7#0,t9#0] n32=32 n64=40 n0=0 set32_t32=[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t16#0,t17#0,t18#0,t19#0,t2#0,t21#0,t23#0,t24#0,t25#0,t26#0,t28#0,t3#0,t30#0,t31#0,t33#0,t35#0,t36#0,t37#0,t38#0,t39#0,t4#0,t5#0,t6#0,t7#0,t9#0] relpos32_t32=[66.0000,0.0000|6.0000,0.0000|20.0000,0.0000|34.0000,0.0000|48.0000,0.0000|62.0000,0.0000|76.0000,0.0000|10.0000,0.0000|24.0000,0.0000|38.0000,0.0000|52.0000,0.0000|72.0000,0.0000|0.0000,0.0000|14.0000,0.0000|28.0000,0.0000|42.0000,0.0000|56.0000,0.0000|70.0000,0.0000|4.0000,0.0000|18.0000,0.0000|32.0000,0.0000|46.0000,0.0000|60.0000,0.0000|74.0000,0.0000|8.0000,0.0000|22.0000,0.0000|36.0000,0.0000|50.0000,0.0000|2.0000,0.0000|78.0000,0.0000|12.0000,0.0000|26.0000,0.0000] set64=[t0#0,t1#0,t10#0,t11#0,t12#0,t13#0,t14#0,t15#0,t16#0,t17#0,t18#0,t19#0,t2#0,t20#0,t21#0,t22#0,t23#0,t24#0,t25#0,t26#0,t27#0,t28#0,t29#0,t3#0,t30#0,t31#0,t32#0,t33#0,t34#0,t35#0,t36#0,t37#0,t38#0,t39#0,t4#0,t5#0,t6#0,t7#0,t8#0,t9#0] relpos64_head=[66.0000,0.0000|6.0000,0.0000|20.0000,0.0000|34.0000,0.0000|48.0000,0.0000|62.0000,0.0000|76.0000,0.0000|10.0000,0.0000]'),
    ('r95b_order_layers_k0', 'r95b_order.gd', ["--arm=layers", "--k=0"], 0,
     'PASS r95b_order layers k=0 add_order=[a,b,c,d,e] pt0_ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,4,1,2,0;t8:3,4,0,1,2;t16:1,2,3,4,0;t32:2,3,4,0,1] pt0_distinct=7 pt0_vec=[c#0,d#0,e#0,a#0,b#0] pt0_relpos=[16.0000,0.0000|24.0000,0.0000|32.0000,0.0000|0.0000,0.0000|8.0000,0.0000] pt0_t2_vec=[e#0,a#0,c#0,d#0,b#0] pt0_t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] pt0_t2_eq_sh=true ptL_vec=[c#0,d#0,e#0,a#0,b#0] sh_vec=[c#0,d#0,e#0,a#0,b#0] sh_relpos=[16.0000,0.0000|24.0000,0.0000|32.0000,0.0000|0.0000,0.0000|8.0000,0.0000] pt_eq_sh=true sh_len=5'),
    ('r95b_order_layers_k1', 'r95b_order.gd', ["--arm=layers", "--k=1"], 0,
     'PASS r95b_order layers k=1 add_order=[a,b,c,d,e] pt0_ladder=[t2:4,0,2,3,1;t3:4,0,1,3,2;t4:4,0,1,2,3;t6:3,0,1,2,4;t8:3,0,2,4,1;t16:1,4,0,2,3;t32:4,0,2,3,1] pt0_distinct=6 pt0_vec=[e#0,a#0,c#0,d#0,b#0] pt0_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] pt0_t2_vec=[e#0,a#0,c#0,d#0,b#0] pt0_t2_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|8.0000,0.0000] pt0_t2_eq_sh=false ptL_vec=[clb#0] sh_vec=[e#0,a#0,c#0,d#0,clb#0,b#0] sh_relpos=[32.0000,0.0000|0.0000,0.0000|16.0000,0.0000|24.0000,0.0000|16.0000,0.0000|8.0000,0.0000] pt_eq_sh=false sh_len=6'),
    ('r95b_order_rigid', 'r95b_order.gd', ["--arm=rigid"], 0,
     'PASS r95b_order rigid add_order=[a,b,c,d,e] ladder=[t1:2;t2:2;t3:2;t5:2;t10:2] distinct_ticks=1 t10_relpos=[15.9999,14.8732]'),
    # --- r96 block: PackedScene/ResourceSaver/ResourceLoader round-trip
    # lattice -----------------------------------------------------------
    # Fixture scene_io_lattice.gd is an r96-author FOLD of the frozen
    # r96-scout probe (corpus/live/r96-scout/probes/scene_io_lattice.gd
    # sha256 2eded40b74971c4f…, 805 lines); fixture sha256 recorded in
    # reports/round-96/r96-author.md. Folds (all boundary-driven):
    #   * pack_basic: size_in_190_200 -> size_in_176_194. Save size is
    #     174 fixed bytes + digit-width of the two minted node unique_ids;
    #     ids are bounded < 2^31 (1-10 digits) so [176,194] is the provable
    #     support while the frozen bound flipped once at 189 in the
    #     boundary's size scans (documented rare-flake class).
    #   * extres: the frozen id_stable_across_saves / id_stable_same_obj_
    #     resave booleans encoded the scout's refuted "ext ids are random
    #     per save" model. r96-boundary measured ext ids as a pure function
    #     of (output path, slot): keys renamed id_differs_across_paths /
    #     id_differs_other_path (both now true — the measured physical
    #     fact, re-signed under the boundary law) and a same-path resave
    #     block adds save_same_path / id_stable_same_path /
    #     same_path_bytes_identical (all true).
    #   * L4 law comment corrected to the boundary id law (comment-only).
    # Boundary probes land byte-identical: r96b_cache.gd (deep cache-mode
    # lattice + threaded load), r96b_id.gd (path+slot id law incl. sticky
    # resave hazard), r96b_seq.gd (pinned-bundle byte determinism incl.
    # ext resources — the headline), r96b_var.gd (unique_id-only variance
    # on a feature-rich scene, persistent conns/groups, meta order, no
    # public id lever, <2^31 gate), r96b_phase.gd (physics/process-frame
    # phase attacks at 5 tick offsets each — no phase coordinate),
    # r96b_seed.gd (loaded-resource id sequences reproduce across
    # processes). r96b_size.gd deliberately NOT landed — its size-law
    # conclusion is the pack_basic fold above.
    # Deliberately NOT authored (boundary-rejected / measured-unstable):
    #   * r96b_id_finger0 — first-process draws of Resource.new() vary
    #     across processes (5/5 distinct; the generator is not
    #     process-global for pathless base-class instances).
    #   * r96b_id_seqAA3 / subextra1 — strict subsets of seqA2/subextra3.
    #   * r96b_var_idstat min=/max= tokens — process-random minted ids
    #     (5/5 distinct); only n=200 distinct=200 (collision-free
    #     breadth) and the <2^31/pinned-drop gates are pinned.
    #   * r96b_seed fresh2 — two fresh gradients' sequences were equal
    #     in-run but the claim adds nothing over seedcheck.
    #   * any raw unique_id/sub_id/ext_id literal under random minting —
    #     ids are sequence/path dependent (boundary: never assert raw
    #     unless pinned or masked); every pinned literal here is
    #     path-derived and reproduced identically in proj_alt receipts.
    # 60 rows: 13 scout-surviving cells + 47 boundary cells. Every arm
    # byte-stable across 114 scout + 5-family/8-rep boundary receipts
    # (canonical lines identical in all retained receipts) and this
    # seat's fresh-process smoke pass on the fixture bytes.
    # Rows inserted ahead of the crash/descendant tail —
    # descendant_pipe_detached_control's sleep-8 gap stays adjacent to
    # the meta probes.
    ('r96_scene_io_census', 'scene_io_lattice.gd', ['--arm=census'], 0,
     'PASS scene_io_lattice census ps_methods=_get_bundled_scene,_set_bundled_scene,can_instantiate,get_state,instantiate,pack ps_props=bundled ps_consts=GEN_EDIT_STATE_DISABLED=0,GEN_EDIT_STATE_INSTANCE=1,GEN_EDIT_STATE_MAIN=2,GEN_EDIT_STATE_MAIN_INHERITED=3 saver_methods=add_resource_format_saver,get_recognized_extensions,get_resource_id_for_path,remove_resource_format_saver,save,set_uid saver_flags=FLAG_NONE=0,FLAG_RELATIVE_PATHS=1,FLAG_BUNDLE_RESOURCES=2,FLAG_CHANGE_PATH=4,FLAG_OMIT_EDITOR_PROPERTIES=8,FLAG_SAVE_BIG_ENDIAN=16,FLAG_COMPRESS=32,FLAG_REPLACE_SUBRESOURCE_PATHS=64 loader_methods=add_resource_format_loader,exists,get_cached_ref,get_dependencies,get_recognized_extensions_for_type,get_resource_uid,has_cached,list_directory,load,load_threaded_get,load_threaded_get_status,load_threaded_request,remove_resource_format_loader,set_abort_on_missing_resources loader_modes=THREAD_LOAD_INVALID_RESOURCE=0,THREAD_LOAD_IN_PROGRESS=1,THREAD_LOAD_FAILED=2,THREAD_LOAD_LOADED=3,CACHE_MODE_IGNORE=0,CACHE_MODE_REUSE=1,CACHE_MODE_REPLACE=2,CACHE_MODE_IGNORE_DEEP=3,CACHE_MODE_REPLACE_DEEP=4 uid_methods=add_id,create_id,create_id_for_path,ensure_path,get_id_path,has_id,id_to_text,path_to_uid,remove_id,set_id,text_to_id,uid_to_path uid_consts=INVALID_ID=-1 res_props=Resource,resource_local_to_scene,resource_name,resource_path,resource_scene_unique_id ss_methods=get_base_scene_state,get_connection_binds,get_connection_count,get_connection_flags,get_connection_method,get_connection_signal,get_connection_source,get_connection_target,get_connection_unbinds,get_node_count,get_node_groups,get_node_index,get_node_instance,get_node_instance_placeholder,get_node_name,get_node_owner_path,get_node_path,get_node_property_count,get_node_property_name,get_node_property_value,get_node_type,get_path,is_node_instance_placeholder empty_can_instantiate=false pack_is_instance_method=true'),
    ('r96_scene_io_pack_basic', 'scene_io_lattice.gd', ['--arm=pack_basic'], 0,
     'PASS scene_io_lattice pack_basic save=OK(0) can=true nodes=2 names=Root,Child pcounts=1,1 types=Node2D,Node2D state_path_empty=true header=[gd_scene format=3] has_uid=false has_unique_id=true size_in_176_194=true sha_len=64 inst_name=Root inst_pos=(10.0, 20.0) kids=1 kid_name=Child kid_pos=(3.0, 4.0) kid_owner_root=true scene_file_is_path=true back_path_is_path=true resave=OK(0) resave_same_in_process=true load_cached_identity=true'),
    ('r96_scene_io_ownership', 'scene_io_lattice.gd', ['--arm=ownership'], 0,
     'PASS scene_io_lattice ownership save=OK(0) packed_nodes=2 packed_names=Root,Owned orphan_dropped=true deep_dropped=true bad_owner_refused=true self_owner_refused=true cleared_owner_null=true child_of_tree_nodes=1 unparented_nodes=2 inst_child_owner_root=true owner_paths=Root:.:,Owned:./Owned:.'),
    ('r96_scene_io_formats', 'scene_io_lattice.gd', ['--arm=formats'], 0,
     'PASS scene_io_lattice formats grad_tres=OK(0) size=101 sha=94ca8c1804aa166ebfce76ff354bc9adbcf5fb0ea108436dedf560fd7ba2356a header=[gd_resource type="Gradient" format=3] colors_match=true grad_res=OK(0) size=354 sha=6f13538bfb452af9193d4ba487ccdf755afda3db8d4f5034c3f149c703e3ef76 magic=RSRC colors_match=true text_eq_bin=false grad_refused=tscn=File unrecognized(15),tres.bak=File unrecognized(15),resx=File unrecognized(15),json=File unrecognized(15) refused_files_absent=true scene_scn=OK(0) scene_res=OK(0) scn_eq_res=true both_reload=true scene_tres_refused=File unrecognized(15)'),
    ('r96_scene_io_det', 'scene_io_lattice.gd', ['--arm=det'], 0,
     'PASS scene_io_lattice det save=OK(0) same_obj_resave=OK(0) unpinned_sha_len=64 two_builds_same=false subid_minted=true subid_settable=true bundle_keys=conn_count,conns,editable_instances,id_paths,names,node_count,node_ids,node_paths,nodes,variants,version bundle_version=3 node_ids_len=2 pinned_save=OK(0) pinned_save2=OK(0) pinned_sha=a9041c7939a77470f126e51458f7bb14e9a5b1a36fba46bbcbf5c8a572b84fb9 two_pinned_builds_same=true pinned_unique_ids=true instantiate_ok=true'),
    ('r96_scene_io_uid', 'scene_io_lattice.gd', ['--arm=uid'], 0,
     'PASS scene_io_lattice uid create_id_text_prefix=true create_id_unregistered=true get_id_path_unknown_empty=true roundtrip=103876737118377468 roundtrip_text=uid://bqk3m5n7qar1 invalid_text=-1 invalid_text_back=uid://<invalid> invalid_id=-1 tres_save=OK(0) header_has_uid=false saver_id_before=-1 loader_uid_before=-1 loader_uid_after_add=4242 saver_id_after_add=-1 scene_save=OK(0) ext_line_has_uid=false header_has_uid=false any_uid_token=false'),
    ('r96_scene_io_takeover', 'scene_io_lattice.gd', ['--arm=takeover'], 0,
     'PASS scene_io_lattice takeover save=OK(0) path_after_save_empty=true load_after_save_is_new=true b_wins=true b_path_is_p=true a_path_empty=true c_wins=true b_displaced=true disk_sha=ad113a5cb9144c27c0461d59b0c4164804f769acb97990f688b978e3c3c98716 disk_unchanged=true exists=true exists_missing=true has_cached=true get_cached_ref=true deps_empty=true'),
    ('r96_scene_io_cache', 'scene_io_lattice.gd', ['--arm=cache'], 0,
     'PASS scene_io_lattice cache save=OK(0) default_identity=true ignore_distinct=true ignore_path_kept=true ignore_two_distinct=true external_write=OK(0) stale_after_write=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] repl_same_object=true repl_refreshed=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] after_repl_identity=true ignore_refreshed=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] reuse_is_repl=true cached_now_refreshed=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] exists_dir=false exists_empty=false'),
    ('r96_scene_io_subres', 'scene_io_lattice.gd', ['--arm=subres'], 0,
     'PASS scene_io_lattice subres save=OK(0) subid=Gradient_643c0 subid_present=true shared_across_instances=true shared_with_source=true mutation_leaks=true local_save=OK(0) flag_in_file=true local_shared=false local_leak=false nest_save=OK(0) nested_reuses_subid=true dup_shallow_distinct=true dup_deep_distinct=true'),
    ('r96_scene_io_extres', 'scene_io_lattice.gd', ['--arm=extres'], 0,
     'PASS scene_io_lattice extres ext_save=OK(0) save=OK(0) save2=OK(0) save_same_obj=OK(0) ext_line=true id_prefix=true id_differs_across_paths=true id_differs_other_path=true save_same_path=OK(0) id_stable_same_path=true same_path_bytes_identical=true gen_id_len=5 inst_is_loaded=true two_instances_share=true inst_path_is_ext=true deps=["user://r96/ext.tres"] bundle_flag=OK(0) inlined_as_subresource=true no_ext_line=true nopath_save=OK(0) serialized_as_subresource=true no_ext_line=true relative_flag=OK(0) keeps_path=true'),
    ('r96_scene_io_editstate', 'scene_io_lattice.gd', ['--arm=editstate'], 0,
     'PASS scene_io_lattice editstate save=OK(0) states=s0[kids=1,owner=true,name=EditRoot,ph=false,ed=false]|s1[kids=1,owner=true,name=EditRoot,ph=false,ed=false]|s2[kids=1,owner=true,name=EditRoot,ph=false,ed=false]|s3[kids=1,owner=true,name=EditRoot,ph=false,ed=false] scene_file_is_path=true part_of_edited=false editable_readback=true placeholder_readback=true unique_name_before=false unique_name_after=true root_placeholder=false'),
    ('r96_scene_io_refuse', 'scene_io_lattice.gd', ['--arm=refuse'], 0,
     "PASS scene_io_lattice refuse save_missing_dir=Can't open(19) no_file=true save_null=Invalid parameter(31) save_empty_path=Invalid parameter(31) save_no_ext=File unrecognized(15) save_dir=File unrecognized(15) load_missing_null=true load_dir_null=true load_empty_null=true pack_null=Invalid parameter(31) empty_can_instantiate=false empty_instantiate_null=true relative_save=OK(0) relative_file_created=true relative_in_project_dir=true deleted=true set_path_collision_refused=true"),
    ('r96_scene_io_edges', 'scene_io_lattice.gd', ['--arm=edges'], 0,
     'PASS scene_io_lattice edges save=OK(0) inst_names=NameRoot,NameRoot added_names=NameRoot,@Node2D@2 auto_renamed=true state_path_is_p=true duplicate_cls=PackedScene packed_twice_same_object=false groups_save=OK(0) state_groups=["grp_a", "grp_b"] inst_groups=grp_a,grp_b owner_paths=ORoot:.:,OChild:./OChild:.,OGrand:./OChild/OGrand:.'),
    # r96-boundary id law — ext/sub ids are f(output path, slot):
    # reproduced byte-identically across processes at fixed paths.
    ('r96b_id_seqA2', 'r96b_id.gd', ['--arm=seqA2'], 0,
     'PASS r96b_id seqA2 seq=a:1_vwxho/OK a:1_vwxho/OK'),
    ('r96b_id_seqAB2', 'r96b_id.gd', ['--arm=seqAB2'], 0,
     'PASS r96b_id seqAB2 seq=a:1_vwxho/OK b:1_0187o/OK a:1_vwxho/OK'),
    ('r96b_id_seq2obj', 'r96b_id.gd', ['--arm=seq2obj'], 0,
     'PASS r96b_id seq2obj obj1=1_vwxho obj2=1_vwxho'),
    ('r96b_id_twoext', 'r96b_id.gd', ['--arm=twoext'], 0,
     'PASS r96b_id twoext seq=a:1_c7i3r,2_ku7em b:1_cre6b,2_kmhwg a:1_c7i3r,2_ku7em'),
    ('r96b_id_extother', 'r96b_id.gd', ['--arm=extother'], 0,
     'PASS r96b_id extother id=1_vwxho'),
    ('r96b_id_extshift', 'r96b_id.gd', ['--arm=extshift'], 0,
     'PASS r96b_id extshift pre=dg01n,6ddvb,3nsch ext_id=1_vwxho'),
    ('r96b_id_mint_two', 'r96b_id.gd', ['--arm=mint_two'], 0,
     'PASS r96b_id mint_two seq=pa:Gradient_elxub sp:Gradient_xlqlr pa:Gradient_elxub sp:Gradient_xlqlr'),
    ('r96b_id_subsamepath', 'r96b_id.gd', ['--arm=subsamepath'], 0,
     'PASS r96b_id subsamepath seq=m0:Gradient_xlqlr m1:Gradient_xlqlr'),
    ('r96b_id_subcontent', 'r96b_id.gd', ['--arm=subcontent'], 0,
     'PASS r96b_id subcontent id=Gradient_xlqlr'),
    ('r96b_id_subextra0', 'r96b_id.gd', ['--arm=subextra0'], 0,
     'PASS r96b_id subextra0 extra=0 id=Gradient_xlqlr'),
    ('r96b_id_subextra3', 'r96b_id.gd', ['--arm=subextra3'], 0,
     'PASS r96b_id subextra3 extra=3 id=Gradient_xlqlr'),
    ('r96b_id_subsame', 'r96b_id.gd', ['--arm=subsame'], 0,
     'PASS r96b_id subsame id1=Gradient_elxub id2=Gradient_elxub'),
    ('r96b_id_subpath', 'r96b_id.gd', ['--arm=subpath'], 0,
     'PASS r96b_id subpath seq=a:Gradient_elxub b:Gradient_elxub a:Gradient_elxub'),
    ('r96b_id_fingerB', 'r96b_id.gd', ['--arm=fingerB'], 0,
     'PASS r96b_id fingerB vals=dg01n,6ddvb,3nsch,07j4t,2c3ee,pghoq,dqro8,lahlw'),
    # r96-boundary determinism: pinning bundle node_ids +
    # resource_scene_unique_id makes even ext-resource scenes
    # byte-identical across processes (minimal/extpin pin sha_raw; the
    # BUNDLE flag inlines deps into sub_resources).
    ('r96b_seq_extseq', 'r96b_seq.gd', ['--arm=extseq'], 0,
     'PASS r96b_seq extseq save=OK save2=OK save_same_obj=OK ext_ids1=1_efiak ext_ids2=1_f4hst ext_ids1b=1_xfevf sha_uonly=6213ed4980248283a13a4259482c5790a3878fdf75f3698f385f045532aa36fd sha_usub=6213ed4980248283a13a4259482c5790a3878fdf75f3698f385f045532aa36fd'),
    ('r96b_seq_extpin', 'r96b_seq.gd', ['--arm=extpin'], 0,
     'PASS r96b_seq extpin save=OK save2=OK ext_ids1=1_fukgi ext_ids2=1_fa8qf sha_raw=a6fa9a9e0c4661fa8d319ac93e8db6b8c17e71ce3d8d51eb394a9381cb0ee88a sha_uonly=1f5ea37c55787e43418bb5157fae62fc99f97dbaf196183d31fc7108340a421e two_builds_same_text=false unique_pinned=true'),
    ('r96b_seq_extbundle', 'r96b_seq.gd', ['--arm=extbundle'], 0,
     'PASS r96b_seq extbundle save=OK ids1=Gradient_jbi7l sha_raw=6074989d6503c1a72c59de380883b003972b7f103fc4e45ea1f1ef202583e156 sha_uonly=84cd406dcb3b6479b4a77d14b3199338616ee778c8d9a10cecd019deaf9aff26 sha_u_sub=aa74d540a72391153eca41ca9be36279c328c40cb8c1c5717eb7a88c67457ce5 ext_line=false sub_line=true unique_pinned=true'),
    ('r96b_seq_extgen', 'r96b_seq.gd', ['--arm=extgen'], 0,
     'PASS r96b_seq extgen seq=r0s0=1_6o14o/OK g0s0=ies2y r0s1=1_dwhle/OK g0s1=nb1tx r1s0=1_ii61a/OK g1s0=sxvai r1s1=1_xjtd8/OK g1s1=dsgfn'),
    ('r96b_seq_minimal', 'r96b_seq.gd', ['--arm=minimal'], 0,
     'PASS r96b_seq minimal save=OK ids=1_k3tv1,Gradient_gtys7 sha_raw=c16f3241a476f4de1484bf07fea7c6a7dc9f5ef8c3408f18eed5f95c6361e0b9 sha_uonly=27eead3cdb1ecec7b8d2ddbe70f430e8ff95e8f013b12a6dd748976944c61de1'),
    # r96-boundary deep cache lattice: shallow REPLACE/IGNORE refresh only
    # the top resource (deps stay stale); REPLACE_DEEP refreshes deps
    # in-place (identity kept); IGNORE_DEEP loads the graph fresh
    # (old cache objects untouched); threaded load is deterministic.
    ('r96b_cache_deep_reuse', 'r96b_cache.gd', ['--arm=deep_reuse'], 0,
     'PASS r96b_cache deep_reuse mode=reuse save_dep=OK save_sc=OK col_before=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_same=true ch_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] ch_same=true dep_obj_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] cached_dep_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_path_kept=true'),
    ('r96b_cache_deep_replace', 'r96b_cache.gd', ['--arm=deep_replace'], 0,
     'PASS r96b_cache deep_replace mode=replace save_dep=OK save_sc=OK col_before=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_same=true ch_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] ch_same=true dep_obj_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] cached_dep_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_path_kept=true'),
    ('r96b_cache_deep_ignore', 'r96b_cache.gd', ['--arm=deep_ignore'], 0,
     'PASS r96b_cache deep_ignore mode=ignore save_dep=OK save_sc=OK col_before=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_same=false ch_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] ch_same=true dep_obj_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] cached_dep_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_path_kept=true'),
    ('r96b_cache_deep_repl_deep', 'r96b_cache.gd', ['--arm=deep_repl_deep'], 0,
     'PASS r96b_cache deep_replace_deep mode=replace_deep save_dep=OK save_sc=OK col_before=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_same=true ch_col=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] ch_same=true dep_obj_col=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] cached_dep_col=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_path_kept=true'),
    ('r96b_cache_deep_ign_deep', 'r96b_cache.gd', ['--arm=deep_ign_deep'], 0,
     'PASS r96b_cache deep_ignore_deep mode=ignore_deep save_dep=OK save_sc=OK col_before=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_same=false ch_col=[(0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] ch_same=false dep_obj_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] cached_dep_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] sc_path_kept=true'),
    ('r96b_cache_ignoredeep', 'r96b_cache.gd', ['--arm=ignoredeep'], 0,
     'PASS r96b_cache ignoredeep fresh_sc_same_cached=false fresh_sc_path_kept=true fresh_child_same_cached_dep=false after_sc_same_cached=true fresh_dep_same_cached=true'),
    ('r96b_cache_repl_uncached', 'r96b_cache.gd', ['--arm=repl_uncached'], 0,
     'PASS r96b_cache repl_uncached first_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] second_same=true cached_after=true cached_same=true'),
    ('r96b_cache_reuse_delete', 'r96b_cache.gd', ['--arm=reuse_delete'], 0,
     'PASS r96b_cache reuse_delete del=true after_delete_same=true after_delete_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] reuse_same=true exists=true'),
    ('r96b_cache_reuse_delay', 'r96b_cache.gd', ['--arm=reuse_delay'], 0,
     'PASS r96b_cache reuse_delay immediate_same=true immediate_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] after2500ms_same=true after2500ms_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] reuse_same=true'),
    ('r96b_cache_threaded', 'r96b_cache.gd', ['--arm=threaded'], 0,
     'PASS r96b_cache threaded req=OK status=3 got_col=[(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0, 1.0)] cached_same_as_got=true status_after=0 has_cached=true'),
    # r96-boundary variance surface: on a feature-rich 10-node scene
    # (shared/nested/local sub-resources, 6 persistent connections,
    # scrambled persistent groups, 8 metadata keys, fractional floats)
    # unique_id stays the ONLY byte variance; pinning node_ids +
    # resource_scene_unique_id pins sha_raw across processes.
    # Connections serialize sorted-canonical; persistent groups serialize
    # sorted; metadata keeps insertion order; there is no public Node
    # unique_id lever; minted ids are bounded < 2^31 and pinned ids
    # >= 2^31 are silently dropped on save.
    ('r96b_var_rich', 'r96b_var.gd', ['--arm=rich'], 0,
     'PASS r96b_var rich save=OK nodes=10 sha_uonly=3c89984fd6bde63d749b3de761f9e19a944b499b193e6fb7c88fb288be6be8c4 sha_u_sub=9d1963b2c10905ff611aabe6f796e50bb1d8eb7bbefbbabb7f97041658d526de pinned_save=OK pinned_nodes=10 pinned_sha=e6675739cc972b2a8c7f414b21dd5e8e043ebdb61dc2e28270c2733b005afa94 pinned_uonly=c060161cbdd0c48a2c1283aabdf5c1c6479f288c4766f1cac3c6a1c37349fb03'),
    ('r96b_var_conn', 'r96b_var.gd', ['--arm=conn'], 0,
     'PASS r96b_var conn save=OK nconn=6 conns=[connection signal="renamed" from="N0" to="N2" method="get_path"]|[connection signal="renamed" from="N0" to="N5" method="get_path"]|[connection signal="renamed" from="N1" to="N4" method="get_path"]|[connection signal="renamed" from="N2" to="N0" method="get_path"]|[connection signal="renamed" from="N3" to="N1" method="get_path"]|[connection signal="renamed" from="N4" to="N3" method="get_path"] sha_uonly=a231c0644085647052f31c32431e9f5326afb086a24a1a2ebb459173c54a7954'),
    ('r96b_var_groups', 'r96b_var.gd', ['--arm=groups'], 0,
     'PASS r96b_var groups save=OK lines=[node name="GA" type="Node2D" parent="." unique_id=# groups=["alpha", "bravo", "mike", "zulu"]]|[node name="GB" type="Node2D" parent="." unique_id=# groups=["mike", "zulu"]] sha_uonly=12459b60839f480a01bb5e00826c88dffb87dbf5f07d2c4844171c21f52abb81'),
    ('r96b_var_meta', 'r96b_var.gd', ['--arm=meta'], 0,
     'PASS r96b_var meta save=OK lines=metadata/k08 = 0|metadata/k03 = 1000|metadata/k11 = 2000|metadata/k01 = 3000|metadata/k07 = 4000|metadata/k02 = 5000|metadata/k10 = 6000|metadata/k05 = 7000 sha_uonly=998695a4af9a438fa41f514491c81616e488d29aae5398cbbab9065da732af58'),
    ('r96b_var_lever', 'r96b_var.gd', ['--arm=lever'], 0,
     'PASS r96b_var lever has_get=false has_set=false node_methods=set_scene_file_path,get_scene_file_path,set_scene_instance_load_placeholder,get_scene_instance_load_placeholder,set_unique_name_in_owner,is_unique_name_in_owner readback= text_has_setter_value=n/a'),
    ('r96b_var_idstat_breadth', 'r96b_var.gd', ['--arm=idstat'], 0,
     'PASS r96b_var idstat n=200 distinct=200'),
    ('r96b_var_idstat_u31_gate', 'r96b_var.gd', ['--arm=idstat'], 0,
     'gt2p31=0 pin_save=OK pin_found=true,true,false,false,false instantiate_ok=true'),
    # r96-boundary phase attacks: minted ids, ext ids, and pinned-bundle
    # saves carry no physics/process-frame phase coordinate — identical
    # payloads at k={0,1,2,5,30} ticks in both schedulers.
    ('r96b_phase_ph0', 'r96b_phase.gd', ['--arm=ph0'], 0,
     'PASS r96b_phase ph0 k=0 use_process=false ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_ph1', 'r96b_phase.gd', ['--arm=ph1'], 0,
     'PASS r96b_phase ph1 k=1 use_process=false ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_ph2', 'r96b_phase.gd', ['--arm=ph2'], 0,
     'PASS r96b_phase ph2 k=2 use_process=false ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_ph5', 'r96b_phase.gd', ['--arm=ph5'], 0,
     'PASS r96b_phase ph5 k=5 use_process=false ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_ph30', 'r96b_phase.gd', ['--arm=ph30'], 0,
     'PASS r96b_phase ph30 k=30 use_process=false ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_pph0', 'r96b_phase.gd', ['--arm=pph0'], 0,
     'PASS r96b_phase pph0 k=0 use_process=true ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_pph1', 'r96b_phase.gd', ['--arm=pph1'], 0,
     'PASS r96b_phase pph1 k=1 use_process=true ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_pph2', 'r96b_phase.gd', ['--arm=pph2'], 0,
     'PASS r96b_phase pph2 k=2 use_process=true ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_pph5', 'r96b_phase.gd', ['--arm=pph5'], 0,
     'PASS r96b_phase pph5 k=5 use_process=true ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    ('r96b_phase_pph30', 'r96b_phase.gd', ['--arm=pph30'], 0,
     'PASS r96b_phase pph30 k=30 use_process=true ext_id=1_qotou sub_id=Gradient_doj0s gen1=jk34a save=OK save2=OK save3=OK uonly_sha=4a3df3fd08a2ffc5f78534aceb67ad41d6cc4eb1da80be1a5e6633d66f8692fe pinned_sha=c264d6ebfdd2f071841f65a79f759ff31128f0527948fdf53060923b318b001a pinned_uonly=4d032ff636f1015fcb07f89fdf958e1a8d8f346394b8f6c57e106ee4cdc41201'),
    # r96-boundary seed check: a loaded resource's
    # generate_scene_unique_id() sequence reproduces byte-identically
    # across processes (path-seeded); A==B holds because REUSE returns
    # the same cached object (B continues A's sequence) — paths C and
    # fresh D differ.
    ('r96b_seed_seedcheck', 'r96b_seed.gd', ['--arm=seedcheck'], 0,
     'PASS r96b_seed seedcheck A=aymj7,7o2mc,7hw4g,ipe4k B=1q5w0,cfyh7,d1oyj,rjvfj C=rl1nt,ewl6n,ch4ud,r4oop D=8od4a,nuoth,pm58n,vab63 A_eq_B=false A_eq_C=false A_eq_D=false'),
    # r100 author — Viewport/Control GUI input routing + pointer-gesture
    # lattice, and the boundary's corrected mechanisms. 25 rows:
    #   14 scout cells (r100_gui.gd — BYTE-COPY of the frozen r100-scout
    #      probe, sha256 dd826f6e7b74ba62fcfd175ab7a1cf0c40fd9712de4b33a18554930cf6dad073,
    #      every cell byte-identical over 6 canonical + 2 loadtest reps)
    #   11 boundary rows (r100b_phase.gd sha256 49298e6cc18c4e0de627105b9d95ff28ed2ccfa52bb1cc2da364b76d5430d4b7
    #      — 8 arms; r100b_emul.gd sha256 31087e7821eb4d2d5cf4bd28d9e5d8ca11bd52f83057fcd41889ecfecdbd4960
    #      — 1 arm; r100b_seq.gd sha256 4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd
    #      — 2 variants) — all BYTE-COPYs of the frozen r100-boundary probes,
    #      no fixture folds; every boundary fold lands row-side here.
    #
    # r100-boundary verdicts applied — the encoded law is the surviving one:
    #   * CONFIRMED byte-identical in 7 launch modes (quiet, 16-hog load,
    #     --fixed-fps 30/60/120/1, threaded 2D physics): routing matrix +
    #     set_input_as_handled, push_input-is-a-scene-tree-injection (incl.
    #     synchronous hover), event.position control-locality vs the
    #     cursor-derived helpers, the hover-clip/button-routing asymmetry,
    #     drop-target = hover-picked, touch positional/tracked + both
    #     emulation directions, SubViewport input isolation + private
    #     cursor, warp/OS-cursor inertness, focus-owned key delivery, and
    #     the headless-null render surface. No envelope/mode split needed.
    #   * REFUTED as worded — "drag start = accumulated |relative| > 10":
    #     the law is |SUM of relative| > 10 on a motion whose own
    #     button_mask carries LEFT (dp_sign_same: relative +6 then -6, net
    #     displacement 0, sum-of-absolutes 12 -> NO drag; dp_rel_only:
    #     relative 30 with the event's own position unchanged -> drag;
    #     dp_pos_only: position 40 with relative 0 -> no drag). The scout's
    #     d7 row is consistent with both models; dragphase is the
    #     separating sign test.
    #   * REFUTED — "parse_input_event moves the cursor": the write is
    #     FLUSH-GATED (cursorphase: mm_imm=(0.0, 0.0) at the call,
    #     mm_flush=(20.0, 20.0) after Input.flush_buffered_events(); same
    #     for the button state held 0 -> 1), and the implicit input flush
    #     runs BEFORE the process_frame signal (flushpos sig@1=(20.0, 20.0)),
    #     so the scout's post-await cursor observable survives unchanged —
    #     only the mechanism statement was wrong.
    #   * NEW mechanisms: delivery order is _input then _gui_input (orderin),
    #     so a _gui_input-side set_input_as_handled cannot suppress the
    #     _input copy; parse-path motions COALESCE at the flush (one event,
    #     summed relative, last position) while push-path events stay 1:1
    #     (coalesce); the engine never computes double_click for synthetic
    #     events (dblclick); hover is synchronous with push_input
    #     (hoverphase); get_last_mouse_velocity stays (0.0, 0.0) at every
    #     sampled phase on both paths (velphase — the scout's do-not-pin
    #     warning was about the warp path, which no row prints).
    #   * NEW HAZARD — the cells are single-cell-per-process ONLY: with tree
    #     cleanup the leaked viewport cursor + emulated mouse-button state
    #     still diverge (seq_clean 10/14; first divergence the cursor cell's
    #     c0=(30.0, 14.0), pinned here); without cleanup the tree leftovers
    #     dominate (seq_noclean 5/14; first divergence hover h0=P, pinned
    #     here). execute() launches one fresh process per case, so the rows
    #     are safe — any future batched probe must reset both states.
    # All 25 signatures are full PASS lines verified fresh-process x3 in a
    # scratch replicating this harness's staging, classified with the
    # production clause on merged stdout+stderr: 75/75 accepts, 0
    # rejections, 0 unstable cells. Rows inserted ahead of the
    # crash/descendant tail — descendant_pipe_detached_control's sleep-8 gap
    # stays adjacent to the meta probes.
    ('r100_gui_census', 'r100_gui.gd', ['--arm=census'], 0,
     'PASS r100_gui census dv=headless vpsize=(64.0, 64.0) final=(1.0000,0.0000;0.0000,1.0000;0.0000,0.0000) mf_ctrl=0 mf_label=2 mf_button=0 mf_panel=0 mf_container=1 focus_mode_ctrl=0 vpmethods=[push_input=1|push_unhandled_input=1|gui_get_focus_owner=1|gui_get_hovered_control=1|gui_is_dragging=1|gui_get_drag_data=1|gui_release_focus=1|set_input_as_handled=1|is_input_handled=1|get_mouse_position=1|warp_mouse=1|get_final_transform=1] ctrlmethods=[force_drag=1|accept_event=1|grab_focus=1|has_focus=1|release_focus=1|get_local_mouse_position=1|set_drag_preview=1] inputmethods=[warp_mouse=1|get_mouse_position=0|set_emulate_mouse_from_touch=1|is_emulating_mouse_from_touch=1|set_emulate_touch_from_mouse=1|is_emulating_touch_from_mouse=1|get_last_mouse_velocity=1|get_last_mouse_screen_velocity=1|parse_input_event=1|flush_buffered_events=1|is_mouse_button_pressed=1] emul_mouse=1 emul_touch=0 mbprops=[alt_pressed|button_index|button_mask|canceled|ctrl_pressed|device|double_click|factor|global_position|meta_pressed|position|pressed|resource_local_to_scene|resource_name|script|shift_pressed|window_id] mmprops=[alt_pressed|button_mask|ctrl_pressed|device|global_position|meta_pressed|pen_inverted|position|pressure|relative|resource_local_to_scene|resource_name|screen_relative|screen_velocity|script|shift_pressed|tilt|velocity|window_id] stprops=[canceled|device|double_tap|index|position|pressed|resource_local_to_scene|resource_name|script|window_id] sdprops=[device|index|pen_inverted|position|pressure|relative|resource_local_to_scene|resource_name|screen_relative|screen_velocity|script|tilt|velocity|window_id]'),
    ('r100_gui_routing', 'r100_gui.gd', ['--arm=routing'], 0,
     'PASS r100_gui routing s1_cc[[C:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|C:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]]- s2_ci[-][P:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s3_cp[[C:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|C:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]][P:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s4_ch[[C:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|C:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]]- s5_ci_pp[-][P:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s6_ii[-]- s7_inparent[-][P:mb(b=1,p=1,dc=0,bm=0,pos=24.0,24.0,gpos=24.0,24.0)|P:mb(b=1,p=0,dc=0,bm=0,pos=24.0,24.0,gpos=24.0,24.0)] s8_out[-]- s9_rb[-][P:mb(b=2,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] s10_input_state held_push=0 cursor=(0.0, 0.0)'),
    ('r100_gui_hover', 'r100_gui.gd', ['--arm=hover'], 0,
     'PASS r100_gui hover h0=null h1=A ev=[A_in] h2=A ev=[A_in] h3=B ev=[A_in|A_out|B_in] h4=null ev=[A_in|A_out|B_in|B_out] h5=C ev=[A_in|A_out|B_in|B_out] h6_press=A ev=[A_in|A_out|B_in|B_out|A_in] h7_after_release=A'),
    ('r100_gui_motion', 'r100_gui.gd', ['--arm=motion'], 0,
     'PASS r100_gui motion m1[[S:mm(bm=0,pos=10.0,10.0,gpos=10.0,10.0,rel=5.0,7.0,vel=0.0,0.0)]] m2[[S:mm(bm=0,pos=20.0,30.0,gpos=20.0,30.0,rel=10.0,20.0,vel=0.0,0.0)]] m3_dc[[S:mb(b=1,p=1,dc=1,bm=0,pos=10.0,10.0,gpos=10.0,10.0)|S:mb(b=1,p=0,dc=0,bm=0,pos=10.0,10.0,gpos=10.0,10.0)]] m4_push_input_state held=0 cursor=(0.0, 0.0) vel=(0.0, 0.0)'),
    ('r100_gui_localpos', 'r100_gui.gd', ['--arm=localpos'], 0,
     'PASS r100_gui localpos lp_push_p[-] c[[C:mb(b=1,p=1,dc=0,bm=0,pos=6.0,2.0,gpos=30.0,14.0)]] loc_c=-24.0,-12.0 lp_push_local_p[-] c[[C:mb(b=1,p=1,dc=0,bm=0,pos=6.0,2.0,gpos=30.0,14.0)]] lp_parse_p[-] c[[C:mb(b=1,p=1,dc=0,bm=0,pos=6.0,2.0,gpos=30.0,14.0)]] loc_c=6.0,2.0 gloc_c=30.0,14.0'),
    ('r100_gui_cursor', 'r100_gui.gd', ['--arm=cursor'], 0,
     'PASS r100_gui cursor c0=(0.0, 0.0) c1_push_mm=(0.0, 0.0) c2_push_mb=(0.0, 0.0) c3_parse_mb=(24.0, 24.0) c4_parse_mm=(30.0, 30.0) c5_gpos_drives=(60.0, 60.0) c6_parse_st=(44.0, 44.0) c7_push_mm2=(44.0, 44.0) c8 ds=(0, 0)'),
    ('r100_gui_clip', 'r100_gui.gd', ['--arm=clip'], 0,
     'PASS r100_gui clip cp0_vis=[P: (0.0, 0.0), S: (64.0, 64.0)] cp_hover(62.0, 4.0)=ED cp_press(62.0, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=2.0,4.0,gpos=62.0,4.0)] fa=- cp_hover(63.9, 4.0)=ED cp_press(63.9, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=3.9,4.0,gpos=63.9,4.0)] fa=- cp_hover(64.0, 4.0)=null cp_press(64.0, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=4.0,4.0,gpos=64.0,4.0)] fa=- cp_hover(64.1, 4.0)=null cp_press(64.1, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=4.1,4.0,gpos=64.1,4.0)] fa=- cp_hover(70.0, 4.0)=null cp_press(70.0, 4.0) in=- ed=[ED:mb(b=1,p=1,dc=0,bm=0,pos=10.0,4.0,gpos=70.0,4.0)] fa=- cp_hover(90.0, 4.0)=null cp_press(90.0, 4.0) in=- ed=- fa=[FA:mb(b=1,p=1,dc=0,bm=0,pos=10.0,4.0,gpos=90.0,4.0)] cp_hover200=null'),
    ('r100_gui_drag', 'r100_gui.gd', ['--arm=drag'], 0,
     'PASS r100_gui drag d1_at_threshold drag=0 calls=0 d2_over_threshold drag=1 calls=1 data=fromA at=[(8.0,8.0)] d3_over_b drag=1 a_drop=[can(fromA)] b_drop=[can(fromA)] b_get=0 d4_over_b2 b_drop=[can(fromA)|can(fromA)] d5_release drag=0 b_drop=[can(fromA)|can(fromA)|can(fromA)|drop(fromA)] d6_unmasked_motion drag=0 calls=1 d7_accum[1:0 2:1 3:1 ] calls=2 d8_no_target drag=0 a_drop=[can(fromA)|can(fromA)|can(fromA)|can(fromA)|drop(fromA)|can(fromA)|can(fromA)|drop(fromA)] b_drop=[can(fromA)|can(fromA)|can(fromA)|drop(fromA)] d9_force drag=1 data=forced calls=0 d10_force_over_d d_drop=[can(forced)] d11_force_drop drag=0 d_drop=[can(forced)|can(forced)|drop(forced)] d12_nodrop drag=0 d_drop=[can(forced)|can(forced)|drop(forced)|can(no)]'),
    ('r100_gui_touch', 'r100_gui.gd', ['--arm=touch'], 0,
     'PASS r100_gui touch t1_push_a=- b=[B:st(i=0,p=1,dt=1,pos=4.0,4.0)] t2_pushdrag_a=- b=[B:sd(i=0,pos=-12.0,4.0,rel=-16.0,0.0)] t3_emul_touch held=1 a=[A:mb(b=1,p=1,dc=0,bm=1,pos=8.0,8.0,gpos=8.0,8.0)|A:st(i=0,p=1,dt=0,pos=8.0,8.0)] b=- emul=1 t4_emul_mouse a_gui=- a_in=[A:st(i=0,p=1,dt=0,pos=20.0,4.0)|A:mb(b=1,p=1,dc=0,bm=0,pos=20.0,4.0,gpos=20.0,4.0)] emul_t=1'),
    ('r100_gui_subvp', 'r100_gui.gd', ['--arm=subvp'], 0,
     'PASS r100_gui subvp v0_local=1 size=(64, 64) cursor=(0.0, 0.0) v1_sub[[S:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]] root=- v2_hovered=S cursor_sub=(8.0, 8.0) cursor_root=(0.0, 0.0) v3_root_push_sub[-] root=[R:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)] v4_cursors sub=(8.0, 8.0) root=(0.0, 0.0) v5_local_false local=0 s2=[[S2:mb(b=1,p=1,dc=0,bm=0,pos=12.0,12.0,gpos=12.0,12.0)]] cursor=(12.0, 12.0)'),
    ('r100_gui_warp', 'r100_gui.gd', ['--arm=warp'], 0,
     'PASS r100_gui warp w0 dv=headless cursor=(0.0, 0.0) ds_mouse=(0, 0) w1 after_push cursor=(0.0, 0.0) ds_mouse=(0, 0) w2 after_input_warp cursor=(0.0, 0.0) ds_mouse=(0, 0) w3 after_vp_warp cursor=(0.0, 0.0) ds_mouse=(0, 0) w4 mode=0'),
    ('r100_gui_focus', 'r100_gui.gd', ['--arm=focus'], 0,
     'PASS r100_gui focus f0 owner=F f_focus=1 g_focus=0 f1_key gui_f=[F:key(k=65,p=1)] gui_g=- in_f=[F:key(k=65,p=1)] f2_handled gui_f=[F:key(k=65,p=1)] gui_g=- f3_regrab gui_f=- gui_g=[G:key(k=65,p=1)] owner=G f4_released gui_f=- gui_g=- owner=null'),
    ('r100_gui_render', 'r100_gui.gd', ['--arm=render'], 0,
     'PASS r100_gui render r0 tex_cls=ViewportTexture size=(64.0, 64.0) r1 img_null=1 r2 adapter= rd_null=1 r3 method=forward_plus screens=0 ssize=(0, 0) win_size=(64, 64) r4 light sh=0 filt=0 smooth=0.0 blend=0 r5 gpu_capture=[P: (0.0, 0.0), S: (0.0, 0.0)]'),
    ('r100_gui_osmeta', 'r100_gui.gd', ['--arm=osmeta'], 0,
     'PASS r100_gui osmeta Thread[e=1,m=7] Mutex[e=1,m=3] Semaphore[e=1,m=3] WorkerThreadPool[e=1,m=9] Time[e=1,m=21] os=Linux procs_gt0=1 wtp_has_thread_count=0'),
    ('r100b_phase_cursorphase', 'r100b_phase.gd', ['--arm=cursorphase'], 0,
     'PASS r100b_phase cursorphase init=(0.0, 0.0) mm_imm=(0.0, 0.0) mm_flush=(20.0, 20.0) mm_f1=(20.0, 20.0) mm_f2=(20.0, 20.0) mb_imm=(20.0, 20.0) held=0 mb_flush=(24.0, 24.0) held=1 mb_f1=(24.0, 24.0) held=1 push_imm=(24.0, 24.0) push_f1=(24.0, 24.0) gpos_imm=(24.0, 24.0) gpos_f1=(52.0, 52.0) hovered=null'),
    ('r100b_phase_hoverphase', 'r100b_phase.gd', ['--arm=hoverphase'], 0,
     'PASS r100b_phase hoverphase h0=null ev=- pf=0 h_imm=A ev=[in@0] h_f1=A ev=[in@0] h_f2=A ev=[in@0] leave_imm=null ev=[in@0|out@2] leave_f1=null ev=[in@0|out@2] press_imm=A press_f1=A rel_f1=A'),
    ('r100b_phase_dragphase', 'r100b_phase.gd', ['--arm=dragphase'], 0,
     'PASS r100b_phase dragphase dp_multiframe[1:0 2:1 3:1 ] calls=1 dp_sameframe[1:0 2:1 3:1 ] calls=2 dp_sign_same drag=0 calls=0 dp_sign_multi mid=0 after=0 calls=0 dp_net16 drag=1 calls=1 dp_10p5 drag=1 calls=1 dp_small3 drag=1 calls=1 dp_rel_only drag=1 calls=1 dp_pos_only drag=0 calls=0 dp_pos_thresh at10=0 at11=0 calls=0'),
    ('r100b_phase_coalesce', 'r100b_phase.gd', ['--arm=coalesce'], 0,
     'PASS r100b_phase coalesce p2_imm n=0 rel=(0.0, 0.0) log=- p2_flush n=1 rel=(20.0, 0.0) p2_f1 n=1 rel=(20.0, 0.0) log=[S:mm(bm=0,pos=20.0,10.0,gpos=20.0,10.0,rel=20.0,0.0,vel=0.0,0.0)] p2_sep imm n=1 p2_sep flush n=2 rel=(20.0, 0.0) log=[S:mm(bm=0,pos=30.0,10.0,gpos=30.0,10.0,rel=10.0,0.0,vel=0.0,0.0)|S:mm(bm=0,pos=40.0,10.0,gpos=40.0,10.0,rel=10.0,0.0,vel=0.0,0.0)] push2 imm n=2 rel=(20.0, 0.0) log=[S:mm(bm=0,pos=50.0,10.0,gpos=50.0,10.0,rel=10.0,0.0,vel=0.0,0.0)|S:mm(bm=0,pos=60.0,10.0,gpos=60.0,10.0,rel=10.0,0.0,vel=0.0,0.0)] push2_f1 n=2 rel=(20.0, 0.0)'),
    ('r100b_phase_velphase', 'r100b_phase.gd', ['--arm=velphase'], 0,
     'PASS r100b_phase velphase v0_none=(0.0, 0.0) screen=(0.0, 0.0) v1_push=(0.0, 0.0) v2_parse_imm=(0.0, 0.0) screen=(0.0, 0.0) v3_f1=(0.0, 0.0) v4_f2=(0.0, 0.0) v5_parse2_imm=(0.0, 0.0) v6_f1=(0.0, 0.0)'),
    ('r100b_phase_flushpos', 'r100b_phase.gd', ['--arm=flushpos'], 0,
     'PASS r100b_phase flushpos pre=(0.0, 0.0) pf=0 post_parse=(0.0, 0.0) after_await=(20.0, 20.0) log=[sig@1=(20.0, 20.0)] post_parse2=(20.0, 20.0) after_await2=(44.0, 44.0) log=[sig@1=(20.0, 20.0)|sig@2=(44.0, 44.0)] post_flush=(12.0, 12.0) after_await3=(12.0, 12.0) log=[sig@1=(20.0, 20.0)|sig@2=(44.0, 44.0)|sig@3=(12.0, 12.0)]'),
    ('r100b_phase_orderin', 'r100b_phase.gd', ['--arm=orderin'], 0,
     'PASS r100b_phase orderin press[[i:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|g:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]] motion[[i:mm(bm=0,pos=12.0,12.0,gpos=12.0,12.0,rel=4.0,4.0,vel=0.0,0.0)|g:mm(bm=0,pos=12.0,12.0,gpos=12.0,12.0,rel=4.0,4.0,vel=0.0,0.0)]] key[[i:key(k=65,p=1)|g:key(k=65,p=1)]] touch[[i:st(i=0,p=1,dt=0,pos=8.0,8.0)|g:st(i=0,p=1,dt=0,pos=8.0,8.0)]] handled_press[[i:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|g:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]] two_in_frame[[i:mm(bm=0,pos=20.0,20.0,gpos=20.0,20.0,rel=8.0,8.0,vel=0.0,0.0)|g:mm(bm=0,pos=20.0,20.0,gpos=20.0,20.0,rel=8.0,8.0,vel=0.0,0.0)|i:mb(b=1,p=1,dc=0,bm=0,pos=20.0,20.0,gpos=20.0,20.0)|g:mb(b=1,p=1,dc=0,bm=0,pos=20.0,20.0,gpos=20.0,20.0)]]'),
    ('r100b_phase_dblclick', 'r100b_phase.gd', ['--arm=dblclick'], 0,
     'PASS r100b_phase dblclick parsed_pair[[A:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|A:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|A:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|A:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]] pushed_pair[[A:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|A:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|A:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)|A:mb(b=1,p=0,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]] parsed_third[[A:mb(b=1,p=1,dc=0,bm=0,pos=8.0,8.0,gpos=8.0,8.0)]]'),
    ('r100b_emul_state', 'r100b_emul.gd', [], 0,
     'PASS r100b_emul held0=0 emul_mouse=1 touch_press held=1 cursor=(44.0, 44.0) touch_release held=0 second_press held=1 cursor=(10.0, 10.0)'),
    ('r100b_seq_clean', 'r100b_seq.gd', ['--clean=1'], 0,
     'PASS r100_gui cursor c0=(30.0, 14.0) c1_push_mm=(30.0, 14.0) c2_push_mb=(30.0, 14.0) c3_parse_mb=(24.0, 24.0) c4_parse_mm=(30.0, 30.0) c5_gpos_drives=(60.0, 60.0) c6_parse_st=(44.0, 44.0) c7_push_mm2=(44.0, 44.0) c8 ds=(0, 0)'),
    ('r100b_seq_noclean', 'r100b_seq.gd', ['--clean=0'], 0,
     'PASS r100_gui hover h0=P h1=A ev=[A_in] h2=A ev=[A_in] h3=B ev=[A_in|A_out|B_in] h4=null ev=[A_in|A_out|B_in|B_out] h5=C ev=[A_in|A_out|B_in|B_out] h6_press=A ev=[A_in|A_out|B_in|B_out|A_in] h7_after_release=A'),
    ("crash_spontaneous_sigabrt", "spontaneous_crash_probe.gd", ["--spontaneous-crash"], -6, "SPONTANEOUS_CRASH_PROBE: expected signature"),
    ("crash_self_sigkill", "spontaneous_crash_probe.gd", ["--spontaneous-sigkill"], -9, "SPONTANEOUS_CRASH_PROBE: expected signature"),
    ("descendant_pipe_detached_control", "descendant_pipe_probe.gd", ["--spawn-detach"], 0, "DESCENDANT_PIPE_PROBE: expected signature"),
    # r63 KNOWN-ACCEPTING FORGERY ROW: the child withholds the signature; a
    # pipe-holding descendant writes it after the parent's exit
    # (reparenting-gated) and releases the pipes before the bound. The row
    # documents that signature presence is origin-blind — this PASS is a
    # forged signature accepted; see meta probe_descendant_signature_spoof.
    ("descendant_pipe_forged_signature_release", "descendant_pipe_probe.gd", ["--spawn-forge-release"], 0, "DESCENDANT_PIPE_PROBE: expected signature"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-failing", action="store_true", help="also mutate scratch scene B and prove detection")
    parser.add_argument("--fault-injection", action="store_true", help="run isolated executor fault probes (separate from seeded battery)")
    parser.add_argument("--probe-unrelated-error", action="store_true", help="append unrelated ERROR diagnostics to real export outputs and reclassify")
    parser.add_argument("--probe-export-launch", action="store_true", help="export and launch positive/control startup scenes in bounded scratch Linux/X11 builds")
    parser.add_argument("--probe-godot-error", action="store_true", help="run paired real Godot push_error diagnostic classification probes")
    parser.add_argument("--probe-stream-attribution", action="store_true", help="run paired real Godot stdout/stderr stream-attribution classification probes")
    parser.add_argument("--probe-crash-exit", action="store_true", help="run a paired real-Godot normal-exit versus signal-termination probe")
    parser.add_argument("--probe-timeout", action="store_true", help="run a paired real-Godot normal-exit versus timeout probe")
    parser.add_argument("--probe-midlineforge-ladder", action="store_true", help="run the midlineforge descendant-write offset ladder across the 200ms signature gap (fabrication-window bound measurement)")
    parser.add_argument("--probe-midlineforge-gapladder", action="store_true", help="run the midlineforge crossed gap ladder — fixed 80ms write offset across signature gaps {50,100,200,400,800}ms plus crossed cells (300,400)/(300,800)/(600,800) (pins the fabrication bound's referent: gap-relative vs absolute)")
    parser.add_argument("--probe-audio-warning", action="store_true", help="classify captured r12 leaked and clean audio outputs with the production audio verdict")
    parser.add_argument("--godot", default="godot")
    parser.add_argument("--runs", type=Path, default=HERE.parent / "live" / "runs")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.runs / stamp
    scratch = run_dir / "scratch"
    scratch.mkdir(parents=True)
    for item in HERE.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, scratch / item.name)
        else:
            shutil.copy2(item, scratch / item.name)
    # Give this copied project a unique app_userdata directory for user:// isolation.
    project_file = scratch / "project.godot"
    project_text = project_file.read_text()
    project_text = project_text.replace('config/name="MechanicOneShotTest"',
                                        f'config/name="MechanicOneShotTest-{stamp}"', 1)
    project_file.write_text(project_text)
    # Seeded controls/pickup.tscn references root pickup.gd; stage its scene in scratch.
    shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
    # Godot 4.7.2 may install current_scene one process frame after the change.
    chain = scratch / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in text, "causal fixture changed; cannot apply scratch-only readiness fix"
    chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    results = []

    def run_process(command, timeout_seconds, env=None):
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, env=env)
            return proc.stdout + proc.stderr, proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return output, None, f"TIMEOUT after {timeout_seconds} seconds"
        except OSError as exc:
            return str(exc), None, f"launch error: {exc}"

    def run_process_streams(command, timeout_seconds, env=None):
        # Same launch/timeout/OS-error shape as run_process, but the streams
        # stay separate so a case can pin stderr-only content and anchor its
        # signature to stdout (r89-fold, critic F1). Concatenating the
        # returns reproduces run_process's merged output byte-for-byte in all
        # three paths (success / timeout / OSError).
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, env=env)
            return proc.stdout, proc.stderr, proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return stdout, stderr, None, f"TIMEOUT after {timeout_seconds} seconds"
        except OSError as exc:
            return "", str(exc), None, f"launch error: {exc}"

    def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
        lines = output.splitlines()
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

        unrelated_errors = [line for line in lines if "ERROR:" in line
                            and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
        return (code == expected_exit and error is None and signature in output
                and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)

    def classify_streams(code, error, stdout, stderr, expected_exit, signature, allowed_stderr=()):
        """Classify using separate stdout/stderr. Signature must appear on stdout."""
        if code != expected_exit or error is not None:
            return False
        if signature not in stdout:
            return False
        if "SCRIPT ERROR:" in stdout or "SCRIPT ERROR:" in stderr:
            return False
        if "Parse Error:" in stdout or "Parse Error:" in stderr:
            return False
        stderr_lines = stderr.splitlines()
        allowed = set(allowed_stderr)

        def line_allowed(stripped):
            if stripped in allowed:
                return True
            for a in allowed:
                if a.endswith(",") and stripped.startswith(a) and stripped.count("ERROR:") == 1:
                    return True
            return False

        for line in stderr_lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Any unexpected stderr line rejects. Prefix-only checks would
            # false-admit a printerr that is neither ERROR: nor STREAM_STDERR:.
            if not line_allowed(stripped):
                return False
        return True

    def classify_audio_process(code, error, output, expected_exit, signature, allowed_errors=()):
        # Scope this known ObjectDB shutdown leak warning to audio_playback only;
        # export cases can legitimately print nested-project WARNING lines.
        leaked_objectdb = any(
            re.fullmatch(r"WARNING: [1-9][0-9]* ObjectDB instances were leaked at exit(?: \(run with `--verbose` for details\)\.)?", line.strip())
            for line in output.splitlines())
        return (classify_process(code, error, output, expected_exit, signature, allowed_errors)
                and not leaked_objectdb)

    if args.fault_injection:
        # Fault probes use Python subprocesses, not seeded fixtures or Godot. The
        # deliberately long sleep is bounded only here; the normal CLI is unchanged.
        faults = [
            ("fault_hang", [sys.executable, "-c", "import time; print('FAULT_HANG_STARTED', flush=True); time.sleep(30)"],
             0, "FAULT_HANG_STARTED", 0.25, ()),
            ("fault_clean_expected_negative", [sys.executable, "-c", "print('ERROR: expected negative diagnostic'); raise SystemExit(2)"],
             2, "ERROR: expected negative diagnostic", 2, ("ERROR: expected negative diagnostic",)),
            ("fault_unrelated_error", [sys.executable, "-c", "print('ERROR: expected negative diagnostic'); print('ERROR: unrelated engine failure'); raise SystemExit(2)"],
             2, "ERROR: expected negative diagnostic", 2, ("ERROR: expected negative diagnostic",)),
        ]
        for name, command, expected_exit, signature, timeout_seconds, allowed_errors in faults:
            started = datetime.now(timezone.utc)
            output, code, error = run_process(command, timeout_seconds)
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            passed = classify_process(code, error, output, expected_exit, signature, allowed_errors)
            record = {"case": name, "expected_exit": expected_exit, "signature": signature,
                      "actual_exit": code, "verdict": "PASS" if passed else "FAIL", "error": error,
                      "elapsed_seconds": round(elapsed, 3), "timeout_seconds": timeout_seconds,
                      "output": output.strip().splitlines()}
            results.append(record)
            print(f"{record['verdict']} {name}: exit={code} error={error!r}", flush=True)
        expected_verdicts = {"fault_hang": "FAIL", "fault_clean_expected_negative": "PASS",
                             "fault_unrelated_error": "FAIL"}
        payload = {"mode": "fault_injection", "seeded_battery_run": False, "results": results,
                   "verdict": "PASS" if all(r["verdict"] == expected_verdicts[r["case"]] for r in results)
                   and "FAULT_HANG_STARTED" in "\n".join(results[0]["output"])
                   and "ERROR: expected negative diagnostic" in "\n".join(results[1]["output"])
                   and "ERROR: unrelated engine failure" in "\n".join(results[2]["output"])
                   else "FAIL"}
        (run_dir / "fault-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
        print(f"{payload['verdict']} fault injection: {run_dir / 'fault-verdicts.json'}")
        return 0 if payload["verdict"] == "PASS" else 1

    if args.probe_audio_warning:
        captured = []
        for label, filename in (("captured_leak", "r12-initial-hold.json"),
                                ("captured_clean", "r12-battery-verifier.json")):
            payload = json.loads((HERE.parent / "lessons" / filename).read_text())
            matches = [item for item in payload["results"] if item.get("case") == "audio_playback"]
            if len(matches) != 1 or not isinstance(matches[0].get("output"), list):
                raise ValueError(f"{filename} lacks exactly one captured audio_playback output")
            record = matches[0]
            raw = "\n".join(record["output"])
            verdict = classify_audio_process(record["actual_exit"], record["error"], raw,
                                             record["expected_exit"], record["signature"])
            captured.append({"case": label, "source": filename, "actual_exit": record["actual_exit"],
                             "verdict": "PASS" if verdict else "FAIL", "output": record["output"]})
        expected = ["FAIL", "PASS"]
        meta = {"case": "probe_audio_warning_captured_r12", "verdict":
                "PASS" if [item["verdict"] for item in captured] == expected
                and "WARNING: 2 ObjectDB instances were leaked at exit" in "\n".join(captured[0]["output"])
                and "WARNING: 2 ObjectDB instances were leaked at exit" not in "\n".join(captured[1]["output"])
                else "FAIL",
                "classifier": "production classify_audio_process", "results": captured}
        results.append(meta)
        print(f"{meta['verdict']} captured r12 audio-warning classifier probe", flush=True)

    def execute(name, script, flags, expected_exit, evidence, mutate=False):
        if script in ("__godot_export__", "__godot_export_missing__"):
            export_project = scratch
            preset_name = "Linux/X11"
            if script == "__godot_export_missing__":
                export_project = run_dir / "missing-preset-scratch"
                shutil.copytree(scratch, export_project, ignore=shutil.ignore_patterns(".godot", "out"))
                preset_name = "Missing preset"
            out_dir = export_project / "out"
            out_dir.mkdir(exist_ok=True)
            assert not any(out_dir.iterdir()), "export output directory must start empty"
            export_path = (out_dir / "fixture.x86_64").resolve()
            command = [args.godot, "--headless", "--path", str(export_project),
                       "--export-debug", preset_name, str(export_path)]
        elif script.startswith("__save_process_"):
            mode = script.removeprefix("__save_process_").removesuffix("__")
            script_path = "res://save_process.gd"
            process_flags = {"writer": [], "reader": ["--reader"], "missing": ["--missing"]}[mode]
            command = [args.godot, "--headless", "--path", str(scratch), "--script", script_path, "--", *process_flags]
        else:
            command = [args.godot, "--headless", "--path", str(scratch), "--script", "res://" + script, "--", *flags]
        timeout_seconds = 60 if script.startswith("__godot_export") else 8
        env = None
        if script == "save_roundtrip.gd" or script.startswith("__save_process_"):
            user_data = (run_dir / "xdg-data").resolve()
            user_data.mkdir(exist_ok=True)
            env = os.environ.copy()
            env["XDG_DATA_HOME"] = str(user_data)
        proc_stdout, proc_stderr, code, error = run_process_streams(command, timeout_seconds, env=env)
        output = proc_stdout + proc_stderr
        export_record = None
        if script == "__godot_export__":
            size = export_path.stat().st_size if export_path.is_file() else 0
            digest = hashlib.sha256(export_path.read_bytes()).hexdigest() if size else None
            evidence = f"EXPORT PASS preset=Linux/X11 executable_bytes={size}"
            def classify_export(candidate_output):
                return (classify_process(code, error, candidate_output, 0, "[ DONE ]")
                        and "savepack" in candidate_output
                        and export_path.is_file() and export_path.stat().st_size > 0)
            passed = classify_export(output)
            if args.probe_unrelated_error:
                clean_verdict = classify_export(output)
                injected_output = output + "\nERROR: unrelated injected diagnostic\n"
                injected_verdict = classify_export(injected_output)
                marker_line = next(line for line in output.splitlines() if "savepack" in line)
                suffix_spoof = output.replace(marker_line, marker_line + " ERROR: unrelated injected diagnostic", 1)
                prefix_spoof = output.replace(marker_line, "ERROR: unrelated injected diagnostic " + marker_line, 1)
                suffix_verdict = classify_export(suffix_spoof)
                prefix_verdict = classify_export(prefix_spoof)
                results.append({"case": "probe_unrelated_error_export_readiness", "verdict":
                                "PASS" if clean_verdict and not injected_verdict and not suffix_verdict and not prefix_verdict else "FAIL",
                                "clean_classification": clean_verdict,
                                "injected_classification": injected_verdict,
                                "same_line_suffix_classification": suffix_verdict,
                                "same_line_prefix_classification": prefix_verdict,
                                "raw_output": output.strip().splitlines(),
                                "injected_output": injected_output.strip().splitlines(),
                                "same_line_suffix_output": suffix_spoof.strip().splitlines(),
                                "same_line_prefix_output": prefix_spoof.strip().splitlines(),
                                "injected_line": "ERROR: unrelated injected diagnostic"})
            products = sorted(p.name for p in out_dir.iterdir())
            export_record = {"artifact_bytes": size, "artifact_sha256": digest, "products_created": products, "artifacts_deleted": False}
            for product in out_dir.iterdir():
                if product.is_file():
                    product.unlink()
            export_record["artifacts_deleted"] = not any(out_dir.iterdir())
        elif script == "__godot_export_missing__":
            evidence = "ERROR: Invalid export preset name: Missing preset."
            def classify_export(candidate_output):
                return (classify_process(code, error, candidate_output, expected_exit, evidence, (evidence,))
                        and not any(out_dir.iterdir()))
            passed = classify_export(output)
            if args.probe_unrelated_error:
                clean_verdict = classify_export(output)
                injected_output = output + "\nERROR: unrelated injected diagnostic\n"
                injected_verdict = classify_export(injected_output)
                spoof_output = output.replace(evidence, evidence + " ERROR: unrelated injected diagnostic", 1)
                spoof_verdict = classify_export(spoof_output)
                results.append({"case": "probe_unrelated_error_export_preset_missing", "verdict":
                                "PASS" if clean_verdict and not injected_verdict and not spoof_verdict else "FAIL",
                                "clean_classification": clean_verdict,
                                "injected_classification": injected_verdict,
                                "same_line_spoof_classification": spoof_verdict,
                                "raw_output": output.strip().splitlines(),
                                "injected_output": injected_output.strip().splitlines(),
                                "same_line_spoof_output": spoof_output.strip().splitlines(),
                                "injected_line": "ERROR: unrelated injected diagnostic"})
        else:
            passed = None
        # The mutant is intentionally expected to violate the positive assertion.
        def classify_mutant(candidate_output):
            # Mode-envelope rows carry a tuple of whitelisted payloads; the
            # mutant check keys off the first (pinned-mode) payload only.
            mutant_sig = evidence if isinstance(evidence, str) else evidence[0]
            candidate = (classify_process(code, error, candidate_output, 2, mutant_sig,
                                          ("ERROR: " + mutant_sig,))
                         and "PASS " not in candidate_output)
            if name == "mutant_broken_scene_route":
                candidate = (classify_process(code, error, candidate_output, 2, "chain incomplete",
                                              ("ERROR: chain incomplete",))
                             and "PASS positive input=1" not in candidate_output)
            if name == "mutant_level_collision_removed":
                candidate = (classify_process(code, error, candidate_output, 2, evidence,
                                              ("ERROR: LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry",))
                             and "PASS level_packed_scene=true" not in candidate_output)
            return candidate
        detected = classify_mutant(output)
        if mutate and args.probe_unrelated_error:
            injected_output = output + "\nERROR: unrelated injected diagnostic\n"
            injected_detected = classify_mutant(injected_output)
            first_error_line = next(line for line in output.splitlines() if "ERROR:" in line)
            suffix_spoof = output.replace(first_error_line, first_error_line + " ERROR: unrelated injected diagnostic", 1)
            prefix_spoof = output.replace(first_error_line, "ERROR: unrelated injected diagnostic " + first_error_line, 1)
            suffix_detected = classify_mutant(suffix_spoof)
            prefix_detected = classify_mutant(prefix_spoof)
            results.append({"case": "probe_unrelated_error_" + name, "verdict":
                            "PASS" if detected and not injected_detected and not suffix_detected and not prefix_detected else "FAIL",
                            "clean_classification": detected,
                            "injected_classification": injected_detected,
                            "same_line_suffix_classification": suffix_detected,
                            "same_line_prefix_classification": prefix_detected,
                            "raw_output": output.strip().splitlines(),
                            "injected_output": injected_output.strip().splitlines(),
                            "same_line_suffix_output": suffix_spoof.strip().splitlines(),
                            "same_line_prefix_output": prefix_spoof.strip().splitlines(),
                            "injected_line": "ERROR: unrelated injected diagnostic"})
        expected_errors = ()
        required_stderr = ()
        if passed is None:
            expected_errors = {
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
                "phys2d_events_cm_toggle_cb": (
                    "ERROR: Can't disable contact monitoring during in/out callback. Use call_deferred(\"set_contact_monitor\", false) instead.",
                ),
                "phys2d_events_rb_free_rid": (
                    "ERROR: Parameter \"body\" is null.",
                    "ERROR: Invalid ID.",
                ),
                "phys2d_events_area_monitoring_direct": (
                    "ERROR: Function blocked during in/out signal. Use set_deferred(\"monitoring\", true/false).",
                ),
                "phys2d_events_area_free_rid": (
                    "ERROR: Parameter \"body\" is null.",
                    "ERROR: Invalid ID.",
                ),
                "phys2d_motion_mac_maxcol": ("ERROR: Error calling method from 'callv': 'CharacterBody2D::move_and_collide': Method expected 4 argument(s), but called with 5.",),
                "phys2d_motion_dss_wrongarg": ("ERROR: Required object \"rp_shape_query\" is null.",
                                         "ERROR: Required object \"rp_ray_query\" is null.",
                                         "ERROR: Required object \"rp_point_query\" is null.",),
                "phys2d_joints_joint_unset_refusal": (
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_DAMPED_SPRING" is true. Returning: 0',
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true. Returning: 0',
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true. Returning: false',
                ),
                "phys2d_joints_joint_pin_clear": (
                    'ERROR: Condition "joint->get_type() != JOINT_TYPE_PIN" is true. Returning: 0',
                ),
                "phys2d_joints_joint_freed_rid": (
                    'ERROR: Parameter "joint" is null.',
                    'ERROR: Parameter "prev_joint" is null.',
                ),
                "phys2d_joints_joint_node_freed_rid": (
                    'ERROR: Invalid ID.',
                    'ERROR: Parameter "joint" is null.',
                ),
                # r87 input lattice: null_edge deliberately pokes the null/never-
                # registered refusal surface; ei_bound_refusal triggers the typed
                # event_index>=32 refusal once per out-of-range case (4x same line).
                'input_lattice_null_edge': (
                    'ERROR: Required object "rp_event" is null.',
                    'ERROR: The InputMap action "never_existed" doesn\'t exist.',
                    'ERROR: The InputMap action "never_existed2" doesn\'t exist.',
                    'ERROR: The InputMap action "never_existed3" doesn\'t exist.',
                ),
                'ei_bound_refusal': (
                    'ERROR: Input singleton does not support more than 32 events assigned to an action.',
                ),
                # jpbe arm deliberately parses an event_index=42 event to pin
                # the refusal; the typed ERROR is deterministic (scout err
                # receipts carry it x3) — whitelist it.
                'r87_edge_jpbe': (
                    'ERROR: Input singleton does not support more than 32 events assigned to an action.',
                ),
                # r88: sprite_phys deliberately assigns frame=3 on a sprite
                # with vframes*hframes=2 — the engine refuses loudly and
                # deterministically (scout §3.13 / directive 7).
                'r88_surfaces_sprite_phys': (
                    'ERROR: Index p_frame = 3 is out of bounds (vframes * hframes = 2).',
                ),
                # r89: atlasempty pokes the empty-input refusal
                # (scout §5.2 — "p_rects.is_empty()", a DIFFERENT message
                # from the boundary's per-rect "p_rects[i].width <= 0",
                # which no authored row feeds). polyendpoly drives
                # END_POLYGON on an open AND a closed polyline — the same
                # refusal ERROR fires twice; one exact entry covers both
                # lines (scout §5.3).
                'geo2d_lattice_atlasempty': (
                    'ERROR: Condition "p_rects.is_empty()" is true.',
                ),
                'geo2d_lattice_polyendpoly': (
                    'ERROR: Attempt to offset a polyline like a polygon (use offset_polygon instead).',
                ),
                # r90: comrefuse pokes the value-gated AUTO refusal once
                # (rigid_body_2d.cpp:376 — the ONLY COM error path per
                # boundary §6); the same-value set under AUTO is the silent
                # no-op branch in the same row. impedge drives the two
                # adjacent typed refusals: inertia<0 at :334 once and
                # mass<=0 at :324 twice (mass0 + massneg lanes) — one exact
                # entry covers both mass lines.
                'r90_lattice_comrefuse': (
                    'ERROR: Condition "center_of_mass_mode != CENTER_OF_MASS_MODE_CUSTOM" is true.',
                ),
                'r90_lattice_impedge': (
                    'ERROR: Condition "p_inertia < 0" is true.',
                    'ERROR: Condition "p_mass <= 0" is true.',
                ),
                # r91: sync deliberately reads map_get_closest_point before the
                # first map synchronization — the typed loud refusal
                # (nav_map_2d.cpp:165) fires exactly once per run; bake pokes
                # the orphan-node refusal once (the deprecation WARNING on the
                # outline route carries no "ERROR:" substring, needs no entry).
                'nav_lattice_sync': (
                    'ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.',
                ),
                'nav_lattice_bake': (
                    'ERROR: The root node needs to be inside the SceneTree.',
                ),
                # r92: nine tilemap arms deliberately poke deterministic
                # typed refusals (scout §6.1 — every emitted line verified
                # against canonical + boundary receipts; repeated identical
                # lines are covered by one exact entry, same as
                # geo2d_lattice_polyendpoly). census/timing/quadrant/nav
                # emit no ERROR: line at all and need no entry; nav's only
                # stderr is the make_polygons_from_outlines deprecation
                # WARNING (no ERROR: substring — classifier-inert).
                'r92_tilemap_atlas': (
                    'ERROR: Cannot create tile. The tile is outside the texture or tiles are already present in the space the tile would cover.',
                    'ERROR: The TileSetAtlasSource atlas has no tile at (5, 5).',
                ),
                'r92_tilemap_cells': (
                    'ERROR: Method/function failed. Returning: p_coords',
                    'ERROR: The TileSetAtlasSource atlas has no tile at (9, 9).',
                ),
                'r92_tilemap_custom': (
                    'ERROR: TileSet has no layer with name: absent',
                    'ERROR: TileSet has no layer with name: ghost',
                    'ERROR: TileSet has no layer with name: tag',
                ),
                'r92_tilemap_terrain': (
                    'ERROR: Index p_terrain_set = 5 is out of bounds (tile_set->get_terrain_sets_count() = 1).',
                ),
                'r92_tilemap_pattern': (
                    'ERROR: Condition "!pattern.has(p_coords)" is true. Returning: TileSet::INVALID_SOURCE',
                ),
                'r92_tilemap_encoding': (
                    'ERROR: Corrupted tile map data: tiles might be missing.',
                    'ERROR: Unsupported tile map data format: 513. Expected format ID lower or equal to: 0',
                ),
                'r92_tilemap_fixinvalid': (
                    'ERROR: No TileSet atlas source with id -1.',
                    'ERROR: No TileSet atlas source with id 0.',
                    'ERROR: No TileSet atlas source with id 42.',
                ),
                'r92_tilemap_srcids': (
                    'ERROR: Cannot create TileSet atlas source. Another atlas source exists with id 0.',
                    'ERROR: Condition "p_tile_set_source.is_null()" is true. Returning: TileSet::INVALID_SOURCE',
                    'ERROR: Provided source ID -3 is not valid. Negative source IDs are not allowed.',
                ),
                'r92_tilemap_physics': (
                    'ERROR: Parameter "found" is null.',
                ),
                # r96: ownership deliberately pokes the non-ancestor and
                # self-owner refusals; refuse exercises the save/load
                # refusal surface — each line is a deterministic engine
                # ERROR observed on every scout + boundary receipt
                # (exact strings; the row fails if any of them stops
                # firing — see r96_expected_errors_all_matched).
                'r96_scene_io_ownership': (
                    'ERROR: Invalid owner. Owner must be an ancestor in the tree.',
                    'ERROR: Condition "p_owner == this" is true.',
                ),
                # r96-author fold: the arm reads get_id_path on the FIXED
                # sample uid (bqk3m5n7qar1), not a fresh create_id() — the
                # "Unrecognized UID" diagnostic echoes the queried uid and
                # would otherwise carry a per-process random text. It fires
                # iff the scratch project has .godot/uid_cache.bin (the
                # export_readiness row populates it before this row runs;
                # absent in standalone runs the line is simply absent).
                'r96_scene_io_uid': (
                    'ERROR: Unrecognized UID: "uid://bqk3m5n7qar1".',
                ),
                'r96_scene_io_refuse': (
                    "ERROR: Cannot save file 'user://r96_absent_dir_xyz/deep/x.tscn'.",
                    "ERROR: Can't save empty resource to path 'user://r96/null.tscn'.",
                    "ERROR: Can't save resource to empty path. Provide non-empty path or a Resource with non-empty resource_path.",
                    "ERROR: Cannot open file 'user://r96/nope.tscn'.",
                    'ERROR: Failed loading resource: user://r96/nope.tscn.',
                    "ERROR: Error loading resource: 'user://r96/nope.tscn'.",
                    'ERROR: Resource file not found: user://r96 (expected type: unknown)',
                    "ERROR: Error loading resource: 'user://r96'.",
                    'ERROR: Resource file not found: res:// (expected type: unknown)',
                    "ERROR: Error loading resource: ''.",
                    'ERROR: Parameter "p_scene" is null.',
                    'ERROR: Failed to instantiate scene state of "", node count is 0. Make sure the PackedScene resource is valid.',
                    "ERROR: Another resource is loaded from path 'user://r96/collide.tres' (possible cyclic resource inclusion).",
                ),
                # r100 author: the render cell (and both seq variants that
                # replay it) exercises the dummy rendering storage's
                # backbuffer readback — deterministic headless ERROR, one
                # exact allowlist entry per case (the ERROR line is the
                # classified unit; its backtrace lines carry no ERROR:).
                'r100_gui_render': (
                    'ERROR: Parameter "t" is null.',
                ),
                'r100b_seq_clean': (
                    'ERROR: Parameter "t" is null.',
                ),
                'r100b_seq_noclean': (
                    'ERROR: Parameter "t" is null.',
                ),
            }.get(name, ())
            # r89-fold (critic F1): stderr-fragment pins. geo2d_lattice_lineempty
            # classified on the merged stdout+stderr blob, so a foreign SIGABRT
            # after the signature byte — or the signature emitted on stderr
            # alone — still classified PASS (demonstrated false-positive
            # shapes). The fragments below must each appear ON STDERR, binding
            # the crash to the Clipper2 empty-polyline assert class
            # (operator[] on Clipper2Lib::Point<double> firing the libstdc++
            # __n < this->size() bounds assert), not merely to the -6 signal
            # class, and the row's signature is additionally anchored to
            # stdout. The assert text is toolchain-pinned (libstdc++), a
            # disclosed host-conditional token like joys=0/nmethods=86; the
            # c++/<ver> header path is deliberately NOT pinned.
            required_stderr = {
                'geo2d_lattice_lineempty': (
                    'Clipper2Lib::Point<double>',
                    "Assertion '__n < this->size()' failed.",
                ),
                # r91 teardown negative control: binds the rc=-6 to the glibc
                # heap-corruption abort (live avoidance callback at server
                # teardown), not to the signal class alone. Toolchain-pinned
                # fragment (glibc malloc printer), same class as the Clipper2
                # tokens above; the `(!prev)` tail is deliberately NOT pinned.
                'nav_lattice_teardown_crash': (
                    'double free or corruption',
                ),
                # r92 null-TileSet SIGSEGV negative control: binds the
                # rc=-11 to the engine's own signal-11 crash handler AND
                # the _nullts frame site in this probe — a foreign SIGSEGV
                # (right signal, wrong cause) cannot satisfy the pair.
                # The crash-dump header and the GDScript backtrace site
                # are the pinned fragments; ASLR'd addresses and the C++
                # backtrace are deliberately NOT pinned.
                'r92_tilemap_nullts_crash': (
                    'handle_crash: Program crashed with signal 11',
                    '_nullts (res://tilemap_lattice.gd:927)',
                ),
            }.get(name, ())
            classifier = classify_audio_process if name == "audio_playback" else classify_process
            if isinstance(evidence, (tuple, list)):
                # Mode-envelope row: PASS iff ANY whitelisted payload appears in
                # the merged output (bimodal pins; r87 press_phys/release_edge/
                # ui_ns — both observed modes enumerated, nothing else admitted).
                passed = detected if mutate else any(
                    classifier(code, error, output, expected_exit, sig, expected_errors)
                    for sig in evidence)
            else:
                passed = detected if mutate else classifier(code, error, output, expected_exit, evidence, expected_errors)
            if required_stderr:
                # Stream-anchored: every pinned fragment must appear on the
                # stderr stream alone, and at least one payload of the row's
                # signature must appear on stdout alone — the two directions
                # of the merged-blob blindness closed together.
                sigs = evidence if isinstance(evidence, (tuple, list)) else (evidence,)
                passed = (passed
                          and all(fragment in proc_stderr for fragment in required_stderr)
                          and any(sig in proc_stdout for sig in sigs))
        # A script/parse error never counts as intended mutant detection.
        if "SCRIPT ERROR:" in output or "Parse Error:" in output:
            passed = False
        record = {"case": name, "script": script, "flags": flags, "command": command,
                  "xdg_data_home": env.get("XDG_DATA_HOME") if env else None,
                  "expected_exit": expected_exit, "actual_exit": code, "signature": evidence,
                  "verdict": "PASS" if passed else "FAIL",
                  "error": error, "output": output.strip().splitlines()}
        record["expected_errors"] = list(expected_errors)
        record["required_stderr"] = list(required_stderr)
        if export_record is not None:
            record["export_artifact"] = export_record
        results.append(record)
        print(f"{record['verdict']} {name}: exit={code} signature={evidence!r}", flush=True)

    for case in CASES:
        execute(*case)
    process_records = {r["case"]: r for r in results if r["case"] in {
        "save_process_writer", "save_process_reader", "save_process_missing"}}
    def process_evidence(record, role):
        text = "\n".join(record["output"])
        match = re.search(r"pid=(\d+).*path=(\S+)", text)
        return {"pid": int(match.group(1)) if match else None,
                "path": match.group(2) if match else None,
                "signature": record["signature"], "output": record["output"],
                "command": record["command"], "actual_exit": record["actual_exit"],
                "role": role}
    process_evidence_rows = {
        name: process_evidence(record, name.removeprefix("save_process_"))
        for name, record in process_records.items()}
    writer = process_evidence_rows["save_process_writer"]
    reader = process_evidence_rows["save_process_reader"]
    negative = process_records["save_process_missing"]
    user_data = str((run_dir / "xdg-data").resolve())
    writer_path = Path(writer["path"]) if writer["path"] else None
    user_data_path = Path(user_data)
    try:
        writer_inside_xdg = writer_path is not None and writer_path.is_relative_to(user_data_path)
    except ValueError:
        writer_inside_xdg = False
    process_meta_ok = (
        writer["pid"] is not None and reader["pid"] is not None and writer["pid"] != reader["pid"]
        and writer["path"] == reader["path"] and writer_path is not None
        and writer_inside_xdg
        and "--script" in writer["command"] and "--script" in reader["command"]
        and writer["command"][writer["command"].index("--script") + 1] == reader["command"][reader["command"].index("--script") + 1]
        and process_records["save_process_writer"].get("xdg_data_home") == user_data
        and process_records["save_process_reader"].get("xdg_data_home") == user_data
        and process_records["save_process_missing"].get("xdg_data_home") == user_data
        and all(record["command"][record["command"].index("--path") + 1] == str(scratch)
                for record in process_records.values())
        and process_records["save_process_writer"]["verdict"] == "PASS"
        and process_records["save_process_reader"]["verdict"] == "PASS"
        and negative["verdict"] == "PASS"
        and negative["actual_exit"] == 2
        and "--missing" in negative["command"]
    )
    process_payload = {"mode": "independent_godot_process_save_read",
                       "same_project": True, "same_absolute_xdg_data_home": user_data,
                       "writer_reader_distinct_pid": writer["pid"] != reader["pid"],
                       "evidence": process_evidence_rows,
                       "negative_missing_file_rejected": negative["verdict"] == "PASS",
                       "verdict": "PASS" if process_meta_ok else "FAIL",
                       "bounded_claim": "headless Godot process writes JSON then a distinct Godot process reads exact structure; paired separate-process missing-file rejection; not crash/power-loss durability or arbitrary corruption detection"}
    process_artifact = run_dir / "save-process-verdicts.json"
    process_artifact.write_text(json.dumps(process_payload, indent=2) + "\n")
    results.append({"case": "probe_save_independent_process", "verdict": process_payload["verdict"],
                    "artifact": str(process_artifact), "pids": [writer["pid"], reader["pid"]]})
    print(f"{process_payload['verdict']} independent save process probe: {process_artifact}", flush=True)
    # r61 meta: spontaneous-crash classification discrimination. Re-classifies
    # the already-captured crash-row outputs under mismatched expectations —
    # no extra Godot invocations. Each discriminating arm must reject.
    crash_marker = "SPONTANEOUS_CRASH_PROBE: expected signature"
    crash_allowlist = ("ERROR: r60 spontaneous crash probe",)
    crash_records = {r["case"]: r for r in results
                     if r.get("script") == "spontaneous_crash_probe.gd"}

    def reclassify_crash(record, expected, allowed):
        return classify_process(record["actual_exit"], record["error"],
                                "\n".join(record["output"]), expected,
                                crash_marker, allowed)

    sigabrt = crash_records.get("crash_spontaneous_sigabrt")
    self_sigkill = crash_records.get("crash_self_sigkill")
    crash_discriminations = {
        "sigabrt_expected_-9_rejects": sigabrt is not None and not reclassify_crash(
            sigabrt, -9, crash_allowlist),
        "sigabrt_missing_allowlist_rejects": sigabrt is not None and not reclassify_crash(
            sigabrt, -6, ()),
        "sigabrt_wrong_allowlist_rejects": sigabrt is not None and not reclassify_crash(
            sigabrt, -6, ("ERROR: unrelated different diagnostic",)),
        "self_sigkill_expected_-6_rejects": self_sigkill is not None and not reclassify_crash(
            self_sigkill, -6, crash_allowlist),
    }
    crash_meta_ok = (
        sigabrt is not None and sigabrt["verdict"] == "PASS" and sigabrt["actual_exit"] == -6
        and "ERROR: r60 spontaneous crash probe" in "\n".join(sigabrt["output"])
        and self_sigkill is not None and self_sigkill["verdict"] == "PASS"
        and self_sigkill["actual_exit"] == -9
        and all(crash_discriminations.values()))
    results.append({"case": "probe_spontaneous_crash_classification",
                    "verdict": "PASS" if crash_meta_ok else "FAIL",
                    "mode": "captured_output_reclassification",
                    "sigabrt_exit": sigabrt["actual_exit"] if sigabrt else None,
                    "self_sigkill_exit": self_sigkill["actual_exit"] if self_sigkill else None,
                    "crash_allowlist": list(crash_allowlist),
                    "discriminations": crash_discriminations,
                    "bounded_claim": "spontaneous SIGABRT/SIGKILL exit-shape classification on Linux headless Godot 4.7.2 only; signal origin unprovable from returncode"})
    print(f"{results[-1]['verdict']} spontaneous crash classification meta", flush=True)
    # r62 meta: tree-timeout pipe-EOF misattribution. communicate(timeout) is a
    # completion + pipe-drain deadline, not a liveness bound: a clean-exiting
    # Godot child whose spawned OS descendant keeps the captured stdout/stderr
    # pipes open is still reported TIMEOUT, and the timeout kill targets the
    # direct child only, so the descendant orphans. The CASES row
    # descendant_pipe_detached_control (same fixture, --spawn-detach) is the
    # discriminating control: fds detached at exec -> child-exit-bound PASS
    # while its own descendant silently outlives the run. The hold arm cannot
    # be a CASES tuple (its record carries error set -> always False), so this
    # row drives it under one bounded Popen run; ~3s wall clock per battery.
    pipe_marker = "DESCENDANT_PIPE_PROBE: expected signature"
    pipe_post_exit = "DESCENDANT_PIPE_AFTER_EXIT_WRITE"
    pipe_bound = 3.0
    detached = next((r for r in results
                     if r["case"] == "descendant_pipe_detached_control"), None)
    pipe_hold = {"case": "descendant_pipe_hold_arm", "bound_seconds": pipe_bound,
                 "timed_out": False, "child_exit_at_timeout": None,
                 "actual_exit": None, "error": None, "marker_observed": False,
                 "post_exit_write_captured": False, "godot_pid": None,
                 "descendant_pid": None, "godot_alive_at_return": None,
                 "descendant_alive_at_return": None, "inner_classification": False}
    pipe_proc = None
    pipe_started = time.monotonic()
    pipe_text = ""
    try:
        pipe_proc = subprocess.Popen(
            [args.godot, "--headless", "--path", str(scratch), "--script",
             "res://descendant_pipe_probe.gd", "--", "--spawn-hold"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            pipe_out, pipe_err = pipe_proc.communicate(timeout=pipe_bound)
            pipe_text = (pipe_out or "") + (pipe_err or "")
            pipe_hold["actual_exit"] = pipe_proc.returncode
        except subprocess.TimeoutExpired as exc:
            pipe_hold["timed_out"] = True
            # poll() reaps the direct child: a non-None exit code here proves
            # the bound fired on pipe EOF with the child already dead.
            pipe_hold["child_exit_at_timeout"] = pipe_proc.poll()
            pipe_out = (exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes)
                        else (exc.stdout or ""))
            pipe_err = (exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes)
                        else (exc.stderr or ""))
            pipe_text = pipe_out + pipe_err
            pipe_hold["error"] = f"TIMEOUT after {pipe_bound} seconds"
            for stream in (pipe_proc.stdout, pipe_proc.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            try:
                pipe_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pipe_proc.kill()
                try:
                    pipe_proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pipe_hold["error"] += "; post-kill wait timed out"
    except (OSError, ValueError) as exc:
        pipe_hold["error"] = f"launch/read error: {exc}"
    finally:
        if pipe_proc is not None and pipe_proc.poll() is None:
            pipe_proc.kill()
            try:
                pipe_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                pipe_hold["error"] = (pipe_hold["error"] or "") + "; forced cleanup timed out"
    pipe_hold["elapsed_seconds"] = round(time.monotonic() - pipe_started, 3)
    pipe_hold["marker_observed"] = pipe_marker in pipe_text
    pipe_hold["post_exit_write_captured"] = pipe_post_exit in pipe_text
    pid_match = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", pipe_text)
    pipe_hold["godot_pid"] = int(pid_match.group(1)) if pid_match else None
    pid_match = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", pipe_text)
    pipe_hold["descendant_pid"] = int(pid_match.group(1)) if pid_match else None

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

    pipe_hold["godot_alive_at_return"] = pid_alive(pipe_hold["godot_pid"])
    pipe_hold["descendant_alive_at_return"] = pid_alive(pipe_hold["descendant_pid"])
    pipe_hold["inner_classification"] = classify_process(
        pipe_hold["actual_exit"], pipe_hold["error"], pipe_text, 0, pipe_marker)
    detached_output = "\n".join(detached["output"]) if detached else ""
    detached_pid_match = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", detached_output)
    detached_descendant_pid = int(detached_pid_match.group(1)) if detached_pid_match else None
    detached_descendant_alive = pid_alive(detached_descendant_pid)
    pipe_discriminations = {
        # The pinned misattribution: the bound fired while the direct child
        # was already dead (clean exit 0) — a pipe-drain wait, not liveness.
        "hold_timed_out_with_child_dead": (pipe_hold["timed_out"]
                                         and pipe_hold["child_exit_at_timeout"] == 0),
        # The descendant's line was written ~1s after spawn — after its parent
        # exited — yet was still captured: the runner kept draining the
        # descendant-held pipe past the child's death.
        "hold_post_exit_write_captured": pipe_hold["post_exit_write_captured"],
        # The observed classification under the bound: error set + exit None
        # -> rejects — the verdict a CASES row would misattribute to liveness.
        "hold_misattributed_rejects": pipe_hold["inner_classification"] is False,
        # No process-group kill exists: the descendant is orphaned and still
        # alive after the run returns.
        "hold_descendant_orphaned_alive": pipe_hold["descendant_alive_at_return"] is True,
        # Discriminating control: same fixture/marker, fds detached at exec ->
        # child-exit-bound PASS with no post-exit write captured.
        "detached_case_passes_clean": (detached is not None
                                       and detached["verdict"] == "PASS"
                                       and detached["actual_exit"] == 0
                                       and detached["error"] is None),
        "detached_lacks_post_exit_write": pipe_post_exit not in detached_output,
        # The control's own descendant also outlives the run: the battery has
        # no leak detection; only the pipe route differs between the arms.
        "detached_descendant_orphaned_alive": detached_descendant_alive is True,
    }
    # Harness-side hygiene: reap the orphaned descendants (each is a bounded
    # `sleep` that would self-exit within seconds anyway); never gated verdicts.
    for orphan_pid in (pipe_hold["descendant_pid"], detached_descendant_pid):
        if pid_alive(orphan_pid):
            try:
                os.kill(orphan_pid, signal.SIGKILL)
            except OSError:
                pass
    pipe_meta_ok = all(pipe_discriminations.values())
    results.append({"case": "probe_descendant_pipe_eof",
                    "verdict": "PASS" if pipe_meta_ok else "FAIL",
                    "mode": "bounded_popen_plus_cases_control",
                    "bound_seconds": pipe_bound,
                    "hold_arm": pipe_hold,
                    "hold_output_lines": pipe_text.strip().splitlines(),
                    "detached_control_case": "descendant_pipe_detached_control",
                    "detached_control_descendant_pid": detached_descendant_pid,
                    "discriminations": pipe_discriminations,
                    "bounded_claim": "Linux headless Godot 4.7.2 POSIX pipe semantics: communicate(timeout) is a completion+pipe-drain bound, timeout kill is direct-child-only, descendants orphan; not a Windows/macOS or exported-build claim"})
    print(f"{results[-1]['verdict']} descendant pipe-EOF meta", flush=True)
    # r63 meta: merged-stream signature-spoof boundary — documented
    # forgery-accepting, pinned not fixed. classify_process's signature clause
    # is presence-based over the merged captured output: origin-blind. A
    # pipe-holding descendant that writes the expected signature AFTER the
    # direct child's exit (kernel-reparenting gated; write_ppid != godot_pid
    # is in-record post-orphan provenance) satisfies it. Two complementary
    # records pin the boundary:
    #   hold arm (--spawn-forge-hold, one bounded Popen at 3.0s): the forged
    #     signature lands INSIDE the TIMEOUT record — classification rejects
    #     only via the error/timeout fields (timed_out,
    #     child_exit_at_timeout), never via signature presence.
    #   CASES row descendant_pipe_forged_signature_release
    #   (--spawn-forge-release): the descendant releases the pipes before the
    #     8s bound, so the forged signature lands in a clean exit-0 record and
    #     classifies PASS — a signature the direct child never emitted is
    #     accepted indistinguishably from a genuine one.
    spoof_marker = "DESCENDANT_PIPE_PROBE: expected signature"
    spoof_bound = 3.0
    forged = next((r for r in results
                   if r["case"] == "descendant_pipe_forged_signature_release"), None)
    spoof_hold = {"case": "descendant_pipe_forge_hold_arm", "bound_seconds": spoof_bound,
                  "timed_out": False, "child_exit_at_timeout": None,
                  "actual_exit": None, "error": None, "marker_observed": False,
                  "write_ppid": None, "godot_pid": None, "descendant_pid": None,
                  "godot_alive_at_return": None, "descendant_alive_at_return": None,
                  "descendant_kernel_ppid_at_return": None,
                  "inner_classification": False}
    spoof_proc = None
    spoof_started = time.monotonic()
    spoof_text = ""
    try:
        spoof_proc = subprocess.Popen(
            [args.godot, "--headless", "--path", str(scratch), "--script",
             "res://descendant_pipe_probe.gd", "--", "--spawn-forge-hold"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            spoof_out, spoof_err = spoof_proc.communicate(timeout=spoof_bound)
            spoof_text = (spoof_out or "") + (spoof_err or "")
            spoof_hold["actual_exit"] = spoof_proc.returncode
        except subprocess.TimeoutExpired as exc:
            spoof_hold["timed_out"] = True
            # poll() reaps the direct child: a non-None exit code here proves
            # the bound fired on pipe EOF with the child already dead.
            spoof_hold["child_exit_at_timeout"] = spoof_proc.poll()
            spoof_out = (exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes)
                         else (exc.stdout or ""))
            spoof_err = (exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes)
                         else (exc.stderr or ""))
            spoof_text = spoof_out + spoof_err
            spoof_hold["error"] = f"TIMEOUT after {spoof_bound} seconds"
            for stream in (spoof_proc.stdout, spoof_proc.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            try:
                spoof_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                spoof_proc.kill()
                try:
                    spoof_proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    spoof_hold["error"] += "; post-kill wait timed out"
    except (OSError, ValueError) as exc:
        spoof_hold["error"] = f"launch/read error: {exc}"
    finally:
        if spoof_proc is not None and spoof_proc.poll() is None:
            spoof_proc.kill()
            try:
                spoof_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                spoof_hold["error"] = (spoof_hold["error"] or "") + "; forced cleanup timed out"
    spoof_hold["elapsed_seconds"] = round(time.monotonic() - spoof_started, 3)
    spoof_hold["marker_observed"] = spoof_marker in spoof_text
    spoof_pid = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", spoof_text)
    spoof_hold["godot_pid"] = int(spoof_pid.group(1)) if spoof_pid else None
    spoof_pid = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", spoof_text)
    spoof_hold["descendant_pid"] = int(spoof_pid.group(1)) if spoof_pid else None
    spoof_pid = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", spoof_text)
    spoof_hold["write_ppid"] = int(spoof_pid.group(1)) if spoof_pid else None
    spoof_hold["godot_alive_at_return"] = pid_alive(spoof_hold["godot_pid"])
    spoof_hold["descendant_alive_at_return"] = pid_alive(spoof_hold["descendant_pid"])
    spoof_hold["inner_classification"] = classify_process(
        spoof_hold["actual_exit"], spoof_hold["error"], spoof_text, 0, spoof_marker)

    def kernel_ppid(pid):
        # /proc/<pid>/stat field 4 — kernel-side ppid, corroborates the
        # descendant's self-reported write_ppid while it still lives (the
        # release arm's descendant exits before return and cannot be checked;
        # its write_ppid is fixture-asserted only — r63 critic disclosure).
        if pid is None or pid <= 0:
            return None
        try:
            with open(f"/proc/{pid}/stat") as stat_file:
                return int(stat_file.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            return None

    spoof_hold["descendant_kernel_ppid_at_return"] = kernel_ppid(
        spoof_hold["descendant_pid"])
    forged_output = "\n".join(forged["output"]) if forged else ""
    forged_pid = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", forged_output)
    forged_godot_pid = int(forged_pid.group(1)) if forged_pid else None
    forged_pid = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", forged_output)
    forged_descendant_pid = int(forged_pid.group(1)) if forged_pid else None
    forged_pid = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", forged_output)
    forged_write_ppid = int(forged_pid.group(1)) if forged_pid else None
    spoof_discriminations = {
        # Bound fired on the descendant-held pipes with the direct child
        # already dead — the r62 pinned misattribution shape, now carrying a
        # descendant-authored signature.
        "hold_timed_out_with_child_dead": (spoof_hold["timed_out"]
                                         and spoof_hold["child_exit_at_timeout"] == 0),
        # The expected signature IS in the TIMEOUT record; the child withheld
        # it by construction, so this occurrence is descendant-authored.
        "hold_forged_signature_captured": spoof_hold["marker_observed"],
        # In-record post-orphan provenance: the write's observed ppid is the
        # reparented ppid, not the godot child pid.
        "hold_write_post_orphan": (spoof_hold["write_ppid"] is not None
                                   and spoof_hold["godot_pid"] is not None
                                   and spoof_hold["write_ppid"] != spoof_hold["godot_pid"]),
        # Signature presence alone would accept; this record rejects only
        # through the timeout/error axis.
        "hold_rejects_via_timeout_axis_only": spoof_hold["inner_classification"] is False,
        # No process-group kill exists: the hold descendant orphans alive.
        "hold_descendant_orphaned_alive": spoof_hold["descendant_alive_at_return"] is True,
        # The pinned forgery-accepting boundary: the release CASES row is a
        # PASS whose signature is provably the descendant's post-death write.
        "release_row_passes_on_forged_signature": (forged is not None
            and forged["verdict"] == "PASS" and forged["actual_exit"] == 0
            and forged["error"] is None and spoof_marker in forged_output),
        "release_write_post_orphan": (forged_write_ppid is not None
                                      and forged_godot_pid is not None
                                      and forged_write_ppid != forged_godot_pid),
        # Kernel corroboration of the self-reported ppid: the hold descendant
        # is still alive at return, so /proc/<pid>/stat ppid must equal the
        # reparented ppid it claimed and differ from the dead godot pid —
        # closes the fabricated-write_ppid slip class on this arm (r63
        # critic). The release descendant is already dead at return; its
        # write_ppid stays fixture-asserted.
        "hold_write_ppid_kernel_corroborated": (
            spoof_hold["write_ppid"] is not None
            and spoof_hold["descendant_kernel_ppid_at_return"]
                == spoof_hold["write_ppid"]
            and spoof_hold["godot_pid"] is not None
            and spoof_hold["write_ppid"] != spoof_hold["godot_pid"]),
        # Provenance anchor: the release row's output must carry the child's
        # own withheld banner — without it the signature's descendant
        # authorship is unproven within the record.
        "release_withheld_banner_present": (
            "DESCENDANT_PIPE_FORGE child_signature=withheld" in forged_output),
        # On the classification-visible fields the forged PASS is
        # indistinguishable from the genuine detached control; only the
        # child-death/timeout evidence could ever tell them apart, and the
        # release record carries none.
        "release_shape_matches_genuine": (
            forged is not None and detached is not None
            and forged["verdict"] == detached["verdict"] == "PASS"
            and forged["actual_exit"] == detached["actual_exit"] == 0
            and forged["error"] is None and detached["error"] is None
            and (spoof_marker in forged_output)
                == (spoof_marker in detached_output)),
    }
    # Harness-side hygiene: reap the orphaned forged-signature descendants
    # (bounded sleeps that would self-exit in seconds anyway); never gated.
    for orphan_pid in (spoof_hold["descendant_pid"], forged_descendant_pid):
        if pid_alive(orphan_pid):
            try:
                os.kill(orphan_pid, signal.SIGKILL)
            except OSError:
                pass
    spoof_meta_ok = all(spoof_discriminations.values())
    results.append({"case": "probe_descendant_signature_spoof",
                    "verdict": "PASS" if spoof_meta_ok else "FAIL",
                    "mode": "bounded_popen_plus_cases_forgery_row",
                    "bound_seconds": spoof_bound,
                    "hold_arm": spoof_hold,
                    "hold_output_lines": spoof_text.strip().splitlines(),
                    "forged_release_case": "descendant_pipe_forged_signature_release",
                    "forged_release_descendant_pid": forged_descendant_pid,
                    "discriminations": spoof_discriminations,
                    "bounded_claim": "signature presence over merged captured output is origin-blind: a descendant's post-child-exit write of the expected signature satisfies it; accepted (verdict PASS) whenever the pipes release before the bound, separable only via the timed_out/child_exit_at_timeout evidence when held past it — documented forgery-accepting boundary, not a fix; Linux headless Godot 4.7.2 POSIX pipe semantics only"})
    print(f"{results[-1]['verdict']} descendant signature-spoof meta", flush=True)
    # r64 meta: while-live signature gate — the XConnector wave-3 synthesis
    # proposal ported to this fixture as a NEW observation path (additive;
    # classify_process is untouched). The pinned r63 boundary showed the
    # signature clause is origin-blind: a descendant's post-death write
    # satisfies it. This arm re-runs the SAME fixture arms under a
    # poll()-gated read: the marker is accepted only when observed while the
    # direct child is alive (poll() is None at the marker-completing read).
    # Prediction under test: forged signatures are reparenting-gated
    # post-death writes, so they can never be observed while-live — the gate
    # rejects a PRESENT marker; genuine child signatures are written before
    # quit() and observed inside the child's teardown window. A genuine rep
    # whose marker observation lands post-death falsifies the gate's
    # discrimination; the per-rep timing fields bound that nondeterminism
    # instead of hiding it.
    gate_marker = "DESCENDANT_PIPE_PROBE: expected signature"
    gate_bound = 3.0
    gate_poll_tick = 0.005
    # Load-bearing primitive: process.poll() (waitpid) — it REAPS the child,
    # so a dead process never reads alive. os.kill(pid,0)/pid_alive must NOT
    # be substituted: an unreaped zombie satisfies kill(pid,0) and measured
    # 13/13 false-accepts of the forged post-death signature (r64 critic).

    def gated_signature_run(case, extra_args):
        record = {"case": case, "flags": list(extra_args),
                  "bound_seconds": gate_bound, "timed_out": False,
                  "actual_exit": None, "error": None,
                  "marker_observed": False, "marker_observed_at": None,
                  "child_alive_at_marker_observation": None,
                  "child_alive_after_marker_read": None,
                  "dead_observed_at": None, "elapsed_seconds": None,
                  "withheld_banner": False, "write_ppid": None,
                  "godot_pid": None, "descendant_pid": None,
                  "descendant_alive_at_return": None,
                  "descendant_kernel_ppid_at_return": None,
                  "gated_signature_accepted": False,
                  "inner_classification": False}
        record["command"] = [args.godot, "--headless", "--path", str(scratch),
                             "--script", "res://descendant_pipe_probe.gd",
                             "--"] + list(extra_args)
        process = None
        started = time.monotonic()
        captured = bytearray()
        try:
            process = subprocess.Popen(record["command"], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            deadline = started + gate_bound
            with selectors.DefaultSelector() as gate_selector:
                gate_selector.register(process.stdout, selectors.EVENT_READ)
                gate_selector.register(process.stderr, selectors.EVENT_READ)
                while gate_selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        record["timed_out"] = True
                        break
                    events = gate_selector.select(
                        min(gate_poll_tick, max(0.0, remaining)))
                    now = time.monotonic()
                    if (record["dead_observed_at"] is None
                            and process.poll() is not None):
                        record["dead_observed_at"] = round(now - started, 6)
                    for key, _ in events:
                        alive_before = process.poll() is None
                        try:
                            chunk = os.read(key.fileobj.fileno(), 65536)
                        except OSError:
                            chunk = b""
                        if not chunk:
                            gate_selector.unregister(key.fileobj)
                            continue
                        captured += chunk
                        if (not record["marker_observed"]
                                and gate_marker.encode() in captured):
                            record["marker_observed"] = True
                            record["marker_observed_at"] = round(now - started, 6)
                            record["child_alive_at_marker_observation"] = alive_before
                            record["child_alive_after_marker_read"] = (
                                process.poll() is None)
            # dead_observed_at: first gated-read tick that saw the child dead;
            # None means the loop ended on pipe EOF before poll() observed the
            # exit (EOF can precede zombie reapability by microseconds) — for a
            # genuine arm that is itself while-live evidence.
            if (record["dead_observed_at"] is None
                    and process.poll() is not None):
                record["dead_observed_at"] = round(time.monotonic() - started, 6)
            if record["timed_out"]:
                record["error"] = f"TIMEOUT after {gate_bound} seconds"
            for stream in (process.stdout, process.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    record["error"] = (record["error"] or "") + "; post-kill wait timed out"
            record["actual_exit"] = process.returncode
        except (OSError, ValueError) as exc:
            record["error"] = f"launch/read error: {exc}"
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    record["error"] = (record["error"] or "") + "; forced cleanup timed out"
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        gate_text = captured.decode(errors="replace")
        record["withheld_banner"] = (
            "DESCENDANT_PIPE_FORGE child_signature=withheld" in gate_text)
        pid_match = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", gate_text)
        record["godot_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", gate_text)
        record["descendant_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", gate_text)
        record["write_ppid"] = int(pid_match.group(1)) if pid_match else None
        record["descendant_alive_at_return"] = pid_alive(record["descendant_pid"])
        record["descendant_kernel_ppid_at_return"] = kernel_ppid(
            record["descendant_pid"])
        record["gated_signature_accepted"] = bool(
            record["marker_observed"]
            and record["child_alive_at_marker_observation"])
        # The same captured bytes under the un-gated classifier: on the
        # release arm this is True while the gate rejects — the divergence
        # the pinned r63 boundary predicts.
        record["inner_classification"] = classify_process(
            record["actual_exit"], record["error"], gate_text, 0, gate_marker)
        record["output_lines"] = gate_text.strip().splitlines()
        return record

    gate_genuine = [gated_signature_run(f"genuine_default_r{i}", [])
                    for i in range(3)]
    gate_detach = [gated_signature_run("genuine_detach", ["--spawn-detach"])]
    gate_release = [gated_signature_run(f"forge_release_r{i}",
                                        ["--spawn-forge-release"])
                    for i in range(3)]
    gate_hold = gated_signature_run("forge_hold", ["--spawn-forge-hold"])
    gate_forged = gate_release + [gate_hold]
    gate_discriminations = {
        # Genuine signature: every default-arm rep's marker was captured and
        # observed while the child was still alive -> the gate accepts.
        "genuine_marker_accepted_while_live": all(
            r["marker_observed"]
            and r["child_alive_at_marker_observation"] is True
            and r["gated_signature_accepted"] for r in gate_genuine),
        # No genuine rep's marker ever landed post-death: zero observed
        # post-death observations across the reps (the falsification axis —
        # one False here means the gate cannot distinguish).
        "genuine_never_observed_post_death": all(
            r["child_alive_at_marker_observation"] is not False
            for r in gate_genuine),
        # Detached-descendant control: a genuine marker is not penalized for
        # a descendant that outlives the child with detached fds — the gate
        # discriminates the write's timing, not descendant existence.
        "detach_marker_accepted_while_live": (
            gate_detach[0]["marker_observed"]
            and gate_detach[0]["child_alive_at_marker_observation"] is True
            and gate_detach[0]["gated_signature_accepted"]),
        # The forged release-arm signature IS captured — provably after the
        # child's death was already observed (dead_observed_at precedes
        # marker_observed_at; the write is reparenting-gated): the gate
        # rejects a present marker, never an absent one.
        "forge_release_marker_captured_post_death": all(
            r["marker_observed"]
            and r["child_alive_at_marker_observation"] is False
            and r["dead_observed_at"] is not None
            and r["marker_observed_at"] is not None
            and r["dead_observed_at"] <= r["marker_observed_at"]
            for r in gate_release),
        # The un-gated classifier accepts exactly what the gate rejects:
        # same captured bytes, inner_classification True, gate False.
        "forge_release_gate_rejects_what_classifier_accepts": all(
            (not r["gated_signature_accepted"])
            and r["inner_classification"] is True for r in gate_release),
        # Hold arm: the same post-death forged write lands inside the bound
        # record and the gate rejects it there too.
        "forge_hold_marker_captured_post_death": (
            gate_hold["marker_observed"]
            and gate_hold["child_alive_at_marker_observation"] is False
            and gate_hold["dead_observed_at"] is not None
            and gate_hold["marker_observed_at"] is not None
            and gate_hold["dead_observed_at"] <= gate_hold["marker_observed_at"]),
        "forge_hold_gate_rejects": not gate_hold["gated_signature_accepted"],
        # Provenance: forged outputs carry the child's withheld banner plus a
        # write_ppid != godot_pid — the signature is descendant-authored.
        "forge_withheld_banner_present": all(
            r["withheld_banner"] for r in gate_forged),
        "forge_write_post_orphan": all(
            r["write_ppid"] is not None and r["godot_pid"] is not None
            and r["write_ppid"] != r["godot_pid"] for r in gate_forged),
        # Kernel corroboration on the hold arm (its descendant is still alive
        # at return — ~6s hold past the 3.0s bound): /proc ppid equals the
        # self-reported write_ppid. Release descendants exit before return;
        # their write_ppid stays fixture-asserted (r63 disclosure).
        "forge_hold_write_ppid_kernel_corroborated": (
            gate_hold["write_ppid"] is not None
            and gate_hold["descendant_kernel_ppid_at_return"]
                == gate_hold["write_ppid"]),
        "hold_descendant_orphaned_alive": (
            gate_hold["descendant_alive_at_return"] is True),
        # Headline divergence: every genuine arm accepted, every forged arm
        # rejected, on the same fixture and marker.
        "gate_discriminates_forged_from_genuine": (
            all(r["gated_signature_accepted"]
                for r in gate_genuine + gate_detach)
            and not any(r["gated_signature_accepted"] for r in gate_forged)),
    }
    # Harness-side hygiene: reap the orphaned descendants (bounded sleeps
    # that self-exit in seconds anyway); never gated.
    for gate_orphan in {r["descendant_pid"] for r in gate_detach + gate_forged}:
        if pid_alive(gate_orphan):
            try:
                os.kill(gate_orphan, signal.SIGKILL)
            except OSError:
                pass
    gate_meta_ok = all(gate_discriminations.values())
    results.append({"case": "probe_while_live_signature_gate",
                    "verdict": "PASS" if gate_meta_ok else "FAIL",
                    "mode": "poll_gated_bounded_popen_signature_read",
                    "bound_seconds": gate_bound,
                    "poll_tick_seconds": gate_poll_tick,
                    "arms": gate_genuine + gate_detach + gate_release + [gate_hold],
                    "discriminations": gate_discriminations,
                    "bounded_claim": "a poll()-gated signature read accepts the expected marker only when observed while the direct child is alive: genuine child signatures (default and detached-descendant arms) were observed while-live in every rep; reparenting-gated forged signatures (--spawn-forge-release/--spawn-forge-hold) arrived after observed child death in every rep and were rejected though present — on this fixture the gate discriminates forged post-death writes from genuine writes; not a claim that observation-time liveness proves authorship in general (a pre-death-scheduled or faster-racing forge is out of scope); Linux headless Godot 4.7.2 POSIX semantics only"})
    print(f"{results[-1]['verdict']} while-live signature-gate meta", flush=True)
    # r65 meta: forged-REJECTION dual — the error-axis mirror of the r63
    # signature-spoof boundary the r64 gate narrowed. classify_process's
    # error clause is a presence scan over the merged captured bytes: any
    # line containing "ERROR:" outside the per-case allowlist rejects,
    # regardless of which process wrote it or when. The new fixture arms
    # keep the CHILD clean (genuine signature printed while alive, exit 0)
    # and move the un-allowlisted error marker into a reparenting-gated
    # descendant write AFTER the child's death:
    #   release arm (--spawn-errforge-release): post-death error + write_ppid
    #     provenance, pipes release before the bound -> a clean exit-0 +
    #     signature-present record that FAILs only on the descendant's line.
    #   hold arm (--spawn-errforge-hold): same forged write with pipes held
    #     ~6s -> the error lands inside the TIMEOUT record (double-axis
    #     rejection: error + timeout) and the still-alive descendant's
    #     /proc ppid kernel-corroborates write_ppid.
    #   genuine control (--emit-errforge): the CHILD emits byte-identical
    #     error text pre-death via push_error (engine stderr path) -> the
    #     genuine-error control; classification-visible fields match the
    #     forged release record modulo the provenance lines (banner /
    #     spawned_pid / write_ppid / push_error at-line).
    # The arms are meta-driven bounded Popens, NOT CASES tuples: an
    # expected-FAIL record is inexpressible in the all-PASS battery (the
    # r62 hold-arm precedent). A dual-marker gated read then documents the
    # while-live gate's interplay: it accepts the genuine while-live
    # signature and never evaluates the error line — the forged error is
    # gate-invisible; rejection stays in the un-gated classifier.
    errforge_signature = "DESCENDANT_PIPE_PROBE: expected signature"
    errforge_error = "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
    errforge_bound = 3.0

    def errforge_run(case, extra_args, bound=errforge_bound):
        # Bounded Popen producing the record shape a CASES row would carry:
        # exit/error/output through the same communicate(timeout) bound.
        record = {"case": case, "flags": list(extra_args),
                  "bound_seconds": bound, "timed_out": False,
                  "child_exit_at_timeout": None, "actual_exit": None,
                  "error": None, "elapsed_seconds": None,
                  "signature_observed": False, "error_marker_captured": False,
                  "banner": None, "write_ppid": None, "godot_pid": None,
                  "descendant_pid": None, "descendant_alive_at_return": None,
                  "descendant_kernel_ppid_at_return": None,
                  "error_lines": [], "inner_classification": False,
                  "stripped_classification": None, "output_lines": []}
        record["command"] = [args.godot, "--headless", "--path", str(scratch),
                             "--script", "res://descendant_pipe_probe.gd",
                             "--"] + list(extra_args)
        proc = None
        started = time.monotonic()
        text = ""
        try:
            proc = subprocess.Popen(record["command"], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True,
                                    bufsize=1)
            try:
                ef_out, ef_err = proc.communicate(timeout=bound)
                text = (ef_out or "") + (ef_err or "")
                record["actual_exit"] = proc.returncode
            except subprocess.TimeoutExpired as exc:
                record["timed_out"] = True
                # poll() reaps the direct child: a non-None exit code here
                # proves the bound fired on pipe EOF with the child dead.
                record["child_exit_at_timeout"] = proc.poll()
                ef_out = (exc.stdout.decode(errors="replace")
                          if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
                ef_err = (exc.stderr.decode(errors="replace")
                          if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
                text = ef_out + ef_err
                record["error"] = f"TIMEOUT after {bound} seconds"
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
                        record["error"] += "; post-kill wait timed out"
        except (OSError, ValueError) as exc:
            record["error"] = f"launch/read error: {exc}"
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    record["error"] = (record["error"] or "") + "; forced cleanup timed out"
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        record["signature_observed"] = errforge_signature in text
        record["error_marker_captured"] = errforge_error in text
        record["error_lines"] = sorted(
            {line.strip() for line in text.splitlines() if "ERROR:" in line})
        for banner_line in text.splitlines():
            if banner_line.startswith("DESCENDANT_PIPE_ERRFORGE child"):
                record["banner"] = banner_line.strip()
        pid_match = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
        record["godot_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
        record["descendant_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(r"DESCENDANT_PIPE_ERRFORGE write_ppid=(\d+)", text)
        record["write_ppid"] = int(pid_match.group(1)) if pid_match else None
        record["descendant_alive_at_return"] = pid_alive(record["descendant_pid"])
        record["descendant_kernel_ppid_at_return"] = kernel_ppid(
            record["descendant_pid"])
        record["inner_classification"] = classify_process(
            record["actual_exit"], record["error"], text, 0, errforge_signature)
        # Counterfactual: the same captured bytes minus every ERROR: line —
        # isolates the forged error as the sole flip cause on clean records.
        stripped_text = "\n".join(
            line for line in text.splitlines() if "ERROR:" not in line)
        record["stripped_classification"] = classify_process(
            record["actual_exit"], record["error"], stripped_text, 0,
            errforge_signature)
        record["output_lines"] = text.strip().splitlines()
        return record

    def gated_errforge_run(case, extra_args):
        # Dual-marker variant of the r64 gated_signature_run: tracks BOTH
        # the signature marker and the ERROR: marker, pinning liveness at
        # each completing read — measures whether a while-live criterion on
        # the error axis would discriminate, and whether the built gate's
        # signature-only criterion sees the forged-error arm at all.
        record = {"case": case, "flags": list(extra_args),
                  "bound_seconds": errforge_bound, "timed_out": False,
                  "actual_exit": None, "error": None,
                  "signature_observed": False, "signature_observed_at": None,
                  "child_alive_at_signature_observation": None,
                  "child_alive_after_signature_read": None,
                  "error_observed": False, "error_observed_at": None,
                  "child_alive_at_error_observation": None,
                  "child_alive_after_error_read": None,
                  "dead_observed_at": None, "elapsed_seconds": None,
                  "banner": None, "write_ppid": None, "godot_pid": None,
                  "descendant_pid": None, "descendant_alive_at_return": None,
                  "descendant_kernel_ppid_at_return": None,
                  "gated_signature_accepted": False,
                  "inner_classification": False}
        record["command"] = [args.godot, "--headless", "--path", str(scratch),
                             "--script", "res://descendant_pipe_probe.gd",
                             "--"] + list(extra_args)
        process = None
        started = time.monotonic()
        captured = bytearray()
        signature_bytes = errforge_signature.encode()
        error_bytes = errforge_error.encode()
        try:
            process = subprocess.Popen(record["command"], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            deadline = started + errforge_bound
            with selectors.DefaultSelector() as ef_selector:
                ef_selector.register(process.stdout, selectors.EVENT_READ)
                ef_selector.register(process.stderr, selectors.EVENT_READ)
                while ef_selector.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        record["timed_out"] = True
                        break
                    events = ef_selector.select(
                        min(gate_poll_tick, max(0.0, remaining)))
                    now = time.monotonic()
                    if (record["dead_observed_at"] is None
                            and process.poll() is not None):
                        record["dead_observed_at"] = round(now - started, 6)
                    for key, _ in events:
                        alive_before = process.poll() is None
                        try:
                            chunk = os.read(key.fileobj.fileno(), 65536)
                        except OSError:
                            chunk = b""
                        if not chunk:
                            ef_selector.unregister(key.fileobj)
                            continue
                        captured += chunk
                        if (not record["signature_observed"]
                                and signature_bytes in captured):
                            record["signature_observed"] = True
                            record["signature_observed_at"] = round(now - started, 6)
                            record["child_alive_at_signature_observation"] = alive_before
                            record["child_alive_after_signature_read"] = (
                                process.poll() is None)
                        if (not record["error_observed"]
                                and error_bytes in captured):
                            record["error_observed"] = True
                            record["error_observed_at"] = round(now - started, 6)
                            record["child_alive_at_error_observation"] = alive_before
                            record["child_alive_after_error_read"] = (
                                process.poll() is None)
            if (record["dead_observed_at"] is None
                    and process.poll() is not None):
                record["dead_observed_at"] = round(time.monotonic() - started, 6)
            if record["timed_out"]:
                record["error"] = f"TIMEOUT after {errforge_bound} seconds"
            for stream in (process.stdout, process.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    record["error"] = (record["error"] or "") + "; post-kill wait timed out"
            record["actual_exit"] = process.returncode
        except (OSError, ValueError) as exc:
            record["error"] = f"launch/read error: {exc}"
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    record["error"] = (record["error"] or "") + "; forced cleanup timed out"
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        ef_gate_text = captured.decode(errors="replace")
        for banner_line in ef_gate_text.splitlines():
            if banner_line.startswith("DESCENDANT_PIPE_ERRFORGE child"):
                record["banner"] = banner_line.strip()
        pid_match = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", ef_gate_text)
        record["godot_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", ef_gate_text)
        record["descendant_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(r"DESCENDANT_PIPE_ERRFORGE write_ppid=(\d+)", ef_gate_text)
        record["write_ppid"] = int(pid_match.group(1)) if pid_match else None
        record["descendant_alive_at_return"] = pid_alive(record["descendant_pid"])
        record["descendant_kernel_ppid_at_return"] = kernel_ppid(
            record["descendant_pid"])
        record["gated_signature_accepted"] = bool(
            record["signature_observed"]
            and record["child_alive_at_signature_observation"])
        record["inner_classification"] = classify_process(
            record["actual_exit"], record["error"], ef_gate_text, 0,
            errforge_signature)
        record["output_lines"] = ef_gate_text.strip().splitlines()
        return record

    def split_errforge_run(case, extra_args, bound=errforge_bound):
        # Separate-PIPE capture: which stream carries the error marker is
        # classification-invisible after the merge — this records it anyway.
        record = {"case": case, "flags": list(extra_args),
                  "bound_seconds": bound, "actual_exit": None, "error": None,
                  "error_on_stdout": False, "error_on_stderr": False,
                  "merged_classification": None,
                  "raw_stdout_lines": [], "raw_stderr_lines": []}
        record["command"] = [args.godot, "--headless", "--path", str(scratch),
                             "--script", "res://descendant_pipe_probe.gd",
                             "--"] + list(extra_args)
        stdout_text, stderr_text = "", ""
        try:
            proc = subprocess.run(record["command"], capture_output=True,
                                  text=True, timeout=bound)
            stdout_text, stderr_text = proc.stdout or "", proc.stderr or ""
            record["actual_exit"] = proc.returncode
        except subprocess.TimeoutExpired as exc:
            stdout_text = (exc.stdout.decode(errors="replace")
                           if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
            stderr_text = (exc.stderr.decode(errors="replace")
                           if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
            record["error"] = f"TIMEOUT after {bound} seconds"
        except OSError as exc:
            record["error"] = f"launch error: {exc}"
        record["error_on_stdout"] = errforge_error in stdout_text
        record["error_on_stderr"] = errforge_error in stderr_text
        record["merged_classification"] = classify_process(
            record["actual_exit"], record["error"], stdout_text + stderr_text,
            0, errforge_signature)
        record["raw_stdout_lines"] = stdout_text.strip().splitlines()
        record["raw_stderr_lines"] = stderr_text.strip().splitlines()
        return record

    ef_release = errforge_run("errforge_release", ["--spawn-errforge-release"])
    ef_hold = errforge_run("errforge_hold", ["--spawn-errforge-hold"])
    ef_genuine = errforge_run("errforge_genuine", ["--emit-errforge"])
    ef_gate_release = [gated_errforge_run(f"errforge_release_gate_r{i}",
                                          ["--spawn-errforge-release"])
                       for i in range(3)]
    ef_gate_genuine = [gated_errforge_run(f"errforge_genuine_gate_r{i}",
                                          ["--emit-errforge"])
                       for i in range(2)]
    ef_release_split = split_errforge_run("errforge_release_split",
                                          ["--spawn-errforge-release"])
    ef_genuine_split = split_errforge_run("errforge_genuine_split",
                                          ["--emit-errforge"])

    def cases_visible(rec):
        # The fields a CASES row / classify_process verdict actually reads:
        # exit, runner error, signature presence, and the ERROR: line set.
        return {"actual_exit": rec["actual_exit"], "error": rec["error"],
                "signature_observed": rec["signature_observed"],
                "error_lines": rec["error_lines"],
                "classification": rec["inner_classification"]}

    ef_line_diff = sorted(
        set(ef_release["output_lines"]) ^ set(ef_genuine["output_lines"]))
    ef_diff_is_provenance_only = all(
        "ERROR:" not in line and errforge_signature not in line
        for line in ef_line_diff)
    ef_discriminations = {
        # The release arm is the CASES-row shape the claim targets: clean
        # exit 0, no timeout error, genuine signature present — FAILing only
        # because the descendant's post-death ERROR line is in the bytes.
        "release_clean_exit0_record": (
            not ef_release["timed_out"] and ef_release["actual_exit"] == 0
            and ef_release["error"] is None),
        "release_genuine_signature_present": ef_release["signature_observed"],
        "release_forged_error_captured": ef_release["error_marker_captured"],
        "release_error_write_post_orphan": (
            ef_release["write_ppid"] is not None
            and ef_release["godot_pid"] is not None
            and ef_release["write_ppid"] != ef_release["godot_pid"]),
        "release_flips_to_fail": ef_release["inner_classification"] is False,
        # Sole-cause isolation: stripping only the ERROR: lines from the
        # SAME captured bytes restores the PASS — the forged error is the
        # whole of the flip.
        "release_counterfactual_passes_without_error": (
            ef_release["stripped_classification"] is True),
        # Genuine-error control: byte-identical marker, child-authored
        # pre-death, no descendant provenance in the record.
        "genuine_clean_exit0_record": (
            not ef_genuine["timed_out"] and ef_genuine["actual_exit"] == 0
            and ef_genuine["error"] is None),
        "genuine_error_captured": ef_genuine["error_marker_captured"],
        "genuine_error_rejects": ef_genuine["inner_classification"] is False,
        "genuine_counterfactual_passes_without_error": (
            ef_genuine["stripped_classification"] is True),
        "genuine_carries_no_descendant_provenance": (
            ef_genuine["descendant_pid"] is None
            and ef_genuine["write_ppid"] is None),
        # Origin-blindness of the rejection axis: forged and genuine error
        # records agree on every classification-visible field; the output
        # line sets differ only in classification-invisible provenance lines
        # (banner / godot_pid / spawned_pid / write_ppid / push_error
        # at-line) — the r63-style withheld/ppid provenance, nothing else.
        "error_marker_bytes_identical": (
            ef_release["error_lines"] == ef_genuine["error_lines"]
            == [errforge_error]),
        "forged_vs_genuine_cases_fields_identical": (
            cases_visible(ef_release) == cases_visible(ef_genuine)),
        "forged_vs_genuine_differ_only_in_provenance": ef_diff_is_provenance_only,
        # The sibling CASES-row baseline: detached control stays a clean
        # exit-0 PASS — the forged error line is the only added content.
        "detached_control_row_still_passes": (
            detached is not None and detached["verdict"] == "PASS"
            and detached["actual_exit"] == 0 and detached["error"] is None),
        # Hold arm: the same forged write lands inside the TIMEOUT record —
        # rejection via the error axis AND the timeout axis together.
        "hold_timed_out_with_child_dead": (
            ef_hold["timed_out"] and ef_hold["child_exit_at_timeout"] == 0),
        "hold_forged_error_captured": ef_hold["error_marker_captured"],
        "hold_rejects": ef_hold["inner_classification"] is False,
        # Double-axis: strip every ERROR: line from the SAME captured bytes
        # and the hold record still rejects — the timeout axis alone does it.
        "hold_timeout_alone_rejects": (
            ef_hold["stripped_classification"] is False),
        "hold_write_ppid_kernel_corroborated": (
            ef_hold["write_ppid"] is not None
            and ef_hold["descendant_kernel_ppid_at_return"]
                == ef_hold["write_ppid"]
            and ef_hold["godot_pid"] is not None
            and ef_hold["write_ppid"] != ef_hold["godot_pid"]),
        "hold_descendant_orphaned_alive": (
            ef_hold["descendant_alive_at_return"] is True),
        # While-live gate interplay: the r64 criterion tracks the signature
        # marker only. On the forged-error arm the signature is genuinely
        # while-live -> the gate ACCEPTS; the forged error is captured
        # post-death but is gate-invisible. Rejection stays downstream in
        # the un-gated classifier: gate-accepted and still FAIL.
        "gate_release_signature_accepted_while_live": all(
            r["signature_observed"]
            and r["child_alive_at_signature_observation"] is True
            and r["gated_signature_accepted"] for r in ef_gate_release),
        "gate_release_forged_error_observed_post_death": all(
            r["error_observed"]
            and r["child_alive_at_error_observation"] is False
            and r["dead_observed_at"] is not None
            and r["error_observed_at"] is not None
            and r["dead_observed_at"] <= r["error_observed_at"]
            for r in ef_gate_release),
        "gate_does_not_reject_forged_error_arm": all(
            r["gated_signature_accepted"] and r["error_observed"]
            and r["inner_classification"] is False for r in ef_gate_release),
        "gate_genuine_error_observed_while_live": all(
            r["error_observed"]
            and r["child_alive_at_error_observation"] is True
            for r in ef_gate_genuine),
        # The timing data an error-axis gate would need is captured: forged
        # errors observed only post-death, genuine errors only while-live —
        # the same split r64 proved for the signature axis.
        "gate_error_axis_timing_split": (
            all(r["child_alive_at_error_observation"] is False
                for r in ef_gate_release)
            and all(r["child_alive_at_error_observation"] is True
                    for r in ef_gate_genuine)),
        # Stream split: descendant echo -> stdout, engine push_error ->
        # stderr; the merged classifier cannot see either origin.
        "forged_error_lands_on_stdout": (
            ef_release_split["error_on_stdout"]
            and not ef_release_split["error_on_stderr"]),
        "genuine_error_lands_on_stderr": (
            ef_genuine_split["error_on_stderr"]
            and not ef_genuine_split["error_on_stdout"]),
        "merged_classification_stream_blind": (
            ef_release_split["merged_classification"] is False
            and ef_genuine_split["merged_classification"] is False),
    }
    # Harness-side hygiene: reap the orphaned errforge descendants (bounded
    # sleeps that would self-exit in seconds anyway); never gated.
    for ef_orphan in {r["descendant_pid"] for r in
                      [ef_release, ef_hold, ef_genuine] + ef_gate_release}:
        if pid_alive(ef_orphan):
            try:
                os.kill(ef_orphan, signal.SIGKILL)
            except OSError:
                pass
    ef_meta_ok = all(ef_discriminations.values())
    results.append({"case": "probe_descendant_error_spoof",
                    "verdict": "PASS" if ef_meta_ok else "FAIL",
                    "mode": "bounded_popen_dual_marker_gate_and_stream_split",
                    "bound_seconds": errforge_bound,
                    "release_arm": ef_release,
                    "hold_arm": ef_hold,
                    "genuine_control": ef_genuine,
                    "gated_release_reps": ef_gate_release,
                    "gated_genuine_reps": ef_gate_genuine,
                    "split_release": ef_release_split,
                    "split_genuine": ef_genuine_split,
                    "provenance_only_line_diff": ef_line_diff,
                    "discriminations": ef_discriminations,
                    "bounded_claim": "the un-allowlisted-ERROR rejection axis is as origin-blind as the signature axis: a reparenting-gated descendant's post-death error write lands in the merged capture and flips a clean exit-0 + signature-present record to FAIL, byte-identical in classification-visible fields to the child-authored push_error control, separable only by the r63-style provenance lines (banner/spawned_pid/write_ppid) and write timing; the r64 while-live gate does NOT reject the forged-error arm — its criterion is the signature marker only, so the genuine while-live signature is accepted and the post-death error is gate-invisible, though the gated read does record the error arriving only after observed child death; Linux headless Godot 4.7.2 POSIX pipe semantics only"})
    print(f"{results[-1]['verdict']} descendant error-spoof meta", flush=True)
    # r66 meta: rejection-clause SURFACE map — tracks the r65 critic/boundary
    # measured edges that never became rows. Declared falsifiable claim: the
    # rejection clause's verdict is a pure function of merged-output line
    # presence modulo the allowlist — forgeable in BOTH directions (evasion
    # and fabrication) by a post-death descendant. Four new fixture arms are
    # meta-driven bounded Popens (never CASES tuples: expected-FAIL/evading
    # records are inexpressible in the all-PASS battery, r62 precedent):
    #   --spawn-allowforge   descendant echoes save_corrupt_negative's
    #     byte-exact ALLOWLISTED error post-death -> (a) the allowlist is the
    #     clause's preemptor row: identical captured bytes reject under ()
    #     and are verdict-inert under the matching entry (absorbed), and a
    #     foreign entry does not absorb.
    #   --spawn-splitforge   descendant writes "ERR\n" then "OR: ..." — the
    #     ERROR: token split across a newline EVADES the line-local scan:
    #     forged bytes captured, zero lines contain "ERROR:" -> PASS.
    #   --spawn-seamforge    descendant leaves an UNTERMINATED "...ERROR"
    #     stdout tail and a ": ..." stderr head post-death -> the runner's
    #     stdout+stderr concat FABRICATES a reject line present in neither
    #     stream (paired split-stream run proves the line's non-existence).
    #   --spawn-midlineforge descendant writes pre-death (write_ppid ==
    #     godot_pid) into the 200ms gap between the signature's two printraw
    #     halves -> fabricated ERROR: line AND destroyed signature substring
    #     (dual-clause corruption; the r65 stripped counterfactual cannot
    #     isolate the error as sole cause).
    # (b) the allowlist's three entry shapes (exact / `,`-prefix+count==1 /
    #   structured chain-incomplete) are re-measured through the REAL
    #   classify_process on captured + synthetic lines — the hcom-shaped
    #   gates.
    # (d) dead-entry census: every per-case expected_errors entry checked
    #   against this run's captured outputs (which entries no reachable
    #   child output tripped), plus the whole-blob SCRIPT ERROR:/Parse
    #   Error: clauses and the audio ObjectDB clause — carried as data,
    #   self-validated by the real classifier (bare vs allowlisted).
    surface_bound = 3.0
    surface_signature = "DESCENDANT_PIPE_PROBE: expected signature"
    allowforge_error = ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON "
                        "rejected signature=JSON_PARSE_ERROR")
    splitforge_tail = "OR: DESCENDANT_PIPE_SPLITFORGE newline-split diagnostic"
    seam_stdout_tail = "DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR"
    seam_stderr_head = ": SEAMFORGE phantom fabricated line"
    seam_fabricated = seam_stdout_tail + seam_stderr_head
    midline_error = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"

    def surface_run(case, extra_args, ppid_token, bound=surface_bound):
        # Bounded Popen producing the record shape a CASES row would carry:
        # exit/error/output through the same communicate(timeout) bound.
        record = {"case": case, "flags": list(extra_args),
                  "bound_seconds": bound, "timed_out": False,
                  "child_exit_at_timeout": None, "actual_exit": None,
                  "error": None, "elapsed_seconds": None,
                  "signature_observed": False, "error_lines": [],
                  "write_ppid": None, "godot_pid": None,
                  "descendant_pid": None, "descendant_alive_at_return": None,
                  "descendant_kernel_ppid_at_return": None,
                  "inner_classification": False, "output_lines": []}
        record["command"] = [args.godot, "--headless", "--path", str(scratch),
                             "--script", "res://descendant_pipe_probe.gd",
                             "--"] + list(extra_args)
        proc = None
        started = time.monotonic()
        text = ""
        try:
            proc = subprocess.Popen(record["command"], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True,
                                    bufsize=1)
            try:
                sf_out, sf_err = proc.communicate(timeout=bound)
                text = (sf_out or "") + (sf_err or "")
                record["actual_exit"] = proc.returncode
            except subprocess.TimeoutExpired as exc:
                record["timed_out"] = True
                record["child_exit_at_timeout"] = proc.poll()
                sf_out = (exc.stdout.decode(errors="replace")
                          if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
                sf_err = (exc.stderr.decode(errors="replace")
                          if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
                text = sf_out + sf_err
                record["error"] = f"TIMEOUT after {bound} seconds"
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
                        record["error"] += "; post-kill wait timed out"
        except (OSError, ValueError) as exc:
            record["error"] = f"launch/read error: {exc}"
        finally:
            if proc is not None and proc.poll() is None:
                proc.kill()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    record["error"] = (record["error"] or "") + "; forced cleanup timed out"
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        record["signature_observed"] = surface_signature in text
        record["error_lines"] = sorted(
            {line.strip() for line in text.splitlines() if "ERROR:" in line})
        pid_match = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
        record["godot_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
        record["descendant_pid"] = int(pid_match.group(1)) if pid_match else None
        pid_match = re.search(re.escape(ppid_token) + r"(\d+)", text)
        record["write_ppid"] = int(pid_match.group(1)) if pid_match else None
        record["descendant_alive_at_return"] = pid_alive(record["descendant_pid"])
        record["descendant_kernel_ppid_at_return"] = kernel_ppid(
            record["descendant_pid"])
        record["inner_classification"] = classify_process(
            record["actual_exit"], record["error"], text, 0, surface_signature)
        record["output_lines"] = text.strip().splitlines()
        return record, text

    def surface_split_run(case, extra_args, bound=surface_bound):
        # Separate-PIPE capture: the fabricated seam line's non-existence is
        # stream-level data the merged clause can never see — record it.
        record = {"case": case, "flags": list(extra_args),
                  "bound_seconds": bound, "actual_exit": None, "error": None,
                  "merged_classification": None,
                  "raw_stdout_lines": [], "raw_stderr_lines": []}
        record["command"] = [args.godot, "--headless", "--path", str(scratch),
                             "--script", "res://descendant_pipe_probe.gd",
                             "--"] + list(extra_args)
        try:
            proc = subprocess.run(record["command"], capture_output=True,
                                  text=True, timeout=bound)
            stdout_text, stderr_text = proc.stdout or "", proc.stderr or ""
            record["actual_exit"] = proc.returncode
        except subprocess.TimeoutExpired as exc:
            stdout_text = (exc.stdout.decode(errors="replace")
                           if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
            stderr_text = (exc.stderr.decode(errors="replace")
                           if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
            record["error"] = f"TIMEOUT after {bound} seconds"
        except OSError as exc:
            stdout_text, stderr_text = "", ""
            record["error"] = f"launch error: {exc}"
        record["raw_stdout_lines"] = stdout_text.strip().splitlines()
        record["raw_stderr_lines"] = stderr_text.strip().splitlines()
        record["stdout_tail_line"] = (record["raw_stdout_lines"][-1]
                                    if record["raw_stdout_lines"] else None)
        record["stderr_head_line"] = (record["raw_stderr_lines"][0]
                                    if record["raw_stderr_lines"] else None)
        record["merged_classification"] = classify_process(
            record["actual_exit"], record["error"], stdout_text + stderr_text,
            0, surface_signature)
        return record

    sf_allow, sf_allow_text = surface_run(
        "surface_allowforge", ["--spawn-allowforge"],
        "DESCENDANT_PIPE_ALLOWFORGE write_ppid=")
    sf_split, sf_split_text = surface_run(
        "surface_splitforge", ["--spawn-splitforge"],
        "DESCENDANT_PIPE_SPLITFORGE write_ppid=")
    sf_seam, sf_seam_text = surface_run(
        "surface_seamforge", ["--spawn-seamforge"],
        "DESCENDANT_PIPE_SEAMFORGE write_ppid=")
    sf_mid, sf_mid_text = surface_run(
        "surface_midlineforge", ["--spawn-midlineforge"],
        "DESCENDANT_PIPE_MIDLINE write_ppid=")
    sf_seam_split = surface_split_run(
        "surface_seamforge_split", ["--spawn-seamforge"])

    def surface_classify(text, allowed=()):
        return classify_process(0, None, text, 0, surface_signature, allowed)

    def shape_text(line):
        return f"Godot banner\n{surface_signature}\n{line}\n"

    allowforge_stripped = "\n".join(
        line for line in sf_allow_text.splitlines() if "ERROR:" not in line)
    splitforge_stripped_lines = [line.strip() for line in
                                 sf_split_text.splitlines()]
    splitforge_contiguous = sf_split_text.replace("ERR\nOR:", "ERROR:")
    mid_stripped = "\n".join(
        line for line in sf_mid_text.splitlines() if "ERROR:" not in line)
    midline_spliced = next(
        (line.strip() for line in sf_mid_text.splitlines()
         if "DESCENDANT_PIPE_PROBE: expected " in line
         and midline_error in line), None)

    comma_entry = ("ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file "
                   "rejected signature=FILE_NOT_FOUND,")
    comma_line = ("ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file "
                  "rejected signature=FILE_NOT_FOUND, path=/tmp/x")
    structured_entry = "ERROR: chain incomplete"
    structured_line = ("ERROR: chain incomplete collections=1 "
                       "scene=SceneB:<Node#7> old_alive=false")
    # (b) hcom-shaped entry gates re-measured through the REAL classifier —
    # each cell is (entry, line, expected_absorbed): the observed verdict is
    # `absorbed` = classify under (entry,) on a record whose only ERROR: is
    # that line.
    shape_matrix = {
        "exact__exact_line": {
            "entry_shape": "exact", "line": allowforge_error,
            "expected_absorbed": True,
            "absorbed": surface_classify(shape_text(allowforge_error),
                                         (allowforge_error,))},
        "exact__suffixed_twin": {
            "entry_shape": "exact",
            "line": allowforge_error + " ERROR: tail-forged",
            "expected_absorbed": False,
            "absorbed": surface_classify(
                shape_text(allowforge_error + " ERROR: tail-forged"),
                (allowforge_error,))},
        "comma__prefix_line": {
            "entry_shape": "comma_prefix", "line": comma_line,
            "expected_absorbed": True,
            "absorbed": surface_classify(shape_text(comma_line),
                                         (comma_entry,))},
        "comma__count2_tail_forge": {
            "entry_shape": "comma_prefix",
            "line": comma_line + " ERROR: tail-forged",
            "expected_absorbed": False,
            "absorbed": surface_classify(
                shape_text(comma_line + " ERROR: tail-forged"),
                (comma_entry,))},
        "comma__unanchored_line": {
            "entry_shape": "comma_prefix",
            "line": "prefix text " + comma_line,
            "expected_absorbed": False,
            "absorbed": surface_classify(
                shape_text("prefix text " + comma_line), (comma_entry,))},
        "comma_entry__exact_shaped_line": {
            "entry_shape": "comma_prefix", "line": allowforge_error,
            "expected_absorbed": False,
            "absorbed": surface_classify(sf_allow_text,
                                         (allowforge_error + ",",))},
        "structured__full_shape": {
            "entry_shape": "structured", "line": structured_line,
            "expected_absorbed": True,
            "absorbed": surface_classify(shape_text(structured_line),
                                         (structured_entry,))},
        "structured__missing_conjunct": {
            "entry_shape": "structured",
            "line": ("ERROR: chain incomplete collections=1 "
                     "scene=SceneB:<Node#7>"),
            "expected_absorbed": False,
            "absorbed": surface_classify(
                shape_text("ERROR: chain incomplete collections=1 "
                           "scene=SceneB:<Node#7>"), (structured_entry,))},
        "structured__count2_tail_forge": {
            "entry_shape": "structured",
            "line": structured_line + " ERROR: tail-forged",
            "expected_absorbed": False,
            "absorbed": surface_classify(
                shape_text(structured_line + " ERROR: tail-forged"),
                (structured_entry,))},
    }

    # (d) dead-entry census — data, self-validated by the real classifier.
    # surface_allowed_error mirrors allowed_error (nested in
    # classify_process) solely to attribute WHICH entry matched WHICH line;
    # the load-bearing verdict is re-derived via classify_process itself.
    def surface_allowed_error(line, allowed):
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

    def entry_shape(entry):
        if entry == "ERROR: chain incomplete":
            return "structured"
        if entry.endswith(","):
            return "comma_prefix"
        return "exact"

    census_rows = []
    for row in results:
        entries = row.get("expected_errors") or []
        if not entries or not isinstance(row.get("output"), list):
            continue
        row_text = "\n".join(row["output"])
        entry_records = []
        for entry in entries:
            matched = [line.strip() for line in row["output"]
                       if surface_allowed_error(line, entry)]
            entry_records.append({"entry": entry, "shape": entry_shape(entry),
                                  "matched_lines": len(matched),
                                  "first_match": matched[0] if matched else None,
                                  "dead_in_run": not matched})
        # r89 reviewer F6 guard: a tuple signature passed straight into
        # classify_process would raise TypeError (`signature in output`) and
        # crash the census instead of failing a discrimination. Unreachable
        # today — no envelope row carries expected_errors entries — but an
        # envelope row that gains one must still classify. Dispatch on the
        # signature tuple exactly as execute() does: PASS iff ANY whitelisted
        # payload satisfies the clause.
        census_signatures = (row["signature"]
                             if isinstance(row["signature"], (tuple, list))
                             else (row["signature"],))
        bare_rejects = not any(
            classify_process(
                row["actual_exit"], row["error"], row_text,
                row["expected_exit"], sig, ())
            for sig in census_signatures)
        allowlisted_passes = any(
            classify_process(
                row["actual_exit"], row["error"], row_text,
                row["expected_exit"], sig, tuple(entries))
            for sig in census_signatures)
        census_rows.append({
            "case": row["case"], "verdict": row["verdict"],
            "entries": entry_records,
            "any_entry_matched": any(not e["dead_in_run"]
                                     for e in entry_records),
            "bare_classification_rejects": bare_rejects,
            "allowlisted_classification_passes": allowlisted_passes})
    dead_entries = [{"case": r["case"], "entry": e["entry"],
                     "shape": e["shape"]}
                    for r in census_rows for e in r["entries"]
                    if e["dead_in_run"]]
    blob_clause_counts = {
        "SCRIPT ERROR:": 0, "Parse Error:": 0,
        "ERROR:_per_line_lines": 0,
        "objectdb_leak_audio_lines": 0}
    for row in results:
        for line in row.get("output") or []:
            if "SCRIPT ERROR:" in line:
                blob_clause_counts["SCRIPT ERROR:"] += 1
            if "Parse Error:" in line:
                blob_clause_counts["Parse Error:"] += 1
            if "ERROR:" in line:
                blob_clause_counts["ERROR:_per_line_lines"] += 1
            if re.fullmatch(
                    r"WARNING: [1-9][0-9]* ObjectDB instances were leaked at exit"
                    r"(?: \(run with `--verbose` for details\)\.)?",
                    line.strip()):
                blob_clause_counts["objectdb_leak_audio_lines"] += 1
    surface_census = {
        "scope": "every CASES row carrying expected_errors in this battery "
                 "run; opt-in probe rows execute after this census (their "
                 "inline allowlists are listed, not censused)",
        "rows_with_expected_errors": len(census_rows),
        "rows": census_rows,
        "dead_entry_count": len(dead_entries),
        "dead_entries": dead_entries,
        "scan_clause_census": blob_clause_counts,
        "clause_granularity": ("\"ERROR:\" is per-line "
                               "(output.splitlines() scan); \"SCRIPT ERROR:\" "
                               "and \"Parse Error:\" are whole-blob "
                               "substrings — the labrat-flagged granularity "
                               "asymmetry: a newline-split SCRIPT/parse "
                               "token evades entirely"),
        "allowlists_outside_expected_errors": [
            "export_preset_missing executes classify with (evidence,) inline",
            "classify_mutant holds three inline tuples (probe-failing only)",
            "stream probe uses classify_streams allowed_stderr=()",
            "probe_audio_warning uses default allowlist ()"],
    }

    error_spoof_row = next((r for r in results
                            if r["case"] == "probe_descendant_error_spoof"), None)
    prior_meta_stable = (
        error_spoof_row is not None and error_spoof_row["verdict"] == "PASS"
        and len(error_spoof_row.get("discriminations", {})) == 29
        and all(error_spoof_row["discriminations"].values())
        and all((next((r for r in results if r["case"] == name), None) or {})
                .get("verdict") == "PASS"
                for name in ("probe_save_independent_process",
                             "probe_spontaneous_crash_classification",
                             "probe_descendant_pipe_eof",
                             "probe_descendant_signature_spoof",
                             "probe_while_live_signature_gate")))
    seam_stdout_last = sf_seam_split["raw_stdout_lines"][-1].strip() \
        if sf_seam_split["raw_stdout_lines"] else None
    seam_stderr_first = sf_seam_split["raw_stderr_lines"][0].strip() \
        if sf_seam_split["raw_stderr_lines"] else None
    seam_fabricated_lines = [line.strip() for line in
                             sf_seam_text.splitlines()
                             if line.strip() == seam_fabricated]
    sf_discriminations = {
        # (a) allowlist-as-preemptor on REAL captured bytes: the forged
        # allowlisted line is verdict-inert iff the matching entry is given.
        "allowforge_clean_exit0_record": (
            not sf_allow["timed_out"] and sf_allow["actual_exit"] == 0
            and sf_allow["error"] is None),
        "allowforge_signature_present": sf_allow["signature_observed"],
        "allowforge_forged_error_captured": (
            sf_allow["error_lines"] == [allowforge_error]),
        "allowforge_write_post_orphan": (
            sf_allow["write_ppid"] is not None
            and sf_allow["godot_pid"] is not None
            and sf_allow["write_ppid"] != sf_allow["godot_pid"]),
        "allowforge_rejects_without_allowlist": (
            surface_classify(sf_allow_text, ()) is False),
        "allowforge_absorbed_by_matching_allowlist": (
            surface_classify(sf_allow_text, (allowforge_error,)) is True),
        "allowforge_rejects_under_foreign_allowlist": (
            surface_classify(sf_allow_text,
                             ("ERROR: unrelated different diagnostic",))
            is False),
        "allowforge_counterfactual_passes_without_error": (
            surface_classify(allowforge_stripped, ()) is True),
        # (b) the hcom-shaped entry gates — all nine cells land as declared.
        "allowlist_shape_matrix_all_expected": all(
            cell["absorbed"] == cell["expected_absorbed"]
            for cell in shape_matrix.values()),
        # (c) line-faithfulness — evasion: the split token's bytes are in
        # the record yet no line contains "ERROR:" -> merged scan accepts.
        "splitforge_clean_exit0_record": (
            not sf_split["timed_out"] and sf_split["actual_exit"] == 0
            and sf_split["error"] is None),
        "splitforge_signature_present": sf_split["signature_observed"],
        "splitforge_forged_bytes_in_record": (
            "ERR" in splitforge_stripped_lines
            and splitforge_tail in splitforge_stripped_lines),
        "splitforge_no_error_line_captured": sf_split["error_lines"] == [],
        "splitforge_evades_merged_scan": (
            sf_split["inner_classification"] is True),
        "splitforge_contiguous_twin_rejects": (
            surface_classify(splitforge_contiguous, ()) is False),
        "splitforge_write_post_orphan": (
            sf_split["write_ppid"] is not None
            and sf_split["godot_pid"] is not None
            and sf_split["write_ppid"] != sf_split["godot_pid"]),
        # (c) line-faithfulness — fabrication: the reject line exists only
        # in the merged concat; the split-stream run proves it is present
        # in neither stdout nor stderr's own line set.
        "seamforge_clean_exit0_record": (
            not sf_seam["timed_out"] and sf_seam["actual_exit"] == 0
            and sf_seam["error"] is None),
        "seamforge_signature_present": sf_seam["signature_observed"],
        "seamforge_fabricated_line_in_merged": len(seam_fabricated_lines) == 1,
        "seamforge_fabricated_line_rejects": (
            sf_seam["inner_classification"] is False),
        "seamforge_line_in_neither_stream": (
            seam_fabricated not in sf_seam_split["raw_stdout_lines"]
            and seam_fabricated not in sf_seam_split["raw_stderr_lines"]
            and seam_stdout_last == seam_stdout_tail
            and seam_stderr_first == seam_stderr_head),
        "seamforge_split_run_also_rejects_post_merge": (
            sf_seam_split["merged_classification"] is False),
        "seamforge_write_post_orphan": (
            sf_seam["write_ppid"] is not None
            and sf_seam["godot_pid"] is not None
            and sf_seam["write_ppid"] != sf_seam["godot_pid"]),
        # (c) mid-signature splice: fabricated ERROR: line AND destroyed
        # signature substring — the r65 sole-cause counterfactual cannot
        # isolate the error (strip the error lines and the record still
        # rejects on the signature axis).
        "midlineforge_error_spliced_into_signature": (
            midline_spliced is not None),
        "midlineforge_signature_destroyed": (
            sf_mid["signature_observed"] is False),
        "midlineforge_rejects": sf_mid["inner_classification"] is False,
        "midlineforge_counterfactual_defeated": (
            surface_classify(mid_stripped, ()) is False),
        "midlineforge_write_pre_death": (
            sf_mid["write_ppid"] is not None
            and sf_mid["godot_pid"] is not None
            and sf_mid["write_ppid"] == sf_mid["godot_pid"]),
        # Headline: each arm's verdict follows merged-output line presence
        # modulo the allowlist — forgeable in both directions.
        "surface_verdicts_follow_merged_line_presence": (
            surface_classify(sf_allow_text, ()) is False
            and surface_classify(sf_allow_text, (allowforge_error,)) is True
            and sf_split["inner_classification"] is True
            and sf_seam["inner_classification"] is False
            and sf_mid["inner_classification"] is False),
        # (d) census integrity — carried as data; only coverage/consistency
        # is gated (dead entries themselves are data, not a failure).
        "census_covers_all_allowlisted_rows": all(
            (r.get("expected_errors") or []) == [] or any(
                cr["case"] == r["case"] for cr in census_rows)
            for r in results if isinstance(r.get("output"), list)),
        "census_bare_classifier_consistent": all(
            r["any_entry_matched"] == r["bare_classification_rejects"]
            for r in census_rows),
        "census_allowlisted_reproduces_verdicts": all(
            r["allowlisted_classification_passes"] == (r["verdict"] == "PASS")
            for r in census_rows),
        # Within-run prior-row stability anchors.
        "detached_control_row_still_passes": (
            detached is not None and detached["verdict"] == "PASS"
            and detached["actual_exit"] == 0 and detached["error"] is None),
        "prior_meta_rows_stable_29_discriminations": prior_meta_stable,
        # r79 critic C2: expected_errors was ceiling-not-floor — a dead
        # allowlist entry (never matched a real emitted line) passed
        # silently. All phys2d_* entries must each match (r80 critic C1:
        # the prefix covers phys2d_motion_* too, not just phys2d_events_).
        "phys2d_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("phys2d_")
            for e in r["entries"]),
        # r87 critic F3 / reviewer F3 / scribe F3: the r87 whitelist cases
        # (input_lattice_null_edge, r87_edge_jpbe, ei_bound_refusal) were
        # outside the phys2d_ prefix — ceiling-not-floor again. Prefixes
        # cover all r87 whitelist-bearing cases; entry-less cases are inert.
        "r87_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith(("input_lattice_", "r87_edge_",
                                    "ei_bound"))
            for e in r["entries"]),
        # r88 author: the new whitelist cases use the r88_ prefix, outside
        # the r87 gate's coverage — extend the all-matched floor
        # deliberately so a dead r88 entry cannot pass silently either.
        "r88_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("r88_")
            for e in r["entries"]),
        # r89 author: the new whitelist cases use the geo2d_lattice_ prefix
        # (atlasempty, polyendpoly); input89_edges_ carries no entries but is
        # covered so a future r89 entry under it cannot die silently either —
        # same named-by-round / covers-round-prefixes shape as the r87 gate.
        "r89_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith(("geo2d_lattice_", "input89_edges_"))
            for e in r["entries"]),
        # r90 author: the r90 block's whitelist-bearing cases (comrefuse,
        # impedge) and every sibling row carry the r90_ prefix — same
        # named-by-round / covers-round-prefixes shape as the r87/r89 gates.
        "r90_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("r90_")
            for e in r["entries"]),
        # r91 author: the two whitelist-bearing cases (nav_lattice_sync,
        # nav_lattice_bake) and every sibling row carry the nav_lattice_
        # prefix — same named-by-round / covers-round-prefixes shape.
        "r91_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("nav_lattice_")
            for e in r["entries"]),
        # r92 author: the nine whitelist-bearing cases (atlas … physics)
        # and every sibling row carry the r92_ prefix — same
        # named-by-round / covers-round-prefixes shape as r87–r91.
        "r92_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("r92_")
            for e in r["entries"]),
        # r93 author: the r93 block carries no expected_errors entries
        # today (every arm is ERROR:-clean, 0 B stderr across the 78
        # scout + 274 boundary receipts) — the gate is carried anyway so
        # a future r93 allowlist entry cannot die silently; same
        # named-by-round / covers-round-prefixes shape as r87–r92.
        "r93_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("r93_")
            for e in r["entries"]),
        # r94 author: the r94 block carries no expected_errors entries
        # today (every arm is ERROR:-clean, 0 B stderr across the 143
        # scout + 734 boundary receipts and this seat's smoke pass) — the
        # gate is carried anyway so a future r94 allowlist entry cannot
        # die silently; same named-by-round / covers-round-prefixes shape
        # as r87–r93.
        "r94_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith("r94_")
            for e in r["entries"]),
        # r95 author: the r95 block carries no expected_errors entries
        # today (every arm is ERROR:-clean, 0 B stderr across the 150
        # scout + 261 boundary receipts and this seat's 52-arm smoke
        # pass on the fixture bytes) — the gate is carried anyway so a
        # future r95 allowlist entry cannot die silently; same
        # named-by-round / covers-round-prefixes shape as r87-r94.
        "r95_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith(("dss_lattice_", "r95b_order_"))
            for e in r["entries"]),
        # r96 author: the two whitelist-bearing cases (ownership pokes
        # the non-ancestor + self-owner refusals; refuse exercises the
        # save/load refusal surface — 15 entries total) and every sibling
        # row carry the r96_scene_io_ / r96b_ prefixes — same
        # named-by-round / covers-round-prefixes shape as r87-r95.
        "r96_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith(("r96_scene_io_", "r96b_"))
            for e in r["entries"]),
        # r100 author: the three whitelist-bearing cases (the render cell's
        # deterministic dummy-texture readback ERROR plus its two seq
        # replays) carry the r100_gui_ / r100b_ prefixes — same
        # named-by-round / covers-round-prefixes shape as r87-r96, so a dead
        # r100 allowlist entry cannot pass silently.
        "r100_expected_errors_all_matched": all(
            not e["dead_in_run"]
            for r in census_rows
            if r["case"].startswith(("r100_gui_", "r100b_"))
            for e in r["entries"]),
    }
    # Harness-side hygiene: reap any lingering surface descendants (all arms
    # self-exit in well under a second; never gated).
    for sf_orphan in (sf_allow["descendant_pid"], sf_split["descendant_pid"],
                      sf_seam["descendant_pid"], sf_mid["descendant_pid"]):
        if pid_alive(sf_orphan):
            try:
                os.kill(sf_orphan, signal.SIGKILL)
            except OSError:
                pass
    sf_meta_ok = all(sf_discriminations.values())
    results.append({"case": "probe_error_clause_surface",
                    "verdict": "PASS" if sf_meta_ok else "FAIL",
                    "mode": "bounded_popen_surface_arms_plus_allowlist_census",
                    "bound_seconds": surface_bound,
                    "arms": [sf_allow, sf_split, sf_seam, sf_mid],
                    "seam_split_run": sf_seam_split,
                    "midline_spliced_line": midline_spliced,
                    "shape_matrix": shape_matrix,
                    "census": surface_census,
                    "discriminations": sf_discriminations,
                    "bounded_claim": "the rejection clause's verdict is a pure function of merged-output line presence modulo the per-case allowlist — measured forgeable in both directions by a post-death descendant on this fixture: (a) a forged error matching the allowlist is verdict-inert (absorbed) while the identical captured bytes reject under () and under a foreign entry; (b) exact/, -prefix/count==1/structured entry shapes all gate as declared incl. tail-forge count==2 defeats; (c) ERR\\n+OR: newline-split EVADES the line-local scan while a stdout-tail+stderr-head seam FABRICATES a reject line present in neither stream, and a pre-death mid-signature splice fabricates an error line AND destroys the signature substring (dual-clause corruption); (d) dead-entry census over expected_errors carried as data, self-validated by the real classifier; Linux headless Godot 4.7.2 POSIX pipe semantics only"})
    print(f"{results[-1]['verdict']} error-clause surface meta", flush=True)
    if args.probe_midlineforge_ladder:
        # r68 meta: the midlineforge fabrication-window bound measured as an
        # offset LADDER, not the r66/r67 80ms point sample. Each nominal
        # descendant write offset re-runs the real --spawn-midlineforge arm
        # (delay parameterized via --midline-offset-ms=N, default 80 — the
        # point sample) for fixed reps through the same bounded-Popen record
        # shape as the surface arms. Per rep the merged record is checked for
        # the spliced head+ERROR line (fabrication landed inside the gap)
        # versus an intact signature (write missed the gap — lands after the
        # tail). Claimed strict bound: fabrication lands exactly on a
        # downward-closed nominal-offset set — every landed offset is below
        # every missed offset, with any jitter-split (mixed) cell inside the
        # gap between them. Opt-in only: flagless battery rows are unchanged.
        midline_ladder_offsets = (0, 40, 80, 120, 160, 240)
        midline_ladder_reps = 3
        midline_gap_ms = 200
        ladder_cells = []
        for off_ms in midline_ladder_offsets:
            cell_reps = []
            for rep_i in range(midline_ladder_reps):
                lad_rec, lad_text = surface_run(
                    f"midline_ladder_{off_ms}ms_r{rep_i}",
                    ["--spawn-midlineforge", f"--midline-offset-ms={off_ms}"],
                    "DESCENDANT_PIPE_MIDLINE write_ppid=")
                lad_rec["spliced_line"] = next(
                    (line.strip() for line in lad_text.splitlines()
                     if "DESCENDANT_PIPE_PROBE: expected " in line
                     and midline_error in line), None)
                lad_rec["fabrication_landed"] = (
                    lad_rec["spliced_line"] is not None)
                cell_reps.append(lad_rec)
            reps_landed = sum(1 for r in cell_reps if r["fabrication_landed"])
            ladder_cells.append({
                "offset_ms": off_ms, "reps": cell_reps,
                "reps_landed": reps_landed,
                "outcome": ("fabricated" if reps_landed == midline_ladder_reps
                            else "missed" if reps_landed == 0 else "mixed")})
        landed_offsets = [c["offset_ms"] for c in ladder_cells
                          if c["outcome"] == "fabricated"]
        missed_offsets = [c["offset_ms"] for c in ladder_cells
                          if c["outcome"] == "missed"]
        mixed_offsets = [c["offset_ms"] for c in ladder_cells
                         if c["outcome"] == "mixed"]
        all_ladder_reps = [r for c in ladder_cells for r in c["reps"]]
        measured_window = {
            "landed_offsets_ms": landed_offsets,
            "missed_offsets_ms": missed_offsets,
            "mixed_offsets_ms": mixed_offsets,
            "lo_edge_ms": min(landed_offsets) if landed_offsets else None,
            "hi_edge_ms": min(missed_offsets) if missed_offsets else None,
            "nominal_gap_ms": midline_gap_ms,
            "bound_semantics": ("fabrication lands iff the descendant write "
                                "reaches the captured pipe between the "
                                "signature head flush and the tail flush; a "
                                "nominal offset differs from its gap-relative "
                                "position by fork/exec+sleep latency (~2-3ms "
                                "measured on this host — write_ms - head_ms "
                                "= offset + ~2.5), so the nominal hi edge "
                                "sits just under the 200ms gap end")}
        ladder_discriminations = {
            # Every rep is a clean exit-0 record — the ladder measures byte
            # placement, never a crash/timeout interaction.
            "ladder_all_reps_clean_exit0": all(
                r["actual_exit"] == 0 and r["error"] is None
                and not r["timed_out"] for r in all_ladder_reps),
            # Provenance: every write is pre-death (write_ppid == godot_pid).
            "ladder_all_writes_pre_death": all(
                r["write_ppid"] is not None and r["godot_pid"] is not None
                and r["write_ppid"] == r["godot_pid"] for r in all_ladder_reps),
            # Both outcomes reject: fabrication via signature+error clauses,
            # a missed write via the standalone ERROR: line.
            "ladder_all_reps_reject": all(
                r["inner_classification"] is False for r in all_ladder_reps),
            # The r66 point sample reproduces: 80ms fabricates in every rep.
            "point_sample_80ms_still_fabricates": (
                [c["outcome"] for c in ladder_cells if c["offset_ms"] == 80]
                == ["fabricated"]),
            # Over the 200ms gap: 240ms never fabricates in any rep.
            "over_gap_240ms_never_fabricates": (
                [c["outcome"] for c in ladder_cells if c["offset_ms"] == 240]
                == ["missed"]),
            # Strict measured bound: the landed set is downward-closed —
            # every fabricated offset below every missed offset, with any
            # jitter-split cell inside the band between them.
            "window_is_strict_threshold": (
                bool(landed_offsets) and bool(missed_offsets)
                and max(landed_offsets) < min(missed_offsets)
                and all(max(landed_offsets) < m < min(missed_offsets)
                        for m in mixed_offsets)),
            # Fabrication couples exactly to signature destruction per rep:
            # a landed splice destroys the marker; a miss leaves it intact.
            "fabrication_iff_signature_destroyed": all(
                r["fabrication_landed"] == (not r["signature_observed"])
                for r in all_ladder_reps),
            # The fabricated line is byte-exact head+ERROR fusion.
            "spliced_line_is_head_error_fusion": all(
                r["spliced_line"] is None
                or (r["spliced_line"].startswith(
                        "DESCENDANT_PIPE_PROBE: expected ")
                    and midline_error in r["spliced_line"])
                for r in all_ladder_reps),
        }
        # Harness-side hygiene: reap any lingering ladder descendants (each
        # exits right after its write; never gated).
        for lad_orphan in {r["descendant_pid"] for r in all_ladder_reps}:
            if pid_alive(lad_orphan):
                try:
                    os.kill(lad_orphan, signal.SIGKILL)
                except OSError:
                    pass
        ladder_meta_ok = all(ladder_discriminations.values())
        ladder_payload = {
            "mode": "real_godot_midlineforge_offset_ladder",
            "bound_seconds": surface_bound,
            "offsets_ms": list(midline_ladder_offsets),
            "reps_per_offset": midline_ladder_reps,
            "ladder": ladder_cells,
            "measured_window": measured_window,
            "discriminations": ladder_discriminations,
            "verdict": "PASS" if ladder_meta_ok else "FAIL",
            "bounded_claim": ("the midlineforge fabrication window has a "
                              "strict measured nominal-offset bound on this "
                              "host: every offset whose descendant write "
                              "reaches the captured stdout pipe between the "
                              "signature head and tail flushes fabricates "
                              "the merged ERROR: line AND destroys the "
                              "signature; offsets at/over the gap edge miss "
                              "(signature intact, error standalone); "
                              "measured on Linux headless Godot 4.7.2 with "
                              "~2.5ms fork/exec+sleep latency between "
                              "nominal offset and gap-relative position")}
        ladder_artifact = run_dir / "midlineforge-ladder-verdicts.json"
        ladder_artifact.write_text(json.dumps(ladder_payload, indent=2) + "\n")
        results.append({"case": "probe_midlineforge_ladder",
                        "verdict": ladder_payload["verdict"],
                        "artifact": str(ladder_artifact),
                        "measured_window": measured_window,
                        "discriminations": ladder_discriminations})
        print(f"{ladder_payload['verdict']} midlineforge offset-ladder meta: {ladder_artifact}", flush=True)
    if args.probe_midlineforge_gapladder:
        # r69 meta: pin the fabrication-window bound's REFERENT — gap-
        # relative vs absolute — via the crossed ladder the r68 offset
        # ladder cannot express. --midline-offset-ms is held at 80 (the
        # r66 point sample) while the signature gap itself is swept via
        # --midline-gap-ms=N (default 200 — the r66/r68 arm is byte-
        # stable). Declared falsifiable claim: the window follows
        # offset<gap — fabrication lands iff the descendant write
        # reaches the captured pipe before the tail flush AT ANY gap
        # size. Falsified if fabrication persists at a gap below the
        # write's position (gap=50: the write demonstrably lands
        # post-tail — an intact signature is the byte-order ground
        # truth, since write_ppid==godot_pid can lag the ppid flip by
        # process teardown and is carried as data only) or fails at a
        # gap far above it (gap=800); either outcome would make the
        # bound an absolute write-latency constant instead of the gap.
        # Predicted set under the claim (nominal offset<gap; effective
        # position = offset + ~2.5ms spawn latency, nearest cell margin
        # ~17.5ms >> ~1ms jitter): fabricated at {100,200,400,800},
        # missed at {50}.
        gapladder_gaps = (50, 100, 200, 400, 800)
        gapladder_offset_ms = 80
        gapladder_reps = 3
        # Declared sweep at fixed offset 80 + the crossed cells the r69
        # critic proved are the ONLY region distinguishing gap-relative
        # from an absolute ~198ms-style edge: offset inside (edge, gap).
        # (300,400)/(300,800)/(600,800) fabricate under gap-relative
        # (pos<gap) but must ALL miss under any absolute edge < pos.
        gapladder_cells = ([(gapladder_offset_ms, g) for g in gapladder_gaps]
                           + [(300, 400), (300, 800), (600, 800)])
        gap_cells = []
        for offset_ms, gap_ms in gapladder_cells:
            cell_reps = []
            for rep_i in range(gapladder_reps):
                gap_rec, gap_text = surface_run(
                    f"midline_off{offset_ms}_gap_{gap_ms}ms_r{rep_i}",
                    ["--spawn-midlineforge",
                     f"--midline-offset-ms={offset_ms}",
                     f"--midline-gap-ms={gap_ms}"],
                    "DESCENDANT_PIPE_MIDLINE write_ppid=")
                gap_rec["gap_ms"] = gap_ms
                gap_rec["offset_ms"] = offset_ms
                gap_rec["spliced_line"] = next(
                    (line.strip() for line in gap_text.splitlines()
                     if "DESCENDANT_PIPE_PROBE: expected " in line
                     and midline_error in line), None)
                gap_rec["fabrication_landed"] = (
                    gap_rec["spliced_line"] is not None)
                # Data only — NOT a post-tail gate: the ppid flip lags
                # the tail flush by process teardown, so a post-tail
                # write can still sample write_ppid==godot_pid. Byte
                # order (spliced_line / signature_observed) is ground
                # truth.
                gap_rec["write_pre_death"] = (
                    gap_rec["write_ppid"] is not None
                    and gap_rec["godot_pid"] is not None
                    and gap_rec["write_ppid"] == gap_rec["godot_pid"])
                cell_reps.append(gap_rec)
            reps_landed = sum(1 for r in cell_reps
                              if r["fabrication_landed"])
            gap_cells.append({
                "gap_ms": gap_ms,
                "offset_ms": offset_ms,
                "write_inside_gap": offset_ms < gap_ms,
                "reps": cell_reps,
                "reps_landed": reps_landed,
                "outcome": ("fabricated"
                            if reps_landed == gapladder_reps
                            else "missed" if reps_landed == 0
                            else "mixed")})
        landed_gaps = [c["gap_ms"] for c in gap_cells
                       if c["outcome"] == "fabricated"]
        missed_gaps = [c["gap_ms"] for c in gap_cells
                       if c["outcome"] == "missed"]
        mixed_gaps = [c["gap_ms"] for c in gap_cells
                      if c["outcome"] == "mixed"]
        inside_gaps = [c["gap_ms"] for c in gap_cells
                       if c["write_inside_gap"]]
        outside_cells = [c for c in gap_cells if not c["write_inside_gap"]]
        # Crossed cells (offset above the r68 ~198ms edge, inside the
        # gap): the only region separating gap-relative from an absolute
        # edge — under gap-relative they fabricate (pos<gap); under any
        # absolute edge below their position they must all miss.
        cross_cells = [c for c in gap_cells if c["offset_ms"] > 198]
        cross_all_fab = all(c["outcome"] == "fabricated"
                            for c in cross_cells)
        cross_all_miss = all(c["outcome"] == "missed" for c in cross_cells)
        all_gap_reps = [r for c in gap_cells for r in c["reps"]]
        # The referent verdict, computed from the measured pattern:
        # gap-relative iff fabrication lands exactly on the cells whose
        # gap exceeds the write offset (incl. the crossed cells);
        # absolute-edge iff the crossed cells all miss while the base
        # inside cells fabricate; absolute-write-latency iff it lands on
        # EVERY cell; anything else is unclassified data.
        if (sorted(landed_gaps) == sorted(inside_gaps)
                and (not cross_cells or cross_all_fab)):
            referent_verdict = "gap_relative"
        elif cross_all_miss and all(
                c["outcome"] == "fabricated" for c in gap_cells
                if c["offset_ms"] <= 198 and c["write_inside_gap"]):
            referent_verdict = "absolute_edge"
        elif (not mixed_gaps and not missed_gaps
              and len(landed_gaps) == len(gap_cells)):
            referent_verdict = "absolute_write_latency"
        else:
            referent_verdict = "unclassified"
        measured_referent = {
            "offset_ms": gapladder_offset_ms,
            "crossed_cells_ms": [
                [c["offset_ms"], c["gap_ms"]] for c in cross_cells],
            "landed_gaps_ms": landed_gaps,
            "missed_gaps_ms": missed_gaps,
            "mixed_gaps_ms": mixed_gaps,
            "inside_gap_gaps_ms": inside_gaps,
            "referent_verdict": referent_verdict,
            "bound_semantics": (
                "the fabrication lands iff the descendant write reaches "
                "the captured stdout pipe before the signature tail "
                "flush — write position inside the gap. Effective write "
                "position = nominal offset + ~2.5ms fork/exec+sleep "
                "latency (r68 measured), so at offset 80 the write sits "
                "~82.5ms: inside every gap >= 100 cell (margin >= ~17ms "
                "vs ~1ms jitter) and outside the 50ms cell. Post-tail "
                "ground truth is byte order — the intact signature line "
                "+ standalone ERROR line — never write_ppid, whose flip "
                "lags process teardown (a post-tail write can still "
                "sample write_ppid==godot_pid); pre-death is proven the "
                "other direction: a splice at gap >= 100 means the "
                "child was still inside delay_msec when the write "
                "landed")}
        gapladder_discriminations = {
            # Every rep is a clean exit-0 record — the ladder measures
            # byte placement, never a crash/timeout interaction.
            "gapladder_all_reps_clean_exit0": all(
                r["actual_exit"] == 0 and r["error"] is None
                and not r["timed_out"] for r in all_gap_reps),
            # Both outcomes still reject: fabrication via
            # signature+error clauses, a post-tail write via the
            # standalone ERROR: line.
            "gapladder_all_reps_reject": all(
                r["inner_classification"] is False
                for r in all_gap_reps),
            # Fabrication couples exactly to signature destruction per
            # rep (r68 coupling carried across the gap axis).
            "gapladder_fabrication_iff_signature_destroyed": all(
                r["fabrication_landed"] == (not r["signature_observed"])
                for r in all_gap_reps),
            # The spliced line is byte-exact head+ERROR fusion.
            "gapladder_spliced_line_is_head_error_fusion": all(
                r["spliced_line"] is None
                or (r["spliced_line"].startswith(
                        "DESCENDANT_PIPE_PROBE: expected ")
                    and midline_error in r["spliced_line"])
                for r in all_gap_reps),
            # The r66/r68 anchor cell reproduces at the default gap:
            # gap=200 == the historic arm byte-for-byte, fabricated in
            # every rep.
            "gap200_anchor_still_fabricates": (
                [c["outcome"] for c in gap_cells if c["gap_ms"] == 200]
                == ["fabricated"]),
            # Horn 1: fabrication does NOT persist at gap < write
            # position — the 50ms cell misses in every rep and the
            # intact signature (byte-order ground truth) proves the
            # write landed post-tail.
            "sub_offset_gap_never_fabricates": all(
                c["outcome"] == "missed" for c in outside_cells),
            "sub_offset_signature_intact_post_tail": all(
                r["signature_observed"] for c in outside_cells
                for r in c["reps"]),
            # Horn 2: fabrication does NOT fail at gap > write
            # position — every super-offset cell fabricates in every
            # rep, and every such write is provably pre-death
            # (write_ppid==godot_pid while the child is still inside
            # delay_msec(gap>=100): reliable in this direction).
            "super_offset_gaps_always_fabricate": all(
                c["outcome"] == "fabricated" for c in gap_cells
                if c["write_inside_gap"]),
            "super_offset_writes_pre_death": all(
                r["write_pre_death"] for c in gap_cells
                if c["write_inside_gap"] for r in c["reps"]),
            # THE referent discrimination: the measured pattern is
            # exactly offset<gap — the declared claim.
            "window_referent_is_gap_relative": (
                referent_verdict == "gap_relative"),
            # The crossed cells are the distinguishing region: every
            # offset>198 inside-gap cell fabricates — refuting any
            # absolute edge below ~602ms (r69 critic correction; the
            # declared fixed-offset grid alone cannot separate the
            # models).
            "crossed_cells_refute_absolute_edge": cross_all_fab,
            # Wiring witness: crossed-cell wall time tracks the gap —
            # a miswired run that ignored --midline-gap-ms finishes in
            # ~0.1s; elapsed > gap/2 proves the long gap ran.
            "crossed_cells_elapsed_tracks_gap": all(
                r["elapsed_seconds"] is not None
                and r["elapsed_seconds"] > c["gap_ms"] / 2000.0
                for c in cross_cells for r in c["reps"]),
        }
        # Harness-side hygiene: reap any lingering gapladder
        # descendants (each exits right after its write; never gated).
        for gap_orphan in {r["descendant_pid"] for r in all_gap_reps}:
            if pid_alive(gap_orphan):
                try:
                    os.kill(gap_orphan, signal.SIGKILL)
                except OSError:
                    pass
        gapladder_meta_ok = all(gapladder_discriminations.values())
        gapladder_payload = {
            "mode": "real_godot_midlineforge_gap_ladder",
            "bound_seconds": surface_bound,
            "offset_ms": gapladder_offset_ms,
            "gaps_ms": list(gapladder_gaps),
            "crossed_cells_ms": [
                [c["offset_ms"], c["gap_ms"]] for c in cross_cells],
            "reps_per_gap": gapladder_reps,
            "gapladder": gap_cells,
            "measured_referent": measured_referent,
            "discriminations": gapladder_discriminations,
            "verdict": "PASS" if gapladder_meta_ok else "FAIL",
            "bounded_claim": (
                "the midlineforge fabrication-window bound is "
                "gap-relative, not an absolute write-latency constant: "
                "at a fixed 80ms write offset the splice lands exactly "
                "on the cells whose signature gap exceeds the write "
                "position (measured: fabricated at {100,200,400,800}, "
                "missed at 50 with the intact signature proving the "
                "post-tail write), and the crossed cells (offset>198 "
                "inside the gap) fabricate too — refuting any absolute "
                "edge below ~602ms; the bound's referent is the gap — "
                "write position < tail flush — on Linux headless Godot "
                "4.7.2 POSIX pipe semantics only")}
        gapladder_artifact = run_dir / "midlineforge-gapladder-verdicts.json"
        gapladder_artifact.write_text(
            json.dumps(gapladder_payload, indent=2) + "\n")
        results.append({"case": "probe_midlineforge_gapladder",
                        "verdict": gapladder_payload["verdict"],
                        "artifact": str(gapladder_artifact),
                        "measured_referent": measured_referent,
                        "discriminations": gapladder_discriminations})
        print(f"{gapladder_payload['verdict']} midlineforge gap-ladder meta: {gapladder_artifact}", flush=True)
    if args.probe_failing:
        destination = scratch / "scene_b.tscn"
        original = destination.read_text()
        assert 'marker = "B"' in original, "seeded scene B marker changed; cannot run mutation"
        destination.write_text(original.replace('marker = "B"', 'marker = "BROKEN"', 1))
        execute("mutant_broken_scene_route", "causal_chain.gd", [], 2, "chain incomplete", mutate=True)
        execute("mutant_level_collision_removed", "level_collision/level_probe.gd", ["--no-collision"], 2,
                "LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry", mutate=True)
    if args.probe_export_launch:
        # Isolated Linux/X11 exported-app launch probe. Both variants are scratch-only;
        # the negative removes only the startup script attachment, then exercises
        # the exact same signature assertion against the launched process.
        launch_root = run_dir / "export-launch"
        positive = launch_root / "positive"
        negative = launch_root / "negative"
        shutil.copytree(scratch, positive, ignore=shutil.ignore_patterns(".godot", "out"))
        shutil.copytree(scratch, negative, ignore=shutil.ignore_patterns(".godot", "out"))
        expected_launch = "EXPORT_LAUNCH_READY scene=fixture"
        launch_results = []

        def configure_launch(project, with_event):
            scene = project / "export_launch.tscn"
            script = project / "export_launch.gd"
            scene.write_text('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://export_launch.gd" id="1"]\n\n[node name="ExportLaunch" type="Node"]\nscript = ExtResource("1")\n')
            event_code = ('    print("EXPORT_LAUNCH_READY scene=fixture")\n' if with_event else '')
            script.write_text('extends Node\n\nfunc _ready() -> void:\n' + event_code + '    get_tree().quit()\n')
            project_file = project / "project.godot"
            config = project_file.read_text()
            config = config.replace('config/features=PackedStringArray("4.7")\n', 'config/features=PackedStringArray("4.7")\nrun/main_scene="res://export_launch.tscn"\n', 1)
            project_file.write_text(config)

        def launch_variant(label, project, with_event):
            configure_launch(project, with_event)
            out_dir = project / "out"
            out_dir.mkdir(exist_ok=True)
            executable = (out_dir / "fixture-launch.x86_64").resolve()
            export_cmd = [args.godot, "--headless", "--path", str(project), "--export-debug", "Linux/X11", str(executable)]
            exp_output, exp_code, exp_error = run_process(export_cmd, 60)
            exp_ok = (classify_process(exp_code, exp_error, exp_output, 0, "[ DONE ]")
                      and "savepack" in exp_output and executable.is_file() and executable.stat().st_size > 0)
            export_bytes = executable.stat().st_size if executable.is_file() else 0
            pack_path = executable.with_suffix(".pck")
            pack_bytes = pack_path.stat().st_size if pack_path.is_file() else 0
            pack_sha256 = hashlib.sha256(pack_path.read_bytes()).hexdigest() if pack_bytes else None
            launch_cmd = [str(executable), "--headless"]
            # Run with cwd containing only exported products, never source project files.
            launch_cwd = str(out_dir)
            launch_output, launch_code, launch_error = "", None, "export failed; launch skipped"
            if exp_ok:
                try:
                    proc = subprocess.run(launch_cmd, cwd=launch_cwd, capture_output=True, text=True, timeout=5)
                    launch_output, launch_code, launch_error = proc.stdout + proc.stderr, proc.returncode, None
                except subprocess.TimeoutExpired as exc:
                    launch_output = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                    launch_output += (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                    launch_code, launch_error = None, "TIMEOUT after 5 seconds"
            signature_lines = [line.strip() for line in launch_output.splitlines() if line.strip() == expected_launch]
            asserted = (exp_ok and classify_process(launch_code, launch_error, launch_output, 0, expected_launch)
                        and len(signature_lines) == 1 and not (Path(launch_cwd) / "project.godot").exists()
                        and not (Path(launch_cwd) / "export_launch.gd").exists()
                        and not (Path(launch_cwd) / "export_launch.tscn").exists())
            clean_without_signature = (launch_code == 0 and launch_error is None
                and "SCRIPT ERROR:" not in launch_output and "Parse Error:" not in launch_output
                and "ERROR:" not in launch_output)
            products = sorted(item.name for item in out_dir.iterdir())
            executable_sha256 = hashlib.sha256(executable.read_bytes()).hexdigest() if executable.is_file() else None
            for item in list(out_dir.iterdir()):
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            launch_results.append({"case": label, "expected_signature": expected_launch,
                "expected_startup_event": with_event, "export_command": export_cmd,
                "export_exit": exp_code, "export_error": exp_error,
                "export_output": exp_output.strip().splitlines(), "export_bytes": export_bytes,
                "executable_sha256": executable_sha256, "pack_bytes": pack_bytes,
                "pack_sha256": pack_sha256,
                "launch_command": launch_cmd, "launch_cwd": launch_cwd, "launch_exit": launch_code,
                "launch_error": launch_error, "launch_output": launch_output.strip().splitlines(),
                "clean_process_without_signature": clean_without_signature,
                "same_signature_assertion": asserted, "products_before_cleanup": products,
                "products_after_cleanup": sorted(item.name for item in out_dir.iterdir())})

        launch_variant("export_launch_positive", positive, True)
        launch_variant("export_launch_missing_startup_event", negative, False)
        launch_payload = {"display": os.environ.get("DISPLAY"), "expected_signature": expected_launch,
                          "results": launch_results,
                          "verdict": "PASS" if launch_results[0]["same_signature_assertion"]
                          and launch_results[1]["export_exit"] == 0
                          and launch_results[1]["export_bytes"] > 0
                          and not launch_results[1]["same_signature_assertion"]
                          and launch_results[1]["clean_process_without_signature"]
                          and launch_results[0]["pack_sha256"] != launch_results[1]["pack_sha256"]
                          and all(not r["products_after_cleanup"] for r in launch_results) else "FAIL"}
        (run_dir / "export-launch-verdicts.json").write_text(json.dumps(launch_payload, indent=2) + "\n")
        results.append({"case": "probe_export_launch", "verdict": launch_payload["verdict"],
                        "artifact": str(run_dir / "export-launch-verdicts.json"),
                        "positive_assertion": launch_results[0]["same_signature_assertion"],
                        "negative_assertion": launch_results[1]["same_signature_assertion"]})
        print(f"{launch_payload['verdict']} export launch probe: {run_dir / 'export-launch-verdicts.json'}", flush=True)

    if args.probe_godot_error:
        expected_error = "ERROR: " + "EXPECTED_NEGATIVE: deliberate assertion rejected"
        unrelated_error = "ERROR: " + "UNRELATED_FAULT: unrelated engine diagnostic"
        probe_results = []
        for label, flags in (("godot_error_expected_negative", []),
                             ("godot_error_unrelated", ["--unrelated-error"])):
            command = [args.godot, "--headless", "--path", str(scratch), "--script",
                       "res://godot_error_probe.gd", "--", *flags]
            output, code, error = run_process(command, 8)
            inner = classify_process(code, error, output, 1,
                                     "EXPECTED_NEGATIVE: deliberate assertion rejected",
                                     (expected_error,))
            record = {"case": label, "command": command, "expected_exit": 1,
                      "actual_exit": code, "error": error,
                      "signature": "EXPECTED_NEGATIVE: deliberate assertion rejected",
                      "inner_classification": inner, "raw_output": output,
                      "raw_output_lines": output.strip().splitlines()}
            probe_results.append(record)
            print(f"{'PASS' if inner else 'FAIL'} {label}: exit={code} classification={inner}", flush=True)
        clean, fault = probe_results
        def exact_error_lines(record, diagnostic):
            return [line.strip() for line in record["raw_output_lines"]
                    if line.strip().startswith("ERROR:") and line.strip() == diagnostic]

        clean_expected_lines = exact_error_lines(clean, expected_error)
        fault_expected_lines = exact_error_lines(fault, expected_error)
        fault_unrelated_lines = exact_error_lines(fault, unrelated_error)
        script_paths = [record["command"][record["command"].index("--script") + 1]
                        for record in probe_results]
        same_script = len(set(script_paths)) == 1 and script_paths[0] == "res://godot_error_probe.gd"
        same_expected_exit = clean["expected_exit"] == fault["expected_exit"] == 1
        same_signature = clean["signature"] == fault["signature"]
        clean_emitted_expected = len(clean_expected_lines) == 1
        fault_emitted_expected = len(fault_expected_lines) == 1
        fault_emitted_unrelated = len(fault_unrelated_lines) == 1
        meta_pass = (clean["inner_classification"] and not fault["inner_classification"]
                     and clean_emitted_expected and fault_emitted_expected and fault_emitted_unrelated
                     and clean["actual_exit"] == fault["actual_exit"] == 1
                     and same_script and same_expected_exit and same_signature)
        probe_payload = {"mode": "real_godot_push_error", "same_script": same_script,
                         "script_paths": script_paths, "same_expected_exit": same_expected_exit,
                         "same_signature": same_signature,
                         "expected_diagnostic": expected_error,
                         "unrelated_diagnostic": unrelated_error, "results": probe_results,
                         "expected_error_lines": {"clean": clean_expected_lines, "fault": fault_expected_lines},
                         "unrelated_error_lines": fault_unrelated_lines,
                         "emitted_expected_once_in_both": clean_emitted_expected and fault_emitted_expected,
                         "unrelated_emitted_once_in_fault": fault_emitted_unrelated,
                         "verdict": "PASS" if meta_pass else "FAIL"}
        artifact = run_dir / "godot-error-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({"case": "probe_godot_error", "verdict": probe_payload["verdict"],
                        "artifact": str(artifact), "inner_classifications":
                        [r["inner_classification"] for r in probe_results]})
        print(f"{probe_payload['verdict']} Godot diagnostic probe: {artifact}")

    if args.probe_stream_attribution:
        def run_process_streams(command, timeout_seconds):
            try:
                proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
                return proc.stdout, proc.stderr, proc.returncode, None
            except subprocess.TimeoutExpired as exc:
                out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                return out, err, None, f"TIMEOUT after {timeout_seconds} seconds"
            except OSError as exc:
                return "", str(exc), None, f"launch error: {exc}"

        stdout_sig = "STREAM_STDOUT: expected attribution marker"
        stderr_diag = "STREAM_STDERR: unrelated attribution diagnostic"
        probe_results = []
        for label, flags in (("stream_accept", []),
                             ("stream_reject", ["--stderr-unrelated"])):
            command = [args.godot, "--headless", "--path", str(scratch), "--script",
                       "res://stream_attribution_probe.gd", "--", *flags]
            stdout, stderr, code, error = run_process_streams(command, 8)
            inner = classify_streams(code, error, stdout, stderr, 0, stdout_sig, allowed_stderr=())
            record = {
                "case": label,
                "command": command,
                "expected_exit": 0,
                "actual_exit": code,
                "error": error,
                "signature": stdout_sig,
                "inner_classification": inner,
                "raw_stdout": stdout,
                "raw_stderr": stderr,
                "raw_stdout_lines": stdout.strip().splitlines() if stdout else [],
                "raw_stderr_lines": stderr.strip().splitlines() if stderr else [],
            }
            probe_results.append(record)
            print(f"{'PASS' if inner else 'FAIL'} {label}: exit={code} classification={inner}", flush=True)

        accept, reject = probe_results

        def has_exact_stdout(record, marker_text):
            return any(line.strip() == marker_text for line in record["raw_stdout_lines"])

        def has_exact_stderr(record, marker_text):
            return any(line.strip() == marker_text for line in record["raw_stderr_lines"])

        script_paths = [record["command"][record["command"].index("--script") + 1]
                        for record in probe_results]
        same_script = (len(set(script_paths)) == 1
                       and script_paths[0] == "res://stream_attribution_probe.gd")
        accept_stdout_ok = has_exact_stdout(accept, stdout_sig)
        reject_stdout_ok = has_exact_stdout(reject, stdout_sig)
        accept_no_stderr_diag = not has_exact_stderr(accept, stderr_diag)
        reject_has_stderr_diag = has_exact_stderr(reject, stderr_diag)
        same_exit = accept["actual_exit"] == reject["actual_exit"] == 0
        meta_pass = (
            accept["inner_classification"] is True
            and reject["inner_classification"] is False
            and accept_stdout_ok and reject_stdout_ok
            and accept_no_stderr_diag and reject_has_stderr_diag
            and same_exit and same_script
            and accept["error"] is None and reject["error"] is None
        )

        # r67 additive meta arm: PER-CHANNEL divergence map between the merged
        # classifier (classify_process over stdout + stderr) and the
        # per-stream classifier (classify_streams). Each arm is one real
        # Godot run of the same fixture steering ERROR:/signature bytes per
        # channel; the SAME captured streams are classified by BOTH
        # classifiers and the verdict pair is recorded, alongside
        # allowlist-shape reclassifications that need no extra runs.
        sd_stdout_error = "ERROR: STREAMDIV stdout-carried diagnostic"
        sd_stderr_error = "ERROR: STREAMDIV stderr-carried diagnostic"
        sd_structured_line = ("ERROR: chain incomplete collections=streamdiv "
                              "scene=SceneB:<Node#6700> old_alive=false")
        sd_structured_entry = "ERROR: chain incomplete"
        sd_seam_tail = "STREAMDIV seam tail ends in ERROR"
        sd_seam_head = ": STREAMDIV seam phantom merged-only line"
        sd_script_tail = "STREAMDIV seam tail ends in SCRIPT ERR"
        sd_script_head = "OR: STREAMDIV seamed blob clause"
        sd_sig_head = "STREAM_STDOUT: expected attribution "
        sd_sig_tail = "marker"

        # r68 receipt-shape upgrades. (a) divergent_clause: per-row signature
        # of WHICH classifier clause diverged, from the taxonomy
        # {exit,signature,error_scan,blob,allowlist_shape}. The clause
        # attribution re-derives each classifier's per-clause verdicts on the
        # SAME captured streams through allowlist mirrors — the verdicts
        # themselves stay the real classify_process/classify_streams calls
        # (the r66 surface_allowed_error census precedent: mirrors attribute,
        # they never decide). (b) raw_stdout_sha256/raw_stderr_sha256 pin the
        # exact captured bytes both classifiers consumed — the same-input
        # gate: a dual record proves both verdicts saw byte-identical input.
        # r69 adds raw_merged_sha256 = sha256(so + se): the merged-concat
        # digest binds the byte ORDER the merged classifier consumed —
        # concat-order drift (stderr before stdout, or a seam-mutated
        # concat) changes it while leaving both per-channel digests
        # untouched (the r66 stderr+stdout caveat).
        sd_clause_taxonomy = ("exit", "signature", "error_scan", "blob",
                              "allowlist_shape")

        def sd_merged_line_allowed(line, allowed):
            # Mirror of allowed_error nested in classify_process
            # (attribution only — the verdict is re-derived from the real
            # classify_process call, never from this mirror).
            stripped = line.strip()
            if stripped == allowed:
                return True
            if allowed.endswith(","):
                return (stripped.startswith(allowed)
                        and stripped.count("ERROR:") == 1)
            if allowed == "ERROR: chain incomplete":
                return (stripped.startswith("ERROR: chain incomplete collections=")
                        and "scene=SceneB:<Node#" in stripped
                        and "old_alive=false" in stripped
                        and stripped.count("ERROR:") == 1)
            return False

        def sd_stream_line_allowed(stripped, allowed):
            # Mirror of line_allowed nested in classify_streams.
            if stripped in allowed:
                return True
            for a in allowed:
                if (a.endswith(",") and stripped.startswith(a)
                        and stripped.count("ERROR:") == 1):
                    return True
            return False

        def divergent_clause(so, se, code, error, merged_allowed,
                             stream_allowed):
            """The differing classifier clauses on the SAME captured streams.

            Each classifier's verdict is a conjunction of clauses; a clause
            lands in the signature iff its verdict differs between the
            classifiers on this input. Clause granularity pins the r67
            mechanisms: signature (merged=anywhere, streams=stdout-only),
            blob (whole-blob SCRIPT ERROR:/Parse Error: vs per-stream),
            error_scan (merged scans merged lines for ERROR: — stdout
            coverage + seam fabrication; streams scans every stderr line),
            allowlist_shape (an ERROR:-carrying stderr line absorbed by
            merged's entry shapes yet rejected by streams' matcher, or the
            converse), exit (identical clause on identical input — listed
            for completeness, cannot diverge).
            """
            merged_text = so + se
            diffs = []
            if (stdout_sig in merged_text) != (stdout_sig in so):
                diffs.append("signature")
            merged_blob = ("SCRIPT ERROR:" in merged_text
                           or "Parse Error:" in merged_text)
            stream_blob = any(token in so or token in se
                              for token in ("SCRIPT ERROR:", "Parse Error:"))
            if merged_blob != stream_blob:
                diffs.append("blob")
            merged_rejects = [
                line for line in merged_text.splitlines()
                if "ERROR:" in line
                and not any(sd_merged_line_allowed(line, allowed)
                            for allowed in merged_allowed)]
            stream_rejects = [
                stripped for stripped in
                (line.strip() for line in se.splitlines())
                if stripped
                and not sd_stream_line_allowed(stripped, stream_allowed)]
            if bool(merged_rejects) != bool(stream_rejects):
                # If every streams-rejected stderr line is an ERROR:-carrying
                # line the merged allowlist would absorb, the asymmetry is in
                # entry SHAPE (merged's structured/comma/exact matchers vs
                # line_allowed's exact/comma-only set) — attribute
                # allowlist_shape; otherwise the scan coverage itself
                # diverged (stdout ERROR: absorbed, seam-fabricated line,
                # non-ERROR: stderr strictness).
                if (stream_rejects and all(
                        "ERROR:" in line
                        and any(sd_merged_line_allowed(line, allowed)
                                for allowed in merged_allowed)
                        for line in stream_rejects)):
                    diffs.append("allowlist_shape")
                else:
                    diffs.append("error_scan")
            return diffs

        def dual_classify(so, se, code, error,
                          merged_allowed=(), stream_allowed=()):
            """Run BOTH classifiers over the same captured streams."""
            merged = classify_process(code, error, so + se, 0, stdout_sig,
                                      merged_allowed)
            streams = classify_streams(code, error, so, se, 0, stdout_sig,
                                       stream_allowed)
            return {"merged_allowlist": list(merged_allowed),
                    "stream_allowlist": list(stream_allowed),
                    "merged_classification": merged,
                    "stream_classification": streams,
                    "divergent": merged != streams,
                    "divergent_clause": divergent_clause(
                        so, se, code, error, merged_allowed, stream_allowed),
                    "raw_stdout_sha256": hashlib.sha256(
                        so.encode()).hexdigest(),
                    "raw_stderr_sha256": hashlib.sha256(
                        se.encode()).hexdigest(),
                    "raw_merged_sha256": hashlib.sha256(
                        (so + se).encode()).hexdigest()}

        def streamdiv_arm(case, flags, merged_allowed=(), stream_allowed=()):
            command = [args.godot, "--headless", "--path", str(scratch),
                       "--script", "res://stream_attribution_probe.gd", "--",
                       *flags]
            so, se, code, error = run_process_streams(command, 8)
            merged_text = so + se
            record = {
                "case": case, "command": command, "flags": list(flags),
                "expected_exit": 0, "actual_exit": code, "error": error,
                "signature": stdout_sig,
                "raw_stdout": so, "raw_stderr": se,
                "raw_stdout_lines": (so.strip().splitlines() if so else []),
                "raw_stderr_lines": (se.strip().splitlines() if se else []),
                "stdout_tail_line": (so.splitlines()[-1].strip()
                                     if so.splitlines() else None),
                "stderr_head_line": (se.splitlines()[0].strip()
                                     if se.splitlines() else None),
                "stdout_error_lines": [line.strip() for line in so.splitlines()
                                       if "ERROR:" in line],
                "stderr_error_lines": [line.strip() for line in se.splitlines()
                                       if "ERROR:" in line],
                "merged_error_lines": [line.strip() for line
                                       in merged_text.splitlines()
                                       if "ERROR:" in line],
                "signature_in_stdout": stdout_sig in so,
                "signature_in_stderr": stdout_sig in se,
                "signature_in_merged": stdout_sig in merged_text,
                "script_error_in_stdout": "SCRIPT ERROR:" in so,
                "script_error_in_stderr": "SCRIPT ERROR:" in se,
                "script_error_in_merged": "SCRIPT ERROR:" in merged_text}
            record.update(dual_classify(so, se, code, error,
                                        merged_allowed, stream_allowed))
            print(f"{record['case']}: exit={code} "
                  f"merged={record['merged_classification']} "
                  f"streams={record['stream_classification']} "
                  f"divergent={record['divergent']}", flush=True)
            return record

        sd_pair_dual = {
            "stream_accept": dual_classify(
                accept["raw_stdout"], accept["raw_stderr"],
                accept["actual_exit"], accept["error"]),
            "stream_reject": dual_classify(
                reject["raw_stdout"], reject["raw_stderr"],
                reject["actual_exit"], reject["error"])}
        sd1 = streamdiv_arm("streamdiv_stdout_error", ["--stdout-error"])
        sd2 = streamdiv_arm("streamdiv_stderr_error", ["--stderr-error"])
        sd3 = streamdiv_arm("streamdiv_stderr_structured",
                            ["--stderr-structured"],
                            merged_allowed=(sd_structured_entry,),
                            stream_allowed=(sd_structured_entry,))
        sd4 = streamdiv_arm("streamdiv_sig_on_stderr", ["--sig-on-stderr"],
                            stream_allowed=(stdout_sig,))
        sd5 = streamdiv_arm("streamdiv_seam_error", ["--seam-error"],
                            stream_allowed=(sd_seam_head,))
        sd6 = streamdiv_arm("streamdiv_seam_script", ["--seam-script"],
                            stream_allowed=(sd_script_head,))
        sd7 = streamdiv_arm("streamdiv_seam_sig", ["--seam-sig"],
                            stream_allowed=(sd_sig_tail,))
        sd_arms = [sd1, sd2, sd3, sd4, sd5, sd6, sd7]
        sd_reclass = {
            "stderr_error__exact_entry": dual_classify(
                sd2["raw_stdout"], sd2["raw_stderr"], sd2["actual_exit"],
                sd2["error"], (sd_stderr_error,), (sd_stderr_error,)),
            "stderr_error__foreign_entry": dual_classify(
                sd2["raw_stdout"], sd2["raw_stderr"], sd2["actual_exit"],
                sd2["error"], ("ERROR: unrelated different diagnostic",),
                ("ERROR: unrelated different diagnostic",)),
            "stderr_structured__exact_line_entry": dual_classify(
                sd3["raw_stdout"], sd3["raw_stderr"], sd3["actual_exit"],
                sd3["error"], (sd_structured_line,), (sd_structured_line,)),
            "stderr_structured__bare": dual_classify(
                sd3["raw_stdout"], sd3["raw_stderr"], sd3["actual_exit"],
                sd3["error"]),
            "sig_on_stderr__bare": dual_classify(
                sd4["raw_stdout"], sd4["raw_stderr"], sd4["actual_exit"],
                sd4["error"]),
            "seam_error__bare": dual_classify(
                sd5["raw_stdout"], sd5["raw_stderr"], sd5["actual_exit"],
                sd5["error"]),
        }
        sd5_fabricated = sd_seam_tail + sd_seam_head
        sd6_fabricated = sd_script_tail + sd_script_head
        divergence_table = (
            [{"case": name, **dual} for name, dual in sd_pair_dual.items()]
            + [{"case": a["case"],
                "merged_allowlist": a["merged_allowlist"],
                "stream_allowlist": a["stream_allowlist"],
                "merged_classification": a["merged_classification"],
                "stream_classification": a["stream_classification"],
                "divergent": a["divergent"],
                "divergent_clause": a["divergent_clause"],
                "raw_stdout_sha256": a["raw_stdout_sha256"],
                "raw_stderr_sha256": a["raw_stderr_sha256"],
                "raw_merged_sha256": a["raw_merged_sha256"]} for a in sd_arms])
        sd_discriminations = {
            # The headline absorption: a stdout-carried ERROR: line is
            # PASS-shaped under classify_streams — stdout is never
            # error-scanned — while merged classification rejects.
            "stdout_error_diverges_streams_absorbs": (
                sd1["stream_classification"] is True
                and sd1["merged_classification"] is False),
            "stdout_error_line_only_on_stdout": (
                sd1["stdout_error_lines"] == [sd_stdout_error]
                and sd1["stderr_error_lines"] == []
                and sd1["merged_error_lines"] == [sd_stdout_error]),
            # Concordant control: the same ERROR: bytes on stderr reject
            # both classifiers bare, absorb under the byte-exact entry,
            # reject under a foreign entry — channel placement, not the
            # bytes, is the axis.
            "stderr_error_concordant_both_reject": (
                sd2["merged_classification"] is False
                and sd2["stream_classification"] is False
                and sd2["stderr_error_lines"] == [sd_stderr_error]
                and sd2["stdout_error_lines"] == []),
            "stderr_error_exact_entry_absorbs_both": (
                sd_reclass["stderr_error__exact_entry"]
                ["merged_classification"] is True
                and sd_reclass["stderr_error__exact_entry"]
                ["stream_classification"] is True),
            "stderr_error_foreign_entry_rejects_both": (
                sd_reclass["stderr_error__foreign_entry"]
                ["merged_classification"] is False
                and sd_reclass["stderr_error__foreign_entry"]
                ["stream_classification"] is False),
            # The allowlist's per-stream match: the structured chain-
            # incomplete entry exists only in merged's allowed_error —
            # line_allowed knows exact and `,`-prefix shapes only.
            "structured_entry_diverges_allowlist_shape": (
                sd3["merged_classification"] is True
                and sd3["stream_classification"] is False
                and sd3["stderr_error_lines"] == [sd_structured_line]),
            "structured_exact_line_absorbs_both": (
                sd_reclass["stderr_structured__exact_line_entry"]
                ["merged_classification"] is True
                and sd_reclass["stderr_structured__exact_line_entry"]
                ["stream_classification"] is True),
            "structured_bare_rejects_both": (
                sd_reclass["stderr_structured__bare"]
                ["merged_classification"] is False
                and sd_reclass["stderr_structured__bare"]
                ["stream_classification"] is False),
            # Signature channel: merged accepts signature bytes anywhere;
            # streams requires them on stdout — stderr-carried signature
            # rejects even with stderr fully allowlisted (signature axis
            # is the sole cause).
            "sig_on_stderr_diverges": (
                sd4["merged_classification"] is True
                and sd4["stream_classification"] is False
                and sd4["signature_in_stderr"] is True
                and sd4["signature_in_stdout"] is False),
            "sig_on_stderr_streams_rejects_solely_on_signature": (
                sd4["stream_allowlist"] == [stdout_sig]
                and sd4["stream_classification"] is False
                and sd_reclass["sig_on_stderr__bare"]
                ["stream_classification"] is False),
            # Seam position pins: fabricated reject bytes exist only in the
            # merged concat — per-stream checks are seam-immune.
            "seam_error_diverges_streams_absorbs": (
                sd5["stream_classification"] is True
                and sd5["merged_classification"] is False),
            "seam_error_line_in_neither_stream": (
                sd5["merged_error_lines"] == [sd5_fabricated]
                and sd5["stdout_tail_line"] == sd_seam_tail
                and sd5["stderr_head_line"] == sd_seam_head
                and sd5_fabricated not in sd5["raw_stdout_lines"]
                and sd5_fabricated not in sd5["raw_stderr_lines"]),
            "seam_error_streams_bare_rejects_stderr_strictness": (
                sd_reclass["seam_error__bare"]
                ["stream_classification"] is False),
            "seam_script_diverges_blob_clause": (
                sd6["stream_classification"] is True
                and sd6["merged_classification"] is False
                and sd6["script_error_in_merged"] is True
                and sd6["script_error_in_stdout"] is False
                and sd6["script_error_in_stderr"] is False
                and sd6_fabricated not in sd6["raw_stdout_lines"]
                and sd6_fabricated not in sd6["raw_stderr_lines"]),
            "seam_sig_diverges_signature_seam": (
                sd7["merged_classification"] is True
                and sd7["stream_classification"] is False
                and sd7["signature_in_merged"] is True
                and sd7["signature_in_stdout"] is False
                and sd7["signature_in_stderr"] is False
                and sd7["raw_stdout"].endswith(sd_sig_head)),
            # The pre-existing reject arm is itself divergent: a plain
            # non-"ERROR:" stderr line is invisible to merged yet rejects
            # streams — stderr strictness covers ANY unallowlisted line.
            "reject_arm_diverges_non_error_stderr": (
                sd_pair_dual["stream_reject"]["merged_classification"] is True
                and sd_pair_dual["stream_reject"]["stream_classification"]
                is False),
            "accept_arm_concordant": (
                sd_pair_dual["stream_accept"]["merged_classification"]
                is True
                and sd_pair_dual["stream_accept"]["stream_classification"]
                is True),
            # Coverage/consistency of the measured map.
            "divergence_rows_match_expectation": (
                {row["case"] for row in divergence_table if row["divergent"]}
                == {"stream_reject", "streamdiv_stdout_error",
                    "streamdiv_stderr_structured", "streamdiv_sig_on_stderr",
                    "streamdiv_seam_error", "streamdiv_seam_script",
                    "streamdiv_seam_sig"}
                and {row["case"] for row in divergence_table
                     if not row["divergent"]}
                == {"stream_accept", "streamdiv_stderr_error"}),
            "all_divergence_arms_exit0_clean": all(
                a["actual_exit"] == 0 and a["error"] is None
                for a in sd_arms),
            "all_divergence_arms_same_script": all(
                a["command"][a["command"].index("--script") + 1]
                == "res://stream_attribution_probe.gd" for a in sd_arms),
            # r68 receipt-shape upgrades — gated, additive.
            # divergent_clause names the exact diverging clause per row;
            # the map is a measured invariant (re-derived per clause on the
            # same captured streams), not a relabel: seam_script trips BOTH
            # the blob and error_scan clauses on the same fabricated line.
            "divergent_clause_map_exact": (
                {row["case"]: tuple(row["divergent_clause"])
                 for row in divergence_table}
                == {"stream_accept": (),
                    "stream_reject": ("error_scan",),
                    "streamdiv_stdout_error": ("error_scan",),
                    "streamdiv_stderr_error": (),
                    "streamdiv_stderr_structured": ("allowlist_shape",),
                    "streamdiv_sig_on_stderr": ("signature",),
                    "streamdiv_seam_error": ("error_scan",),
                    "streamdiv_seam_script": ("blob", "error_scan"),
                    "streamdiv_seam_sig": ("signature",)}),
            # Attribution is complete and nonempty exactly on divergent rows.
            "divergent_clause_nonempty_iff_divergent": all(
                bool(row["divergent_clause"]) == row["divergent"]
                for row in divergence_table),
            "divergent_clause_taxonomy_bounded": all(
                set(row["divergent_clause"]) <= set(sd_clause_taxonomy)
                for row in divergence_table),
            # Same-input gate: every dual record's digests equal the digests
            # of the exact captured streams that fed BOTH classifiers — arms
            # digest their own raw_stdout/raw_stderr; pair rows digest the
            # accept/reject captures; each reclassification digests its
            # source arm's streams (reclassified inputs are the SAME bytes).
            # r69: raw_merged_sha256 also equals sha256 of the CANONICAL
            # stdout+stderr concat — a concat-order drift (stderr before
            # stdout) would leave both per-channel digests untouched yet
            # flip the merged digest (the r66 stderr+stdout caveat).
            "dual_records_same_input_digests": (
                all(a["raw_stdout_sha256"]
                    == hashlib.sha256(a["raw_stdout"].encode()).hexdigest()
                    and a["raw_stderr_sha256"]
                    == hashlib.sha256(a["raw_stderr"].encode()).hexdigest()
                    and a["raw_merged_sha256"]
                    == hashlib.sha256(
                        (a["raw_stdout"] + a["raw_stderr"]).encode()
                    ).hexdigest()
                    for a in sd_arms)
                and sd_pair_dual["stream_accept"]["raw_stdout_sha256"]
                == hashlib.sha256(accept["raw_stdout"].encode()).hexdigest()
                and sd_pair_dual["stream_accept"]["raw_stderr_sha256"]
                == hashlib.sha256(accept["raw_stderr"].encode()).hexdigest()
                and sd_pair_dual["stream_accept"]["raw_merged_sha256"]
                == hashlib.sha256(
                    (accept["raw_stdout"] + accept["raw_stderr"]).encode()
                ).hexdigest()
                and sd_pair_dual["stream_reject"]["raw_stdout_sha256"]
                == hashlib.sha256(reject["raw_stdout"].encode()).hexdigest()
                and sd_pair_dual["stream_reject"]["raw_stderr_sha256"]
                == hashlib.sha256(reject["raw_stderr"].encode()).hexdigest()
                and sd_pair_dual["stream_reject"]["raw_merged_sha256"]
                == hashlib.sha256(
                    (reject["raw_stdout"] + reject["raw_stderr"]).encode()
                ).hexdigest()
                and all(sd_reclass[key]["raw_stdout_sha256"]
                        == src["raw_stdout_sha256"]
                        and sd_reclass[key]["raw_stderr_sha256"]
                        == src["raw_stderr_sha256"]
                        and sd_reclass[key]["raw_merged_sha256"]
                        == src["raw_merged_sha256"]
                        for key, src in
                        (("stderr_error__exact_entry", sd2),
                         ("stderr_error__foreign_entry", sd2),
                         ("stderr_structured__exact_line_entry", sd3),
                         ("stderr_structured__bare", sd3),
                         ("sig_on_stderr__bare", sd4),
                         ("seam_error__bare", sd5)))),
        }
        sd_meta_ok = all(sd_discriminations.values())

        probe_payload = {
            "mode": "real_godot_stream_attribution",
            "same_script": same_script,
            "script_paths": script_paths,
            "stdout_signature": stdout_sig,
            "stderr_diagnostic": stderr_diag,
            "results": probe_results,
            "accept_emitted_stdout_marker": accept_stdout_ok,
            "reject_emitted_stdout_marker": reject_stdout_ok,
            "accept_lacks_stderr_diagnostic": accept_no_stderr_diag,
            "reject_emitted_stderr_diagnostic": reject_has_stderr_diag,
            "same_exit_zero": same_exit,
            "divergence": {
                "mode": "dual_classifier_same_captured_streams",
                "pair_reclassifications": sd_pair_dual,
                "arms": sd_arms,
                "allowlist_reclassifications": sd_reclass,
                "divergence_table": divergence_table,
                "discriminations": sd_discriminations,
                "bounded_claim": (
                    "same captured stdout/stderr pairs classified by BOTH "
                    "classifiers: stdout-carried ERROR: is PASS-shaped under "
                    "classify_streams (stdout never error-scanned) while "
                    "merged rejects; a non-ERROR: stderr line rejects "
                    "streams only; the structured chain-incomplete allowlist "
                    "entry is merged-only; signature must be stdout-carried "
                    "for streams but anywhere for merged; stdout-tail + "
                    "stderr-head seam bytes fabricate merged-only "
                    "ERROR:/SCRIPT ERROR:/signature text that per-stream "
                    "checks are immune to; one Linux headless Godot 4.7.2 "
                    "fixture, deterministic byte placement")},
            "verdict": "PASS" if meta_pass and sd_meta_ok else "FAIL",
            "bounded_claim": (
                "one Godot 4.7.2 headless stream-attribution pair; "
                "not crash classification, not process-tree timeout, "
                "not export reliability, not rendered output"
            ),
        }
        artifact = run_dir / "stream-attribution-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({
            "case": "probe_stream_attribution",
            "verdict": probe_payload["verdict"],
            "artifact": str(artifact),
            "inner_classifications": [r["inner_classification"] for r in probe_results],
        })
        print(f"{probe_payload['verdict']} stream attribution probe: {artifact}")

    if args.probe_crash_exit:
        marker_text = "CRASH_EXIT_PROBE: expected signature"
        script_path = "res://crash_exit_probe.gd"
        timeout_seconds = 8
        cleanup_seconds = 3
        expected_exit = 1
        probe_results = []
        accept_command = [args.godot, "--headless", "--path", str(scratch), "--script",
                          script_path, "--"]
        accept_output, accept_code, accept_error = run_process(accept_command, timeout_seconds)
        accept_classification = classify_process(accept_code, accept_error, accept_output,
                                                 expected_exit, marker_text)
        probe_results.append({"case": "crash_exit_accept", "command": accept_command,
                              "expected_exit": expected_exit, "actual_exit": accept_code,
                              "error": accept_error, "marker_observed": marker_text in accept_output,
                              "inner_classification": accept_classification,
                              "raw_output": accept_output,
                              "raw_output_lines": accept_output.strip().splitlines()})

        reject_command = [args.godot, "--headless", "--path", str(scratch), "--script",
                          script_path, "--", "--hold-open"]
        reject = {"case": "crash_exit_signal_reject", "command": reject_command,
                  "expected_exit": expected_exit, "signal_name": "SIGTERM", "timeout_seconds": timeout_seconds,
                  "cleanup_seconds": cleanup_seconds, "actual_exit": None,
                  "error": None, "marker_observed": False, "process_was_running": False,
                  "signal_sent": False, "inner_classification": False,
                  "raw_stdout": "", "raw_stderr": ""}
        process = None
        try:
            if os.name != "posix" or not hasattr(signal, "SIGTERM"):
                reject["error"] = "SIGTERM probe unsupported on this platform"
            else:
                process = subprocess.Popen(reject_command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, bufsize=1)
                selector = selectors.DefaultSelector()
                selector.register(process.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + timeout_seconds
                observed_line = False
                while time.monotonic() < deadline and not observed_line:
                    if process.poll() is not None:
                        break
                    events = selector.select(min(0.1, max(0.0, deadline - time.monotonic())))
                    for key, _ in events:
                        line = key.fileobj.readline()
                        if line:
                            reject["raw_stdout"] += line
                            observed_line = line.strip() == marker_text
                selector.close()
                reject["marker_observed"] = observed_line
                reject["process_was_running"] = process.poll() is None
                if not reject["marker_observed"]:
                    reject["error"] = "marker not observed before bounded timeout or process exit"
                elif not reject["process_was_running"]:
                    reject["error"] = "process was not live after marker observation"
                else:
                    process.send_signal(signal.SIGTERM)
                    reject["signal_sent"] = True
                try:
                    remaining_out, reject["raw_stderr"] = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += remaining_out
                except subprocess.TimeoutExpired:
                    reject["error"] = "signal cleanup timed out; forced kill used"
                    process.kill()
                    remaining_out, reject["raw_stderr"] = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += remaining_out
                reject["actual_exit"] = process.returncode
                if reject["signal_sent"] and process.returncode == -signal.SIGTERM:
                    reject["inner_classification"] = classify_process(
                        process.returncode, None, reject["raw_stdout"] + reject["raw_stderr"],
                        expected_exit, marker_text)
                elif reject["signal_sent"] and reject["error"] is None:
                    reject["error"] = f"expected return code {-signal.SIGTERM}, got {process.returncode}"
        except (OSError, ValueError) as exc:
            reject["error"] = f"signal probe launch/read error: {exc}"
            if process is not None and process.poll() is None:
                process.kill()
                try:
                    out, err = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += out
                    reject["raw_stderr"] += err
                    reject["actual_exit"] = process.returncode
                except subprocess.TimeoutExpired:
                    reject["error"] += "; forced cleanup timed out"
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                try:
                    out, err = process.communicate(timeout=cleanup_seconds)
                    reject["raw_stdout"] += out
                    reject["raw_stderr"] += err
                    reject["actual_exit"] = process.returncode
                except subprocess.TimeoutExpired:
                    reject["error"] = (reject["error"] or "") + "; bounded forced cleanup timed out"
        probe_results.append(reject)
        accept = probe_results[0]
        same_script = all(record["command"][record["command"].index("--script") + 1] == script_path
                          for record in probe_results)
        same_marker = all(record.get("marker_observed") for record in probe_results)
        same_expected_exit = all(record["expected_exit"] == expected_exit for record in probe_results)
        meta_pass = (accept["inner_classification"] is True
                     and reject["inner_classification"] is False
                     and reject["process_was_running"] and reject["signal_sent"]
                     and reject["actual_exit"] == -signal.SIGTERM
                     and reject["error"] is None and same_script and same_marker and same_expected_exit)
        probe_payload = {"mode": "real_godot_crash_exit", "platform": sys.platform,
                         "signal": "SIGTERM", "signal_return_code": -signal.SIGTERM,
                         "same_script": same_script, "same_expected_exit": same_expected_exit,
                         "signature": marker_text, "results": probe_results,
                         "bounded_claim": "one real Godot normal exit versus POSIX SIGTERM; no general crash or process-tree guarantee",
                         "verdict": "PASS" if meta_pass else "FAIL"}
        artifact = run_dir / "crash-exit-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({"case": "probe_crash_exit", "verdict": probe_payload["verdict"],
                        "artifact": str(artifact),
                        "inner_classifications": [r["inner_classification"] for r in probe_results]})
        print(f"{probe_payload['verdict']} crash-exit probe: {artifact}")

    if args.probe_timeout:
        marker_text = "TIMEOUT_PROBE: expected signature"
        script_path = "res://timeout_probe.gd"
        old_timeout_seconds = 0.75
        measured_delay_seconds = 1.5
        timeout_seconds = 3.0
        cleanup_seconds = 3
        expected_exit = 0
        def bounded_run(case, extra_args, bound):
            command = [args.godot, "--headless", "--path", str(scratch), "--script",
                       script_path, "--"] + extra_args
            record = {"case": case, "command": command, "expected_exit": expected_exit,
                      "timeout_seconds": bound, "cleanup_seconds": cleanup_seconds,
                      "actual_exit": None, "error": None, "marker_observed": False,
                      "timed_out": False, "process_was_running": False,
                      "direct_child_alive_after_cleanup": None, "raw_stdout": "", "raw_stderr": ""}
            process = None
            started_at = time.monotonic()
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, bufsize=1)
                try:
                    out, err = process.communicate(timeout=bound)
                    record["raw_stdout"], record["raw_stderr"] = out, err
                    record["actual_exit"] = process.returncode
                except subprocess.TimeoutExpired as exc:
                    record["timed_out"] = True
                    out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                    err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                    record["raw_stdout"], record["raw_stderr"] = out, err
                    record["marker_observed"] = marker_text in out
                    record["process_was_running"] = process.poll() is None
                    record["error"] = f"TIMEOUT after {bound} seconds"
                    if process.poll() is None:
                        process.kill()
                    more_out, more_err = process.communicate(timeout=cleanup_seconds)
                    record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
                    record["cleanup_exit_code"] = process.returncode
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                record["error"] = f"launch/read/cleanup error: {exc}"
                if process is not None and process.poll() is None:
                    process.kill()
                    try:
                        process.communicate(timeout=cleanup_seconds)
                    except subprocess.TimeoutExpired:
                        record["error"] += "; direct-child cleanup timed out"
            finally:
                if process is not None:
                    record["actual_exit"] = None if record["timed_out"] else process.poll()
                    record["direct_child_alive_after_cleanup"] = process.poll() is None
            record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
            record["marker_observed"] = marker_text in record["raw_stdout"]
            record["inner_classification"] = classify_process(
                record["actual_exit"], record["error"], record["raw_stdout"] + record["raw_stderr"],
                expected_exit, marker_text)
            return record

        old_positive = bounded_run("slow_clean_old_bound", ["--delay-clean"], old_timeout_seconds)
        new_positive = bounded_run("slow_clean_new_bound", ["--delay-clean"], timeout_seconds)
        hold_open = bounded_run("hold_open_new_bound", ["--hold-open"], timeout_seconds)
        probe_results = [old_positive, new_positive, hold_open]
        old_rejects = (old_positive["timed_out"] and old_positive["marker_observed"]
                       and old_positive["inner_classification"] is False
                       and old_positive["direct_child_alive_after_cleanup"] is False)
        new_accepts = (not new_positive["timed_out"] and new_positive["actual_exit"] == expected_exit
                       and new_positive["marker_observed"]
                       and new_positive["inner_classification"] is True)
        hold_rejects = (hold_open["timed_out"] and hold_open["marker_observed"]
                        and hold_open["inner_classification"] is False
                        and hold_open["direct_child_alive_after_cleanup"] is False)
        same_script = all(record["command"][record["command"].index("--script") + 1] == script_path
                          for record in probe_results)
        same_expected_exit = all(record["expected_exit"] == expected_exit for record in probe_results)
        meta_pass = old_rejects and new_accepts and hold_rejects and same_script and same_expected_exit
        probe_payload = {"mode": "real_godot_timeout_three_arm", "platform": sys.platform,
                         "same_script": same_script, "same_expected_exit": same_expected_exit,
                         "signature": marker_text, "results": probe_results,
                         "constants": {"old_timeout_seconds": old_timeout_seconds,
                                       "measured_delay_seconds": measured_delay_seconds,
                                       "new_timeout_seconds": timeout_seconds,
                                       "cleanup_seconds": cleanup_seconds},
                         "bounded_claim": "controlled delayed clean startup is rejected by old bound and accepted by new bound; hold-open marker still times out; direct child cleanup only",
                         "verdict": "PASS" if meta_pass else "FAIL"}
        artifact = run_dir / "timeout-verdicts.json"
        artifact.write_text(json.dumps(probe_payload, indent=2) + "\n")
        results.append({"case": "probe_timeout", "verdict": probe_payload["verdict"],
                        "artifact": str(artifact),
                        "inner_classifications": [r["inner_classification"] for r in probe_results]})
        print(f"{probe_payload['verdict']} timeout probe: {artifact}")

    payload = {"godot": args.godot, "seed": str(HERE), "scratch": str(scratch),
               "probe_failing": args.probe_failing, "results": results,
               "verdict": "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL"}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{payload['verdict']} battery: {run_dir / 'verdicts.json'}")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
