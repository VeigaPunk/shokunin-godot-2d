-- strict viability: only physics+timer+event modules loaded.
function love.load()
  local ok, err = pcall(function()
    local w = love.physics.newWorld(0, 9.81 * 64)
    local b = love.physics.newBody(w, 0, 0, "dynamic")
    local s = love.physics.newCircleShape(10)
    love.physics.newFixture(b, s, 1)
    for _ = 1, 10 do w:update(1 / 60) end
    print(string.format("STRICT | stepped y=%.6f", b:getY()))
  end)
  print("STRICT | pcall=" .. tostring(ok) .. " err=" .. tostring(err))
  love.event.quit(0)
end

function love.update(dt) end
