function love.load()
  print("OFF | love.physics=" .. tostring(love.physics))
  if love.physics then
    local ok, err = pcall(love.physics.newWorld, 0, 1)
    print("OFF | newWorld ok=" .. tostring(ok) .. " err=" .. tostring(err))
  end
  love.event.quit(0)
end

function love.update(dt) end
