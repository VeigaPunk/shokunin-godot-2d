-- r74 love_phys_probe headless conf: strict profile (physics/timer/event
-- kept; everything else off). Same strict module profile the r74 scout
-- scratch measured under; the frontier phys_probe differs (r74 critic C5).
function love.conf(t)
  t.identity = "shokunin-love-phys-probe"
  t.window = false
  t.modules.graphics = false
  t.modules.window = true
  t.modules.image = false
  t.modules.audio = false
  t.modules.sound = false
  t.modules.video = false
  t.modules.font = false
  t.modules.joystick = false
  t.modules.keyboard = false
  t.modules.mouse = false
  t.modules.thread = false
  t.modules.touch = false
  t.modules.sensor = false
end
