-- r74 love_phys_probe: love.physics (Box2D) callback-interior write lattice.
--
-- Falsifiable partition under test (wave-14 arm): a world mutation issued
-- INSIDE a Box2D callback (beginContact/preSolve/postSolve) is gated per
-- class -- {refused | deferred | fatal} -- while the same mutation outside
-- the callback applies immediately (control). The frontier phys_probe
-- (reports/frontier/fb-lovephysics.md) measured the callback dispatch
-- lattice; this probe folds the interior-write gating into the tracked
-- battery (corpus/fixtures/love_battery.py, IW_CELLS).
--
-- One cell per PROCESS, selected by env IW_CELL. Interior cells can be
-- fatal when the mutation is not pcall-contained, so a fatal cell kills
-- only its own process. stdout is flushed per line so pre-crash receipts
-- survive on the pipe; the battery requires the CELL_DONE marker, so a
-- crash mid-cell is a measured FAIL (truncated receipt), never a silent
-- partial pass. Interior cells are spawned LAST by the battery; the
-- process-death tail orders died, then fatal, then corrupt last of all.
--
-- Cell grammar: <when>_<kind>
--   when: bc | pre | post | ext        (ext = outside any callback, control)
--   kind: setpos | setvel | newbody | destroy | setactive | contactmask
--         | setpos_unp | newbody_unp   (uncontained escapes -> fatal)
--         | destroy_unp | setvel_unp   (r75 C1 twins: uncontained, measured
--                                      deferred/applied -- fatal is derived)
--         | setpos_wp                  (r75 C3: write escapes the callback but
--                                      is contained by pcall(world.update) --
--                                      refused-write + step-abort + transient
--                                      lock + collateral exterior refusal)
--         | joint_new | joint_destroy  (r75 joints surface)
--         | setfilter                  (r75 Fixture:setFilterData inside cb)
--         | retfalse                   (r75 preSolve return value consumption)
--         | draindefer                 (r76: accepted queued destroy +
--                                      uncontained throw in one cb, wp-level
--                                      containment -- abort skips the
--                                      epilogue drain; queue drains 1 late)
--         | destroy2                   (r76: destroy in-cb + destroy again
--                                      post-update on the same body)
--         | worlddestroy               (r76: world:destroy() inside cb --
--                                      deferred via destructWorld flag)
--         | jwatch                     (r76: joint_destroy + per-cb jcount
--                                      observer bounding the drain point)
--         | retfalse1                  (r76: preSolve return false on ONE
--                                      contact of a two-contact pair)
--   baseline: no mutation (availability lattice + world:isLocked pins)
--
-- Emitted lines:  IW | cell=<CELL> | <tag> <k=v ...>   (CELL_DONE is bare)
--
-- Scene: identical to the r70/r74-scout frontier scene (static ground +
-- b1/b2/b3 dynamic) so fire step and pose pins inherit that determinism.
-- Mutations fire on b1's first contact of the selected channel only.
--
-- ---- r78 additions: the nested-update damage surface ----------------------
--
-- r77-boundary sec.6 (independently reproduced by the r78 scout, 31 cells x3
-- byte-stable reps) found that a nested `world:update` INSIDE a callback
-- clears b2World's e_locked -- b2World::Step sets m_flags |= e_locked and
-- clears it on exit with no entry assertion (b2World.cpp:908/:960), and only
-- CreateBody / the love-side destroy gates consult it. The r78 cells arm that
-- hole as tracked shapes; every one is pre-measured in
-- reports/round-78/r78-scout.md before it was written here.
--
--   nested_lockclear : the nested update returns with the lock CLEARED, so the
--                      structural write the lock refused a moment ago APPLIES
--                      (Body::destroy() -> IsLocked() is false -> the destroy
--                      executes ON THE SPOT instead of queueing:
--                      Body.cpp:527-538). The inner Step itself re-locks --
--                      the inner callback bracket (locked=true + refused inner
--                      write) is the contrast witness.
--   inner_drain      : the nested update runs its OWN epilogue drain while the
--                      outer callback is still on the stack, so a destroy
--                      queued in the OUTER callback drains at the INNER
--                      epilogue (World::update drains destructBodies then
--                      clears the vectors).
--   dispatch_escape  : destroying a CONTACTING object mid-nested-step. The
--                      destroy completes and the same b2Contact::Update falls
--                      through to its trailing PreSolve dispatch on the freed
--                      contact -> love throws "A fixture has escaped
--                      Memoizer!" (srcline=nil). A Lua error, not a signal:
--                      pcall contains it (rc=0, aborts=1, run recovers), and
--                      it is NOT the r75/r76 refused_abort shape (no assert
--                      text, locked_after=false, no collateral lock refusal).
--   depth2           : nesting AGAIN from a BODY-drain EC re-enters the drain
--                      loop over the vector the outer loop is iterating and
--                      clears it mid-iteration, then re-enters
--                      b2World::DestroyBody on a body whose teardown is in
--                      flight -> SIGSEGV (rc=-11). The depth-2 nested update
--                      RETURNS first (its line is on the pipe); the death is
--                      before any further Lua frame and pcall does NOT contain
--                      a signal (the _wp twin dies identically). The
--                      FIXTURE-drain twin is catchable instead: the re-entrant
--                      Fixture::destroy re-runs b2Body::DestroyFixture and its
--                      b2Assert(found) fires (rc=0, "Box2D assertion failed:
--                      found").
--   zombie_contact   : handles captured inside the drain EC. After a clean
--                      drain (or a natural EndContact) World::EndContact ran
--                      c->invalidate() and every accessor errors with "Attempt
--                      to use destroyed contact." while the fixtures stay
--                      alive; after an ABORTED drain the abort unwound before
--                      invalidate(), so the handle is still fully LIVE at the
--                      same step and only dies after the retry completes.
--   livelock         : an every-entry drain-EC abort NEVER converges -- one
--                      drain EC + one abort per subsequent step for the whole
--                      step budget, with the target body still alive (no
--                      internal counter, guard or backoff).
--   converge         : the same abort converges as soon as the retry stops
--                      aborting, or (transient contact) as soon as the queued
--                      body's contact stops touching.
--
-- Insertion-only: every r78 branch is gated on R78[CELL] ~= nil, so a pre-r78
-- cell (and every r77 cell) takes exactly its earlier path.

local CELL = os.getenv("IW_CELL") or "baseline"

local FIXED = 1 / 60
local GRAV = 9.81 * 64
local STEPS = 200

local function F(x) return string.format("%.17g", x) end
local function EM(s)
  io.write(string.format("IW | cell=%s | %s\n", CELL, s))
  io.stdout:flush()
end

local when, kind = CELL:match("^(%a+)_(.+)$")
local target_cb = nil
if when == "bc" or when == "pre" or when == "post" then target_cb = when end
local is_ext = (when == "ext")
local target_label = "b1"   -- mutate the body whose first contact we track
local wp_mode = (kind == "setpos_wp")     -- contain one level up (world:update pcall)
local retfalse_mode = (kind == "retfalse") -- preSolve returns false for every contact
local wp_aborted, wp_recovered = false, false
local j_pre = nil           -- pre-built joint for joint_destroy/jwatch
-- r76 additions
local dd_mode = (kind == "draindefer")    -- queued destroy + uncontained throw, wp-contained
local d2_mode = (kind == "destroy2")      -- double destroy: in-cb + post-update
local wd_mode = (kind == "worlddestroy")  -- world:destroy() inside a callback
local jw_mode = (kind == "jwatch")        -- joint_destroy + per-cb jcount drain witness
local rf1_mode = (kind == "retfalse1")    -- preSolve return false on ONE contact of a pair
local jw_prev = nil
local rf1_falses, rf1_passes = 0, 0
local f_mask = nil          -- extra b1 fixture for retfalse1

-- ---- r77 additions: release / callback-swap / drain-EC / coroutine / meter --
--
-- Six fronts, each pre-measured live by the r77 scout before arming:
--   1 release      : world:release() INSIDE a callback -> SIGSEGV (rc=-11),
--                    partial receipt, no CELL_DONE reachable; five channels.
--   2 setcallbacks : world:setCallbacks mid-dispatch -> the NEW table handles
--                    the rest of the step (later channels AND later contacts);
--                    a swapped-out table never fires again.
--   3 fxdestroy    : Fixture:destroy() in a callback -> deferred-family, but
--                    the tracked body gate is fixture-blind (count and body
--                    untouched): its own fixture-scoped witness set.
--   4 drain edges  : at the drain EC (locked=false) writes APPLY on the spot
--                    and an abort there leaves the world UNLOCKED.
--   5 coroutine    : coroutine.resume is a containment level; wrap is not.
--   6 meter        : love.physics.setMeter in-cb applies (module global).
--
-- Insertion-only: every branch below is gated on R77[CELL] ~= nil, so a
-- pre-r77 cell takes exactly the pre-r77 path (receipts unchanged modulo the
-- declared-unpinned main.lua:NNN tokens).
local R77 = {
  bc_worldrelease      = { cb = "bc",   act = "worldrelease" },
  pre_worldrelease     = { cb = "pre",  act = "worldrelease" },
  post_worldrelease    = { cb = "post", act = "worldrelease" },
  ec_worldrelease      = { cb = "ec",   act = "worldrelease" },
  drain_worldrelease   = { cb = "bc",   act = "queue_target", drain = "worldrelease" },
  bc_setcallbacks      = { cb = "bc",   act = "setcallbacks" },
  pre_setcallbacks     = { cb = "pre",  act = "setcallbacks" },
  multi_setcallbacks   = { cb = "bc",   act = "setcallbacks", scene = "multi",
                           target = "b4" },
  bc_setcallbacks_nil  = { cb = "bc",   act = "setcallbacks_nil" },
  bc_setcallbacks_back = { cb = "bc",   act = "setcallbacks_back" },
  bc_fixture_destroy   = { cb = "bc",   act = "fixture_destroy" },
  bc_fixture_destroy2  = { cb = "bc",   act = "fixture_destroy2", extra_fx = true },
  ext_fixture_destroy  = {},
  drain_setpos_b2      = { cb = "bc",   act = "queue_target", drain = "setpos_b2" },
  drain_queue_b2       = { cb = "bc",   act = "queue_target", drain = "queue_b2" },
  wp_drain_throw       = { cb = "bc",   act = "queue_target", drain = "throw",
                           wp = true },
  drain_order_joint    = { cb = "bc",   act = "queue_target", drain = "order",
                           target = "b2", joint = true },
  bc_coyield           = { cb = "bc",   act = "coyield" },
  bc_cowrap_unp        = { cb = "bc",   act = "cowrap_unp" },
  bc_cowrap_setpos     = { cb = "bc",   act = "cowrap_setpos" },
  co_update_yield      = { cb = "bc",   act = "coyield", co = true },
  wp_coyield           = { cb = "bc",   act = "coyield", wp = true },
  cowrap_update_yield  = { cb = "bc",   act = "coyield", cowrap = true },
  bc_meter             = { cb = "bc",   act = "meter" },
  pre_meter            = { cb = "pre",  act = "meter" },
  ext_worldrelease     = {},
}
local RS = R77[CELL]        -- nil for every pre-r77 cell
local r77_target = RS and RS.target or nil
local r77_cb = RS and RS.cb or nil
local r77_drain = RS and RS.drain or nil
if RS ~= nil and RS.wp then wp_mode = true end  -- reuse the tracked wp pcall
local r77_fx_a, r77_fx_b    -- fixture handles (fxdestroy cells)
local r77_drain_n = 0
local r77_counts2 = { bc = 0, ec = 0, pre = 0, post = 0 }
local r77_swap_step = -1
local r77_ec_n = 0
local r77_ecpost = false
local r77_aborted, r77_recovered = false, false
local r77_costatus = ""
local r77_labels = {}
-- forward declarations (assigned in the r77 helper block further down)
local r77_dead, r77_fxcount, r77_getcb, r77_obs, r77_drain_hook
local r77_cb2_bc, r77_cb2_ec, r77_cb2_pre, r77_cb2_post
local r77_install_container

-- ---- r78 cell registry ---------------------------------------------------
--
-- (cell, callback act, drain-EC act). `what` = the object the mid-nested-step
-- destroy targets; `target` = the body whose first ground contact arms the
-- cell (b3 rests on the ground from step 4 -> a PERSISTENT touching contact;
-- b1 is the bouncing default -> a TRANSIENT one); `wp` = contain the OUTER
-- update with pcall; `stop` = the abort budget of the throw_stop drain act.
-- (the nested_queue acts queue b3; every row arms on beginContact.)
local R78 = {
  -- 1 lock-clear / inner bracket
  n_baseline              = { act = "nested_probe" },
  n_inner_cb              = { act = "nested_inner_cb" },
  n_depth2_seq            = { act = "nested_twice" },
  -- 2 inner-epilogue drain ownership
  n_queue_inner_drain     = { act = "nested_queue" },
  -- 3 contacting-destroy dispatch escape (contained / uncontained)
  n_destroy_contacting    = { act = "nested_destroy", what = "b1" },
  n_destroy_contacting_wp = { act = "nested_destroy", what = "b1",
                              wp = true },
  n_destroy_ground_wp     = { act = "nested_destroy", what = "g",
                              wp = true },
  n_destroy_fx_wp         = { act = "nested_destroy_fx", wp = true },
  -- 4 depth-2 from the drain EC (body -> SIGSEGV / fixture -> refused)
  n_depth2_drain          = { act = "nested_queue",
                              drain = "nested_update" },
  n_depth2_drain_wp       = { act = "nested_queue",
                              drain = "nested_update", wp = true },
  n_depth2_fxdrain        = { act = "queue_fixture",
                              drain = "nested_update" },
  -- 5 contact zombie handles
  z_drain_use_after       = { act = "queue_body", target = "b3",
                              drain = "capture" },
  z_abort_use_after       = { act = "queue_body", target = "b3",
                              drain = "capture_throw", wp = true },
  z_touch_then_end        = { act = "capture_bc" },
  -- 6 livelock / convergence
  livelock_all            = { act = "queue_body", target = "b3",
                              drain = "throwall", wp = true },
  livelock_stop2          = { act = "queue_body", target = "b3",
                              drain = "throw_stop", stop = 2, wp = true },
  livelock_transient      = { act = "queue_body",
                              drain = "throwall", wp = true },
}
local R78S = R78[CELL]        -- nil for every pre-r78 cell
local r78_cb = "bc"    -- the r78 channel: every row arms on beginContact
local r78_target = R78S and R78S.target or nil
local r78_drain = R78S and R78S.drain or nil
local r78_mut = "b3"   -- the nested_queue acts queue b3 by construction
local r78_stop = R78S and R78S.stop or 0
if R78S ~= nil and R78S.wp then wp_mode = true end
local r78_depth, r78_in_cb = 0, false
local r78_nest_n, r78_nest_ok = 0, 0
local r78_inner_fired = false
local r78_drain_n, r78_aborts = 0, 0
-- drain-EC provenance (boundary §8.1 / critic C2): `r78_pending` is the label
-- of a body the cell itself queued for destruction (queue_body/queue_fixture/
-- nested_queue) and `r78_own_n` counts drain-EC lines that actually drain it.
-- An EndContact emitted for an immediate destroy (nested_destroy*) or a
-- foreign contact is `own=false` — field-identical to a real drain otherwise.
local r78_pending = nil
local r78_own_n = 0
local r78_zh, r78_zfx_a, r78_zfx_b   -- captured contact handle + its fixtures
-- forward declarations (assigned in the r78 helper block further down)
local r78_drain_hook, r78_nested_update, r78_obs
local r78_dead, r78_fxcount, r78_lbl_of, r78_body_of, r78_fx_of_contact
local r78_zprobe, r78_zprobe_fx

local world, g, b1, b2, b3
local fired = false
local fire_step = -1
local step = 0
local after_done = false
local counts = { bc = 0, ec = 0, pre = 0, post = 0 }
local evpin = {}

local function pcall_str(f, ...)
  local ok, res = pcall(f, ...)
  if ok then return true, res end
  return false, tostring(res)
end

-- render a pcall result: false is a VALUE, never "ERR" (avoid the and/or trap)
local function res_str(ok, v)
  if not ok then return "ERR:" .. tostring(v) end
  return tostring(v)
end

local function pos(b)
  local ok, x, y = pcall(b.getPosition, b)
  if not ok then return "ERR:" .. tostring(x) end
  return F(x) .. "," .. F(y)
end

local function vel(b)
  local ok, x, y = pcall(b.getLinearVelocity, b)
  if not ok then return "ERR:" .. tostring(x) end
  return F(x) .. "," .. F(y)
end

-- ---- mutation classes ----------------------------------------------------

local function do_mutation(mkind, contact, body)
  if mkind == "setpos" then
    local ok, err = pcall_str(body.setPosition, body, 1234.5, 678.9)
    EM(string.format("cb_setpos ok=%s err=%s pos_after=%s", tostring(ok), tostring(err), pos(body)))
  elseif mkind == "setpos_unp" then
    -- uncontained variant: the assertion error is NOT pcalled, so it escapes
    -- the callback (and world:update). Measured fatal class: the process
    -- dies with rc=1, error text on stdout, no CELL_DONE.
    body:setPosition(1234.5, 678.9)
    EM(string.format("cb_setpos_unp pos_after=%s", pos(body)))
  elseif mkind == "newbody_unp" then
    -- uncontained newBody: assertion error escapes the callback
    local nb = love.physics.newBody(world, 700, 100, "dynamic")
    EM(string.format("cb_newbody_unp nb_pos=%s count=%d", pos(nb), world:getBodyCount()))
  elseif mkind == "setvel" then
    local ok, err = pcall_str(body.setLinearVelocity, body, 55, -7)
    EM(string.format("cb_setvel ok=%s err=%s vel_after=%s", tostring(ok), tostring(err), vel(body)))
  elseif mkind == "newbody" then
    local c0 = world:getBodyCount()
    local ok, res = pcall_str(function() return love.physics.newBody(world, 700, 100, "dynamic") end)
    if ok then
      EM(string.format("cb_newbody ok=true count_before=%d count_after=%d nb_pos=%s",
        c0, world:getBodyCount(), pos(res)))
    else
      EM(string.format("cb_newbody ok=false err=%s count_before=%d count_after=%d",
        tostring(res), c0, world:getBodyCount()))
    end
  elseif mkind == "destroy" then
    local ok, err = pcall_str(body.destroy, body)
    EM(string.format("cb_destroy ok=%s err=%s alive_in_cb=%s count_after=%d",
      tostring(ok), tostring(err), pos(body), world:getBodyCount()))
  elseif mkind == "setactive" then
    local ok, err = pcall_str(body.setActive, body, false)
    local aok, a = pcall_str(body.isActive, body)
    EM(string.format("cb_setactive ok=%s err=%s isActive_after=%s count_after=%d",
      tostring(ok), tostring(err), res_str(aok, a), world:getBodyCount()))
  elseif mkind == "contactmask" then
    if type(contact.setEnabled) ~= "function" then
      EM("cb_contactmask api_missing=setEnabled")
    else
      local ok, err = pcall_str(contact.setEnabled, contact, false)
      local eok, e = pcall_str(contact.isEnabled, contact)
      local tok, t = pcall_str(contact.isTouching, contact)
      EM(string.format("cb_contactmask ok=%s err=%s isEnabled_after=%s isTouching=%s",
        tostring(ok), tostring(err), res_str(eok, e), res_str(tok, t)))
    end
  elseif mkind == "destroy_unp" then
    -- r75 C1 twin: uncontained destroy (no pcall). If the class were
    -- containment-dependent this would escape; measured deferred instead.
    -- mode=unp is this branch's self-declared identity (r75 critic F1):
    -- the contained twin's EM emits no mode field, so a misdirected cell
    -- fails the cb_destroy.mode pin. For non-throwing writes the
    -- containment axis itself is observational-inert -- that inertness
    -- is the measured C1 claim.
    body:destroy()
    EM(string.format("cb_destroy ok=true err=nil mode=unp alive_in_cb=%s count_after=%d",
      pos(body), world:getBodyCount()))
  elseif mkind == "setvel_unp" then
    -- r75 C1 twin: uncontained non-structural write.
    body:setLinearVelocity(55, -7)
    EM(string.format("cb_setvel ok=true err=nil mode=unp vel_after=%s", vel(body)))
  elseif mkind == "setpos_wp" then
    -- r75 C3: write UNCONTAINED at the callback level; the escape is
    -- caught one level up by the pcall around world:update (love.update).
    body:setPosition(1234.5, 678.9)
    EM(string.format("cb_setpos_wp pos_after=%s", pos(body)))  -- unreached if assert fires
  elseif mkind == "joint_new" then
    local j0 = world:getJointCount()
    local ok, res = pcall_str(function()
      return love.physics.newDistanceJoint(b2, b3, 240, -40, 650, 518.9, false)
    end)
    if ok then
      EM(string.format("cb_joint_new ok=true jtype=%s jcount_before=%d jcount_after=%d",
        tostring(res:getType()), j0, world:getJointCount()))
    else
      EM(string.format("cb_joint_new ok=false err=%s jcount_before=%d jcount_after=%d",
        tostring(res), j0, world:getJointCount()))
    end
  elseif mkind == "joint_destroy" then
    local j0 = world:getJointCount()
    if j_pre == nil then
      EM("cb_joint_destroy api_missing=pre_joint")
    else
      local ok, err = pcall_str(j_pre.destroy, j_pre)
      local dok, d = pcall_str(j_pre.isDestroyed, j_pre)
      EM(string.format("cb_joint_destroy ok=%s err=%s isDestroyed_in_cb=%s jcount_before=%d jcount_after=%d",
        tostring(ok), tostring(err), res_str(dok, d), j0, world:getJointCount()))
    end
  elseif mkind == "setfilter" then
    local fx = body:getFixtures()[1]
    if type(fx.setFilterData) ~= "function" then
      EM("cb_setfilter api_missing=setFilterData")
    else
      local ok, err = pcall_str(fx.setFilterData, fx, 2, 2, 0)
      local c, msk, grp = fx:getFilterData()
      EM(string.format("cb_setfilter ok=%s err=%s filter_after=%d,%d,%d",
        tostring(ok), tostring(err), c, msk, grp))
    end
  elseif mkind == "retfalse" then
    -- the "write" is the preSolve return value itself (c_pre returns false)
    EM("cb_retfalse returned=false")
  elseif mkind == "retfalse1" then
    -- r76: same return-false write but only on ONE contact of the
    -- b1-ground pair (f_mask's contact); the sibling contact returns nil.
    EM("cb_retfalse returned=false scope=contact mask=f_mask")
  elseif mkind == "draindefer" then
    -- r76 drain-deferral (r75 boundary): an ACCEPTED queued destroy plus
    -- an uncontained assert-gated throw in the same callback; the
    -- update-level pcall catches the throw and the abort SKIPS the
    -- epilogue drain -- the queued destroy drains one step late.
    local ok, err = pcall_str(body.destroy, body)
    EM(string.format("cb_destroy ok=%s err=%s mode=queued alive_in_cb=%s count_after=%d",
      tostring(ok), tostring(err), pos(body), world:getBodyCount()))
    body:setPosition(1234.5, 678.9)  -- uncontained: escapes to the wp pcall
    EM("cb_draindefer unreached")    -- unreached if assert fires
  elseif mkind == "destroy2" then
    -- r76: double destroy on the same body -- in-callback (queued), then
    -- a second call post-update after the drain (emitted in love.update).
    local ok, err = pcall_str(body.destroy, body)
    EM(string.format("cb_destroy ok=%s err=%s alive_in_cb=%s count_after=%d",
      tostring(ok), tostring(err), pos(body), world:getBodyCount()))
  elseif mkind == "worlddestroy" then
    -- r76: world:destroy() inside a callback. Source says deferred via
    -- destructWorld (World.cpp:578-581), drained at the very end of the
    -- update epilogue (World.cpp:299) after the object drains.
    local ok, err = pcall_str(world.destroy, world)
    local dok, d = pcall_str(world.isDestroyed, world)
    local cok, cc = pcall_str(world.getBodyCount, world)
    EM(string.format("cb_worlddestroy ok=%s err=%s isDestroyed_in_cb=%s count_after=%s",
      tostring(ok), tostring(err), res_str(dok, d), res_str(cok, cc)))
  elseif mkind == "jwatch" then
    -- r76: joint:destroy() with a per-callback jcount observer armed --
    -- the drop is first observed by the next step's first callback.
    local j0 = world:getJointCount()
    if j_pre == nil then
      EM("cb_joint_destroy api_missing=pre_joint")
    else
      local ok, err = pcall_str(j_pre.destroy, j_pre)
      local dok, d = pcall_str(j_pre.isDestroyed, j_pre)
      EM(string.format("cb_joint_destroy ok=%s err=%s isDestroyed_in_cb=%s jcount_before=%d jcount_after=%d",
        tostring(ok), tostring(err), res_str(dok, d), j0, world:getJointCount()))
    end
  elseif mkind == "worldrelease" then
    -- r77 seed 1: release() from INSIDE the engine's own execution. The
    -- wrapper nulls the proxy and deletes the object while the engine is
    -- still running inside it; the process dies with SIGSEGV once the
    -- callback returns. No CELL_DONE is reachable -- a partial receipt with
    -- the callback's last write as the witness line IS the measurement.
    EM("rel_pre kind=worldrelease")
    local ok, err = pcall_str(world.release, world)
    EM(string.format("rel_call ok=%s err=%s", tostring(ok), tostring(err)))
    EM("rel_alive marker=1")   -- plain write: no world access after the release
    EM("rel_post marker=1")    -- callback body complete; the next WORLD touch
                               -- (the caller's own count/pose report) is the
                               -- death site -- it never reaches the pipe.
  elseif mkind == "setcallbacks" or mkind == "setcallbacks_nil"
         or mkind == "setcallbacks_back" then
    -- r77 seed 2: world:setCallbacks mid-dispatch. The engine reads the
    -- reference at EACH dispatch, so the swap takes effect for every later
    -- dispatch of the step -- later channels AND later contacts. The swap
    -- call itself is the last entry the old table ever sees.
    local n_old = counts[r77_cb]
    -- capture the table the engine is CURRENTLY holding (before the swap):
    -- this is what "swap back" must restore.
    local ob, oe, op, oq = world:getCallbacks()
    local a1, a2, a3, a4 = r77_cb2_bc, r77_cb2_ec, r77_cb2_pre, r77_cb2_post
    if mkind == "setcallbacks_nil" then a1, a2, a3, a4 = nil, nil, nil, nil end
    local ok, err = pcall_str(world.setCallbacks, world, a1, a2, a3, a4)
    r77_swap_step = step
    EM(string.format("cb_setcallbacks ok=%s err=%s swapped_step=%d swapped_n=%d swapped_cb=%s getcb=%s",
      tostring(ok), tostring(err), step, n_old, tostring(r77_cb), r77_getcb()))
    if mkind == "setcallbacks_back" then
      -- last write wins: swap straight back to the captured table
      local ok2, err2 = pcall_str(world.setCallbacks, world, ob, oe, op, oq)
      EM(string.format("cb_setcallbacks2 ok=%s err=%s getcb=%s",
        tostring(ok2), tostring(err2), r77_getcb()))
    end
  elseif mkind == "fixture_destroy" or mkind == "fixture_destroy2" then
    -- r77 seed 3: Fixture:destroy() inside a callback. Deferred-family, but
    -- the tracked body gate cannot see it (count and body are untouched), so
    -- the witness set is fixture-scoped: the handle is STILL alive inside the
    -- call and the fixture list is unchanged; the goodbye is the drain EC at
    -- locked=false; the effect witness is the live sibling (two-fixture cell)
    -- or the tunneling pose (single fixture).
    local fxs = body:getFixtures()
    r77_fx_a, r77_fx_b = fxs[1], fxs[2]   -- list[1] is the LAST created
    local before = r77_fxcount(body)
    local ok, err = pcall_str(r77_fx_a.destroy, r77_fx_a)
    EM(string.format("cb_fxdestroy ok=%s err=%s isDestroyed_in_cb=%s fcount_before=%s fcount_after=%s sib_dead=%s count_after=%d",
      tostring(ok), tostring(err), r77_dead(r77_fx_a), before, r77_fxcount(body),
      r77_dead(r77_fx_b), world:getBodyCount()))
  elseif mkind == "queue_target" then
    -- r77 seed 4: an ACCEPTED queued destroy opens the drain window; the
    -- drain-time action (if any) runs in the update epilogue at locked=false.
    local ok, err = pcall_str(body.destroy, body)
    EM(string.format("cb_destroy ok=%s err=%s mode=queued alive_in_cb=%s count_after=%d",
      tostring(ok), tostring(err), pos(body), world:getBodyCount()))
  elseif mkind == "meter" then
    -- r77 seed 6: setMeter is a module-global write -- there is nothing for
    -- the lock to gate. Decisive witness is the RATIO: every reported
    -- quantity is scaled at the Lua boundary (pos doubles at meter 60) while
    -- the solver's own trajectory is untouched.
    local m0 = love.physics.getMeter()
    local ok, err = pcall_str(love.physics.setMeter, 60)
    local gx, gy = world:getGravity()
    EM(string.format("cb_meter ok=%s err=%s meter_before=%s meter_after=%s pos_now=%s grav_after=%s,%s",
      tostring(ok), tostring(err), tostring(m0),
      tostring(love.physics.getMeter()), pos(body), F(gx), F(gy)))
    local ok2, err2 = pcall_str(love.physics.setMeter, 1)
    EM(string.format("cb_meter2 ok=%s err=%s meter=%s pos_now=%s",
      tostring(ok2), tostring(err2), tostring(love.physics.getMeter()), pos(body)))
  elseif mkind == "coyield" then
    -- r77 seed 5: a yield across the C-call boundary (the engine is inside a
    -- C frame) is an ERROR, never a suspension. (`co_update_yield` and
    -- `cowrap_update_yield` parse to kind=update_yield: the container is the
    -- only difference between the three yield cells.)
    EM("cb_coyield before")
    coroutine.yield("r77")
    EM("cb_coyield after_unreached")
  elseif mkind == "cowrap_unp" then
    -- coroutine.wrap is NOT a containment level: the error is re-raised in
    -- the caller (esc_fn = co) and the assert still escapes the callback.
    local co = coroutine.wrap(function()
      body:setPosition(1234.5, 678.9)
      EM("cb_cowrap_unp inner_after_unreached")
    end)
    EM("cb_cowrap_unp outer_before")
    co()
    EM("cb_cowrap_unp outer_after_unreached")
  elseif mkind == "cowrap_setpos" then
    -- the container is wherever the pcall sits: with the pcall INSIDE the
    -- wrap body the write is a plain refused write (rc=0, step completes).
    local co = coroutine.wrap(function()
      local ok, err = pcall_str(body.setPosition, body, 1234.5, 678.9)
      EM(string.format("cb_setpos ok=%s err=%s scope=cowrap_inner",
        tostring(ok), tostring(err)))
      return "inner-done"
    end)
    local ok, res = pcall(co)
    EM(string.format("cb_cowrap ok=%s res=%s pos_after=%s",
      tostring(ok), tostring(res), pos(body)))
  -- ---- r78 acts: the nested-update damage surface ------------------------
  elseif mkind == "nested_probe" then
    -- lockclear: nest an update, then issue the structural write the lock
    -- refused a moment ago. Witness: lock_after=false + the write APPLIES.
    EM(string.format("r78npre lock=%s count=%d", tostring(world:isLocked()),
      world:getBodyCount()))
    r78_nested_update()
    local ok, err = pcall_str(b1.setPosition, b1, 1234.5, 678.9)
    EM(string.format("r78setpos ok=%s err=%s pos_after=%s",
      tostring(ok), tostring(err), pos(b1)))
  elseif mkind == "nested_inner_cb" then
    -- the same nest, with a velocity write first: the inner Step re-locks
    -- (its own callback bracket is the contrast witness, emitted in on_event)
    -- and the post-nest write still applies.
    local vok, verr = pcall_str(b1.setLinearVelocity, b1, 0, -900)
    EM(string.format("r78npre lock=%s count=%d setvel_ok=%s setvel_err=%s",
      tostring(world:isLocked()), world:getBodyCount(), tostring(vok),
      tostring(verr)))
    r78_nested_update()
    local ok, err = pcall_str(b1.setPosition, b1, 1234.5, 678.9)
    EM(string.format("r78setpos ok=%s err=%s pos_after=%s",
      tostring(ok), tostring(err), pos(b1)))
  elseif mkind == "nested_queue" then
    -- inner-drain ownership: queue a destroy in the OUTER callback, then nest
    -- an update. The nested update's own epilogue drains the queue (its
    -- EndContact is the drain EC at locked=false with depth/in_cb witnesses),
    -- so the target is dead before the outer callback returns.
    local mb = r78_body_of(r78_mut)
    local ok, err = pcall_str(mb.destroy, mb)
    EM(string.format("r78queue what=%s ok=%s err=%s dead_in_cb=%s count=%d",
      tostring(r78_mut), tostring(ok), tostring(err), r78_dead(mb),
      world:getBodyCount()))
    if ok and r78_dead(mb) == "false" then r78_pending = r78_mut end
    r78_nested_update()
    EM(string.format("r78destroy what=%s dead=%s count=%d drain_n=%d",
      tostring(r78_mut), r78_dead(mb), world:getBodyCount(),
      r78_drain_n))
    local sok, serr = pcall_str(b1.setPosition, b1, 1234.5, 678.9)
    EM(string.format("r78setpos ok=%s err=%s pos_after=%s",
      tostring(sok), tostring(serr), pos(b1)))
  elseif mkind == "nested_destroy" then
    -- dispatch escape: nest an update, then destroy a CONTACTING object. The
    -- destroy executes on the spot (lock cleared) and the in-flight contact
    -- Update falls through to a PreSolve dispatch on the freed contact.
    r78_nested_update()
    local target = (R78S.what == "g") and g or b1
    local ok, err = pcall_str(target.destroy, target)
    EM(string.format(
      "r78destroy what=%s ok=%s err=%s dead=%s count=%d",
      tostring(R78S.what), tostring(ok), tostring(err), r78_dead(target),
      world:getBodyCount()))
    local sok, serr = pcall_str(b2.setLinearVelocity, b2, 0, -10)
    EM(string.format("r78destroy_after_write ok=%s err=%s",
      tostring(sok), tostring(serr)))
  elseif mkind == "nested_destroy_fx" then
    -- the fixture member of the same escape: the contacting fixture is torn
    -- down on the spot (the fixture list shrinks inside the callback) and the
    -- same contact Update's trailing PreSolve dispatch escapes.
    r78_nested_update()
    local fx = r78_fx_of_contact(contact, body)
    if fx == nil then
      EM("r78destroy what=fx api_missing=contact_fixture")
    else
      local fb = r78_fxcount(body)
      local ok, err = pcall_str(fx.destroy, fx)
      EM(string.format(
        "r78destroy what=fx ok=%s err=%s dead=%s fcount_before=%s fcount_after=%s count=%d",
        tostring(ok), tostring(err), r78_dead(fx), fb, r78_fxcount(body),
        world:getBodyCount()))
    end
  elseif mkind == "nested_twice" then
    -- sequential depth 2: contained (the corrupt member is the drain-EC one)
    r78_nested_update()
    r78_nested_update()
    local ok, err = pcall_str(b1.setPosition, b1, 1234.5, 678.9)
    EM(string.format("r78setpos ok=%s err=%s pos_after=%s",
      tostring(ok), tostring(err), pos(b1)))
  elseif mkind == "queue_body" then
    -- queue the FIRING body's destroy (drained in an update epilogue) and
    -- hand the drain flavour to the drain hook.
    local ok, err = pcall_str(body.destroy, body)
    EM(string.format("r78queue what=%s ok=%s err=%s dead_in_cb=%s count=%d",
      tostring(body:getUserData() or "?"), tostring(ok), tostring(err),
      r78_dead(body), world:getBodyCount()))
    if ok and r78_dead(body) == "false" then
      r78_pending = tostring(body:getUserData() or "?")
    end
  elseif mkind == "queue_fixture" then
    -- queue the CONTACT's own fixture destroy: the drain EC then comes from
    -- the fixture drain loop (World::update's destructFixtures), and the
    -- re-entrant nested update re-runs Fixture::destroy -> b2Assert(found).
    local fx = r78_fx_of_contact(contact, body)
    if fx == nil then
      EM("r78queue what=fx api_missing=contact_fixture")
    else
      local fb = r78_fxcount(body)
      local ok, err = pcall_str(fx.destroy, fx)
      EM(string.format(
        "r78queue what=fx ok=%s err=%s dead_in_cb=%s fcount_before=%s fcount_after=%s count=%d",
        tostring(ok), tostring(err), r78_dead(fx), fb, r78_fxcount(body),
        world:getBodyCount()))
      if ok and r78_dead(fx) == "false" then
        r78_pending = tostring(body:getUserData() or "?")
      end
    end
  elseif mkind == "capture_bc" then
    -- capture the contact handle at the natural beginContact (control for the
    -- zombie lattice: no drain, no abort, the natural EndContact invalidates)
    r78_zh = contact
    local ok, a, b = pcall(contact.getFixtures, contact)
    if ok then r78_zfx_a, r78_zfx_b = a, b end
    EM(string.format("r78zcap where=bc step=%d getfixtures_ok=%s fa=%s fb=%s",
      step, tostring(ok), ok and r78_lbl_of(a) or tostring(a),
      ok and r78_lbl_of(b) or tostring(b)))
  end
end

-- ---- scene (frontier phys_probe shape) -----------------------------------

local function build()
  world = love.physics.newWorld(0, GRAV, true)
  g = love.physics.newBody(world, 400, 560, "static")
  g:setUserData("g")   -- r78: the static side's label (fixture-owner witness)
  love.physics.newFixture(g, love.physics.newRectangleShape(800, 40))
  b1 = love.physics.newBody(world, 400, 60, "dynamic")
  b1:setUserData("b1")
  local f1 = love.physics.newFixture(b1, love.physics.newCircleShape(20), 1)
  f1:setRestitution(0.8); f1:setFriction(0.3)
  b2 = love.physics.newBody(world, 240, -40, "dynamic")
  b2:setUserData("b2")
  local f2 = love.physics.newFixture(b2, love.physics.newCircleShape(14), 1)
  f2:setRestitution(0.5); f2:setFriction(0.5)
  b3 = love.physics.newBody(world, 650, 518.9, "dynamic")
  b3:setUserData("b3")
  local f3 = love.physics.newFixture(b3, love.physics.newCircleShape(20), 1)
  f3:setRestitution(0.1); f3:setFriction(0.5)
  if rf1_mode then
    -- second circle on b1 -> two simultaneous (b1, ground) contacts
    f_mask = love.physics.newFixture(b1, love.physics.newCircleShape(25, 0, 20), 1)
    f_mask:setRestitution(0.8); f_mask:setFriction(0.3)
  end
end

-- ---- callbacks -----------------------------------------------------------

local function dyn_of(fa, fb)
  local A = fa:getBody()
  local B = fb:getBody()
  if A:getType() == "static" then return B end
  return A
end

local function on_event(ev, fa, fb, contact)
  counts[ev] = counts[ev] + 1
  if dd_mode and ev == "ec" and not world:isLocked() then
    -- drain-time endContact for the deferred body: fires at locked=false
    -- inside the update epilogue (r75 boundary's drain witness)
    EM(string.format("ecunl cb=ec step=%d locked=false count=%d",
      step, world:getBodyCount()))
  end
  if not evpin[ev] then
    evpin[ev] = true
    EM(string.format("evpin cb=%s locked=%s step=%d", ev, tostring(world:isLocked()), step))
  end
  local dyn = dyn_of(fa, fb)
  local label = dyn:getUserData() or "?"
  if R78S ~= nil and r78_depth > 0 and not r78_inner_fired
     and (ev == "bc" or ev == "pre" or ev == "ec") then
    -- r78 inner-Step bracket: the callback of the NESTED Step runs with
    -- e_locked SET again (b2World::Step re-locks for its own duration), so a
    -- structural write is refused there -- the contrast to the lock-cleared
    -- window that opens when the nested Step returns.
    r78_inner_fired = true
    EM(string.format("r78inner cb=%s step=%d locked=%s depth=%d dyn=%s",
      ev, step, tostring(world:isLocked()), r78_depth, label))
    local sok, serr = pcall_str(b1.setPosition, b1, 1234.5, 678.9)
    EM(string.format("r78inner_write ok=%s err=%s",
      tostring(sok), tostring(serr)))
  end
  if RS ~= nil and ev == "ec" then
    r77_ec_n = r77_ec_n + 1
    if r77_ec_n <= 4 then
      EM(string.format("r77ec n=%d step=%d locked=%s dyn=%s",
        r77_ec_n, step, tostring(world:isLocked()), label))
    end
    -- the drain-EC abort's retry witness: the FIRST endContact after the
    -- abort, dispatched inside the next step at locked=true (the abandoned
    -- destroy completes silently one step late).
    if r77_drain == "throw" and wp_aborted and not r77_ecpost and world:isLocked() then
      r77_ecpost = true
      EM(string.format("r77ecpost step=%d locked=true dyn=%s", step, label))
    end
  end
  if target_cb == ev and not fired and label == target_label then
    fired = true
    fire_step = step
    EM(string.format("fire cb=%s kind=%s step=%d locked=%s count=%d pos=%s vel=%s",
      ev, kind, step, tostring(world:isLocked()), world:getBodyCount(), pos(dyn), vel(dyn)))
    do_mutation(kind, contact, dyn)
    EM(string.format("postfire cb=%s step=%d count=%d b1pos=%s", ev, step, world:getBodyCount(), pos(b1)))
  end
  -- r77 arming path: cells whose channel prefix is not bc/pre/post (ec-natural,
  -- multi-contact, drain, coroutine containers) or whose target is not b1.
  -- Cells with a standard prefix keep using the pre-r77 gate above (the two
  -- are disjoint: this one requires target_cb == nil). The mutation is the
  -- SPEC's act (the cell NAME carries the drain flavour), so the fire line
  -- reports act/drain like the pre-measured frontier.
  if target_cb == nil and not fired and r77_cb == ev
     and label == (r77_target or target_label)
     and (r77_cb ~= "ec" or world:isLocked()) then
    fired = true
    fire_step = step
    EM(string.format("fire cb=%s kind=%s step=%d locked=%s count=%d pos=%s vel=%s",
      ev, (RS.act or "none") .. "/" .. (RS.drain or "-"), step,
      tostring(world:isLocked()), world:getBodyCount(), pos(dyn), vel(dyn)))
    do_mutation(RS.act, contact, dyn)
    EM(string.format("postfire cb=%s step=%d count=%d b1pos=%s", ev, step, world:getBodyCount(), pos(b1)))
  end
  -- r78 arming path: cells whose act is a nested update / a queued drain /
  -- a contact-handle capture. Disjoint from the two paths above by registry
  -- (R78[CELL] and R77[CELL] share no key) -- the fire line keeps the r77
  -- shape so `fire.step` and the act/drain identity read the same way.
  if R78S ~= nil and not fired and r78_cb == ev
     and label == (r78_target or target_label) then
    fired = true
    fire_step = step
    EM(string.format("fire cb=%s kind=%s step=%d locked=%s count=%d pos=%s vel=%s",
      ev, R78S.act .. "/" .. (R78S.drain or "-"), step,
      tostring(world:isLocked()), world:getBodyCount(), pos(dyn), vel(dyn)))
    r78_in_cb = true
    do_mutation(R78S.act, contact, dyn)
    r78_in_cb = false
    EM(string.format("postfire cb=%s step=%d count=%d drain_n=%d aborts=%d",
      ev, step, world:getBodyCount(), r78_drain_n, r78_aborts))
  end
  if jw_mode and fired and step <= fire_step + 1 then
    -- r76 jwatch: per-callback joint-count observation. The measured
    -- bracket is jwlive (last-wins: last step-73 cb still seeing the
    -- queued joint, jcount=1, locked) -> jdrain (emitted after
    -- world:update returns, step=73, jcount=0): the drain sits inside
    -- the update-73 epilogue, source-anchored to the joint drain loop
    -- (World.cpp:289-294; 283-287 is the fixture loop). The window is
    -- measured; the exact drain line inside it remains inference.
    -- jwdrop@74 adds nothing beyond the same-side bound.
    local jc = world:getJointCount()
    if jc > 0 then
      EM(string.format("jwlive cb=%s step=%d locked=%s jcount=%d",
        ev, step, tostring(world:isLocked()), jc))
    elseif jw_prev ~= nil and jw_prev > 0 then
      EM(string.format("jwdrop cb=%s step=%d locked=%s jcount=%d",
        ev, step, tostring(world:isLocked()), jc))
    end
    jw_prev = jc
  end
  -- r77: drain-time (locked=false) endContact -- the epilogue-synthesized
  -- goodbye, and the only point inside an update where the world is unlocked.
  -- Deliberately LAST: a release() armed here must be followed by no further
  -- world touch in this callback, so the engine (not Lua) is the thing that
  -- dies -- exactly the pre-measured shape.
  if RS ~= nil and ev == "ec" and not world:isLocked() then
    r77_drain_hook(fa, dyn)
  end
  -- r78: the same drain-time endContact, with the contact handle (the zombie
  -- lattice needs the handle itself) and the nested-depth/in-cb witnesses.
  if R78S ~= nil and ev == "ec" and not world:isLocked() then
    r78_drain_hook(contact, dyn)
  end
end

local function c_bc(fa, fb, contact) on_event("bc", fa, fb, contact) end
local function c_ec(fa, fb, contact) on_event("ec", fa, fb, contact) end
local function c_pre(fa, fb, contact)
  on_event("pre", fa, fb, contact)
  if retfalse_mode then return false end
  if rf1_mode then
    local A, B = fa:getBody(), fb:getBody()
    if A == b1 or B == b1 then
      if fa == f_mask or fb == f_mask then
        rf1_falses = rf1_falses + 1
        return false
      end
      rf1_passes = rf1_passes + 1
    end
  end
end
local function c_post(fa, fb, contact) on_event("post", fa, fb, contact) end

-- ---- r77 helpers ---------------------------------------------------------

r77_dead = function(o)
  if o == nil then return "n/a" end
  local ok, v = pcall(o.isDestroyed, o)
  return res_str(ok, v)
end

r77_fxcount = function(b)
  local ok, t = pcall(b.getFixtures, b)
  if not ok then return "ERR:" .. tostring(t) end
  return tostring(#t)
end

-- replacement callback table (seed 2): separate counters so the old table's
-- freeze is visible; the trace is bounded to the swap step + 1 and each
-- channel carries its OWN tag (a shared tag would lose the same-step witness
-- to last-wins in the flat reader).
r77_cb2_bc = function(fa, fb)
  r77_counts2.bc = r77_counts2.bc + 1
  if r77_counts2.bc <= 4 and step <= r77_swap_step + 1 then
    EM(string.format("cb2bc cb=bc n=%d step=%d locked=%s dyn=%s",
      r77_counts2.bc, step, tostring(world:isLocked()),
      tostring(dyn_of(fa, fb):getUserData())))
  end
end
r77_cb2_ec = function() r77_counts2.ec = r77_counts2.ec + 1 end
r77_cb2_pre = function()
  r77_counts2.pre = r77_counts2.pre + 1
  if r77_counts2.pre <= 4 and step <= r77_swap_step + 1 then
    EM(string.format("cb2pre cb=pre n=%d step=%d locked=%s",
      r77_counts2.pre, step, tostring(world:isLocked())))
  end
end
r77_cb2_post = function()
  r77_counts2.post = r77_counts2.post + 1
  if r77_counts2.post <= 4 and step <= r77_swap_step + 1 then
    EM(string.format("cb2post cb=post n=%d step=%d locked=%s",
      r77_counts2.post, step, tostring(world:isLocked())))
  end
end

-- stable identity readback: tostring(f) embeds a per-process address, so the
-- four values from getCallbacks() are mapped through labels, never printed.
r77_labels[c_bc] = "c_bc"; r77_labels[c_ec] = "c_ec"
r77_labels[c_pre] = "c_pre"; r77_labels[c_post] = "c_post"
r77_labels[r77_cb2_bc] = "cb2_bc"; r77_labels[r77_cb2_ec] = "cb2_ec"
r77_labels[r77_cb2_pre] = "cb2_pre"; r77_labels[r77_cb2_post] = "cb2_post"

r77_getcb = function()
  local ok, a, b, c, d = pcall(world.getCallbacks, world)
  if not ok then return "ERR:" .. tostring(a) end
  local function nm(f)
    if f == nil then return "nil" end
    return r77_labels[f] or "other"
  end
  return table.concat({ nm(a), nm(b), nm(c), nm(d) }, ",")
end

-- one bounded state line, emitted at the fire step and at the final step
-- (last-wins). Carries every r77 witness that is not a mutation line.
r77_obs = function(tag)
  EM(string.format(
    "%s step=%d locked=%s count=%d b1pos=%s b2pos=%s b1dead=%s b2dead=%s fx_a_dead=%s fx_b_dead=%s jcount=%d bc=%d ec=%d pre=%d post=%d bc2=%d ec2=%d pre2=%d post2=%d swap_step=%d drain_n=%d",
    tag, step, tostring(world:isLocked()), world:getBodyCount(), pos(b1), pos(b2),
    r77_dead(b1), r77_dead(b2), r77_dead(r77_fx_a), r77_dead(r77_fx_b),
    world:getJointCount(), counts.bc, counts.ec, counts.pre, counts.post,
    r77_counts2.bc, r77_counts2.ec, r77_counts2.pre, r77_counts2.post,
    r77_swap_step, r77_drain_n))
end

-- drain-time hook (locked=false, inside the update epilogue). Emitted for
-- every r77 cell that sees a drain EC; the action only for the drain cells.
r77_drain_hook = function(fa, dyn)
  r77_drain_n = r77_drain_n + 1
  EM(string.format("drainec n=%d step=%d locked=%s count=%d jcount=%d dyn=%s",
    r77_drain_n, step, tostring(world:isLocked()), world:getBodyCount(),
    world:getJointCount(), tostring(dyn and dyn:getUserData() or "?")))
  local d = r77_drain
  if d == nil then return end
  if d == "worldrelease" then
    -- own tag: the flat reader's key/value split needs space-free values, and
    -- `drainact.n` must stay a bare count.
    EM(string.format("drainrel kind=worldrelease n=%d", r77_drain_n))
    local ok, err = pcall_str(world.release, world)
    EM(string.format("drainrel call_ok=%s call_ret=%s",
      tostring(ok), tostring(err)))
    EM("drainrel alive=1")
  elseif d == "setpos_b2" then
    local ok, err = pcall_str(b2.setPosition, b2, 1234.5, 678.9)
    EM(string.format("drainact n=%d kind=setpos_b2 ok=%s err=%s b2pos=%s",
      r77_drain_n, tostring(ok), tostring(err), pos(b2)))
  elseif d == "queue_b2" then
    local ok, err = pcall_str(b2.destroy, b2)
    EM(string.format("drainact n=%d kind=queue_b2 ok=%s err=%s count_after=%d b2dead=%s",
      r77_drain_n, tostring(ok), tostring(err), world:getBodyCount(), r77_dead(b2)))
  elseif d == "order" then
    -- DestroyBody ordering: attached joints (SayGoodbye) FIRST, then the
    -- contacts (this EndContact), then the fixtures, then the body.
    local fd = res_str(pcall_str(fa.isDestroyed, fa))
    local other = (dyn == b2) and b3 or b2
    EM(string.format("drainact n=%d kind=order j_dead=%s fx_dead=%s body_dead=%s other_dead=%s jcount=%d",
      r77_drain_n, r77_dead(j_pre), fd, r77_dead(dyn), r77_dead(other),
      world:getJointCount()))
  elseif d == "throw" then
    if r77_drain_n == 1 then
      EM(string.format("drainact n=%d kind=throw", r77_drain_n))
      error("R77-DRAIN-THROW")   -- uncontained: escapes the drain loop
    end
    EM(string.format("drainact n=%d kind=retry_noop", r77_drain_n))
  end
end

-- r77 seed 5: coroutine containment, installed as the OUTERMOST container.
-- The World wrapper is a userdata (its methods cannot be replaced), and
-- callbacks.lua:162 reads the global `love.update` at every frame, so the
-- container is installed by wrapping love.update: the engine call under test
-- then runs inside the coroutine and nowhere else.
r77_install_container = function()
  local orig = love.update
  if RS.co then
    love.update = function(dt)
      local co = coroutine.create(function() return orig(dt) end)
      local ok, err = coroutine.resume(co)
      r77_costatus = tostring(coroutine.status(co))
      if not ok then
        -- the error comes BACK AS A VALUE: this line exists only because
        -- resume returned instead of propagating.
        r77_aborted = true
        local stripped = tostring(err):gsub("^[^:]+:%d+: ", "")
        EM(string.format("coused step=%d ok=false err=%s costatus=%s",
          step, stripped, r77_costatus))
        EM(string.format("r77abort step=%d update_ok=false err=%s locked_after=%s",
          step, stripped, tostring(world:isLocked())))
        EM(string.format("r77abortq step=%d count=%d b1pos=%s b1dead=%s",
          step, world:getBodyCount(), pos(b1), r77_dead(b1)))
        local sok, serr = pcall_str(b1.setPosition, b1, 999, 999)
        EM(string.format("r77abortext ok=%s err=%s pos_after=%s",
          tostring(sok), tostring(serr), pos(b1)))
      elseif r77_aborted and not r77_recovered then
        r77_recovered = true
        EM(string.format("r77recover step=%d locked_after=%s count=%d b1pos=%s",
          step, tostring(world:isLocked()), world:getBodyCount(), pos(b1)))
      end
      return ok, err
    end
  else
    love.update = function(dt)
      local f = coroutine.wrap(function() return orig(dt) end)
      f()                          -- the error is re-raised HERE (esc_fn = f)
      if fire_step >= 0 and step >= fire_step then
        EM(string.format("r77cowrap_after_unreached step=%d", step))
      end
    end
  end
end

-- ---- r78 helpers ---------------------------------------------------------

r78_dead = function(o)
  if o == nil then return "n/a" end
  local ok, v = pcall(o.isDestroyed, o)
  return res_str(ok, v)
end

r78_fxcount = function(b)
  if b == nil then return "n/a" end
  local ok, t = pcall(b.getFixtures, b)
  if not ok then return "ERR:" .. tostring(t) end
  return tostring(#t)
end

r78_lbl_of = function(fx)
  if fx == nil then return "nil" end
  local ok, b = pcall(fx.getBody, fx)
  if not ok then return "ERR:" .. tostring(b) end
  local ok2, ud = pcall(b.getUserData, b)
  if not ok2 then return "ERR:" .. tostring(ud) end
  if ud == nil then return "?" end
  return tostring(ud)
end

r78_body_of = function(l)
  -- every nested_queue row queues b3; the b1/b2/g arms were never passed
  if l == "b3" then return b3 end
  return nil
end

r78_fx_of_contact = function(contact, body)
  if contact == nil then return nil end
  local ok, fa, fb = pcall(contact.getFixtures, contact)
  if not ok then return nil end
  if fa ~= nil and fa:getBody() == body then return fa end
  if fb ~= nil and fb:getBody() == body then return fb end
  return fa
end

-- Every r78 nested world:update goes through here, so depth/in_cb accounting
-- is uniform across the callback and drain-time call sites. The receipt is
-- emitted AFTER the call returns -- for the depth-2 drain cell that line is
-- the last one on the pipe (the process dies before any further Lua frame).
r78_nested_update = function()
  r78_nest_n = r78_nest_n + 1
  local tag = "r78nest" .. r78_nest_n
  r78_depth = r78_depth + 1
  local depth_now = r78_depth
  local ok, err = pcall_str(world.update, world, FIXED)
  r78_depth = r78_depth - 1
  if ok then r78_nest_ok = r78_nest_ok + 1 end
  EM(string.format("%s ok=%s err=%s lock_after=%s count=%d depth=%d in_cb=%s",
    tag, tostring(ok), tostring(err), tostring(world:isLocked()),
    world:getBodyCount(), depth_now, tostring(r78_in_cb)))
  return ok, err
end

-- contact-handle probe: every read is pcall'd (an invalidated handle errors on
-- all of them) and no per-process pointer is printed.
r78_zprobe = function(tag)
  if r78_zh == nil then
    EM(string.format("%s z=nil", tag))
    return
  end
  local ok1, v1 = pcall(r78_zh.isTouching, r78_zh)
  local ok2, a, b = pcall(r78_zh.getFixtures, r78_zh)
  local ok3, c1, c2 = pcall(r78_zh.getChildren, r78_zh)
  local ok4 = pcall(r78_zh.getFriction, r78_zh)
  local ok5 = pcall(r78_zh.getPositions, r78_zh)
  EM(string.format(
    "%s touch=%s fix_ok=%s fa=%s fb=%s ch_ok=%s ca=%s cb=%s fric_ok=%s pos_ok=%s",
    tag, res_str(ok1, v1), tostring(ok2),
    ok2 and r78_lbl_of(a) or tostring(a),
    ok2 and r78_lbl_of(b) or tostring(b),
    tostring(ok3), tostring(c1), tostring(c2),
    tostring(ok4), tostring(ok5)))
end

r78_zprobe_fx = function(tag)
  EM(string.format("%s fxa=%s fxb=%s", tag,
    r78_dead(r78_zfx_a), r78_dead(r78_zfx_b)))
  if r78_zfx_a ~= nil then
    local ok, v = pcall(r78_zfx_a.getBody, r78_zfx_a)
    EM(string.format("%s fxa_body=%s", tag,
      res_str(ok, ok and r78_lbl_of(r78_zfx_a) or v)))
  end
end

-- drain-time hook (locked=false, inside an update epilogue). Emitted for every
-- r78 cell that sees a drain EC; the action only for the drain cells.
r78_drain_hook = function(contact, dyn)
  r78_drain_n = r78_drain_n + 1
  local dyn_lbl = tostring(dyn and dyn:getUserData() or "?")
  local own = r78_pending ~= nil and dyn_lbl == r78_pending
  if own then r78_own_n = r78_own_n + 1 end
  EM(string.format(
    "r78drainec n=%d step=%d locked=%s depth=%d in_cb=%s count=%d dyn=%s own=%s own_n=%d",
    r78_drain_n, step, tostring(world:isLocked()), r78_depth,
    tostring(r78_in_cb), world:getBodyCount(), dyn_lbl, tostring(own),
    r78_own_n))
  local d = r78_drain
  if d == nil then return end
  if d == "nested_update" then
    if r78_drain_n == 1 then
      EM(string.format(
        "r78drainact n=1 kind=nested_update depth_before=%d lock=%s count=%d",
        r78_depth, tostring(world:isLocked()), world:getBodyCount()))
      r78_nested_update()
    end
  elseif d == "capture" or d == "capture_throw" then
    r78_zh = contact
    local ok, a, b = pcall(contact.getFixtures, contact)
    if ok then r78_zfx_a, r78_zfx_b = a, b end
    EM(string.format(
      "r78zcap where=drain n=%d step=%d getfixtures_ok=%s fa=%s fb=%s touch=%s",
      r78_drain_n, step, tostring(ok),
      ok and r78_lbl_of(a) or tostring(a),
      ok and r78_lbl_of(b) or tostring(b),
      res_str(pcall(contact.isTouching, contact))))
    if d == "capture_throw" and r78_drain_n == 1 then
      -- ONE abort (the pre-measured shape): the abort unwinds out of
      -- b2ContactManager::Destroy after the EndContact dispatch and before
      -- the unlink, so Contact::invalidate() never runs -- the captured
      -- handle stays live this step and dies only after the retry completes.
      EM(string.format("r78drainact n=%d kind=throw", r78_drain_n))
      error("R78-DRAIN-ABORT")
    end
  elseif d == "throwall" then
    EM(string.format("r78drainact n=%d kind=throwall", r78_drain_n))
    error("R78-DRAIN-THROWALL")
  elseif d == "throw_stop" then
    if r78_drain_n <= r78_stop then
      EM(string.format("r78drainact n=%d kind=throw", r78_drain_n))
      error("R78-DRAIN-THROW-" .. r78_drain_n)
    end
    EM(string.format("r78drainact n=%d kind=noop", r78_drain_n))
  end
end

-- one bounded state line at the fire step and at the final step (last-wins).
r78_obs = function(tag)
  EM(string.format(
    "%s step=%d locked=%s count=%d b1pos=%s b3pos=%s b1dead=%s b3dead=%s " ..
    "nest_n=%d nest_ok=%d depth=%d drain_n=%d aborts=%d in_cb=%s",
    tag, step, tostring(world:isLocked()), world:getBodyCount(), pos(b1),
    pos(b3), r78_dead(b1), r78_dead(b3), r78_nest_n, r78_nest_ok, r78_depth,
    r78_drain_n, r78_aborts, tostring(r78_in_cb)))
end

-- ---- exterior controls (outside any callback) ----------------------------

local function run_ext()
  if kind == "setpos" then
    EM("ext_before pos=" .. pos(b1))
    local ok, err = pcall_str(b1.setPosition, b1, 1234.5, 678.9)
    EM(string.format("ext_setpos ok=%s err=%s pos_after=%s", tostring(ok), tostring(err), pos(b1)))
  elseif kind == "newbody" then
    local c0 = world:getBodyCount()
    local ok, res = pcall_str(function() return love.physics.newBody(world, 700, 100, "dynamic") end)
    EM(string.format("ext_newbody ok=%s count_before=%d count_after=%d",
      tostring(ok), c0, world:getBodyCount()))
    if ok then EM("ext_newbody nb_pos=" .. pos(res)) end
  elseif kind == "destroy" then
    local c0 = world:getBodyCount()
    local ok, err = pcall_str(b1.destroy, b1)
    EM(string.format("ext_destroy ok=%s err=%s count_before=%d count_after=%d b1pos_after=%s",
      tostring(ok), tostring(err), c0, world:getBodyCount(), pos(b1)))
  elseif kind == "worldrelease" then
    -- r77 seed 1 control: the same release() from OUTSIDE the engine's own
    -- execution. The proxy is nulled and the object deleted, but every later
    -- Lua touch is a CATCHABLE error (no signal) -- the process then dies
    -- rc=1 at the first UNGUARDED touch (love.update's own world call).
    EM("ext_rel_pre")
    local ok, err = pcall_str(world.release, world)
    EM(string.format("ext_rel_call ok=%s err=%s", tostring(ok), tostring(err)))
    local wok, werr = pcall(world.getBodyCount, world)
    EM(string.format("ext_rel_world_access ok=%s err=%s", tostring(wok), tostring(werr)))
    local bok, bres = pcall(b1.getPosition, b1)
    EM(string.format("ext_rel_body_access ok=%s err=%s", tostring(bok), tostring(bres)))
  elseif kind == "fixture_destroy" then
    -- r77 seed 3 control: the same fixture destroy from outside is IMMEDIATE
    -- (handle dead and list shrunk inside the call, no goodbye) and the body
    -- loses its only collision -> it falls through the ground forever.
    local fx = b1:getFixtures()[1]
    r77_fx_a = fx
    local ok, err = pcall_str(fx.destroy, fx)
    EM(string.format("ext_fxdestroy ok=%s err=%s isDestroyed_after=%s fcount=%s count_after=%d b1pos=%s",
      tostring(ok), tostring(err), r77_dead(fx), r77_fxcount(b1),
      world:getBodyCount(), pos(b1)))
  end
end

-- ---- phases --------------------------------------------------------------

function love.load()
  local maj, min, rev, cod = love.getVersion()
  EM(string.format("viability love=%d.%d.%d codename=%s physics=%s jit=%s",
    maj, min, rev, tostring(cod), tostring(love.physics ~= nil),
    tostring(jit ~= nil and jit.version or "none")))
  build()
  if RS ~= nil then
    if RS.scene == "multi" then
      -- second pair: b4's begin is dispatched FIRST at the fire step, so the
      -- swap armed there takes effect for b1's begin in the SAME step.
      local b4 = love.physics.newBody(world, 560, 60, "dynamic")
      b4:setUserData("b4")
      local f4 = love.physics.newFixture(b4, love.physics.newCircleShape(20), 1)
      f4:setRestitution(0.8); f4:setFriction(0.3)
    end
    if RS.extra_fx then
      -- second circle on b1 -> a live sibling witness for a partial destroy
      f_mask = love.physics.newFixture(b1, love.physics.newCircleShape(25, 0, 20), 1)
      f_mask:setRestitution(0.8); f_mask:setFriction(0.3)
    end
    if RS.joint then
      j_pre = love.physics.newDistanceJoint(b2, b3, 240, -40, 650, 518.9, false)
    end
  end
  world:setCallbacks(c_bc, c_ec, c_pre, c_post)
  if RS ~= nil and (RS.co or RS.cowrap) then
    -- install the coroutine container around love.update (the engine call
    -- under test then runs inside the coroutine and nowhere else).
    r77_install_container()
  end
  EM(string.format("built bodies=%d locked=%s", world:getBodyCount(), tostring(world:isLocked())))
  if kind == "joint_destroy" or jw_mode then
    j_pre = love.physics.newDistanceJoint(b2, b3, 240, -40, 650, 518.9, false)
    EM(string.format("pre_joint jtype=%s jcount=%d", tostring(j_pre:getType()), world:getJointCount()))
  end
  if is_ext then run_ext() end
end

function love.update(dt)
  step = step + 1
  local uok, uerr = true, nil
  if wp_mode or dd_mode then
    uok, uerr = pcall(world.update, world, FIXED)
  else
    world:update(FIXED)
  end
  if not uok then
    -- r75 C3 update-level containment: the interior write aborted the step;
    -- the world stays transiently locked until the next successful update,
    -- which also refuses an unrelated LEGAL exterior write (collateral).
    wp_aborted = true
    local err = tostring(uerr)
    local stripped = err:gsub("^[^:]+:%d+: ", "")
    -- r78 insertion: an abort can repeat once per step for the WHOLE run (the
    -- every-entry drain-EC livelock aborts 197 times at 200 steps), so the r78
    -- receipt is bounded -- count every abort, emit the first two -- and it
    -- carries r78-only tags, so no r78 receipt can collide with a pre-r78 key.
    if R78S ~= nil then
      r78_aborts = r78_aborts + 1
      if r78_aborts <= 2 then
        EM(string.format("r78wpcall n=%d step=%d update_ok=false err=%s srcline=%s locked_after=%s",
          r78_aborts, step, stripped, tostring(err:match(":(%d+):")),
          tostring(world:isLocked())))
        local sok, serr = pcall_str(b1.setPosition, b1, 999, 999)
        EM(string.format("r78wpext n=%d ok=%s err=%s pos_after=%s",
          r78_aborts, tostring(sok), tostring(serr), pos(b1)))
      end
    end
    -- The pre-r78 emission block below is byte-unchanged: it is skipped for
    -- r78 cells by this guard, whose body is deliberately left at its original
    -- indentation so the tracked diff stays insertion-only (zero deleted
    -- lines) while the r78 rows get their own tags.
    if R78S == nil then
    EM(string.format("wpcall step=%d update_ok=false err=%s srcline=%s locked_after=%s",
      step, stripped, tostring(err:match(":(%d+):")), tostring(world:isLocked())))
    EM(string.format("wp_setpos ok=false err=%s pos_after=%s", stripped, pos(b1)))
    local sok, serr = pcall_str(b1.setPosition, b1, 999, 999)
    EM(string.format("wpext ok=%s err=%s pos_after=%s", tostring(sok), tostring(serr), pos(b1)))
    if dd_mode then
      -- drain skipped by the abort: queue still pending, body readable
      EM(string.format("abortq step=%d count=%d b1pos=%s",
        step, world:getBodyCount(), pos(b1)))
    end
    if r77_drain == "throw" then
      -- r77 seed 4: the abort came from INSIDE the drain EC. The world is
      -- left UNLOCKED and the queued destroy survived (body still readable).
      EM(string.format("r77abortq step=%d count=%d b1pos=%s b1dead=%s",
        step, world:getBodyCount(), pos(b1), r77_dead(b1)))
    end
    end
  elseif wp_aborted and not wp_recovered then
    wp_recovered = true
    -- r78 insertion: the first update after an r78 abort -- the drain loop
    -- completed (or the retry stopped aborting) and the world is usable again.
    if R78S ~= nil then
      EM(string.format(
        "r78recover step=%d locked_after=%s count=%d b1pos=%s b1dead=%s b3dead=%s",
        step, tostring(world:isLocked()), world:getBodyCount(), pos(b1),
        r78_dead(b1), r78_dead(b3)))
    end
    if R78S == nil then
    EM(string.format("wpcall_next step=%d update_ok=true locked_after=%s b1pos=%s",
      step, tostring(world:isLocked()), pos(b1)))
    if dd_mode then
      -- the queued destroy drained inside THIS update (one step late)
      EM(string.format("drainlate step=%d count=%d b1pos=%s",
        step, world:getBodyCount(), pos(b1)))
    end
    if r77_drain == "throw" then
      -- the abandoned drain loop completed one step late, with no goodbye
      EM(string.format("r77recover step=%d locked_after=%s count=%d b1pos=%s b1dead=%s",
        step, tostring(world:isLocked()), world:getBodyCount(), pos(b1), r77_dead(b1)))
    end
    end
  end
  if uok and fired and not after_done and step == fire_step then
    after_done = true
    if wd_mode then
      -- the dead-world drain witness is emitted BEFORE after_update:
      -- world:getBodyCount() inside after_update errors on the dead
      -- world (wrap_World.cpp:34 "Attempt to use destroyed world."),
      -- so the after_update line itself is the death site for this cell.
      local dok, d = pcall_str(world.isDestroyed, world)
      EM(string.format("wdrained step=%d isDestroyed=%s", step, res_str(dok, d)))
    end
    EM(string.format("after_update step=%d count=%d b1pos=%s b1vel=%s",
      step, world:getBodyCount(), pos(b1), vel(b1)))
    if j_pre ~= nil then
      local dok, d = pcall_str(j_pre.isDestroyed, j_pre)
      EM(string.format("jdrain step=%d jcount=%d isDestroyed=%s",
        step, world:getJointCount(), res_str(dok, d)))
    end
    if d2_mode then
      -- second destroy on the same body, post-drain (post-update)
      local ok2, err2 = pcall_str(b1.destroy, b1)
      local dok, dd = pcall_str(b1.isDestroyed, b1)
      EM(string.format("post_destroy2 ok=%s err=%s count=%d isDestroyed=%s",
        tostring(ok2), tostring(err2), world:getBodyCount(), res_str(dok, dd)))
    end
    if rf1_mode then
      EM(string.format("rf1counts falses=%d passes=%d", rf1_falses, rf1_passes))
    end
    if RS ~= nil then r77_obs("r77obs") end
    if R78S ~= nil then r78_obs("r78obs") end
  end
  -- ---- r78 post-update witnesses -----------------------------------------
  if R78S ~= nil and fired then
    if r78_drain == "capture" and step == fire_step + 1 then
      -- the handle captured INSIDE the drain EC, probed one step later: the
      -- clean drain's EndContact ran c->invalidate(), so every accessor
      -- errors while the fixtures stay alive.
      r78_zprobe("r78zpost")
      r78_zprobe_fx("r78zpost")
    end
    if r78_drain == "capture_throw" then
      if step == fire_step then
        -- the abort just unwound: EndContact never reached c->invalidate(),
        -- so the SAME handle is still fully usable this step.
        EM(string.format("r78zstate tag=same step=%d drain_n=%d aborts=%d count=%d",
          step, r78_drain_n, r78_aborts, world:getBodyCount()))
        r78_zprobe("r78zsame")
        r78_zprobe_fx("r78zsame")
      elseif step == fire_step + 2 then
        -- after the retry completed: now it is invalidated.
        EM(string.format("r78zstate tag=late step=%d drain_n=%d aborts=%d count=%d",
          step, r78_drain_n, r78_aborts, world:getBodyCount()))
        r78_zprobe("r78zlate")
        r78_zprobe_fx("r78zlate")
      end
    end
    if R78S.act == "capture_bc" and step == fire_step + 2 then
      -- the natural EndContact (no drain, no abort) invalidates too
      r78_zprobe("r78zend")
      r78_zprobe_fx("r78zend")
    end
    if step == fire_step + 1 then
      EM(string.format(
        "r78nextstep step=%d count=%d b1pos=%s b3pos=%s drain_n=%d aborts=%d",
        step, world:getBodyCount(), pos(b1), pos(b3), r78_drain_n, r78_aborts))
    end
  end
  if step >= STEPS then
    EM(string.format(
      "final steps=%d count=%d b1pos=%s b2pos=%s bc=%d ec=%d pre=%d post=%d fired=%s fire_step=%d",
      step, world:getBodyCount(), pos(b1), pos(b2),
      counts.bc, counts.ec, counts.pre, counts.post, tostring(fired), fire_step))
    if RS ~= nil then r77_obs("r77obs") end
    if R78S ~= nil then r78_obs("r78obs") end
    EM("CELL_DONE")
    love.event.quit(0)
  end
end

-- r79 boundary-exec probe 5: windowed-surface error-handler hardening.
love.errorhandler = function(msg)
  print("Error: " .. tostring(msg))
  print(debug.traceback("stack traceback:", 2))
  return function() return 1 end
end
