# frontier-a — pygame 2.6.1 + SDL 2.32 headless pre-measurement

Seat: g2d-frontier-a (LEAF). Host: devin — Python 3.14.7, `pygame 2.6.1
(SDL 2.32.72)` at `/usr/bin/python3`. Host HAS a live compositor
(Hyprland, `WAYLAND_DISPLAY=wayland-1`, `DISPLAY=:0` via Xwayland) — so
"no env" is NOT headless here (see T2). Scratch + receipts:
`corpus/live/frontier-pygame/` (`pygame_probe.py`, `capture_probe.py`,
`run.stdout.txt`, `run.stderr.txt`, `capture.stdout.txt`, `env-matrix.txt`).

## Verdict

**VIABLE headless.** Exact env: `SDL_VIDEODRIVER=dummy` is the only
hard requirement; `SDL_AUDIODRIVER=dummy` recommended for determinism;
`PYGAME_HIDE_SUPPORT_PROMPT=1` recommended to keep stdout parseable.
Cadence is a pure Python-loop property (no engine runner). Child-stdout
surface is **writer-flush-bound** like LOVE — no Godot-style splice
seam — but Python stdio adds a **withholding window** (block buffering)
that pins every fixture to `print(flush=True)` or `python3 -u`.
`pygame.event.pump()` is not needed headless. One crash surface found
on the *non*-dummy path (`get_wm_info` under wayland → SIGSEGV).

## (a) Viability — exact env (env-matrix.txt)

| env | result |
|---|---|
| `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` | exit 0, `init (5,0)`, `get_driver()=dummy`, `set_mode(320,240)` ok, flags `0x1000000` |
| no env (this host) | exit 0 but binds **real wayland window** (flags `0x1010002`) — NOT headless |
| bare env, no `DISPLAY`/`WAYLAND_DISPLAY`, no `SDL_*` | `pygame.error: No available video device` — no silent dummy fallback; on a compositorless host dummy is strictly required |
| `SDL_VIDEODRIVER=bogus` | `pygame.error: bogus not available` — explicit bad env is fatal, good failure mode |
| `SDL_VIDEODRIVER=dummy` + `SDL_AUDIODRIVER=bogus` | `init` returns `(4,1)`, `mixer.get_init()=None`, no exception — audio failure degrades gracefully; audio env only matters if mixer used |

Cost floor: `import pygame` ~38ms warm; `init()+set_mode` ~230–285ms
warm (~310ms cold). `import pygame` writes a 2-line banner to **stdout**
(`pygame 2.6.1 (SDL 2.32.72, ...)` + `Hello from the pygame community…`)
unless `PYGAME_HIDE_SUPPORT_PROMPT=1` is set **before** import, plus one
avx2 `RuntimeWarning` on **stderr** every import on this build — a
battery parser tolerating preamble lines + reading stderr separately is
mandatory either way.

## (b) Main-loop cadence headless (run.stdout.txt, 4 stable reps)

pygame has no engine loop — the user's Python loop IS the loop; `Clock`
is a pacer, not a scheduler. LOVE's "uncapped ~960Hz" was engine
machinery; pygame's equivalent numbers are bare-Python-loop speed:

- `tick(60)` ×240: dt mean **16.05–16.09ms**, min 15.05, max 16.87 →
  effective **~62.1–62.5Hz, never 60**. `SDL_Delay` is ms-granular:
  the 16.67ms target undershoots to ~16ms. `tick(120)` → ~124Hz
  (8.03ms/frame). A battery must pin cadence as a bound, not 60.00.
- `tick()` uncapped ×1200: dt mean **0.000ms**, max 0.007ms, ~7–9.5
  **MHz** bare loop; `tick` ret int-ms = 0; `get_fps()=inf`. Uncapped
  means unbounded CPU spin — cheaper per-frame than LOVE's 960Hz loop
  only because there is no engine work at all.
- `tick_busy_loop(60)` ×120: mean 15.99, max 16.00 — tighter tail than
  sleeping `tick` (max 16.87), same ~62.5Hz.
- Timer floor: `pygame.time` is ms-granular (`get_ticks` int ms; `tick`
  returns int ms — sub-ms cadence invisible through it); accepts float
  fps (`tick(59.94)` ok). Measure dt with `perf_counter`, not tick ret.

## (c) Child-process stdout surface (run.stdout.txt + capture.stdout.txt)

Direction 1 — pygame process → grandchild via `subprocess.Popen`
(flushing child, `python3 -u`): `l1_wait 4.99–5.25ms` (spawn floor),
`l2_wait 120.08–120.11ms` = child's own `sleep(0.12)`, EOF wait
1.3–1.6ms, byte-exact lines, rest_len 0. **Writer-bound pipe — same
verdict as LOVE** (l2 tracks the writer, no hidden buffering), and a
stronger negative vs Godot: pygame contributes *zero* pipe plumbing, so
no midlineforge-style splice/fabrication seam exists at this layer.

Direction 2 — parent → pygame-child (`capture_probe.py`, 4 reps,
identical): `--io-child flush`: line 1 readable at ~46ms (= spawn +
`import pygame` floor), line 2 at ~246ms — writer's clock exactly.
`--io-child buf` (plain `print`, piped): **line 1 withheld until ~246ms**
— lands with line 2 at child exit.

**io verdict:** the pygame stdout surface is writer-flush-bound. The
novel finding is a **withholding window**: Python block-buffers stdout
on pipes, so an unflushed line printed at t=0 is parent-invisible until
buffer-fill (~8KB) or process exit. Mechanism is Python stdio, NOT SDL
— different physics from Godot's fabrication window (bytes fused
between head/tail flush positions vs bytes simply withheld). For a
battery this is a correctness pin: fixtures must emit ARM lines with
`flush=True` (probe does) or run under `python3 -u`, else every
timing assertion sees exit-batched output.

## (d) Event pump — does `pygame.event.pump()` matter headless?

**No.** 400 frames with zero event calls: cadence unaffected
(3.2s @ tick(120), same as with-pump loop), no error; a USEREVENT posted
pre-loop survived unpumped and was retrievable — `event.get()` pumps
implicitly. SDL emits ~9 one-time events around init/set_mode under
dummy (`ActiveEvent`×2, window events ×4, `AudioDeviceAdded`×2), then
the queue is silent while idle — no unbounded growth observed.
**No spontaneous QUIT ever arrives** headless (0.7s poll) — exit must be
self-imposed (frame count / wall clock); SDL QUIT is not a viable
battery termination signal. `display.flip()` is a ~0.001ms no-op.

## Boundary / crash note

`pygame.display.get_wm_info()` on the **wayland** path → SIGSEGV,
exit 139, 2/2 repro. Under dummy → `{}`, clean. Fixtures must never
call it, and `dummy` should be pinned even on compositor hosts —
"works" there means a real window plus a crash surface.

## Reproduce

```
cd corpus/live/frontier-pygame
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 \
    python3 -u pygame_probe.py        # 12s, exit 0, PYGAME_PROBE_DONE
python3 capture_probe.py              # ~1s, exit 0
env -u DISPLAY -u WAYLAND_DISPLAY python3 -c \
    'import pygame; pygame.init(); pygame.display.set_mode((320,240))'
    # -> pygame.error: No available video device
```

## Remaining unknowns (for wave-11)

- Withholding-window upper edge: unmeasured whether a mid-run >8KB
  unflushed write flushes early (partial visibility mid-life) — likely,
  but not measured.
- `pygame.event` queue overflow bound under sustained event injection
  headless (dummy generates none post-init — moot unless fixtures post).
- Mixer determinism under `SDL_AUDIODRIVER=dummy` (init succeeds; no
  sound-device semantics measured).
- pygame-ce vs classic pygame divergence — measured on classic 2.6.1 only.
