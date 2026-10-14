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
-- partial pass. Interior cells are spawned LAST by the battery, the
-- fatal cells last of all.
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
  end
end

-- ---- scene (frontier phys_probe shape) -----------------------------------

local function build()
  world = love.physics.newWorld(0, GRAV, true)
  g = love.physics.newBody(world, 400, 560, "static")
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
  if target_cb == ev and not fired and label == target_label then
    fired = true
    fire_step = step
    EM(string.format("fire cb=%s kind=%s step=%d locked=%s count=%d pos=%s vel=%s",
      ev, kind, step, tostring(world:isLocked()), world:getBodyCount(), pos(dyn), vel(dyn)))
    do_mutation(kind, contact, dyn)
    EM(string.format("postfire cb=%s step=%d count=%d b1pos=%s", ev, step, world:getBodyCount(), pos(b1)))
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
  end
end

-- ---- phases --------------------------------------------------------------

function love.load()
  local maj, min, rev, cod = love.getVersion()
  EM(string.format("viability love=%d.%d.%d codename=%s physics=%s jit=%s",
    maj, min, rev, tostring(cod), tostring(love.physics ~= nil),
    tostring(jit ~= nil and jit.version or "none")))
  build()
  world:setCallbacks(c_bc, c_ec, c_pre, c_post)
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
  elseif wp_aborted and not wp_recovered then
    wp_recovered = true
    EM(string.format("wpcall_next step=%d update_ok=true locked_after=%s b1pos=%s",
      step, tostring(world:isLocked()), pos(b1)))
    if dd_mode then
      -- the queued destroy drained inside THIS update (one step late)
      EM(string.format("drainlate step=%d count=%d b1pos=%s",
        step, world:getBodyCount(), pos(b1)))
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
  end
  if step >= STEPS then
    EM(string.format(
      "final steps=%d count=%d b1pos=%s b2pos=%s bc=%d ec=%d pre=%d post=%d fired=%s fire_step=%d",
      step, world:getBodyCount(), pos(b1), pos(b2),
      counts.bc, counts.ec, counts.pre, counts.post, tostring(fired), fire_step))
    EM("CELL_DONE")
    love.event.quit(0)
  end
end
