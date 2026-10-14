-- r70-critic distinguishing cell: the midlineforge-ANALOGOUS seam.
--
-- The Godot phenomenon was never a read-latency effect: a descendant
-- process inheriting the engine child's fd1 wrote into the SAME pipe the
-- engine was mid-way through writing a signature into -> byte splice.
-- The landed r70 probe's io.popen arm cannot express that (popen child's
-- fd1 is a private capture pipe, not LOVE's stdout). The analogous LOVE
-- seam is os.execute: system() children inherit LOVE's fd1. A '&'-
-- backgrounded grandchild outlives the system() call and writes into our
-- captured stdout at OFFSET_MS inside a GAP_MS head/tail gap.
--
-- If the descendant write lands between head-flush and tail-flush, the
-- captured stream shows the forged splice -- the fabrication window
-- EXISTS on LOVE (via libc, not engine code -- which is also where the
-- Godot window lived: create_process fd-inheritance + harness capture).

local OFFSET_MS = tonumber(os.getenv("OFFSET_MS") or "80")
local GAP_MS    = tonumber(os.getenv("GAP_MS") or "200")

function love.load()
  -- descendant: backgrounded subshell inherits fd1 = LOVE's stdout
  local cmd = string.format(
    "sh -c 'sleep %.3f; printf \"ERROR: LOVE_MIDLINE forged splice\\n\"' &",
    OFFSET_MS / 1000)
  os.execute(cmd)
  io.write("LOVE_SPLICE_PROBE: expected ")   -- head, unterminated
  io.stdout:flush()                          -- guarantee head reaches pipe
  love.timer.sleep(GAP_MS / 1000)            -- the gap
  io.write("signature\n")                    -- tail
  io.stdout:flush()
  print("LOVE_SPLICE_DONE")
  love.event.quit(0)
end

function love.update(dt) end
