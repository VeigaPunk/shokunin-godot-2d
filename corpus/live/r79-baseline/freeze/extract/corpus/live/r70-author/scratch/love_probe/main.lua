local steps = 0
local t0 = love.timer.getTime()
function love.update(dt)
	steps = steps + 1
	if steps >= 10 then
		print("LOVE_PROBE steps=" .. steps .. " dt=" .. dt)
		love.event.quit(0)
	end
end
