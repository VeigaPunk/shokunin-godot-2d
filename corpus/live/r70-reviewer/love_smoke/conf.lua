function love.conf(t)
    t.identity = "r70rev_love_smoke"
    t.window = false
    -- variant B (graphics-off) flips the next line via sed in the runner
    t.modules.graphics = true
    t.modules.audio = false
    t.modules.sound = false
    t.modules.joystick = false
    t.modules.physics = false
    t.modules.video = false
    t.modules.touch = false
end
