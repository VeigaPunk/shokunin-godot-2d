-- frontier-lovephysics: wave-11 candidate "LOVE physics" pre-measurement.
-- LOVE 11.5 headless (window/graphics/image/audio off).
--
-- Arms:
--   VIABILITY : love.physics.newWorld + newBody + fixtures under headless conf
--   STEP/EVT  : contact callback lattice -- a global in_step flag is set
--               around world:step; callbacks report whether they run inside
--               the step call, and capture the contacting body's y/vy AT
--               dispatch time to compare vs y_pre/vy_pre and y_post/vy_post
--               (locates callbacks in Box2D's collide/solve/integrate order)
--   DET       : determinism -- fixed scene, 600 x world:step(1/60), dump of
--               every body's x,y,a,vx,vy,w every 30 steps as %.17g, plus an
--               in-Lua sha256 of the dump blob (byte-identity across runs)
--   PERF      : world:step wall-ms over the 600-step determinism scene
--   ACC       : fixed-dt accumulator fed with the REAL uncapped headless dt;
--               sim_time vs wall_time drift and steps-per-tick histogram
--
-- Deterministic lines (VIABILITY excluded): PHYS-STEP/PHYS-EVT/PHYS-DET/
-- PHYS-DETERM must be byte-identical across runs. PERF/ACC contain clocks.

local FIXED = 1 / 60
local GRAV  = 9.81 * 64

local function EM(tag, s) print("PHYS-" .. tag .. " | " .. s) end
local function F(x) return string.format("%.17g", x) end

local in_step  = false
local cur_step = 0
local evts     = {}
local nbc, nec, npre, npost = 0, 0, 0, 0
local dyn
local world1

local function cbstate(tag, a, b, extra)
  local body = a:getBody()
  if body:getType() == "static" then body = b:getBody() end
  local _, y = body:getPosition()
  local _, vy = body:getLinearVelocity()
  return string.format("%s in_step=%s y=%s vy=%s%s",
    tag, tostring(in_step), F(y), F(vy), extra or "")
end
local function push(tag, a, b, extra)
  local s = cbstate(tag, a, b, extra)
  evts[cur_step] = evts[cur_step] and (evts[cur_step] .. " ;; " .. s) or s
end

local function cbc(a, b, c)  nbc = nbc + 1;  push("BC",   a, b) end
local function cec(a, b, c)  nec = nec + 1;  push("EC",   a, b) end
local function cpre(a, b, c) npre = npre + 1; push("PRE",  a, b) end
local function cpost(a, b, c, ...)
  npost = npost + 1
  local n = select('#', ...)
  local types = {}
  for i = 1, n do types[i] = type(select(i, ...)) end
  push("POST", a, b, string.format(" nargs=%d types=%s",
    n, table.concat(types, ",")))
end

local function build_contact_world()
  world1 = love.physics.newWorld(0, GRAV, true)
  world1:setCallbacks(cbc, cec, cpre, cpost)
  local g = love.physics.newBody(world1, 400, 560, "static")
  love.physics.newFixture(g, love.physics.newRectangleShape(800, 40))
  dyn = love.physics.newBody(world1, 400, 60, "dynamic")
  local bf = love.physics.newFixture(dyn, love.physics.newCircleShape(20), 1)
  bf:setRestitution(0.8); bf:setFriction(0.3)
  local b2 = love.physics.newBody(world1, 240, -40, "dynamic")
  local bf2 = love.physics.newFixture(b2, love.physics.newCircleShape(14), 1)
  bf2:setRestitution(0.5); bf2:setFriction(0.5)
end

-- ---- determinism scene ------------------------------------------------
local det_dump = {}
local function build_determ_world()
  local w = love.physics.newWorld(0, GRAV, true)
  local bodies = {}
  local function add(x, y, t, shape, dens, rest, fric, lvx, lvy)
    local b = love.physics.newBody(w, x, y, t)
    local f = love.physics.newFixture(b, shape, dens or 1)
    if rest then f:setRestitution(rest) end
    if fric then f:setFriction(fric) end
    if lvx then b:setLinearVelocity(lvx, lvy or 0) end
    bodies[#bodies + 1] = b
    return b
  end
  add(400, 560, "static",  love.physics.newRectangleShape(800, 40))
  add(380, 500, "dynamic", love.physics.newRectangleShape(40, 40), 1, 0.2, 0.6)
  add(402, 420, "dynamic", love.physics.newRectangleShape(40, 40), 1, 0.1, 0.8)
  add(500, 300, "dynamic", love.physics.newCircleShape(18),        1, 0.85, 0.3, -40)
  add(350, 200, "dynamic", love.physics.newPolygonShape(-16, -12, 16, -12, 0, 16), 1, 0.4, 0.4)
  return w, bodies
end

local function run_determ()
  local w, bodies = build_determ_world()
  local t0 = love.timer.getTime()
  local smin, smax = math.huge, 0
  for i = 1, 600 do
    local s0 = love.timer.getTime()
    w:update(FIXED)
    local ms = (love.timer.getTime() - s0) * 1000
    smin, smax = math.min(smin, ms), math.max(smax, ms)
    if i % 30 == 0 then
      for j, b in ipairs(bodies) do
        local x, y = b:getPosition()
        local vx, vy = b:getLinearVelocity()
        det_dump[#det_dump + 1] = string.format(
          "PHYS-DET | s=%d i=%d x=%s y=%s a=%s vx=%s vy=%s w=%s",
          i, j, F(x), F(y), F(b:getAngle()), F(vx), F(vy), F(b:getAngularVelocity()))
      end
    end
  end
  local total = (love.timer.getTime() - t0) * 1000
  for _, l in ipairs(det_dump) do print(l) end
  EM("DETERM", "sha256=" .. love.data.hash("sha256", table.concat(det_dump, "\n")))
  EM("PERF", string.format(
    "steps=600 total_ms=%.3f step_mean_ms=%.4f step_min_ms=%.4f step_max_ms=%.4f",
    total, total / 600, smin, smax))
end

-- ---- accumulator (arm d) ----------------------------------------------
local aworld
local acc = { a = 0, wall = 0, steps = 0, n0 = 0, n1 = 0, n2p = 0, maxs = 0, tick0 = 0 }
local ACC_TICKS = 1500
local ACC_TRACE = 120

local function run_accum_tick(dt)
  acc.a = acc.a + dt
  acc.wall = acc.wall + dt
  local s = 0
  while acc.a >= FIXED do
    aworld:update(FIXED)
    acc.a = acc.a - FIXED
    s = s + 1
  end
  acc.steps = acc.steps + s
  if s == 0 then acc.n0 = acc.n0 + 1
  elseif s == 1 then acc.n1 = acc.n1 + 1
  else acc.n2p = acc.n2p + 1 end
  if s > acc.maxs then acc.maxs = s end
  local atick = acc.tick0 + 1
  acc.tick0 = atick
  if atick <= ACC_TRACE then
    EM("ACC", string.format("tick=%d dt_ms=%.3f stepped=%d rem_ms=%.3f",
      atick, dt * 1000, s, acc.a * 1000))
  end
end

local function build_accum_world()
  aworld = love.physics.newWorld(0, GRAV, true)
  local g = love.physics.newBody(aworld, 400, 560, "static")
  love.physics.newFixture(g, love.physics.newRectangleShape(800, 40))
  local b = love.physics.newBody(aworld, 400, 100, "dynamic")
  love.physics.newFixture(b, love.physics.newCircleShape(20), 1)
end

-- ---- phase machine -----------------------------------------------------
local phase = "viability"

function love.update(dt)
  if phase == "viability" then
    local maj, min, rev, cod = love.getVersion()
    EM("VIABILITY", string.format(
      "version=%d.%d.%d codename=%s jit=%s physics=%s window=%s graphics=%s data=%s",
      maj, min, rev, tostring(cod),
      tostring(jit ~= nil and (jit.status and jit.status() or true) or false),
      tostring(love.physics ~= nil), tostring(love.window ~= nil),
      tostring(love.graphics ~= nil), tostring(love.data ~= nil)))
    local ok, err = pcall(build_contact_world)
    EM("VIABILITY", "build=" .. tostring(ok) .. " err=" .. tostring(err))
    phase = "contact"
  elseif phase == "contact" then
    cur_step = cur_step + 1
    local y0 = dyn:getY()
    local _, vy0 = dyn:getLinearVelocity()
    in_step = true
    world1:update(FIXED)
    in_step = false
    local y1 = dyn:getY()
    local _, vy1 = dyn:getLinearVelocity()
    if evts[cur_step] or (cur_step >= 65 and cur_step <= 90) then
      EM("STEP", string.format("i=%d y_pre=%s vy_pre=%s y_post=%s vy_post=%s",
        cur_step, F(y0), F(vy0), F(y1), F(vy1)))
      if evts[cur_step] then EM("EVT", "i=" .. cur_step .. " " .. evts[cur_step]) end
    end
    if cur_step >= 300 then
      EM("COUNTS", string.format("steps=%d BC=%d EC=%d PRE=%d POST=%d",
        cur_step, nbc, nec, npre, npost))
      run_determ()
      build_accum_world()
      phase = "accum"
    end
  elseif phase == "accum" then
    run_accum_tick(dt)
    if acc.tick0 >= ACC_TICKS then
      local sim = acc.steps * FIXED
      EM("ACCSUM", string.format(
        "ticks=%d wall_s=%.6f sim_s=%.6f steps=%d drift_ms=%.4f rem_ms=%.4f n0=%d n1=%d n2p=%d maxs=%d",
        acc.tick0, acc.wall, sim, acc.steps,
        (acc.wall - sim) * 1000, acc.a * 1000,
        acc.n0, acc.n1, acc.n2p, acc.maxs))
      print("PHYS_PROBE_DONE")
      love.event.quit(0)
    end
  end
end
