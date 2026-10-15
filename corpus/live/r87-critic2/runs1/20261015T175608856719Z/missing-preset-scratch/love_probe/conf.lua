-- r70 LOVE headless conf: no window, no graphics; keep the modules the
-- update loop + io surface needs.
function love.conf(t)
  t.identity = "shokunin-love-probe"
  t.window = false
  t.modules.graphics = false
  t.modules.window = false
  t.modules.image = false
  t.modules.audio = false
end
