-- frontier-lovephysics headless conf: same profile as r70 probe
-- (window/graphics/image/audio off). physics/data/timer/event left
-- at default (on).
function love.conf(t)
  t.identity = "shokunin-frontier-lovephysics"
  t.window = false
  t.modules.graphics = false
  t.modules.window = false
  t.modules.image = false
  t.modules.audio = false
end
