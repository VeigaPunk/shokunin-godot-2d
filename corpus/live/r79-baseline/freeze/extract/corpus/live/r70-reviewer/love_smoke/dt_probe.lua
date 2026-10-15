local steps, dmin, dmax, acc = 0, math.huge, 0, 0
function love.update(dt)
    steps = steps + 1; acc = acc + dt
    if steps > 5 then dmin = math.min(dmin, dt); dmax = math.max(dmax, dt) end
    if steps >= 200 then
        print(string.format("DT steps=%d min=%.6f max=%.6f mean=%.6f", steps, dmin, dmax, acc/steps))
        love.event.quit(0)
    end
end
