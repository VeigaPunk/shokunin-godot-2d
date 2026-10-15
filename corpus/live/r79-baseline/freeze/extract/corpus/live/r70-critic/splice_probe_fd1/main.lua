-- control: popen-child descendant reaching LOVE's stdout via /proc/<love>/fd/1
function love.load()
  local stat = io.open("/proc/self/stat"):read("*a")
  local love_pid = stat:match("^(%d+)")
  local cmd = string.format(
    "sh -c 'sleep 0.08; printf \"ERROR: LOVE_FD1_INJECT\\n\" > /proc/%s/fd/1' &",
    love_pid)
  local f = io.popen(cmd, "r")
  io.write("LOVE_FD1_PROBE: expected "); io.stdout:flush()
  love.timer.sleep(0.2)
  io.write("signature\n"); io.stdout:flush()
  print("LOVE_FD1_DONE")
  love.event.quit(0)
end
function love.update(dt) end
