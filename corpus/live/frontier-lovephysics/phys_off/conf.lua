-- physics module explicitly disabled -> love.physics should be absent
function love.conf(t)
  t.identity = "shokunin-frontier-lovephysics-off"
  t.window = false
  t.modules.graphics = false
  t.modules.window = false
  t.modules.image = false
  t.modules.audio = false
  t.modules.physics = false
end
