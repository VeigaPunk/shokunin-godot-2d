function love.load()
    print("LOVE_PROBE_MIN alive=" .. tostring(love ~= nil))
    love.event.quit(0)
end
