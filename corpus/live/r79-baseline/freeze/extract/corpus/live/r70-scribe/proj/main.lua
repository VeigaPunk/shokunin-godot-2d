-- minimal headless smoke: fixed-dt counter, print, quit
local n = 0
function love.update(dt)
    n = n + 1
    if n == 1 or n == 60 then
        print("PROBE tick=" .. n .. " dt=" .. string.format("%.6f", dt))
    end
    if n >= 60 then
        love.event.quit(0)
    end
end
