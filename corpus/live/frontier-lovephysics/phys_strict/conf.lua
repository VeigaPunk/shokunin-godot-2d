-- strict module-dependency check: everything off except physics,
-- timer, event (needed for quit). If physics has a hidden module
-- dependency, newWorld/step will error here.
function love.conf(t)
  t.identity = "shokunin-frontier-lovephysics-strict"
  t.window = false
  t.modules.graphics = false
  t.modules.window = false
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
  t.modules.math = false
  t.modules.system = false
  t.modules.sensor = false
  t.modules.data = false
end
