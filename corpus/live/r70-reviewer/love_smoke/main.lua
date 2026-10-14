-- Minimal headless smoke: fixed-dt update counter + io.popen child-write probe.
local steps = 0
local t0 = nil

function love.load()
    t0 = love.timer.getTime()
    print("SMOKE load t=" .. string.format("%.3f", t0))
end

function love.update(dt)
    steps = steps + 1
    if steps == 10 then
        local h = io.popen("echo PIPE_CHILD_SENTINEL", "r")
        local got = h and h:read("*l") or "NIL"
        if h then h:close() end
        print("SMOKE popen got=" .. tostring(got))
    end
    if steps >= 20 then
        print("SMOKE done steps=" .. steps
            .. " dt_last=" .. string.format("%.6f", dt)
            .. " elapsed=" .. string.format("%.3f", love.timer.getTime() - t0))
        love.event.quit(0)
    end
end
