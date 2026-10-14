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
LAST; the process-death tail orders died, then fatal, then corrupt
(rc=-11) last of all -- each cell is its own process so a death cell is
a measured FAIL-class for that cell only.

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

r77 additions (release / callback-swap / drain-EC legality / coroutine
containment / meter), each pre-measured live by the r77 scout before arming:
  corrupt : world:release() INSIDE a callback. The object is freed while the
            engine is still running inside it -> SIGSEGV (rc=-11, no assert
            text, stderr empty), a partial receipt, no CELL_DONE reachable.
            Measured on all five channels (beginContact / preSolve /
            postSolve / a natural endContact / the drain endContact). The
            exterior twin is `died` (rc=1, catchable, no signal): the class
            is interior-only.
  swapped : world:setCallbacks mid-dispatch. The engine reads the table per
            dispatch, so the new table handles the rest of the step (later
            channels AND later contacts) and the swapped-out table never
            fires again. `muted` is the nil-table member: the surface goes
            mute for the rest of the run with the physics untouched.
  deferred (fixture member): Fixture:destroy() in a callback is the same
            gated write (retained + drained in the update epilogue), but the
            tracked body gate is fixture-BLIND -- the fixture branch gates on
            its own witness set (in-cb handle alive, list unchanged, drain EC
            at locked=false, post-drain fixture dead + body alive + count
            unchanged) instead of forcing the body gate.
  applied (drain member): at the drain EC the world is UNLOCKED, so the very
            write that is refused inside the step applies on the spot. The
            deferred rule is a lock-state rule, not a phase rule.
  immediate: a structural destroy at the drain EC executes on the spot
            (count drops and the handle dies inside the call), i.e. NOT
            deferred -- the contrast member of the same window.
  drain_abort: an abort INSIDE the drain EC. Distinct signature: the world
            is left UNLOCKED (locked_after=false) and the legal exterior
            write is NOT refused as collateral; the accepted queued destroy
            survives (body readable) and completes one step late with the
            same contact's EndContact re-firing inside the next step.
  yield_abort: a yield across the C-call boundary contained at the update
            level. Measured under both containers: coroutine.resume (the
            error comes back as a VALUE, `coused`) and pcall -- same abort
            shape (transient lock + collateral refusal + recovery), so
            resume IS a containment level while coroutine.wrap is not.
  applied (meter member): love.physics.setMeter is a module-global write --
            nothing for the lock to gate; the decisive witness is the RATIO
            (every reported quantity is scaled at the Lua boundary while the
            solver trajectory is untouched).

r78 additions (the nested-update damage surface), each pre-measured live by
the r78 scout before arming (reports/round-78/r78-scout.md, 31 cells x3
byte-stable reps). r77-boundary sec.6 found that a nested world:update inside
a callback CLEARS b2World's e_locked -- b2World::Step clears its own flag on
exit and has no entry assert (b2World.cpp:908/:960), while the love-side
destroy gates consult it (Body.cpp:527-538, Fixture.cpp:337-345):
  nested_lockclear: the nested update returns with the lock CLEARED, so the
            structural write the lock refused a moment ago APPLIES
            (Body::destroy() executes ON THE SPOT instead of queueing). The
            inner Step itself re-locks: the inner callback bracket
            (locked=true + a refused inner write) is the contrast witness.
  inner_drain: the nested update runs its OWN epilogue drain while the outer
            callback is still on the stack, so a destroy queued in the OUTER
            callback drains THERE (World::update drains destructBodies, then
            clears the vectors) -- the target is dead before the outer
            callback returns.
  dispatch_escape: destroying a CONTACTING object mid-nested-step. The destroy
            completes and the same b2Contact::Update falls through to its
            trailing PreSolve dispatch on the freed contact -> love throws
            "A fixture has escaped Memoizer!" (srcline=nil). A Lua error, not
            a signal: pcall contains it (rc=0, aborts=1, recovery to step
            200) and it is NOT the r75/r76 refused_abort shape (no assert
            text on the escape path, locked_after=false, no collateral lock
            refusal). Uncontained it escapes love.update (rc=1, stderr 0 B).
  depth2 (corrupt member): nesting AGAIN from a BODY-drain EC re-enters the
            drain loop over the vector the outer loop is iterating -> SIGSEGV
            (rc=-11, partial receipt, no CELL_DONE). The depth-2 nested update
            RETURNS first (its line is on the pipe); pcall does NOT contain a
            signal (the _wp twin dies identically). The FIXTURE-drain twin is
            the `refused` member instead (catchable b2Assert(found)).
  contact_invalidated / contact_live_after_abort: contact handles captured
            inside the drain EC (or at a plain beginContact). A clean drain or
            a natural EndContact runs c->invalidate() -> every accessor errors
            while the fixtures stay alive; an ABORTED drain unwound before
            invalidate(), so the handle is still fully usable at that step and
            only dies after the retry completes.
  livelock: an every-entry drain-EC abort NEVER converges -- one drain EC +
            one abort per subsequent step for the whole step budget, with
            nothing destroyed (no internal counter, guard or backoff).
  drain_converge: the same abort converges as soon as the retry stops
            aborting (abort budget exhausted) or the queued body's contact
            stops touching (transient contact) -- the destroy then completes.
The r78 rows are inserted ahead of the process-death tail; their own death
rows join the tail (died/fatal, then the dispatch-escape rc=1 row, then the
corrupt rows last of all).
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
        # (World.cpp:289-294 joint loop; 283-287 is the fixture loop).
        # Drain is bounded-measured; the F3 residual (exact drain line,
        # SayGoodbye observer ordering) is NARROWED not closed --
        # SayGoodbye observers land under the r77 surface cells.
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
    # ---- r77 additive cells: callback swap / fixture drain / drain-EC
    # legality / coroutine containment / meter. Each row carries its rc, and
    # the process-death rows are spawned after these, at the table's very end.
    ("iw_bc_setcallbacks", "bc_setcallbacks", "swapped", {
        # the engine reads the callback table per DISPATCH: the same step's
        # later channels (preSolve/postSolve of the firing contact) go to the
        # NEW table, and the old table's counters freeze at the swap value.
        "fire.step": "73", "fire.cb": "bc", "fire.locked": "true",
        "fire.kind": "setcallbacks",
        "fire.pos": "400,520.1500244140625",
        "cb_setcallbacks.err": "nil",
        "cb_setcallbacks.swapped_step": "73",
        "cb_setcallbacks.swapped_n": "2",
        "cb_setcallbacks.swapped_cb": "bc",
        # identity readback through labels -- never a tostring of a function
        "cb_setcallbacks.getcb": "cb2_bc,cb2_ec,cb2_pre,cb2_post",
        "cb2pre.step": "73", "cb2pre.locked": "true",
        "cb2post.step": "73", "cb2post.locked": "true",
        "r77obs.bc2": "3", "r77obs.ec2": "4",
        "r77obs.pre2": "5", "r77obs.post2": "5",
        "final.bc": "2",
        # physics invariant: the run ends exactly on the baseline pose
        "final.b1pos": "400,445.10910034179688",
        "rc": "0", "done": "true"}),
    ("iw_pre_setcallbacks", "pre_setcallbacks", "swapped", {
        # swap armed in preSolve: the SAME contact's postSolve in the same
        # step goes to the new table; the old pre count never grows again.
        "fire.step": "73", "fire.cb": "pre", "fire.locked": "true",
        "fire.kind": "setcallbacks",
        "cb_setcallbacks.swapped_n": "32",
        "cb_setcallbacks.swapped_cb": "pre",
        "cb_setcallbacks.getcb": "cb2_bc,cb2_ec,cb2_pre,cb2_post",
        "cb2post.step": "73", "cb2post.locked": "true",
        "r77obs.bc2": "3", "r77obs.ec2": "4",
        "r77obs.pre2": "4", "r77obs.post2": "5",
        "final.b1pos": "400,445.10910034179688",
        "rc": "0", "done": "true"}),
    ("iw_multi_setcallbacks", "multi_setcallbacks", "swapped", {
        # two pairs land in the same step; the swap is armed on the FIRST
        # (b4's begin), so the LATER contact's begin in the SAME step already
        # goes to the new table -- the old bc count never grows again.
        "built.bodies": "5",
        "fire.step": "73", "fire.cb": "bc", "fire.locked": "true",
        "fire.kind": "setcallbacks/-", "fire.count": "5",
        "fire.pos": "560,520.1500244140625",
        "cb_setcallbacks.swapped_n": "2",
        "cb_setcallbacks.swapped_cb": "bc",
        "cb_setcallbacks.getcb": "cb2_bc,cb2_ec,cb2_pre,cb2_post",
        "cb2bc.step": "73", "cb2bc.locked": "true", "cb2bc.dyn": "b1",
        "cb2pre.step": "73", "cb2post.step": "73",
        "r77obs.bc2": "5", "r77obs.ec2": "6",
        "r77obs.pre2": "7", "r77obs.post2": "7",
        "final.count": "5", "final.bc": "2",
        "final.b1pos": "400,445.10910034179688",
        "rc": "0", "done": "true"}),
    ("iw_bc_setcallbacks_nil", "bc_setcallbacks_nil", "muted", {
        # nil,nil,nil,nil is legal: the callback surface goes MUTE for the
        # rest of the run (every counter frozen, no EndContact ever) while
        # the physics is untouched (the run ends on the baseline pose).
        "fire.step": "73", "fire.cb": "bc", "fire.kind": "setcallbacks_nil",
        "cb_setcallbacks.swapped_n": "2",
        "cb_setcallbacks.swapped_cb": "bc",
        "r77obs.ec": "0",
        "r77obs.pre": "31", "r77obs.post": "31",
        "r77obs.bc2": "0", "r77obs.ec2": "0",
        "r77obs.pre2": "0", "r77obs.post2": "0",
        "final.ec": "0", "final.pre": "31", "final.post": "31",
        "final.b1pos": "400,445.10910034179688",
        "rc": "0", "done": "true"}),
    ("iw_bc_setcallbacks_back", "bc_setcallbacks_back", "swapped", {
        # last write wins inside one callback: the second swap restores the
        # table the engine was holding, so the NEW table never handles a
        # dispatch and the old table keeps counting to the baseline totals.
        "fire.step": "73", "fire.kind": "setcallbacks_back",
        "cb_setcallbacks.getcb": "cb2_bc,cb2_ec,cb2_pre,cb2_post",
        "cb_setcallbacks.swapped_n": "2",
        "cb_setcallbacks2.err": "nil",
        "r77obs.bc": "5", "r77obs.ec": "4",
        "r77obs.pre": "36", "r77obs.post": "36",
        "r77obs.bc2": "0", "r77obs.ec2": "0",
        "r77obs.pre2": "0", "r77obs.post2": "0",
        "final.b1pos": "400,445.10910034179688",
        "rc": "0", "done": "true"}),
    ("iw_bc_fixture_destroy", "bc_fixture_destroy", "deferred", {
        # Fixture:destroy() in-cb is the same gated write, but the tracked
        # body gate is fixture-blind: the fixture-scoped witness set is what
        # this row pins (in-cb handle alive + list unchanged, the goodbye is
        # the drain EC at locked=false, post-drain fixture dead / body alive
        # / count unchanged). Effect witness: b1 loses its collision and
        # tunnels through the ground (final y ~635).
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "fixture_destroy",
        "fire.pos": "400,520.1500244140625",
        "cb_fxdestroy.err": "nil",
        "cb_fxdestroy.fcount_before": "1",
        "cb_fxdestroy.count_after": "4",
        "drainec.step": "73",
        "drainec.dyn": "b1",
        "r77obs.count": "4",
        "after_update.count": "4",
        "after_update.b1pos": "400,511.13113403320312",
        "final.b1pos": "400,635.1639404296875",
        "rc": "0", "done": "true"}),
    ("iw_bc_fixture_destroy2", "bc_fixture_destroy2", "deferred", {
        # two fixtures on b1: the destroyed one is the LAST created (list[1]);
        # the live sibling keeps the collision, so b1 does NOT tunnel -- the
        # sibling's isDestroyed=false plus the non-tunneling pose is the
        # effect witness that separates this from a no-op write.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "fixture_destroy2",
        "cb_fxdestroy.fcount_before": "2",
        "cb_fxdestroy.sib_dead": "false",
        "cb_fxdestroy.count_after": "4",
        "drainec.dyn": "b1",
        "r77obs.fx_b_dead": "false",
        "r77obs.count": "4",
        "after_update.b1pos": "399.9598388671875,511.13873291015625",
        "final.b1pos": "394.08963012695312,445.10308837890625",
        "final.count": "4",
        "rc": "0", "done": "true"}),
    ("iw_ext_fixture_destroy", "ext_fixture_destroy", "applied", {
        # exterior control: immediate (handle dead AND the list shrunk inside
        # the call) and NO goodbye at all (no drain EC) -- the contrast that
        # makes the interior row deferred rather than applied.
        "ext_fxdestroy.err": "nil",
        "ext_fxdestroy.count_after": "4",
        "ext_fxdestroy.b1pos": "400,60",
        # no collision left: b1 falls through the ground forever
        "final.b1pos": "400,3565.44384765625",
        "final.fired": "false", "final.fire_step": "-1",
        "rc": "0", "done": "true"}),
    ("iw_drain_setpos_b2", "drain_setpos_b2", "applied", {
        # the deferred rule is a LOCK-STATE rule, not a phase rule: at the
        # drain EC (locked=false) the very write that is refused inside the
        # step applies on the spot and persists (b2 keeps falling from
        # 1234.5,678.9), while the queued b1 destroy completes in the same
        # epilogue.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "queue_target/setpos_b2",
        "cb_destroy.ok": "true", "cb_destroy.err": "nil",
        "cb_destroy.mode": "queued", "cb_destroy.count_after": "4",
        "drainec.n": "1", "drainec.step": "73",
        "drainec.locked": "false", "drainec.dyn": "b1",
        "drainact.n": "1", "drainact.kind": "setpos_b2",
        "drainact.b2pos": "1234.5,678.9000244140625",
        "r77obs.count": "3", "r77obs.b1dead": "true",
        "r77obs.b2pos": "1234.5,3713.2890625",
        "after_update.count": "3",
        "rc": "0", "done": "true"}),
    ("iw_drain_queue_b2", "drain_queue_b2", "immediate", {
        # a structural destroy at the drain EC executes ON THE SPOT: the
        # count drops and the handle dies INSIDE the call -- not deferred.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "queue_target/queue_b2",
        "cb_destroy.mode": "queued", "cb_destroy.count_after": "4",
        "drainec.n": "1", "drainec.locked": "false",
        "drainec.count": "4",
        "drainact.n": "1", "drainact.kind": "queue_b2",
        "r77obs.count": "2", "r77obs.b2dead": "true",
        "rc": "0", "done": "true"}),
    ("iw_wp_drain_throw", "wp_drain_throw", "drain_abort", {
        # an abort INSIDE the drain EC: the world is left UNLOCKED
        # (locked_after=false) and the legal exterior write is NOT refused as
        # collateral -- the distinct signature. The accepted queued destroy
        # survives the abort (body readable, count still = fire count) and
        # completes one step late, with the same contact's EndContact
        # re-firing inside the next step at locked=true.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "queue_target/throw",
        "cb_destroy.ok": "true", "cb_destroy.mode": "queued",
        "cb_destroy.count_after": "4",
        "drainec.step": "73",
        "drainec.dyn": "b1",
        "drainact.n": "1", "drainact.kind": "throw",
        "wpcall.step": "73",
        "wpcall.err": "R77-DRAIN-THROW",
        # no collateral refusal: the exterior write LANDS
        "wpext.pos_after": "999,999",
        "r77abortq.step": "73", "r77abortq.count": "4",
        "r77ecpost.step": "74",
        "r77ecpost.dyn": "b1",
        "wpcall_next.step": "74",
        "wpcall_next.b1pos": "ERR:Attempt to use destroyed body.",
        "r77recover.step": "74",
        "r77recover.count": "3",
        "final.count": "3",
        "rc": "0", "done": "true"}),
    ("iw_drain_order_joint", "drain_order_joint", "deferred", {
        # DestroyBody ordering inside the drain EC: the attached joint
        # (SayGoodbye) is ALREADY destroyed while the contact's fixture, the
        # body itself and the other body are still valid -- the drain-EC
        # window the r76 jwatch bracket could only bound.
        "built.bodies": "4",
        "fire.step": "100", "fire.locked": "true",
        "fire.kind": "queue_target/order",
        "fire.pos": "26.118637084960938,526.02276611328125",
        "cb_destroy.ok": "true", "cb_destroy.mode": "queued",
        "cb_destroy.count_after": "4",
        "drainec.n": "1", "drainec.step": "100",
        "drainec.locked": "false", "drainec.dyn": "b2",
        "drainact.n": "1", "drainact.kind": "order",
        "drainact.jcount": "0",
        "jdrain.step": "100", "jdrain.jcount": "0",
        "jdrain.isDestroyed": "true",
        "r77obs.count": "3",
        "r77obs.b1dead": "false",
        "rc": "0", "done": "true"}),
    ("iw_bc_cowrap_setpos", "bc_cowrap_setpos", "refused", {
        # the container is wherever the pcall sits: with the pcall INSIDE the
        # wrap body this is a plain refused write (rc=0, step completes, run
        # ends on the baseline pose) -- wrap adds nothing by itself.
        "fire.step": "73", "fire.kind": "cowrap_setpos",
        "fire.pos": "400,520.1500244140625",
        "cb_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setpos.scope": "cowrap_inner",
        "cb_cowrap.ok": "true", "cb_cowrap.res": "inner-done",
        "cb_cowrap.pos_after": "400,520.1500244140625",
        "final.b1pos": "400,445.10910034179688",
        "rc": "0", "done": "true"}),
    ("iw_co_update_yield", "co_update_yield", "yield_abort", {
        # coroutine.resume around the engine call IS a containment level: the
        # yield error comes BACK AS A VALUE (the coused line exists only
        # because resume returned), the run survives to step 200, and the
        # world is transiently locked with the full collateral signature.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "coyield/-",
        "coused.step": "73", "coused.ok": "false",
        "coused.err": "attempt to yield across C-call boundary",
        "r77abort.step": "73", "r77abort.update_ok": "false",
        "r77abortq.count": "4", "r77abortq.b1dead": "false",
        "r77abortext.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "r77recover.step": "74",
        "r77recover.count": "4",
        "r77recover.b1pos": "400,509.53021240234375",
        "final.steps": "200",
        "final.b1pos": "400,461.54888916015625",
        "rc": "0", "done": "true"}),
    ("iw_wp_coyield", "wp_coyield", "yield_abort", {
        # the pcall rung of the same ladder: identical abort signature
        # (transient lock + collateral refusal + recovery) and the SAME final
        # pose as the resume cell -- the container differs, the shape does
        # not. esc_fn names setPosition: the collateral write is what the
        # still-locked world refuses.
        "fire.step": "73", "fire.kind": "coyield/-",
        "wpcall.step": "73", "wpcall.update_ok": "false",
        "wpcall.err": "attempt to yield across C-call boundary",
        "wpext.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "wpcall_next.step": "74", "wpcall_next.update_ok": "true",
        "final.b1pos": "400,461.54888916015625",
        "rc": "0", "done": "true"}),
    ("iw_bc_meter", "bc_meter", "applied", {
        # love.physics.setMeter is a module-global write: nothing for the lock
        # to gate. Decisive witness is the RATIO -- at meter 60 the same world
        # position reports doubled (800,1040.3 = 2x the fire pose) and the
        # reported gravity doubles; after the restore to meter 1 the report is
        # /30 (13.33,17.34). The solver trajectory is untouched: the final
        # pose x30 is the baseline's 400,445.109...
        "fire.step": "73", "fire.cb": "bc", "fire.locked": "true",
        "fire.kind": "meter",
        "fire.pos": "400,520.1500244140625",
        "cb_meter.meter_before": "30", "cb_meter.meter_after": "60",
        "cb_meter.pos_now": "800,1040.300048828125",
        "cb_meter.grav_after": "0,1255.6800537109375",
        "cb_meter2.pos_now": "13.333333015441895,17.338333129882812",
        "final.b1pos": "13.333333015441895,14.836970329284668",
        "rc": "0", "done": "true"}),
    ("iw_pre_meter", "pre_meter", "applied", {
        # preSolve channel: identical shape to the beginContact cell (the
        # write is not lock-gated and the channel is irrelevant).
        "fire.step": "73", "fire.cb": "pre", "fire.locked": "true",
        "fire.kind": "meter",
        "cb_meter.meter_before": "30", "cb_meter.meter_after": "60",
        "cb_meter.pos_now": "800,1040.300048828125",
        "cb_meter.grav_after": "0,1255.6800537109375",
        "cb_meter2.pos_now": "13.333333015441895,17.338333129882812",
        "final.b1pos": "13.333333015441895,14.836970329284668",
        "rc": "0", "done": "true"}),
    # ---- r78 additive cells: the nested-update damage surface. Inserted
    # ahead of the process-death tail; each row pins the decisive witnesses
    # the class gate does not already enforce (poses, counts, census, the
    # drain-entry index) plus the identity of the object/body under test.
    ("iw_n_baseline", "n_baseline", "nested_lockclear", {
        # lock-clear: the nested update returns with the lock CLEARED and the
        # write the lock refused a moment ago APPLIES (Body::destroy() would
        # execute on the spot too). The inner Step re-locks -- its bracket is
        # the contrast, and the pose pins are the nested update's own
        # physics-visible effect (a no-write nest is not a no-op).
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "nested_probe/-",
        "fire.pos": "400,520.1500244140625",
        "r78npre.lock": "true", "r78npre.count": "4",
        "r78nest1.in_cb": "true", "r78nest1.count": "4",
        "r78setpos.pos_after": "1234.5,678.9000244140625",
        "r78nextstep.step": "74",
        "r78nextstep.b1pos": "1234.5,539.9063720703125",
        "r78obs.nest_n": "1", "r78obs.nest_ok": "1", "r78obs.count": "4",
        "final.b1pos": "1234.5,656.3702392578125",
        "final.bc": "4", "final.ec": "3",
        "final.pre": "37", "final.post": "37",
        "done": "true", "rc": "0"}),
    ("iw_n_inner_cb", "n_inner_cb", "nested_lockclear", {
        # the same nest with a velocity write first: the inner-Step bracket
        # (locked=true + a refused inner write) is the measured lock bracket,
        # and the post-nest write still applies.
        "fire.step": "73", "fire.locked": "true",
        "fire.kind": "nested_inner_cb/-",
        "r78npre.setvel_ok": "true", "r78npre.setvel_err": "nil",
        "r78setpos.pos_after": "1234.5,678.9000244140625",
        "r78nextstep.b1pos": "1234.5,531.55010986328125",
        "r78obs.nest_ok": "1",
        "final.b1pos": "1234.5,80.874465942382812",
        "final.bc": "4", "final.ec": "3",
        "final.pre": "37", "final.post": "37",
        "done": "true", "rc": "0"}),
    ("iw_n_depth2_seq", "n_depth2_seq", "nested_lockclear", {
        # TWO sequential nested updates in one callback are contained: both
        # return with the lock cleared (depth=1 each -- they are sequential,
        # not nested in one another) and the write applies. The corrupt
        # member is the drain-EC nest, not depth 2 per se.
        "fire.step": "73", "fire.kind": "nested_twice/-",
        "r78nest1.in_cb": "true",
        "r78nest2.ok": "true", "r78nest2.lock_after": "false",
        "r78nest2.depth": "1", "r78nest2.in_cb": "true",
        "r78obs.nest_n": "2", "r78obs.nest_ok": "2",
        "r78setpos.pos_after": "1234.5,678.9000244140625",
        "r78nextstep.b1pos": "400,509.87939453125",
        "final.b1pos": "400,438.03939819335938",
        "final.bc": "7", "final.ec": "5",
        "final.pre": "40", "final.post": "39",
        "done": "true", "rc": "0"}),
    ("iw_n_queue_inner_drain", "n_queue_inner_drain", "inner_drain", {
        # inner-drain ownership: the destroy queued in the OUTER callback
        # drains at the INNER epilogue (its EndContact is the drain EC at
        # locked=false, depth=1, in_cb=true), so the target is already dead
        # when the nested update returns -- and the run survives to step 200.
        "fire.step": "73", "fire.kind": "nested_queue/-",
        "r78queue.what": "b3", "r78queue.ok": "true",
        "r78queue.count": "4",
        "r78drainec.n": "1", "r78drainec.step": "73",
        "r78drainec.dyn": "b3", "r78drainec.count": "4",
        "r78drainec.own": "true", "r78drainec.own_n": "1",
        "r78destroy.what": "b3", "r78destroy.drain_n": "1",
        "r78nest1.count": "3",
        "postfire.count": "3", "postfire.drain_n": "1",
        "r78nextstep.b3pos": "ERR:Attempt to use destroyed body.",
        "r78obs.b3dead": "true", "r78obs.count": "3",
        "final.count": "3", "final.bc": "4", "final.ec": "4",
        "final.pre": "37", "final.post": "37",
        "final.b1pos": "1234.5,656.3702392578125",
        "done": "true", "rc": "0"}),
    ("iw_n_destroy_contacting_wp", "n_destroy_contacting_wp", "dispatch_escape", {
        # contacting-destroy escape, contained: the destroy executes on the
        # spot (dead + count 3 inside the callback) and the same contact
        # Update's trailing PreSolve dispatch on the freed contact raises
        # love's Memoizer error -- srcline=nil, locked_after=false, and the
        # exterior write is refused by the LIFETIME guard, not by a lock.
        "fire.step": "73", "fire.kind": "nested_destroy/-",
        "r78destroy.what": "b1", "r78destroy.err": "nil",
        "r78destroy.count": "3",
        "r78drainec.n": "1", "r78drainec.dyn": "b1",
        "r78drainec.own": "false", "r78drainec.own_n": "0",
        "r78wpcall.err": "A fixture has escaped Memoizer!",
        "r78wpext.ok": "false",
        "r78wpext.err": "Attempt to use destroyed body.",
        "r78recover.b1dead": "true", "r78recover.count": "3",
        "r78obs.aborts": "1", "r78obs.count": "3",
        "final.count": "3", "final.bc": "8", "final.ec": "6",
        "final.pre": "67", "final.post": "67",
        "final.b1pos": "ERR:Attempt to use destroyed body.",
        "done": "true", "rc": "0"}),
    ("iw_n_destroy_ground_wp", "n_destroy_ground_wp", "dispatch_escape", {
        # the static side of the same escape: two immediate-destroy EndContacts
        # (b1's and b3's, own=false -- nothing was queued, the destroy ran on
        # the spot), then the same Memoizer text -- and the exterior write is NOT
        # refused as collateral (the world is unlocked): 999,999 lands.
        "fire.step": "73", "fire.kind": "nested_destroy/-",
        "r78destroy.what": "g", "r78destroy.err": "nil",
        "r78destroy.count": "3",
        "r78drainec.n": "2", "r78drainec.dyn": "b3",
        "r78drainec.own": "false", "r78drainec.own_n": "0",
        "r78wpcall.err": "A fixture has escaped Memoizer!",
        "r78wpext.ok": "true", "r78wpext.pos_after": "999,999",
        "r78recover.count": "3",
        "r78nextstep.drain_n": "2",
        "r78obs.aborts": "1", "r78obs.drain_n": "2",
        "final.count": "3", "final.bc": "2", "final.ec": "2",
        "final.pre": "33", "final.post": "33",
        "final.b1pos": "999,1105.313720703125",
        "done": "true", "rc": "0"}),
    ("iw_n_destroy_fx_wp", "n_destroy_fx_wp", "dispatch_escape", {
        # the fixture member: the contacting fixture is torn down on the spot
        # (the fixture list shrinks 1 -> 0 inside the callback) while the BODY
        # survives, then the same escape. Same text, different escape site.
        "fire.step": "73", "fire.kind": "nested_destroy_fx/-",
        "r78destroy.what": "fx", "r78destroy.err": "nil",
        "r78destroy.fcount_before": "1", "r78destroy.fcount_after": "0",
        "r78destroy.count": "4",
        "r78drainec.n": "1", "r78drainec.dyn": "b1",
        "r78drainec.own": "false", "r78drainec.own_n": "0",
        "r78wpcall.err": "A fixture has escaped Memoizer!",
        "r78wpext.ok": "true", "r78wpext.pos_after": "999,999",
        "r78obs.aborts": "1", "r78obs.count": "4",
        "final.count": "4", "final.bc": "4", "final.ec": "3",
        "final.pre": "36", "final.post": "36",
        "final.b1pos": "999,1105.313720703125",
        "done": "true", "rc": "0"}),
    ("iw_n_depth2_fxdrain", "n_depth2_fxdrain", "refused", {
        # the fixture-drain twin of the depth-2 nest: the drain EC fires in
        # the OUTER epilogue (depth=0, in_cb=false), the re-entrant
        # Fixture::destroy re-runs b2Body::DestroyFixture, and its
        # b2Assert(found) is CATCHABLE -- rc=0, the run continues to step 200.
        "fire.step": "73", "fire.kind": "queue_fixture/nested_update",
        "r78queue.what": "fx", "r78queue.dead_in_cb": "false",
        "r78queue.fcount_before": "1", "r78queue.fcount_after": "1",
        "r78drainact.n": "1", "r78drainact.depth_before": "0",
        "r78drainec.own": "true", "r78drainec.own_n": "1",
        "r78nest1.err": "Box2D assertion failed: found",
        "r78nest1.in_cb": "false", "r78nest1.count": "4",
        "r78obs.nest_ok": "0", "r78obs.drain_n": "1",
        "r78nextstep.b1pos": "400,491.28445434570312",
        "final.b1pos": "400,647.3021240234375",
        "final.bc": "4", "final.ec": "4",
        "final.pre": "35", "final.post": "35",
        "done": "true", "rc": "0"}),
    ("iw_z_drain_use_after", "z_drain_use_after", "contact_invalidated", {
        # zombie handle, clean drain: the handle captured inside the drain EC
        # is invalidated one step later (every accessor errors) while BOTH of
        # the contact's fixtures stay alive -- the touching path invalidates
        # properly.
        "fire.step": "4", "fire.kind": "queue_body/capture",
        "fire.pos": "650,519.94647216796875",
        "r78queue.what": "b3", "r78queue.dead_in_cb": "false",
        "r78drainec.n": "1", "r78drainec.step": "4",
        "r78drainec.dyn": "b3",
        "r78drainec.own": "true", "r78drainec.own_n": "1",
        "r78zcap.touch": "true",
        "r78zcap.fa": "g", "r78zcap.fb": "b3",
        "r78zpost.fxb": "true",
        "r78obs.count": "3", "r78obs.b3dead": "true",
        "final.count": "3", "final.bc": "5", "final.ec": "5",
        "final.pre": "6", "final.post": "6",
        "final.b1pos": "400,445.10910034179688",
        "done": "true", "rc": "0"}),
    ("iw_z_abort_use_after", "z_abort_use_after", "contact_live_after_abort", {
        # zombie handle, ABORTED drain: the abort unwinds before
        # Contact::invalidate(), so the SAME handle is still fully usable at
        # the abort step (touch/fixtures/children/friction/positions all read)
        # and only dies after the retry completes one step late.
        "fire.step": "4", "fire.kind": "queue_body/capture_throw",
        "r78drainec.n": "2", "r78drainec.step": "5",
        "r78drainec.own": "true", "r78drainec.own_n": "2",
        "r78drainact.kind": "throw", "r78drainact.n": "1",
        "r78wpcall.err": "R78-DRAIN-ABORT",
        "r78wpext.ok": "true",
        "r78zsame.fa": "g", "r78zsame.fb": "b3",
        "r78zsame.ca": "1", "r78zsame.cb": "1",
        "r78zlate.fxa": "false", "r78zlate.fxb": "true",
        "r78zstate.tag": "late", "r78zstate.count": "3",
        "r78recover.step": "5", "r78recover.b3dead": "true",
        "r78obs.drain_n": "2", "r78obs.aborts": "1", "r78obs.count": "3",
        "final.count": "3", "final.bc": "3", "final.ec": "4",
        "final.pre": "5", "final.post": "5",
        "final.b1pos": "999,4502.70068359375",
        "done": "true", "rc": "0"}),
    ("iw_z_touch_then_end", "z_touch_then_end", "contact_invalidated", {
        # the isolation control: a handle captured at a plain beginContact and
        # probed after the natural EndContact -- invalidated, fixtures alive,
        # no drain and no abort anywhere in the receipt.
        "fire.step": "73", "fire.kind": "capture_bc/-",
        "r78zcap.fa": "g", "r78zcap.fb": "b1",
        "r78zend.fxb": "false",
        "r78obs.drain_n": "0", "r78obs.aborts": "0",
        "final.count": "4", "final.bc": "5", "final.ec": "4",
        "final.pre": "36", "final.post": "36",
        "final.b1pos": "400,445.10910034179688",
        "done": "true", "rc": "0"}),
    ("iw_livelock_all", "livelock_all", "livelock", {
        # every-entry drain-EC abort on a PERSISTENT contact: one drain EC +
        # one abort per subsequent step for the whole budget (fire at step 4
        # -> 197 attempts over steps 4-200, the last one AT the final step),
        # nothing destroyed, and the run still ends rc=0. The bound is linear
        # in the caller's step budget -- there is no internal counter, guard
        # or backoff. (`ec` inflates with the aborts: the abort unwinds after
        # the EndContact dispatch, so the same goodbye re-fires.)
        "fire.step": "4", "fire.kind": "queue_body/throwall",
        "r78queue.what": "b3", "r78queue.dead_in_cb": "false",
        "r78drainec.n": "197", "r78drainec.step": "200",
        "r78drainec.dyn": "b3",
        "r78drainec.own": "true", "r78drainec.own_n": "197",
        "r78drainact.kind": "throwall", "r78drainact.n": "197",
        "r78wpcall.err": "R78-DRAIN-THROWALL",
        "r78wpext.pos_after": "999,999",
        "r78obs.count": "4",
        "r78obs.b3pos": "650,519.85009765625",
        "final.steps": "200", "final.count": "4",
        "final.bc": "3", "final.ec": "199",
        "final.pre": "34", "final.post": "34",
        "final.b1pos": "999,4501.82861328125",
        "done": "true", "rc": "0"}),
    ("iw_livelock_stop2", "livelock_stop2", "drain_converge", {
        # the same abort with a two-entry budget: entries 1-2 abort, entry 3
        # is a no-op, the queued destroy completes THERE (drain_n=3, aborts=2,
        # count 4 -> 3) and the run recovers at step 6. Convergence is the
        # retry's own outcome, not a timeout.
        "fire.step": "4", "fire.kind": "queue_body/throw_stop",
        "r78queue.what": "b3", "r78queue.dead_in_cb": "false",
        "r78drainec.n": "3", "r78drainec.step": "6",
        "r78drainec.dyn": "b3",
        "r78drainec.own": "true", "r78drainec.own_n": "3",
        "r78drainact.kind": "noop", "r78drainact.n": "3",
        "r78wpcall.err": "R78-DRAIN-THROW-2",
        "r78wpext.ok": "true",
        "r78recover.step": "6", "r78recover.count": "3",
        "r78obs.drain_n": "3", "r78obs.aborts": "2",
        "r78obs.count": "3", "r78obs.b3dead": "true",
        "final.count": "3", "final.bc": "3", "final.ec": "5",
        "final.pre": "6", "final.post": "6",
        "done": "true", "rc": "0"}),
    ("iw_livelock_transient", "livelock_transient", "drain_converge", {
        # the other convergence path: the target is the BOUNCING body, so the
        # retry at the next step finds no touching contact -> no drain EC, no
        # abort, and the queued destroy completes silently (drain_n stays 1,
        # count 4 -> 3). The bound shape is the CONTACT's lifetime.
        "fire.step": "73", "fire.kind": "queue_body/throwall",
        "r78queue.what": "b1", "r78queue.dead_in_cb": "false",
        "r78drainec.n": "1", "r78drainec.step": "73",
        "r78drainec.dyn": "b1",
        "r78drainec.own": "true", "r78drainec.own_n": "1",
        "r78wpcall.err": "R78-DRAIN-THROWALL",
        "r78wpext.ok": "true",
        "r78recover.step": "74", "r78recover.count": "3",
        "r78obs.drain_n": "1", "r78obs.aborts": "1",
        "r78obs.count": "3", "r78obs.b1dead": "true",
        "final.count": "3", "final.bc": "4", "final.ec": "4",
        "final.pre": "35", "final.post": "35",
        "final.b1pos": "ERR:Attempt to use destroyed body.",
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
    # ---- r77 process-death cells: spawned LAST, after every cell whose
    # witness could otherwise be lost. `died` first, then `fatal`, then the
    # corrupt tail (rc=-11) last of all.
    ("iw_bc_coyield", "bc_coyield", "died", {
        # a yield across the C-call boundary with NO container: an error that
        # escapes love.update. rc=1, no assert text; esc_fn names the yield
        # itself (the wrap twin names the wrap function instead).
        "fire.step": "73", "fire.kind": "coyield", "fire.locked": "true",
        "rc": "1", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "yield"}),
    ("iw_cowrap_update_yield", "cowrap_update_yield", "died", {
        # the same yield under coroutine.wrap at the update level: wrap is NOT
        # a containment level -- the error is re-raised in the caller.
        "fire.step": "73", "fire.kind": "coyield/-", "fire.locked": "true",
        "rc": "1", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "f"}),
    ("iw_ext_worldrelease", "ext_worldrelease", "died", {
        # exterior control: release() outside the engine's own execution is a
        # CATCHABLE error (no signal) on every later Lua touch -- world access
        # hits the proxy guard, body access the lifetime guard -- and the
        # process dies rc=1 at the first UNGUARDED world touch (love.update's
        # own call). Interior-only is what makes `corrupt` mean something.
        # `ext_rel_call.err=true` is release()'s RETURN VALUE, not an error.
        "ext_rel_call.ok": "true", "ext_rel_call.err": "true",
        "ext_rel_world_access.ok": "false",
        "ext_rel_world_access.err":
            "Cannot use object after it has been released.",
        "ext_rel_body_access.ok": "false",
        "ext_rel_body_access.err": "Attempt to use destroyed body.",
        "rc": "1", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "update"}),
    ("iw_bc_cowrap_unp", "bc_cowrap_unp", "fatal", {
        # uncontained assert-gated write inside coroutine.wrap: the error is
        # re-raised in the caller, so the assert still escapes the callback --
        # fatal, with esc_fn=co naming the wrap frame.
        "fire.step": "73", "fire.kind": "cowrap_unp", "fire.locked": "true",
        "rc": "1", "done": "false",
        "err_on": "stdout", "assert_txt": "m_world_islocked", "esc_fn": "co"}),
    # r78 process-death cell: the dispatch escape with NO container. It is a
    # love::Exception from a contact dispatch -- not an assert-gated `fatal`
    # (assert_txt here is the inner-Step bracket's refused write, not the
    # escape's) and not a signal (`died`). Spawned with the death tail.
    ("iw_n_destroy_contacting", "n_destroy_contacting", "dispatch_escape", {
        "fire.step": "73", "fire.kind": "nested_destroy/-",
        "r78destroy.what": "b1",
        "r78destroy.err": "nil",
        "r78destroy.count": "3",
        "r78drainec.n": "1", "r78drainec.dyn": "b1",
        "r78drainec.own": "false", "r78drainec.own_n": "0",
        "r78nest1.count": "4",
        "postfire.count": "3", "postfire.drain_n": "1",
        # the death site: the escape surfaces out of love.update
        "esc_fn": "update",
        "rc": "1", "done": "false"}),
    # corrupt (rc=-11): world:release() INSIDE the engine's own execution, on
    # every dispatch channel. The last emitted line is the callback's own
    # final write (the caller's own count/pose report is the death site and
    # never reaches the pipe); no CELL_DONE is reachable.
    ("iw_bc_worldrelease", "bc_worldrelease", "corrupt", {
        "fire.step": "73", "fire.cb": "bc", "fire.locked": "true",
        "fire.kind": "worldrelease",
        "fire.pos": "400,520.1500244140625",
        "rel_pre.kind": "worldrelease",
        "rel_call.ok": "true", "rel_call.err": "true",
        "rel_alive.marker": "1", "rel_post.marker": "1",
        "rc": "-11", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "none"}),
    ("iw_pre_worldrelease", "pre_worldrelease", "corrupt", {
        "fire.step": "73", "fire.cb": "pre", "fire.locked": "true",
        "fire.kind": "worldrelease",
        "fire.pos": "400,520.1500244140625",
        "rel_pre.kind": "worldrelease",
        "rel_call.ok": "true", "rel_call.err": "true",
        "rel_alive.marker": "1", "rel_post.marker": "1",
        "rc": "-11", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "none"}),
    ("iw_post_worldrelease", "post_worldrelease", "corrupt", {
        # postSolve sees the POST-step pose, like every other postSolve cell
        "fire.step": "73", "fire.cb": "post", "fire.locked": "true",
        "fire.kind": "worldrelease",
        "fire.pos": "400,511.13113403320312",
        "rel_pre.kind": "worldrelease",
        "rel_call.ok": "true", "rel_call.err": "true",
        "rel_alive.marker": "1", "rel_post.marker": "1",
        "rc": "-11", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "none"}),
    ("iw_ec_worldrelease", "ec_worldrelease", "corrupt", {
        # the NATURAL endContact (locked=true, inside the step): the release
        # is not a channel property -- it destroys the world the engine is
        # executing inside, whichever dispatch reaches it.
        "fire.step": "74", "fire.cb": "ec", "fire.locked": "true",
        "fire.kind": "worldrelease/-",
        "fire.pos": "400,511.13113403320312",
        "rel_pre.kind": "worldrelease",
        "rel_call.ok": "true", "rel_call.err": "true",
        "rel_alive.marker": "1", "rel_post.marker": "1",
        "rc": "-11", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "none"}),
    ("iw_drain_worldrelease", "drain_worldrelease", "corrupt", {
        # the DRAIN endContact (locked=false, inside the update epilogue):
        # the same crash from the one window where the world is unlocked.
        # The release is the drain hook's LAST action -- no Lua world touch
        # follows it, so the engine (not a Lua guard) is what dies.
        "fire.step": "73", "fire.cb": "bc", "fire.locked": "true",
        "fire.kind": "queue_target/worldrelease",
        "cb_destroy.ok": "true", "cb_destroy.mode": "queued",
        "cb_destroy.count_after": "4",
        "drainec.n": "1", "drainec.step": "73",
        "drainec.locked": "false", "drainec.dyn": "b1",
        "drainrel.kind": "worldrelease", "drainrel.n": "1",
        "drainrel.call_ok": "true", "drainrel.call_ret": "true",
        "drainrel.alive": "1",
        "rc": "-11", "done": "false",
        "err_on": "none", "assert_txt": "none", "esc_fn": "none"}),
    # r78 corrupt tail (rc=-11, last of all): a nested world:update issued from
    # a BODY-drain EC. The depth-2 nested update RETURNS first -- its receipt
    # is the last line on the pipe -- and the process then dies inside the
    # drain loop, before any further Lua frame. The _wp twin is the SAME
    # witness set: pcall does not contain a signal. `assert_txt` is not pinned
    # here (the inner-Step bracket line carries the IsLocked text; the death
    # itself has no assert text).
    ("iw_n_depth2_drain", "n_depth2_drain", "corrupt", {
        "fire.step": "73", "fire.kind": "nested_queue/nested_update",
        "fire.locked": "true",
        "r78queue.what": "b3", "r78queue.ok": "true",
        "r78queue.dead_in_cb": "false", "r78queue.count": "4",
        "r78drainact.n": "1",
        "r78drainact.depth_before": "1", "r78drainact.lock": "false",
        "r78drainec.dyn": "b3", "r78drainec.own": "true",
        "r78drainec.own_n": "2",
        "r78nest2.count": "3",
        "rc": "-11", "done": "false"}),
    ("iw_n_depth2_drain_wp", "n_depth2_drain_wp", "corrupt", {
        # identical receipt modulo the cell name: the update-level pcall never
        # returns, so a signal is not containable -- the class is the same.
        "fire.step": "73", "fire.kind": "nested_queue/nested_update",
        "fire.locked": "true",
        "r78queue.what": "b3", "r78queue.ok": "true",
        "r78queue.dead_in_cb": "false", "r78queue.count": "4",
        "r78drainact.n": "1",
        "r78drainact.depth_before": "1", "r78drainact.lock": "false",
        "r78drainec.dyn": "b3", "r78drainec.own": "true",
        "r78drainec.own_n": "2",
        "r78nest2.count": "3",
        "rc": "-11", "done": "false"}),
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
    swapped|muted|immediate|drain_abort|yield_abort|corrupt|anomaly}.
    Partial-capture detection is built in: fire-present without
    CELL_DONE is never a pass shape.

    r78 classes: {nested_lockclear|inner_drain|dispatch_escape|
    contact_invalidated|contact_live_after_abort|livelock|drain_converge}.

    r78 members of existing classes (pre-measured, reports/round-78/
    r78-scout.md):
      refused: the r74 member is the lock-guard text ("...IsLocked() ==
              false"); the r78 member is a nested update issued from a
              FIXTURE-drain EC, where the re-entrant Fixture::destroy
              re-runs b2Body::DestroyFixture and its b2Assert(found)
              fires ("Box2D assertion failed: found") -- same shape
              (catchable Box2D assertion refusal), different assert site.
      corrupt: the r77 member is world:release() inside the engine's own
              execution; the r78 member is a depth-2 nested update issued
              from a BODY-drain EC. Both are signal deaths inside engine
              execution (rc=-11, partial receipt, no CELL_DONE); the
              witness sets are disjoint and each is required in full.
    """
    if timed_out:
        return "timeout", f"exceeded {TIMEOUT_S}s"
    done = flat.get("done") == "true"
    has_fire = "fire.step" in flat
    if done and rc == 0:
        if cell == "baseline":
            return "captured", "availability lattice"
        # ---- r77 measured shapes (inserted ahead of the pre-r77 gates) ----
        # Each branch gates on its own decisive witness VALUES and returns
        # anomaly when they are incomplete: no r77 receipt can satisfy a
        # pre-r77 gate by accident, and a partial r77 receipt cannot pass.
        if "cb_meter.ok" in flat:
            # seed 6: love.physics.setMeter is a module-global write -- there
            # is nothing for the lock to gate. The ratio (pos doubling at
            # meter 60, the /30 report afterwards) is pinned per cell.
            if (flat.get("cb_meter.ok") == "true"
                    and flat.get("cb_meter.err") == "nil"
                    and flat.get("cb_meter.meter_after")
                        != flat.get("cb_meter.meter_before")
                    and flat.get("cb_meter2.ok") == "true"
                    and flat.get("cb_meter2.meter") == "1"):
                return "applied", "meter global write under the lock"
            return "anomaly", "meter witness incomplete"
        if "cb_fxdestroy.ok" in flat:
            # seed 3: Fixture:destroy() in a callback is deferred-family, but
            # the tracked body gate is fixture-BLIND (count and body are both
            # untouched by it), so this branch gates on the fixture-scoped
            # witness set: accepted call, handle still alive in-cb, fixture
            # list unchanged, the goodbye is the drain EC at locked=false, and
            # after the drain the fixture is dead while the body is alive and
            # the count is unchanged.
            if (flat.get("cb_fxdestroy.ok") == "true"
                    and flat.get("cb_fxdestroy.isDestroyed_in_cb") == "false"
                    and flat.get("cb_fxdestroy.fcount_after")
                        == flat.get("cb_fxdestroy.fcount_before")
                    and flat.get("drainec.n") == "1"
                    and flat.get("drainec.locked") == "false"
                    and flat.get("r77obs.fx_a_dead") == "true"
                    and flat.get("r77obs.b1dead") == "false"
                    and flat.get("r77obs.count") == flat.get("built.bodies")):
                return "deferred", "fixture drained at locked=false (fixture witness)"
            return "anomaly", "fixture destroy without deferred witness"
        if "ext_fxdestroy.ok" in flat:
            # the exterior control: immediate (handle dead AND the list shrunk
            # inside the call) and there is no goodbye at all.
            if (flat.get("ext_fxdestroy.ok") == "true"
                    and flat.get("ext_fxdestroy.isDestroyed_after") == "true"
                    and flat.get("ext_fxdestroy.fcount") == "0"
                    and "drainec.n" not in flat):
                return "applied", "exterior fixture destroy (immediate)"
            return "anomaly", "exterior fixture destroy witness incomplete"
        if "cb_setcallbacks.ok" in flat:
            # seed 2: world:setCallbacks mid-dispatch. The engine reads the
            # table at each dispatch, so the swap is effective for every later
            # dispatch of the step -- later channels AND later contacts -- and
            # a swapped-out table never fires again. Identity is read back
            # through labels (never a tostring of a function).
            if flat.get("cb_setcallbacks.ok") != "true":
                return "anomaly", "setCallbacks refused"
            labels = flat.get("cb_setcallbacks.getcb", "")
            swapped_cb = flat.get("cb_setcallbacks.swapped_cb", "")
            new_ran = any(flat.get(f"r77obs.{k}2", "0") != "0"
                          for k in ("bc", "ec", "pre", "post"))
            old_at_swap = flat.get("cb_setcallbacks.swapped_n", "")
            old_final = flat.get(f"r77obs.{swapped_cb}", "")
            if labels == "nil,nil,nil,nil":
                # a nil table is legal: the callback surface goes mute for the
                # rest of the run while the physics stays untouched (pinned).
                if not new_ran and old_final == old_at_swap:
                    return "muted", "nil table: surface mute, physics untouched"
                return "anomaly", "nil-table mute witness incomplete"
            if "cb2_" in labels:
                if flat.get("cb_setcallbacks2.ok") == "true":
                    # the revert member: the first readback shows the new
                    # table, the second swap restores the old one, so the new
                    # table never handled a dispatch while the old table kept
                    # counting to its baseline totals.
                    try:
                        grew = int(old_final) > int(old_at_swap)
                    except (TypeError, ValueError):
                        grew = False
                    if (flat.get("cb_setcallbacks2.getcb")
                            == "c_bc,c_ec,c_pre,c_post"
                            and not new_ran and grew):
                        return "swapped", "last write wins; new table never fired"
                    return "anomaly", "revert witness incomplete"
                if new_ran and old_final == old_at_swap:
                    return "swapped", "new table handled the rest; old table frozen"
                return "anomaly", "swap witness incomplete"
            if labels == "c_bc,c_ec,c_pre,c_post":
                # a swap that never took: the readback is still the old table
                # and no new-table dispatch happened -- not this class.
                return "anomaly", "setCallbacks did not change the table"
            return "anomaly", f"unreadable getcb {labels!r}"
        if flat.get("drainact.kind") == "throw":
            # seed 4: an abort INSIDE the drain EC. Distinct signature: the
            # world is left UNLOCKED (locked_after=false) and the legal
            # exterior write is NOT refused as collateral; the accepted queued
            # destroy survives (body readable) and completes one step late.
            if (flat.get("drainec.n") == "1"
                    and flat.get("drainec.locked") == "false"
                    and flat.get("wpcall.update_ok") == "false"
                    and "R77-DRAIN-THROW" in flat.get("wpcall.err", "")
                    and flat.get("wpcall.locked_after") == "false"
                    and flat.get("wp_setpos.ok") == "false"
                    and flat.get("wpext.ok") == "true"
                    and flat.get("r77abortq.count") is not None
                    and flat.get("drainec.count") is not None
                    and flat.get("r77abortq.count") == flat.get("drainec.count")
                    and flat.get("r77abortq.b1dead") == "false"
                    and flat.get("r77ecpost.locked") == "true"
                    and flat.get("wpcall_next.update_ok") == "true"
                    and flat.get("wpcall_next.locked_after") == "false"
                    and flat.get("wpcall_next.b1pos", "").startswith("ERR:")
                    and flat.get("r77recover.locked_after") == "false"
                    and flat.get("r77recover.b1dead") == "true"):
                return "drain_abort", "abort at locked=false; no collateral refusal"
            return "anomaly", "drain-EC abort witness incomplete"
        if "coused.ok" in flat:
            # seed 5, resume rung: coroutine.resume around the engine call.
            # The error comes BACK AS A VALUE -- the coused line exists only
            # because resume returned instead of propagating -- the run
            # survives, and the world is transiently locked with the full
            # collateral signature.
            if ("attempt to yield across C-call boundary" in flat.get("coused.err", "")
                    and flat.get("coused.costatus") == "dead"
                    and flat.get("r77abort.locked_after") == "true"
                    and flat.get("r77abortext.ok") == "false"
                    and flat.get("r77recover.locked_after") == "false"):
                return "yield_abort", "resume returned the yield error; run survived"
            return "anomaly", "resume containment witness incomplete"
        if ("wpcall.update_ok" in flat
                and "attempt to yield across C-call boundary"
                    in flat.get("wpcall.err", "")):
            # seed 5, pcall rung: the SAME abort shape under update-level
            # pcall containment (no resume anywhere in the receipt).
            if (flat.get("wpcall.locked_after") == "true"
                    and flat.get("wpext.ok") == "false"
                    and flat.get("wpcall_next.locked_after") == "false"):
                return "yield_abort", "pcall containment of a yield abort"
            return "anomaly", "yield abort under pcall without witness"
        if flat.get("drainact.kind") == "setpos_b2":
            # seed 4: the deferred rule is a LOCK-STATE rule, not a phase
            # rule. At the drain EC (locked=false) the very write that is
            # refused inside the step applies on the spot and persists.
            if (flat.get("drainact.ok") == "true"
                    and flat.get("drainact.err") == "nil"
                    and flat.get("drainact.b2pos", "").startswith("1234.5,")
                    and flat.get("r77obs.b2pos", "").startswith("1234.5,")):
                return "applied", "drain-EC write applied (world unlocked)"
            return "anomaly", "drain-EC write without applied witness"
        if flat.get("drainact.kind") == "queue_b2":
            # seed 4: a structural destroy at the drain EC is IMMEDIATE, not
            # deferred -- the count drops and the handle dies inside the call.
            if (flat.get("drainact.ok") == "true"
                    and flat.get("drainact.err") == "nil"
                    and flat.get("drainact.b2dead") == "true"
                    and flat.get("drainact.count_after")
                        == str(int(flat.get("drainec.count", "0")) - 1)):
                return "immediate", "drain-EC destroy executed on the spot"
            return "anomaly", "drain-EC destroy without immediate witness"
        if flat.get("drainact.kind") == "order":
            # seed 4: DestroyBody ordering inside the drain EC -- the attached
            # joints (SayGoodbye) are already destroyed, the contact's fixture
            # and the body are still valid, the other body is alive.
            if (flat.get("drainact.j_dead") == "true"
                    and flat.get("drainact.fx_dead") == "false"
                    and flat.get("drainact.body_dead") == "false"
                    and flat.get("drainact.other_dead") == "false"
                    and flat.get("r77obs.b2dead") == "true"):
                return "deferred", "body drained after its joints (order witness)"
            return "anomaly", "drain-order witness incomplete"
        # ---- r78 measured shapes (the nested-update damage surface) ----
        # Each branch gates on its own decisive witness VALUES and returns
        # anomaly when they are incomplete: no r78 receipt can satisfy an
        # earlier gate by accident, and a partial r78 receipt cannot pass.
        # Precedence (documented, not incidental): inner_drain before
        # nested_lockclear (a cell can show both -- the drain ownership is
        # the more specific shape); the zombie branch before the livelock
        # branch (both carry an abort count).
        if (flat.get("r78drainec.in_cb") == "true"
                and flat.get("r78drainec.depth") == "1"
                and flat.get("r78drainec.locked") == "false"):
            # seed 2: the nested update runs its OWN epilogue drain while the
            # outer callback is still on the stack (depth=1, in_cb=true), so
            # the destroy queued in the OUTER callback drains THERE -- the
            # target is already dead when the nested update returns, with the
            # outer callback still running.
            if (flat.get("r78nest1.ok") == "true"
                    and flat.get("r78nest1.lock_after") == "false"
                    and flat.get("r78queue.dead_in_cb") == "false"
                    and flat.get("r78destroy.dead") == "true"
                    and flat.get("r78destroy.count")
                        == str(int(flat.get("built.bodies", "0")) - 1)):
                return "inner_drain", "queued destroy drained at the INNER epilogue"
            return "anomaly", "inner-drain ownership witness incomplete"
        if flat.get("r78drainact.kind") == "nested_update":
            # seed 4: a nested update issued FROM the drain EC. Partition:
            # body-drain -> the re-entrant drain loop re-clears the vector the
            # outer loop is iterating -> SIGSEGV (the rc=-11 gate below);
            # fixture-drain -> the re-entrant Fixture::destroy re-runs
            # b2Body::DestroyFixture, whose b2Assert(found) fires -> a
            # CATCHABLE refusal (rc=0, run continues).
            if (flat.get("r78nest1.ok") == "false"
                    and "Box2D assertion failed: found"
                        in flat.get("r78nest1.err", "")
                    and flat.get("r78nest1.lock_after") == "false"
                    and flat.get("r78nest1.depth") == "1"
                    and flat.get("r78drainec.depth") == "0"
                    and flat.get("r78drainec.in_cb") == "false"
                    and flat.get("r78drainec.locked") == "false"):
                return "refused", "nested update from a fixture-drain EC: b2Assert(found)"
            return "anomaly", "drain-EC nested update without a refused witness"
        if ("r78wpcall.update_ok" in flat
                and "escaped Memoizer" in flat.get("r78wpcall.err", "")):
            # seed 3 (contained): destroying a CONTACTING object right after
            # the nested update cleared the lock. The destroy executes on the
            # spot and the same b2Contact::Update then falls through to its
            # trailing PreSolve dispatch on the freed contact, so love throws
            # "A fixture has escaped Memoizer!" -- srcline=nil (the string
            # carries no Lua line), locked_after=false, and NO collateral lock
            # refusal (the r75/r76 refused_abort conjuncts are all false
            # here). The run recovers and reaches step 200. Gated on the error
            # TEXT so the drain-abort cells (whose r78wpcall carries the
            # drain hook's own throw) fall through to their own branches.
            if (flat.get("r78nest1.lock_after") == "false"
                    and flat.get("r78wpcall.srcline") == "nil"
                    and flat.get("r78wpcall.locked_after") == "false"
                    and flat.get("r78destroy.ok") == "true"
                    and flat.get("r78destroy.dead") == "true"
                    and "assertion" not in flat.get("r78wpext.err", "assertion")
                    and flat.get("r78recover.locked_after") == "false"):
                return ("dispatch_escape",
                        "contacting destroy mid-nested-step: Memoizer escape (contained)")
            return "anomaly", "dispatch-escape witness incomplete"
        if flat.get("r78zcap.where") == "bc":
            # seed 5 (natural-end control): the handle captured at a plain
            # beginContact. The natural EndContact runs c->invalidate(), so
            # every accessor errors while the contact's fixtures stay alive.
            if (flat.get("r78zend.touch", "")
                        .startswith("ERR:Attempt to use destroyed contact.")
                    and flat.get("r78zend.fix_ok") == "false"
                    and flat.get("r78zend.ch_ok") == "false"
                    and flat.get("r78zend.fric_ok") == "false"
                    and flat.get("r78zend.pos_ok") == "false"
                    and flat.get("r78zend.fxa") == "false"
                    and flat.get("r78zend.fxa_body") == "g"):
                return ("contact_invalidated",
                        "handle invalidated by the natural EndContact; fixtures alive")
            return "anomaly", "natural-end zombie witness incomplete"
        if flat.get("r78zcap.where") == "drain":
            # seed 5: the handle captured INSIDE the drain EC. A clean drain
            # invalidates it (EndContact ran c->invalidate()); an ABORTED drain
            # unwound before invalidate(), so the same handle is still fully
            # usable at that step and only dies after the retry completes.
            if (flat.get("r78zpost.touch", "")
                        .startswith("ERR:Attempt to use destroyed contact.")
                    and flat.get("r78zpost.fix_ok") == "false"
                    and flat.get("r78zpost.ch_ok") == "false"
                    and flat.get("r78zpost.fric_ok") == "false"
                    and flat.get("r78zpost.pos_ok") == "false"
                    and flat.get("r78zpost.fxa") == "false"
                    and flat.get("r78zpost.fxa_body") == "g"):
                return ("contact_invalidated",
                        "handle invalidated by the drain; fixtures alive")
            if (flat.get("r78zsame.touch") == "true"
                    and flat.get("r78zsame.fix_ok") == "true"
                    and flat.get("r78zsame.ch_ok") == "true"
                    and flat.get("r78zsame.fric_ok") == "true"
                    and flat.get("r78zsame.pos_ok") == "true"
                    and flat.get("r78zsame.fxa") == "false"
                    and flat.get("r78zsame.fxb") == "false"
                    and flat.get("r78zlate.touch", "")
                        .startswith("ERR:Attempt to use destroyed contact.")
                    and flat.get("r78zlate.fix_ok") == "false"):
                return ("contact_live_after_abort",
                        "aborted drain skipped invalidate(); handle died after the retry")
            return "anomaly", "zombie-contact witness incomplete"
        if "r78obs.aborts" in flat and flat.get("r78obs.aborts") != "0":
            # seed 2: an every-entry drain-EC abort. It NEVER converges -- one
            # drain EC + one abort per subsequent step for the whole step
            # budget, with nothing destroyed (no internal counter, guard or
            # backoff). The converged members stop aborting -- the retry no
            # longer aborts, or the queued body's contact stopped touching --
            # and the destroy completes.
            try:
                steps = int(flat.get("final.steps", "-1"))
                fire = int(flat.get("fire.step", "-2"))
                aborts = int(flat.get("r78obs.aborts", "-1"))
                drain_n = int(flat.get("r78obs.drain_n", "-1"))
                bodies = int(flat.get("built.bodies", "-1"))
                count = int(flat.get("final.count", "-1"))
            except ValueError:
                return "anomaly", "livelock witness not numeric"
            rate = steps - fire + 1
            if (aborts == drain_n == rate and count == bodies
                    and flat.get("r78obs.b1dead") == "false"
                    and flat.get("r78obs.b3dead") == "false"
                    and flat.get("r78wpcall.locked_after") == "false"
                    and flat.get("r78wpext.ok") == "true"):
                return ("livelock",
                        "one drain EC + one abort per step; nothing destroyed")
            # critic C3: converge requires abort<->drain identity -- a real
            # drain act (throw/throwall/noop), the abort text this cell's
            # drain hook threw, and at least one drain. A forged drainec +
            # any aborts would satisfy the bare numerics otherwise.
            if (flat.get("r78drainact.kind") in ("throw", "throwall", "noop")
                    and flat.get("r78wpcall.err", "").startswith("R78-DRAIN-")
                    and aborts >= 1 and drain_n >= 1
                    and drain_n <= aborts + 1 and aborts < rate
                    and count == bodies - 1):
                return "drain_converge", "retry stopped aborting; destroy completed"
            return "anomaly", "livelock/converge witness incomplete"
        if flat.get("r78nest1.ok") == "true":
            # seed 1: a nested world:update inside a callback CLEARS e_locked
            # (b2World::Step clears its own flag on exit and has no entry
            # assert), so the outer step continues UNLOCKED and the structural
            # write the lock refused a moment ago APPLIES. The inner Step
            # re-locks -- its callback bracket (locked=true + a refused inner
            # write) is the contrast witness.
            if (flat.get("r78nest1.lock_after") == "false"
                    and flat.get("r78inner.locked") == "true"
                    and flat.get("r78inner.depth") == "1"
                    and flat.get("r78inner_write.ok") == "false"
                    and "IsLocked() == false" in flat.get("r78inner_write.err", "")
                    and flat.get("r78setpos.ok") == "true"
                    and flat.get("r78setpos.err") == "nil"
                    and flat.get("r78setpos.pos_after", "").startswith("1234.5,678.9")):
                return ("nested_lockclear",
                        "nested update cleared the lock; the write applied")
            return "anomaly", "nested lock-clear witness incomplete"
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
    if not done and rc == -11:
        # seed 1 (r77): world:release() INSIDE the engine's own execution.
        # The wrapper nulls the proxy and deletes the object while the engine
        # is still running inside it, so the process dies with SIGSEGV --
        # rc=-11, no assert text anywhere, stderr empty, and NO CELL_DONE is
        # reachable. A partial receipt whose last line is the callback's own
        # write IS the measurement. (`died` is rc without a signal: a
        # different class, never this one.)
        # Death-site discipline, per member: the r77 conjunct `"postfire" not
        # in flat` tested a key parse_iw never emits (every flat key is
        # `<tag>.<key>`), so it was vacuously true -- and the two release
        # members die at DIFFERENT sites (the callback channels before
        # postfire, the drain EC after it), so they are gated apart.
        if ("fire.step" in flat
                and (("rel_post.marker" in flat and "postfire.step" not in flat)
                     or ("drainrel.alive" in flat and "postfire.step" in flat))):
            return "corrupt", "SIGSEGV after an in-engine release"
        # seed 4 (r78): a nested update issued from a BODY-drain EC. The
        # re-entrant update re-runs the same drain loop over the vector the
        # outer loop is iterating and clears it mid-iteration, then re-enters
        # b2World::DestroyBody on a body whose teardown is in flight. The
        # causal bound is the drain-EC ORIGIN (a body queue drained in an
        # epilogue), not the nest count -- boundary measured the same crash
        # from a depth-1 drain EC, and critic/labrat confirmed the depth==2
        # keys are member descriptors. `depth_before` pins the origin; the
        # nest2/drainec depth==2 conjuncts pin the armed member's shape.
        # The inner update RETURNS first (its receipt is on the pipe) and the
        # process dies before any further Lua frame -- pcall does NOT contain
        # a signal, so the _wp twin dies identically (its witness set is the
        # same, which is why this gate reads the shared keys).
        if ("fire.step" in flat and "postfire.step" not in flat
                and flat.get("r78drainact.kind") == "nested_update"
                and flat.get("r78drainact.depth_before") in ("0", "1")
                and flat.get("r78drainec.own_n", "0") != "0"
                and flat.get("r78nest2.ok") == "true"
                and flat.get("r78nest2.lock_after") == "false"
                and flat.get("r78nest2.depth") == "2"
                and flat.get("r78nest2.in_cb") == "true"
                and flat.get("r78drainec.n") == "2"
                and flat.get("r78drainec.depth") == "2"
                and flat.get("r78drainec.in_cb") == "true"):
            return ("corrupt",
                    "SIGSEGV after a nested update from a body-drain EC")
        return "anomaly", "rc=-11 without a release or nested-drain witness"
    if not done and rc not in (0, None) and "ext_rel_call.ok" in flat:
        # seed 1 control: the SAME release from OUTSIDE the engine's own
        # execution is a CATCHABLE Lua error (no signal): every later Lua
        # touch errors, and the process dies rc=1 at the first unguarded
        # world touch. Interior-only is what makes `corrupt` mean something.
        return "died", "exterior release: catchable error, no signal"
    if has_fire and not done and rc not in (0, None):
        # seed 3 (uncontained, r78): the same contacting-destroy escape with
        # no container. It is a Lua error (rc=1, no signal, stderr empty) that
        # escapes love.update -- NOT an assert-gated `fatal` (the text is
        # love's, not Box2D's) and NOT a signal (`died`). The nested-destroy
        # witness set is required in full.
        if ("escaped Memoizer" in stdout and "postfire.step" in flat
                and flat.get("r78nest1.lock_after") == "false"
                and flat.get("r78destroy.ok") == "true"
                and flat.get("r78destroy.dead") == "true"):
            return ("dispatch_escape",
                    "Memoizer escape escaped love.update (rc=1, no signal)")
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
