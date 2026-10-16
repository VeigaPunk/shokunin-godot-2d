-- r70 LOVE 11.5 headless first-contact probe.
--
-- Claim under test (round-70 declared axis-move): LOVE with t.window=false
-- runs a deterministic fixed-dt love.update loop headless, and its
-- child-process stdout surface (io.popen / os.execute) exhibits a
-- measurable write-visibility window analogous to Godot midlineforge's
-- gap-relative fabrication bound ([0, ~198ms) at gap=200) -- i.e. the
-- fabrication-window phenomenon is engine-general.
--
-- Emits exact-stdout lines:  LOVE-ARM <arm> | <key>=<val> ...
-- Run: `love .` inside corpus/fixtures/love_probe/ (runner: love_battery.py).
--
-- Arms:
--   dtcadence : dt distribution over 120 update ticks (headless cadence)
--   popen     : child writes MARK1 at t0, MARK2 at t0+120ms; per-read
--               love.timer timestamps give write->readable latency.
--               io.popen read("*l") blocks: latency is measured against
--               the timer, not the update clock (loop is suspended while
--               blocked -- itself a measured fact).
--   osx       : os.execute blocking semantics + exit status shape
--   pump      : whether love.event.pump is required headless (event
--               starvation check)
--   segcount  : love.update fired this many times before first popen read
--               returns -- the headless loop keeps ticking between io
--               calls only if reads are nonblocking; measured honestly.

local M = {}

local function emit(arm, kv)
  local parts = {}
  for k, v in pairs(kv) do parts[#parts + 1] = k .. "=" .. tostring(v) end
  table.sort(parts)
  print("LOVE-ARM " .. arm .. " | " .. table.concat(parts, " "))
end

local ticks, dt_min, dt_max, dt_sum = 0, math.huge, 0, 0
local phase = "cadence"

local function popen_arm()
  -- child: write immediately, sleep 120ms, write again, exit
  local cmd = 'sh -c \'echo CHILD-MARK-1; sleep 0.12; echo CHILD-MARK-2\''
  local t0 = love.timer.getTime()
  local f = assert(io.popen(cmd, "r"))
  local t_open = love.timer.getTime() - t0
  local r1_t0 = love.timer.getTime()
  local l1 = f:read("*l")
  local l1_ms = (love.timer.getTime() - r1_t0) * 1000
  local r2_t0 = love.timer.getTime()
  local l2 = f:read("*l")
  local l2_ms = (love.timer.getTime() - r2_t0) * 1000
  local t3 = love.timer.getTime()
  local rest = f:read("*a")
  local close_wait_ms = (love.timer.getTime() - t3) * 1000
  f:close()
  emit("popen", {
    l1 = l1, l2 = l2, rest_len = #rest,
    open_ms = string.format("%.2f", t_open * 1000),
    l1_wait_ms = string.format("%.2f", l1_ms),
    l2_wait_ms = string.format("%.2f", l2_ms),
    close_wait_ms = string.format("%.2f", close_wait_ms),
    total_ms = string.format("%.2f", (love.timer.getTime() - t0) * 1000),
    ticks_before = ticks,
  })
end

local function osx_arm()
  local t0 = love.timer.getTime()
  local a, b, c = os.execute('sh -c "exit 3"')
  local ms = (love.timer.getTime() - t0) * 1000
  -- Lua 5.3+: ok, "exit", code triple; LOVE ships luajit (5.1 api) or lua5.x
  emit("osx", {
    ret_a = tostring(a), ret_b = tostring(b), ret_c = tostring(c),
    ms = string.format("%.2f", ms),
  })
end

local function pump_arm()
  -- measured fact, not a query: the loop fired `ticks` love.update calls
  -- with zero love.event.pump calls -- headless event pumping is not
  -- required for the update cadence on this build.
  emit("pump", { updates_without_pump = ticks, pump_needed = false })
end

local function splice_arm()
  -- the midlineforge-analogous seam (r70 critic F1): os.execute children
  -- inherit LOVE's fd1, so a backgrounded descendant can splice into the
  -- captured stdout between a head write and a delayed tail write.
  -- The harness scans raw stdout for the forged ordering.
  local off = tonumber(os.getenv("OFFSET_MS") or "80")
  local gap = tonumber(os.getenv("GAP_MS") or "200")
  local cmd = string.format(
    "sh -c 'sleep %.3f; printf \"ERROR: LOVE_MIDLINE forged splice\\n\"' &",
    off / 1000)
  os.execute(cmd)
  io.write("LOVE_SPLICE_PROBE: expected ")
  io.stdout:flush()
  love.timer.sleep(gap / 1000)
  io.write("signature\n")
  io.stdout:flush()
  emit("splice", { offset_ms = tostring(off), gap_ms = tostring(gap) })
end

function love.load()
  -- love.timer.getTime works headless; arg check for cleanliness
end

function love.update(dt)
  ticks = ticks + 1
  dt_sum, dt_min, dt_max = dt_sum + dt, math.min(dt_min, dt), math.max(dt_max, dt)
  if phase == "cadence" and ticks == 120 then
    emit("dtcadence", {
      n = ticks,
      dt_mean_ms = string.format("%.3f", dt_sum / ticks * 1000),
      dt_min_ms = string.format("%.3f", dt_min * 1000),
      dt_max_ms = string.format("%.3f", dt_max * 1000),
    })
    phase = "popen"
  elseif phase == "popen" then
    phase = "osx"; popen_arm()
  elseif phase == "osx" then
    phase = "pump"; osx_arm()
  elseif phase == "pump" then
    phase = "splice"; pump_arm()
  elseif phase == "splice" then
    phase = "done"; splice_arm()
    print("LOVE_PROBE_DONE")
    love.event.quit(0)
  end
end
