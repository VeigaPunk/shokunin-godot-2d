"""r70 LOVE 11.5 headless battery: run corpus/fixtures/love_probe under
`love <dir>` and pin the measured first-contact lattice.

Sibling runner to run_battery.py -- the Godot battery stays untouched
(prior rows byte-stable); this runner owns the LOVE runtime surface.

r70 measured lattice (operator first-contact, 3 stable reps):
  - headless `love` runs with t.window=false + graphics/window off:
    exit 0, LOVE_PROBE_DONE.
  - update cadence is UNCAPPED (~960Hz, dt_mean ~1.04ms) -- not the
    60Hz display cadence; vsync/fps-cap are windowed-mode phenomena.
  - io.popen: write->readable latency tracks the writer (l2_wait ~120.7ms
    = child's sleep 120ms, no hidden buffering); byte-exact lines; EOF
    wait <0.2ms. Blocking reads suspend the update loop (measured).
  - os.execute returns Lua-5.1-shape RAW status (exit 3 -> 768), single
    value -- not the 5.2+ (ok,"exit",code) triple.
  - love.event.pump is not required for the update loop headless.

Case model: each CASES row asserts keys on an emitted
`LOVE-ARM <arm> | k=v` line; values pin either an exact byte or a numeric
bound tuple (lo, hi) -- jittered quantities carry measured bounds only.

r74 lattice (love.physics callback-interior writes, IW_CELLS): one
`love love_phys_probe` process per cell (IW_CELL env). Writes inside
Box2D callbacks (beginContact/preSolve/postSolve) are gated per class --
the measured partition is {refused | deferred | fatal | applied}:
  refused : structural mutation (setPosition/newBody/setActive) -> catchable
            "Box2D assertion failed: ...IsLocked() == false" Lua error
            (this build surfaces b2Assert via loveAssert as a Lua error,
            not a silent no-op and not a process abort).
  deferred: body:destroy() -> ok=true, body alive for the rest of the
            callback+step; drained inside the world:update epilogue with a
            synthesized EndContact at locked=false (r74 reviewer D1: the
            drain happens inside the update call, not after it returns).
  fatal   : fatal(lua) only -- an assert-gated structural write NOT
            pcall-contained -> error escapes world:update -> LOVE error
            handler -> rc=1, "Error:" on stdout, no CELL_DONE (partial
            capture, measured not silent). Scope (r74 critic C1/C2): the
            pinned *_unp cells cover assert-gated structural writes only --
            destroy/setvel uncontained stay deferred/applied, and a
            process-abort shape (SIGABRT, e.g. own-fixture sensor->solid
            morph per r74-boundary) classifies `died`, never `fatal`.
  applied : non-structural writes (setLinearVelocity, contact:setEnabled
            in preSolve) are legal inside the lock.
Exterior (ext_*) controls apply immediately. Interior cells are spawned
LAST and the fatal cells last of all -- each cell is its own process so
a fatal cell is a measured FAIL-class for that cell only.

r75 additions (critic-deferred cells + joints/return surface):
  refused_abort: r74 critic C3 -- the SAME assert-gated write contained one
            level UP (pcall around world:update, the idiomatic game-loop
            containment) is still a refused write, but the step ABORTS:
            update_ok=false, the world stays transiently locked until the
            next update, an unrelated legal exterior write is refused as
            collateral, and callback counts shift. Distinct measured shape
            -> distinct class; "refused" is containment-level relative.
  ignored : r75 -- a Lua preSolve `return false` is NOT consumed by the
            binding (Box2D PreSolve is void): the full impulse still lands
            (b1vel 0,-611.09 vs the masked 0,763.87). A silently-ignored
            write attempt is neither refused (no assert) nor applied.
            (`cb_retfalse.returned` is a harness echo of the intent; the
            landed impulse is the falsifiable witness.)
  C1 twins: bc_destroy_unp / bc_setvel_unp stay deferred/applied
            uncontained -- fatal is derived (assert-gated x uncontained).
  joints  : newDistanceJoint inside cb -> refused (world-level IsLocked
            assert); joint:destroy() inside cb -> deferred (jcount drains
            1->0 by update end; the epilogue drain POINT is inferred --
            jdrain.isDestroyed=true is the landed witness).
  setfilter: Fixture:setFilterData inside cb -> applied on this build
            (no IsLocked assert); downstream witness is the refilter
            tunneling b1 through the ground (final b1pos y>540).
  esc_fn  : traceback `in function '<name>'` pinned on the *_unp rows as
            the independent which-call-threw witness (r74 critic C4).

r76 additions (drain observers + destroy edges):
  deferred_abort: r75-boundary drain-deferral hazard -- an ACCEPTED
            queued destroy plus an uncontained assert-gated throw in the
            same callback, contained one level up. The abort skips that
            step's epilogue drain (abortq: count stays = fire.count, the
            body pose still readable); the queue persists and drains
            inside the NEXT update (drainlate step = abort step + 1,
            drain EC observed at locked=false -> ecunl). Accepted-write
            + abort is a distinct measured shape, parallel to
            refused_abort (refused write + abort).
  destroy2: a second destroy() on the same body post-drain is refused by
            the LIFETIME guard ("Attempt to use destroyed body."), not
            the IsLocked assert; the run completes (class stays deferred).
  worlddestroy: world:destroy() inside a callback is deferred too --
            destructWorld flag (World.cpp:578-581), drained at the very
            end of the update epilogue (World.cpp:299); the next world
            access dies on the "Attempt to use destroyed world." guard
            -> died (rc=1, no assert text, esc_fn = the death site).
  jwatch  : joint_destroy with a per-callback jcount observer: the drain
            point is bounded between the last step-73 cb (jcount=1,
            locked) and update-73 return (jcount=0); SayGoodbye is NOT
            exposed on this build (World method-table census) -- the
            bound is the measured drain point.
  retfalse1: return false armed on ONE contact of a two-contact b1/ground
            pair -- the discrimination executes (falses=1 passes=1) and
            the return is still not consumed (impulse lands) -> ignored.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE_DIR = HERE / "love_probe"
IW_PROBE_DIR = HERE / "love_phys_probe"
TIMEOUT_S = 30

# (name, arm, key, pinned)  pinned: exact value or (lo, hi) float bound
CASES = [
    ("dtcadence_n",            "dtcadence", "n",          "120"),
    ("dtcadence_mean_uncapped","dtcadence", "dt_mean_ms", (0.5, 4.0)),
    ("dtcadence_min_subms",    "dtcadence", "dt_min_ms",  (0.0, 0.1)),
    ("dtcadence_max_cheap",    "dtcadence", "dt_max_ms",  (0.5, 8.0)),
    ("popen_l1_exact",         "popen",     "l1",         "CHILD-MARK-1"),
    ("popen_l2_exact",         "popen",     "l2",         "CHILD-MARK-2"),
    ("popen_l1_wait_fast",     "popen",     "l1_wait_ms", (0.2, 30.0)),
    # l2_wait tracks the child's own 120ms sleep -> pipe visibility is
    # writer-bound, no engine-layer fabrication/absorption window
    ("popen_l2_wait_writer",   "popen",     "l2_wait_ms", (110.0, 140.0)),
    ("popen_close_fast",       "popen",     "close_wait_ms", (0.0, 5.0)),
    ("popen_total",            "popen",     "total_ms",   (115.0, 170.0)),
    ("popen_rest_empty",       "popen",     "rest_len",   "0"),
    ("osx_raw_status_shape",   "osx",       "ret_a",      "768"),
    ("osx_single_return",      "osx",       "ret_b",      "nil"),
    ("pump_not_needed",        "pump",      "pump_needed","false"),
    ("pump_updates_counted",   "pump",      "updates_without_pump", "123"),
]

ARM_LINE = re.compile(r"^LOVE-ARM (\S+) \| (.*)$")


SPLICE_CELLS = [
    # (name, offset_ms, gap_ms, expected) — cells measured 3/3 by the r70
    # critic's distinguishing probe (corpus/live/r70-critic/splice_probe).
    # In-window: descendant write lands inside the head->tail gap and the
    # captured line splices; beyond/crossed cells bound the referent as
    # gap-relative (offset < gap fabricates, offset > gap does not).
    ("splice_inwindow", 80, 200, "spliced"),
    ("splice_beyond", 240, 200, "clean"),
    ("splice_crossed", 300, 400, "spliced"),
    ("splice_tight", 80, 50, "clean"),
]


def splice_verdict(stdout):
    lines = stdout.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("LOVE_SPLICE_PROBE: expected "):
            tail = line[len("LOVE_SPLICE_PROBE: expected "):]
            if tail == "ERROR: LOVE_MIDLINE forged splice":
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                return "spliced" if nxt == "signature" else "spliced-no-tail"
            if tail == "signature":
                return "clean"
            return "ambiguous:" + tail[:40]
    return "missing"


# ---- r74 interior-write lattice ------------------------------------------
#
# (case, cell, expected_class, {flat_key: pinned})
# expected_class = the class partition defined by iw_classify (the
# surviving authority; enumerating it here drifted stale once already).
# flat keys are
# `<tag>.<key>` from the probe's `IW | cell=<cell> | <tag> k=v ...` lines,
# plus synthesized keys:
#   rc / done / err_on / assert_txt / esc_fn / evpin_<cb>_lck / evpin_<cb>_step
# Measured on this host (r74: 18 cells x>=2 stable reps; the r74-scout
# scratch receipts are byte-identical twins of this probe's output; r75:
# 7 more cells x>=2 stable reps measured in corpus/live/r75-author/cells).
IW_CELLS = [
    # availability lattice: reads inside callbacks are legal; locked=true
    ("iw_avail_lattice", "baseline", "captured", {
        "built.bodies": "4", "built.locked": "false",
        "viability.love": "11.5.0",
        "evpin_bc_lck": "true", "evpin_pre_lck": "true",
        "evpin_post_lck": "true", "evpin_ec_lck": "true",
        "evpin_ec_step": "74",
        "final.steps": "200", "final.count": "4",
        "final.bc": "5", "final.ec": "4",
        "final.pre": "36", "final.post": "36",
        "final.fired": "false", "done": "true", "rc": "0"}),
    # exterior controls -- the same mutations outside any callback apply
    ("iw_ext_setpos", "ext_setpos", "applied", {
        "ext_setpos.ok": "true", "ext_setpos.err": "nil",
        "ext_before.pos": "400,60",
        "ext_setpos.pos_after": "1234.5,678.9000244140625",
        "done": "true", "rc": "0"}),
    ("iw_ext_newbody", "ext_newbody", "applied", {
        "ext_newbody.ok": "true",
        "ext_newbody.count_before": "4", "ext_newbody.count_after": "5",
        "ext_newbody.nb_pos": "700,100",
        "done": "true", "rc": "0"}),
    ("iw_ext_destroy", "ext_destroy", "applied", {
        # immediate: body is dead the instant the call returns (contrast
        # with the deferred interior class below)
        "ext_destroy.ok": "true",
        "ext_destroy.count_before": "4", "ext_destroy.count_after": "3",
        "ext_destroy.b1pos_after": "ERR:Attempt to use destroyed body.",
        "done": "true", "rc": "0"}),
    # interior structural writes -> refused (catchable Lua assert)
    ("iw_bc_setpos", "bc_setpos", "refused", {
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "setpos",
        "cb_setpos.ok": "false",
        "cb_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setpos.pos_after": "400,520.1500244140625",
        "after_update.b1pos": "400,511.13113403320312",
        "evpin_ec_lck": "true", "done": "true", "rc": "0"}),
    ("iw_pre_setpos", "pre_setpos", "refused", {
        "fire.step": "73", "fire.cb": "pre",
        "fire.kind": "setpos",
        "cb_setpos.ok": "false",
        "cb_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setpos.pos_after": "400,520.1500244140625",
        "done": "true", "rc": "0"}),
    ("iw_post_setpos", "post_setpos", "refused", {
        # postSolve channel sees the POST-step pose (frontier channel split)
        "fire.step": "73", "fire.cb": "post",
        "fire.kind": "setpos",
        "fire.pos": "400,511.13113403320312",
        "cb_setpos.ok": "false",
        "cb_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setpos.pos_after": "400,511.13113403320312",
        "done": "true", "rc": "0"}),
    ("iw_bc_newbody", "bc_newbody", "refused", {
        # world-level fn: assert text drops the m_world-> prefix
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "newbody",
        "cb_newbody.ok": "false",
        "cb_newbody.err": "Box2D assertion failed: IsLocked() == false",
        "cb_newbody.count_before": "4", "cb_newbody.count_after": "4",
        "done": "true", "rc": "0"}),
    ("iw_pre_newbody", "pre_newbody", "refused", {
        "fire.cb": "pre",
        "fire.kind": "newbody",
        "cb_newbody.ok": "false",
        "cb_newbody.err": "Box2D assertion failed: IsLocked() == false",
        "cb_newbody.count_after": "4", "done": "true", "rc": "0"}),
    ("iw_post_newbody", "post_newbody", "refused", {
        "fire.cb": "post",
        "fire.kind": "newbody",
        "cb_newbody.ok": "false",
        "cb_newbody.err": "Box2D assertion failed: IsLocked() == false",
        "cb_newbody.count_after": "4", "done": "true", "rc": "0"}),
    # interior destroy -> deferred (drained after world:update, ec at
    # locked=false inside the update epilogue)
    ("iw_bc_destroy", "bc_destroy", "deferred", {
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "destroy",
        "cb_destroy.ok": "true", "cb_destroy.err": "nil",
        "cb_destroy.alive_in_cb": "400,520.1500244140625",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "after_update.b1pos": "ERR:Attempt to use destroyed body.",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "done": "true", "rc": "0"}),
    ("iw_pre_destroy", "pre_destroy", "deferred", {
        "fire.cb": "pre",
        "fire.kind": "destroy",
        "cb_destroy.ok": "true",
        "cb_destroy.alive_in_cb": "400,520.1500244140625",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "done": "true", "rc": "0"}),
    ("iw_post_destroy", "post_destroy", "deferred", {
        "fire.cb": "post",
        "fire.kind": "destroy",
        "cb_destroy.ok": "true",
        "cb_destroy.alive_in_cb": "400,511.13113403320312",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "done": "true", "rc": "0"}),
    # edges: active-body write refused; contact mask + velocity accepted
    ("iw_bc_setactive", "bc_setactive", "refused", {
        "fire.step": "73",
        "fire.kind": "setactive",
        "cb_setactive.ok": "false",
        "cb_setactive.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setactive.isActive_after": "true",
        "cb_setactive.count_after": "4", "done": "true", "rc": "0"}),
    ("iw_pre_contactmask", "pre_contactmask", "applied", {
        # legal single-step mask: no impulse lands that update
        "fire.cb": "pre", "fire.step": "73",
        "fire.kind": "contactmask",
        "cb_contactmask.ok": "true",
        "cb_contactmask.isEnabled_after": "false",
        "cb_contactmask.isTouching": "true",
        "after_update.b1pos": "400,531.054443359375",
        "after_update.b1vel": "0,763.8724365234375",
        "done": "true", "rc": "0"}),
    ("iw_bc_setvel", "bc_setvel", "applied", {
        # non-structural write has no locked assert
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "setvel",
        "cb_setvel.ok": "true", "cb_setvel.err": "nil",
        "cb_setvel.vel_after": "55,-7",
        # r74-critic rank 5: the write is effect-bearing -- the velocity
        # is still 55,-7 after the rest of the step ran
        "after_update.b1vel": "55,-7",
        "done": "true", "rc": "0"}),
    # ---- r75 additive cells (all measured non-fatal on this build) ----
    ("iw_bc_setpos_wp", "bc_setpos_wp", "refused_abort", {
        # r74 critic C3: same setpos write, containment moved one level up
        # (pcall around world:update). Refused write + aborted step +
        # transient lock + collateral exterior refusal + next-step recovery.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "setpos_wp",
        "wpcall.step": "73", "wpcall.update_ok": "false",
        "wpcall.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "wpcall.locked_after": "true",
        "wp_setpos.ok": "false",
        "wp_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        # refused write moved nothing: pos_after == fire.pos
        "wp_setpos.pos_after": "400,520.1500244140625",
        "fire.pos": "400,520.1500244140625",
        "wpext.ok": "false",
        # exterior collateral refusal carries the same assert text and
        # leaves the pose untouched
        "wpext.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "wpext.pos_after": "400,520.1500244140625",
        "wpcall_next.step": "74", "wpcall_next.update_ok": "true",
        "wpcall_next.locked_after": "false",
        "wpcall_next.b1pos": "400,509.53021240234375",
        "final.pre": "37", "final.post": "37",
        "done": "true", "rc": "0"}),
    ("iw_bc_joint_new", "bc_joint_new", "refused", {
        # joints surface: newDistanceJoint inside cb -> world-level assert
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "joint_new",
        "cb_joint_new.ok": "false",
        "cb_joint_new.err": "Box2D assertion failed: IsLocked() == false",
        "cb_joint_new.jcount_before": "0",
        "cb_joint_new.jcount_after": "0",
        "after_update.b1pos": "400,511.13113403320312",
        "done": "true", "rc": "0"}),
    ("iw_bc_joint_destroy", "bc_joint_destroy", "deferred", {
        # joint:destroy() inside cb drains by update end like
        # body:destroy() (jcount 1->0, handle flips isDestroyed after);
        # unlike bodies there is no locked=false drain event -- the
        # drain point is inferred from the count pair, not witnessed
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "joint_destroy",
        "pre_joint.jtype": "distance", "pre_joint.jcount": "1",
        "cb_joint_destroy.ok": "true", "cb_joint_destroy.err": "nil",
        "cb_joint_destroy.isDestroyed_in_cb": "false",
        "cb_joint_destroy.jcount_before": "1",
        "cb_joint_destroy.jcount_after": "1",
        "jdrain.step": "73", "jdrain.jcount": "0",
        "jdrain.isDestroyed": "true",
        "done": "true", "rc": "0"}),
    ("iw_bc_setfilter", "bc_setfilter", "applied", {
        # Fixture:setFilterData is NOT locked-asserted on this build;
        # the refilter tunnels b1 through the ground after the write
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "setfilter",
        "cb_setfilter.ok": "true", "cb_setfilter.err": "nil",
        "cb_setfilter.filter_after": "2,2,0",
        "after_update.b1vel": "0,-611.09796142578125",
        "final.b1pos": "400,635.1639404296875",
        "final.bc": "4", "final.ec": "3",
        "done": "true", "rc": "0"}),
    ("iw_pre_retfalse", "pre_retfalse", "ignored", {
        # preSolve `return false` is not consumed: the full impulse lands
        # (contrast pre_contactmask's suppressed 0,763.87)
        "fire.cb": "pre", "fire.step": "73", "fire.locked": "true",
        "fire.kind": "retfalse",
        "cb_retfalse.returned": "false",
        "after_update.b1vel": "0,-611.09796142578125",
        "final.pre": "36", "final.post": "36",
        "done": "true", "rc": "0"}),
    # ---- r76 additive cells (drain observers + destroy edges) ----
    ("iw_bc_draindefer", "bc_draindefer", "deferred_abort", {
        # r75-boundary drain-deferral hazard: an ACCEPTED queued destroy
        # plus an uncontained assert-gated throw in the same callback,
        # contained one level up. The abort skips the step-73 epilogue
        # drain; the queued destroy survives and drains inside the
        # step-74 update -- one step late.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "draindefer", "fire.count": "4",
        "fire.pos": "400,520.1500244140625",
        "cb_destroy.ok": "true", "cb_destroy.err": "nil",
        "cb_destroy.mode": "queued",
        "cb_destroy.alive_in_cb": "400,520.1500244140625",
        "cb_destroy.count_after": "4",
        # the escaping write is refused even as the step aborts
        "wpcall.step": "73", "wpcall.update_ok": "false",
        "wpcall.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "wpcall.locked_after": "true",
        "wp_setpos.ok": "false",
        "wp_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "wpext.ok": "false",
        # drain-skipped witness: queue still pending, body pose readable
        "abortq.step": "73", "abortq.count": "4",
        "abortq.b1pos": "400,520.1500244140625",
        # the drain lands one update late; its synthesized EC is observed
        # at locked=false and is this run's first ec event
        "ecunl.step": "74", "ecunl.locked": "false",
        "evpin_ec_lck": "false", "evpin_ec_step": "74",
        "wpcall_next.step": "74", "wpcall_next.update_ok": "true",
        "wpcall_next.locked_after": "false",
        "wpcall_next.b1pos": "ERR:Attempt to use destroyed body.",
        "drainlate.step": "74", "drainlate.count": "3",
        "drainlate.b1pos": "ERR:Attempt to use destroyed body.",
        "final.count": "3", "final.bc": "4", "final.ec": "3",
        "final.pre": "36", "final.post": "36",
        "done": "true", "rc": "0"}),
    ("iw_bc_destroy2", "bc_destroy2", "deferred", {
        # double destroy on the same body: in-callback (queued + drained)
        # then a second call post-update -- refused by the LIFETIME guard
        # (luax_checkbody "Attempt to use destroyed body."), not the
        # IsLocked assert; the count stays 3 and the run completes.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "destroy2",
        "cb_destroy.ok": "true", "cb_destroy.err": "nil",
        "cb_destroy.alive_in_cb": "400,520.1500244140625",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "after_update.b1pos": "ERR:Attempt to use destroyed body.",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "post_destroy2.ok": "false",
        "post_destroy2.err": "Attempt to use destroyed body.",
        "post_destroy2.count": "3",
        "post_destroy2.isDestroyed": "true",
        "final.count": "3", "final.pre": "35", "final.post": "35",
        "done": "true", "rc": "0"}),
    ("iw_bc_jwatch", "bc_jwatch", "deferred", {
        # joint drain bounded by observation: every step-73 callback still
        # sees jcount=1 (last observer = post, locked=true), jdrain reads
        # 0 at update-73 return, and the first callback of step 74 sees 0.
        # The only code in that window is the update-73 epilogue
        # (World.cpp:283-299) -- the drain point is bounded-measured, the
        # r75-critic F3 residual closed without any SayGoodbye API.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "jwatch",
        "pre_joint.jtype": "distance", "pre_joint.jcount": "1",
        "cb_joint_destroy.ok": "true", "cb_joint_destroy.err": "nil",
        "cb_joint_destroy.isDestroyed_in_cb": "false",
        "cb_joint_destroy.jcount_before": "1",
        "cb_joint_destroy.jcount_after": "1",
        "jwlive.cb": "post", "jwlive.step": "73",
        "jwlive.locked": "true", "jwlive.jcount": "1",
        "jdrain.step": "73", "jdrain.jcount": "0",
        "jdrain.isDestroyed": "true",
        "jwdrop.cb": "ec", "jwdrop.step": "74",
        "jwdrop.locked": "true", "jwdrop.jcount": "0",
        "after_update.count": "4",
        "after_update.b1pos": "400,511.13113403320312",
        "final.bc": "8", "final.ec": "8",
        "final.pre": "172", "final.post": "172",
        "done": "true", "rc": "0"}),
    ("iw_pre_retfalse1", "pre_retfalse1", "ignored", {
        # return false armed on ONE contact of the b1-ground pair only
        # (f_mask's); the sibling contact passes. On this build the return
        # is still not consumed (the full impulse lands, vy<0) -- the cell
        # pins that the discrimination executed (falses=1 passes=1) and
        # the contact-scoped granularity for any future consuming build.
        "fire.step": "73", "fire.cb": "pre", "fire.locked": "true",
        "fire.kind": "retfalse1",
        "cb_retfalse.returned": "false",
        "after_update.b1pos": "399.9598388671875,511.13873291015625",
        "after_update.b1vel": "-2.8143491744995117,-611.97412109375",
        "rf1counts.falses": "1", "rf1counts.passes": "1",
        "evpin_ec_lck": "true", "evpin_ec_step": "74",
        "final.b1pos": "455.884765625,477.90667724609375",
        "final.bc": "6", "final.ec": "5",
        "final.pre": "37", "final.post": "37",
        "done": "true", "rc": "0"}),
    # r75 critic-C1 uncontained twins: measured non-fatal (fatal is
    # derived = assert-gated write x uncontained, not uncontained alone)
    ("iw_bc_destroy_unp", "bc_destroy_unp", "deferred", {
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "destroy_unp",
        # mode= is the uncontained branch's self-declared identity
        # (r75 critic F1): the contained twin emits no mode field, so a
        # misdirected/wrong-branch receipt fails this pin. The
        # containment axis itself is observational-inert for this
        # non-throwing write -- that inertness is the C1 claim.
        "cb_destroy.mode": "unp",
        "cb_destroy.ok": "true", "cb_destroy.err": "nil",
        "cb_destroy.alive_in_cb": "400,520.1500244140625",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "after_update.b1pos": "ERR:Attempt to use destroyed body.",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "done": "true", "rc": "0"}),
    ("iw_bc_setvel_unp", "bc_setvel_unp", "applied", {
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "setvel_unp",
        "cb_setvel.mode": "unp",  # unp-branch identity (see destroy_unp)
        "cb_setvel.ok": "true", "cb_setvel.err": "nil",
        "cb_setvel.vel_after": "55,-7",
        "after_update.b1vel": "55,-7",
        "done": "true", "rc": "0"}),
    # r76 process-death edge: died sits with the fatal tail; the fatal
    # rows remain last of all.
    ("iw_bc_worlddestroy", "bc_worlddestroy", "died", {
        # world:destroy() inside a callback is DEFERRED like bodies (the
        # destructWorld flag, World.cpp:578-581) and drains at the very
        # END of the update epilogue (World.cpp:299), after the object
        # drains. Every subsequent world access dies on the lifetime
        # guard -- the probe's own after_update getBodyCount is the death
        # site (rc=1, "Attempt to use destroyed world.", no assert text).
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "worlddestroy",
        "cb_worlddestroy.ok": "true", "cb_worlddestroy.err": "nil",
        "cb_worlddestroy.isDestroyed_in_cb": "false",
        "cb_worlddestroy.count_after": "4",
        "wdrained.step": "73", "wdrained.isDestroyed": "true",
        "rc": "1", "done": "false",
        "err_on": "none", "assert_txt": "none",
        # esc_fn witnesses the death site: the next world call
        "esc_fn": "getBodyCount"}),
    # uncontained escapes -> fatal, spawned LAST
    ("iw_bc_setpos_unp", "bc_setpos_unp", "fatal", {
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "setpos_unp",
        "rc": "1", "done": "false",
        "err_on": "stdout", "assert_txt": "m_world_islocked",
        "esc_fn": "setPosition"}),
    ("iw_bc_newbody_unp", "bc_newbody_unp", "fatal", {
        "fire.step": "73",
        "fire.kind": "newbody_unp",
        "rc": "1", "done": "false",
        "err_on": "stdout", "assert_txt": "islocked",
        "esc_fn": "newBody"}),
]

IW_LINE = re.compile(r"^IW \| cell=(\S+) \| (.*)$")
IW_KV = re.compile(r"(\w+)=")


def parse_iw(stdout):
    """Parse `IW | cell=<c> | <tag> k=v ...` lines.

    Values may contain spaces (assert text, ERR: strings): a value runs
    until the next `word=` boundary or end of line. Returns flat:
    `<tag>.<key>` -> last-wins merge across lines.
    """
    flat = {}
    for line in stdout.splitlines():
        m = IW_LINE.match(line.strip())
        if not m:
            continue
        body = m.group(2).strip()
        if body == "CELL_DONE":
            flat["done"] = "true"
            continue
        parts = [(mm.start(), mm.group(1)) for mm in IW_KV.finditer(body)]
        if not parts:
            continue
        tag = body[:parts[0][0]].strip()
        kv = {}
        for i, (at, k) in enumerate(parts):
            end = parts[i + 1][0] if i + 1 < len(parts) else len(body)
            kv[k] = body[at + len(k) + 1:end].strip()
        if tag == "evpin":
            cb = kv.get("cb", "?")
            flat[f"evpin_{cb}_lck"] = kv.get("locked", "?")
            flat[f"evpin_{cb}_step"] = kv.get("step", "?")
        for k, v in kv.items():
            flat[f"{tag}.{k}"] = v
    flat.setdefault("done", "false")
    return flat


def iw_classify(cell, flat, rc, timed_out, stdout):
    """Map one cell's capture onto {captured|applied|refused|deferred|
    refused_abort|deferred_abort|ignored|fatal|timeout|died|nolaunch|
    anomaly}.
    Partial-capture detection is built in: fire-present without
    CELL_DONE is never a pass shape."""
    if timed_out:
        return "timeout", f"exceeded {TIMEOUT_S}s"
    done = flat.get("done") == "true"
    has_fire = "fire.step" in flat
    if done and rc == 0:
        if cell == "baseline":
            return "captured", "availability lattice"
        if flat.get("wpcall.update_ok") == "false":
            # r75 C3 + critic F2: gate on the abort VALUE, not key
            # presence -- a receipt that merely mentions wpcall.* (e.g.
            # scout L1 captures where last-wins left update_ok=true)
            # falls through to the decisive cb_* evidence below.
            # r76 P1: the shared refused-write abort witness hoists to
            # one authority used by both abort arms.
            abort_w = (flat.get("wpcall.locked_after") == "true"
                       and flat.get("wp_setpos.ok") == "false"
                       and "assertion" in flat.get("wp_setpos.err", "")
                       and flat.get("wpext.ok") == "false"
                       and flat.get("wpcall_next.update_ok") == "true"
                       and flat.get("wpcall_next.locked_after") == "false")
            if flat.get("cb_destroy.ok") == "true":
                # r76 drain-deferral: an ACCEPTED queued destroy rode the
                # aborted step. The step-73 epilogue drain was skipped
                # (abortq: count still = fire.count, pose readable); the
                # queue persists and drains inside the next update
                # (drainlate step = wpcall.step + 1, handle dead, drain
                # EC observed at locked=false). Distinct measured shape
                # -> distinct class (accepted write + abort), parallel
                # to refused_abort (refused write + abort).
                try:
                    late = int(flat.get("drainlate.step", "-2")) == \
                        int(flat.get("wpcall.step", "-1")) + 1
                except ValueError:
                    late = False
                # r76 reviewer F1: abortq.b1pos gated positively -- an
                # ABSENT key must not satisfy the conjunct.
                b1pos_live = (bool(flat.get("abortq.b1pos"))
                              and not flat.get("abortq.b1pos", "")
                                      .startswith("ERR:"))
                if (abort_w
                        and flat.get("abortq.count")
                            == flat.get("fire.count")
                        and b1pos_live
                        and late
                        and flat.get("ecunl.locked") == "false"
                        and flat.get("drainlate.b1pos", "")
                            .startswith("ERR:")):
                    return ("deferred_abort",
                            "queued destroy survived abort; drained one step late")
                return "anomaly", "deferred-abort witness incomplete"
            if abort_w:
                return ("refused_abort",
                        "step abort + transient lock + recovery")
            return "anomaly", "wp containment witness incomplete"
        if "cb_retfalse.returned" in flat:
            # r75: the binding does not consume the preSolve return --
            # the class stands on the impulse landing (vel y < 0), not
            # on the returned=false label alone.
            vy = flat.get("after_update.b1vel", ",").split(",")[-1]
            try:
                impulse_landed = float(vy) < 0
            except ValueError:
                impulse_landed = False
            if flat["cb_retfalse.returned"] == "false" and impulse_landed:
                return "ignored", "preSolve return not consumed"
            return "anomaly", "retfalse without ignored witness"
        mut = next((t for t in ("cb_setpos", "cb_newbody", "cb_destroy",
                              "cb_setactive", "cb_contactmask", "cb_setvel",
                              "cb_joint_new", "cb_joint_destroy",
                              "cb_setfilter",
                              "ext_setpos", "ext_newbody", "ext_destroy")
                    if f"{t}.ok" in flat), None)
        if mut is None:
            return "anomaly", "CELL_DONE but no mutation line"
        if flat[f"{mut}.ok"] == "false":
            if "assertion" in flat.get(f"{mut}.err", ""):
                return "refused", flat[f"{mut}.err"]
            return "anomaly", "ok=false without Box2D assertion"
        if flat[f"{mut}.ok"] == "true":
            if mut == "cb_destroy":
                try:
                    drop = int(flat.get("after_update.count", "-1")) == \
                        int(flat.get("built.bodies", "0")) - 1
                except ValueError:
                    drop = False
                ec_lck = flat.get("evpin_ec_lck")
                dead = flat.get("after_update.b1pos", "").startswith("ERR:")
                if drop and dead and ec_lck == "false":
                    return "deferred", "drain ec at locked=false"
                return "anomaly", "destroy ok without deferred witness"
            if mut == "cb_joint_destroy":
                try:
                    jdrop = int(flat.get("jdrain.jcount", "-1")) == \
                        int(flat.get("cb_joint_destroy.jcount_before",
                                     "0")) - 1
                except ValueError:
                    jdrop = False
                if jdrop and flat.get("jdrain.isDestroyed") == "true":
                    return "deferred", "joint drained by update end (epilogue inferred)"
                return "anomaly", "joint destroy ok without deferred witness"
            return "applied", mut
        return "anomaly", f"unhandled ok={flat[f'{mut}.ok']!r}"
    if has_fire and not done and rc not in (0, None):
        if "Box2D assertion" in stdout:
            return "fatal", f"rc={rc}, assert text on stdout"
        return "died", f"rc={rc} without assert text"
    if not has_fire and not done:
        return "nolaunch", f"rc={rc} and no fire line"
    return "anomaly", f"rc={rc} done={done} fire={has_fire}"


def iw_flat_extras(flat, rc, stdout, stderr):
    flat["rc"] = str(rc)
    if "m_world->IsLocked() == false" in stdout:
        flat["assert_txt"] = "m_world_islocked"
    elif "IsLocked() == false" in stdout:
        flat["assert_txt"] = "islocked"
    elif "Box2D assertion" in stdout:
        flat["assert_txt"] = "other"
    else:
        flat["assert_txt"] = "none"
    if "Box2D assertion" in stdout:
        flat["err_on"] = "stdout"
    elif "Box2D assertion" in stderr:
        flat["err_on"] = "stderr"
    else:
        flat["err_on"] = "none"
    # r75 critic C4: independent which-call-threw witness -- first quoted
    # `in function '<name>'` traceback frame (the boot.lua frames use the
    # <...> form and never match).
    m_fn = re.search(r"in function '([^']+)'", stdout)
    flat["esc_fn"] = m_fn.group(1) if m_fn else "none"


def run_process(command, timeout_seconds, env_extra=None):
    try:
        env = dict(os.environ)
        env.update(env_extra or {})
        proc = subprocess.run(command, capture_output=True, text=True,
                              timeout=timeout_seconds, env=env)
        return proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        def text(v):
            return v.decode(errors="replace") if isinstance(v, bytes) else (v or "")
        return (text(exc.stdout), text(exc.stderr), None,
                f"TIMEOUT after {timeout_seconds} seconds")
    except OSError as exc:
        return "", str(exc), None, f"launch error: {exc}"


def parse_arms(stdout):
    arms = {}
    for line in stdout.splitlines():
        m = ARM_LINE.match(line.strip())
        if not m:
            continue
        arm, body = m.groups()
        kv = dict(p.split("=", 1) for p in body.split() if "=" in p)
        arms.setdefault(arm, {}).update(kv)
    return arms


def check(pinned, got):
    """Return reason string or None."""
    if got is None:
        return "key missing"
    if isinstance(pinned, tuple):
        try:
            v = float(got)
        except (TypeError, ValueError):
            return f"{got!r} not numeric"
        if not (pinned[0] <= v <= pinned[1]):
            return f"{got!r} outside pinned bound {pinned}"
        return None
    if got != pinned:
        return f"{got!r} != pinned {pinned!r}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--love",
                        default="/usr/bin/love" if Path("/usr/bin/love").exists() else "love")
    parser.add_argument("--runs", type=Path, default=HERE.parent / "live" / "runs")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.runs / ("love-" + stamp)
    run_dir.mkdir(parents=True)

    version_out, _, version_code, version_err = run_process(
        [args.love, "--version"], 20)
    love_version = version_out.strip().splitlines()[0] if version_out.strip() else ""

    started = datetime.now(timezone.utc)
    stdout, stderr, code, error = run_process(
        [args.love, str(PROBE_DIR)], TIMEOUT_S)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    (run_dir / "probe.stdout.txt").write_text(stdout)
    (run_dir / "probe.stderr.txt").write_text(stderr)

    arms = parse_arms(stdout)
    launch_ok = error is None and code == 0
    done_marker = "LOVE_PROBE_DONE" in [l.strip() for l in stdout.splitlines()]

    results = []
    for name, arm, key, pinned in CASES:
        got = arms.get(arm, {}).get(key)
        reason = None if arm in arms else f"missing LOVE-ARM {arm}"
        if reason is None:
            reason = check(pinned, got)
        results.append({"case": name, "arm": arm, "key": key,
                        "pinned": list(pinned) if isinstance(pinned, tuple) else pinned,
                        "observed": got,
                        "verdict": "PASS" if reason is None else "FAIL",
                        "reasons": ([] if reason is None else [reason])})

    for name, off, gap, expected in SPLICE_CELLS:
        c_stdout, c_stderr, c_code, c_err = run_process(
            [args.love, str(PROBE_DIR)], TIMEOUT_S,
            {"OFFSET_MS": str(off), "GAP_MS": str(gap)})
        (run_dir / f"splice-{off}-{gap}.stdout.txt").write_text(c_stdout)
        got = splice_verdict(c_stdout) if c_err is None else "launch:" + c_err
        results.append({"case": name, "arm": "splice",
                        "key": f"offset={off},gap={gap}",
                        "pinned": expected, "observed": got,
                        "verdict": "PASS" if got == expected else "FAIL",
                        "reasons": ([] if got == expected else
                                    [f"expected {expected}"])})

    # r74 interior-write lattice: one love process per cell, spawned last
    # (fatal cells are last in the table -- a fatal cell kills only its
    # own launch and its truncated receipt is the measurement).
    for name, cell, expected, pins in IW_CELLS:
        c_stdout, c_stderr, c_code, c_err = run_process(
            [args.love, str(IW_PROBE_DIR)], TIMEOUT_S,
            {"IW_CELL": cell})
        (run_dir / f"iw-{cell}.stdout.txt").write_text(c_stdout)
        (run_dir / f"iw-{cell}.stderr.txt").write_text(c_stderr)
        flat = parse_iw(c_stdout)
        iw_flat_extras(flat, c_code, c_stdout, c_stderr)
        cls, detail = iw_classify(
            cell, flat, c_code,
            c_err is not None and c_err.startswith("TIMEOUT"), c_stdout)
        reasons = []
        if c_err is not None:
            reasons.append(c_err)
        if cls != expected:
            reasons.append(f"class {cls} != {expected} ({detail})")
        for k, pinned in pins.items():
            reason = check(pinned, flat.get(k))
            if reason is not None:
                reasons.append(f"{k}: {reason}")
        results.append({"case": name, "arm": "iw",
                        "key": f"cell={cell}", "rc": c_code,
                        "pinned": expected, "observed": cls,
                        "verdict": "PASS" if not reasons else "FAIL",
                        "reasons": reasons})

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = len(results) - passed
    for r in results:
        print(f"{r['verdict']:8} {r['case']:28} {r['arm']}|{r['key']}"
              + ("" if r['verdict'] == 'PASS' else f"  {';'.join(r['reasons'])}"))

    print(f"totals: cases={len(results)} pass={passed} fail={failed} "
          f"launch_ok={launch_ok} done_marker={done_marker} exit={code}")

    verdict = "PASS" if (failed == 0 and launch_ok and done_marker) else "FAIL"
    payload = {"love": args.love, "love_version": love_version,
               "love_version_exit": version_code,
               "love_version_error": version_err,
               "probe_dir": str(PROBE_DIR), "probe_exit": code,
               "probe_error": error, "probe_elapsed_s": elapsed,
               "started_utc": stamp, "done_marker": done_marker,
               "results": results,
               "totals": {"cases": len(results), "pass": passed, "fail": failed},
               "verdict": verdict}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{verdict} battery: {run_dir / 'verdicts.json'}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
