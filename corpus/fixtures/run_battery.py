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
        output, code, error = run_process(command, timeout_seconds, env=env)
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
            candidate = (classify_process(code, error, candidate_output, 2, evidence,
                                          ("ERROR: " + evidence,))
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
            }.get(name, ())
            classifier = classify_audio_process if name == "audio_playback" else classify_process
            passed = detected if mutate else classifier(code, error, output, expected_exit, evidence, expected_errors)
        # A script/parse error never counts as intended mutant detection.
        if "SCRIPT ERROR:" in output or "Parse Error:" in output:
            passed = False
        record = {"case": name, "script": script, "flags": flags, "command": command,
                  "xdg_data_home": env.get("XDG_DATA_HOME") if env else None,
                  "expected_exit": expected_exit, "actual_exit": code, "signature": evidence,
                  "verdict": "PASS" if passed else "FAIL",
                  "error": error, "output": output.strip().splitlines()}
        record["expected_errors"] = list(expected_errors)
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
        bare_rejects = not classify_process(
            row["actual_exit"], row["error"], row_text,
            row["expected_exit"], row["signature"], ())
        allowlisted_passes = classify_process(
            row["actual_exit"], row["error"], row_text,
            row["expected_exit"], row["signature"], tuple(entries))
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
