local n = 0
function love.update(dt)
  n = n + 1
  if n == 3 then
    io.stdout:write("PROBE n=" .. n .. " dt=" .. tostring(dt) .. "\n")
    io.stdout:flush()
    love.event.quit(0)
  end
end
