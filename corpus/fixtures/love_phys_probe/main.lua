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
-- uncontained (*_unp) cells last of all.
--
-- Cell grammar: <when>_<kind>
--   when: bc | pre | post | ext        (ext = outside any callback, control)
--   kind: setpos | setvel | newbody | destroy | setactive | contactmask
--         | setpos_unp | newbody_unp   (uncontained escapes -> fatal)
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
end

local function c_bc(fa, fb, contact) on_event("bc", fa, fb, contact) end
local function c_ec(fa, fb, contact) on_event("ec", fa, fb, contact) end
local function c_pre(fa, fb, contact) on_event("pre", fa, fb, contact) end
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
  if is_ext then run_ext() end
end

function love.update(dt)
  step = step + 1
  world:update(FIXED)
  if fired and not after_done and step == fire_step then
    after_done = true
    EM(string.format("after_update step=%d count=%d b1pos=%s b1vel=%s",
      step, world:getBodyCount(), pos(b1), vel(b1)))
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
