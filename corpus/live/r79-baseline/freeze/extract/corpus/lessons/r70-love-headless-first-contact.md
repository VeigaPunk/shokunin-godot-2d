# r70 — LOVE 11.5 headless first contact

New 2D runtime. Declared claim "engine-general fabrication window" was
**falsified at the engine layer** — honest negative result:

- `t.window=false` + graphics/window/image/audio modules off runs
  headless clean (exit 0, `love.event.quit(0)` honored).
- Headless `love.update` is **uncapped** (~960Hz, dt_mean ~1.04ms) —
  the 60Hz cadence is a windowed/vsync property, not a LOVE property.
- `io.popen` write→readable latency tracks the writer (~sleep duration),
  byte-exact lines, EOF wait <0.2ms. No engine-layer fabrication window:
  the Godot midlineforge bound is a Godot-runner pipe-plumbing property.
- `os.execute` returns raw status ×256 single-value (Lua 5.1 shape),
  not the 5.2+ triple.
- Blocking reads suspend the whole update loop; `love.event.pump` is
  not needed headless.
- Fixture pattern: `corpus/fixtures/love_probe/` + sibling
  `love_battery.py` (bound-pinned, not point-pinned, on jittered keys).
