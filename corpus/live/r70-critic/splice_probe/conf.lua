-- r70-critic distinguishing cell: same headless profile as the landed probe.
function love.conf(t)
  t.identity = "shokunin-love-splice-probe"
  t.window = false
  t.modules.graphics = false
  t.modules.window = false
  t.modules.image = false
  t.modules.audio = false
end
