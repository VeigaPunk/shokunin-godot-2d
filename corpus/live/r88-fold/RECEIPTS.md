# r88-fold receipts index

All under `corpus/live/r88-fold/` (untracked).

| artifact | content |
|---|---|
| `scratch/` | runnable copy of `corpus/fixtures/` post-fold (run_battery.py excluded per battery convention; `r88_surfaces.gd` sha `9631961d…` == working tree) |
| `arms/<arm>.{0..3}.out/.err` | direct arm reps, battery launch shape (`godot --headless --path scratch --script res://r88_surfaces.gd -- --arm=<arm>`, timeout 8) — post-fix measurement |
| `arms/sprite_phys_x{0..3}.*` | extra sprite_phys reps (7 total) |
| `runs1/20261015T190329837761Z/verdicts.json` | full battery rep1 — **FAIL**: `audio_bus_route_invalid_control` pre-existing load flake (`advanced=false` under 3 concurrent batteries) + consequential `probe_error_clause_surface` census-consistency FAIL; all 9 touched rows PASS |
| `runs1-console.log` | rep1 console |
| `runs2/20261015T190805853864Z/verdicts.json` | full battery rep2 — **PASS 215/215** (5-payload phys_peer envelope) |
| `runs2-console.log` | rep2 console |
| `runs3/20261015T191326575298Z/verdicts.json` | full battery rep3 — **PASS 215/215** on final bytes (6-payload envelope); phys_peer landed delta=1 mode live; `r88_expected_errors_all_matched=true` |
| `runs3-console.log` | rep3 console |
| `loaded/phys_peer.{0..149}.out/.err` | 150 hogged reps (16 `yes` hogs + ~10-way launch concurrency): ev_step_delta {0:98, 1:19, 2:6, 3:8, 4:4, 5:15} — every payload byte-matches an envelope entry |
| `loaded/{mp_loopback,mp_spawner,sprite_phys,light_props,audio_pos}.{0..9}.out/.err` | 10 focused reps each under the same hog window — PASS-payload uniq=1 each; zero `Couldn't create an ENet host` anywhere; sprite_phys exactly 1 whitelisted ERROR per rep |
