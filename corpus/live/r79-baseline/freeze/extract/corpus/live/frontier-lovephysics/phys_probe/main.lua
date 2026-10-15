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
local dyn                       -- b1: fast drop, restitution 0.8
local world1
local cbodies = {}              -- ordered dynamic bodies
local cpre_state, cpost_state = {}, {}  -- label -> "y vy" snapshots

local function cbstate(tag, a, b, extra)
  local body = a:getBody()
  if body:getType() == "static" then body = b:getBody() end
  local _, y = body:getPosition()
  local _, vy = body:getLinearVelocity()
  local label = body:getUserData() or "?"
  return label, string.format("%s in_step=%s y=%s vy=%s%s",
    tag, tostring(in_step), F(y), F(vy), extra or "")
end
local function push(tag, a, b, extra)
  local label, s = cbstate(tag, a, b, extra)
  evts[cur_step] = evts[cur_step] or {}
  local prev = evts[cur_step][label]
  evts[cur_step][label] = prev and (prev .. " ;; " .. s) or s
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

local function snap(body)
  local _, y = body:getPosition()
  local _, vy = body:getLinearVelocity()
  return F(y), F(vy)
end

local function build_contact_world()
  world1 = love.physics.newWorld(0, GRAV, true)
  world1:setCallbacks(cbc, cec, cpre, cpost)
  local g = love.physics.newBody(world1, 400, 560, "static")
  love.physics.newFixture(g, love.physics.newRectangleShape(800, 40))
  -- b1: fast first touch (falls ~460px -> TOI-path contact expected)
  dyn = love.physics.newBody(world1, 400, 60, "dynamic")
  dyn:setUserData("b1")
  local bf = love.physics.newFixture(dyn, love.physics.newCircleShape(20), 1)
  bf:setRestitution(0.8); bf:setFriction(0.3)
  cbodies[1] = dyn
  -- b2: second fast body, offset; interleaved events with b1
  local b2 = love.physics.newBody(world1, 240, -40, "dynamic")
  b2:setUserData("b2")
  local bf2 = love.physics.newFixture(b2, love.physics.newCircleShape(14), 1)
  bf2:setRestitution(0.5); bf2:setFriction(0.5)
  cbodies[2] = b2
  -- b3: slow first touch (starts ~1px above contact) -> narrowphase-path
  local b3 = love.physics.newBody(world1, 650, 518.9, "dynamic")
  b3:setUserData("b3")
  local bf3 = love.physics.newFixture(b3, love.physics.newCircleShape(20), 1)
  bf3:setRestitution(0.1); bf3:setFriction(0.5)
  cbodies[3] = b3
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
  local raw = love.data.hash("sha256", table.concat(det_dump, "\n"))
  EM("DETERM", "sha256=" .. love.data.encode("string", "hex", raw))
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

-- scripted-dt accumulator: same math, fed a jitter pattern with stalls to
-- show burst stepping. Script: 30x1.1ms, 50ms stall, 30x1.1ms, 33ms stall,
-- 30x8.3ms. Not engine dt -- pure accumulator-math measurement.
local acc2 = { a = 0, wall = 0, steps = 0, n0 = 0, n1 = 0, n2p = 0, maxs = 0 }
local acc2_script
local acc2_i = 0

local function build_acc2()
  local s = {}
  for _ = 1, 30 do s[#s + 1] = 0.0011 end
  s[#s + 1] = 0.050
  for _ = 1, 30 do s[#s + 1] = 0.0011 end
  s[#s + 1] = 0.033
  for _ = 1, 30 do s[#s + 1] = 0.0083 end
  acc2_script = s
end

local function run_acc2_tick()
  acc2_i = acc2_i + 1
  local dt = acc2_script[acc2_i]
  if not dt then return false end
  acc2.a = acc2.a + dt
  acc2.wall = acc2.wall + dt
  local s = 0
  while acc2.a >= FIXED do
    aworld:update(FIXED)
    acc2.a = acc2.a - FIXED
    s = s + 1
  end
  acc2.steps = acc2.steps + s
  if s == 0 then acc2.n0 = acc2.n0 + 1
  elseif s == 1 then acc2.n1 = acc2.n1 + 1
  else acc2.n2p = acc2.n2p + 1 end
  if s > acc2.maxs then acc2.maxs = s end
  if s > 1 or dt > 0.02 then
    EM("ACC2", string.format("tick=%d dt_ms=%.2f stepped=%d rem_ms=%.3f",
      acc2_i, dt * 1000, s, acc2.a * 1000))
  end
  return acc2_i < #acc2_script
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
    for _, b in ipairs(cbodies) do
      local y, vy = snap(b)
      cpre_state[b:getUserData()] = y .. " " .. vy
    end
    in_step = true
    world1:update(FIXED)
    in_step = false
    for _, b in ipairs(cbodies) do
      local y, vy = snap(b)
      cpost_state[b:getUserData()] = y .. " " .. vy
    end
    -- trajectory window around b1's expected first contact
    if cur_step >= 70 and cur_step <= 76 then
      local y, vy = cpost_state.b1:match("(%S+) (%S+)")
      EM("STEP", string.format("i=%d b1 y_pre=%s y_post=%s vy_post=%s",
        cur_step, (cpre_state.b1:match("(%S+)")), y, vy))
    end
    if evts[cur_step] then
      for _, b in ipairs(cbodies) do
        local label = b:getUserData()
        if evts[cur_step][label] then
          local ypre, vypre = cpre_state[label]:match("(%S+) (%S+)")
          local ypost, vypost = cpost_state[label]:match("(%S+) (%S+)")
          EM("EVT", string.format(
            "i=%d body=%s y_pre=%s vy_pre=%s y_post=%s vy_post=%s :: %s",
            cur_step, label, ypre, vypre, ypost, vypost,
            evts[cur_step][label]))
        end
      end
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
      build_acc2()
      phase = "acc2"
    end
  elseif phase == "acc2" then
    if not run_acc2_tick() then
      local sim = acc2.steps * FIXED
      EM("ACC2SUM", string.format(
        "ticks=%d wall_s=%.6f sim_s=%.6f steps=%d drift_ms=%.4f rem_ms=%.4f n0=%d n1=%d n2p=%d maxs=%d",
        acc2_i, acc2.wall, sim, acc2.steps,
        (acc2.wall - sim) * 1000, acc2.a * 1000,
        acc2.n0, acc2.n1, acc2.n2p, acc2.maxs))
      print("PHYS_PROBE_DONE")
      love.event.quit(0)
    end
  end
end
