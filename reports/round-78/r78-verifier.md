# game-dev-2d round 78 — verifier (g2d): independent re-derivation of 1a03b7a

Seat `VERIFIER` (LEAF) | lane `g2d` | round 78 | host **devin**.
Runtime LOVE 11.5 (`/usr/bin/love`), Python 3.14. HEAD `1a03b7a` at seat
start. Writes: this report, `corpus/live/r78-verifier/**` (gitignored).
**No git mutation, no tracked file touched.** `lsp` disclosure: no `lsp`
device and no Lua/Python language server on this host — verification
carriers are fresh-process execution receipts, byte diffs, and git plumbing.

Author under audit: lane report `reports/round-78/r78-author.md`
(381 lines), work commit `1a03b7a` ("r78 work: nested-update damage
surface — 17 cells"); scout report `reports/round-78/r78-scout.md`, wave-18
`shokunin-train-20261101-w18` (fleet-root report `.ufo/reports/round-78/`
holds only the g3d lane's).

## Verdicts (per author claim)

| # | author claim | verdict | basis |
|---|---|---|---|
| 1 | **92/92 ×4 consecutive runs on the final revision** | **AGREE** | two full battery runs in **my own** processes: `corpus/live/r78-verifier/runs/love-20261014T21{4247513502Z,4307020467Z}/verdicts.json`, both `cases=92 pass=92 fail=0`. I also re-read the author's four claimed final runs (`love-20261014T21{0544087564Z,0613696721Z,0635061798Z,0943322605Z}`): all `92/92/0`; the disclosed intermediate revision runs (`…T21{0016171220Z,0125788543Z}`) are `92/92/0` and the provenance run `…T205937122136Z` is `91/92/1` as the author states. |
| 2 | **insertion-only** | **AGREE** | `git show --stat 1a03b7a` → `love_battery.py 565/5` (net **+560/−5**), `love_phys_probe/main.lua +479/−0`, report `+381`. Receipt level vs the r77 closeout run: 112 prior receipts compared, **101 byte-identical**, 11 differ **only** in declared-unpinned `main.lua:NNN`/`srcline=NNN` tokens, **0 semantic** diffs; 34 new receipts (17 cells × stdout+stderr). Zero unexplained diffs. |
| 3 | **7 new classes + 2 extended members reproduce in fresh processes** | **AGREE** | my 17-cell re-derivation ×2 reps (`corpus/live/r78-verifier/cells/v1.summary.json`, `stable_bytes=true` for all 17): `nested_lockclear ×3`, `inner_drain ×1`, `dispatch_escape ×4` (3× rc=0 contained, `n_destroy_contacting` rc=1 uncontained), `refused ×1`, `contact_invalidated ×2`, `contact_live_after_abort ×1`, `livelock ×1`, `drain_converge ×2`, `corrupt ×2` (both rc=−11, `done=false`). Every class matches the author's §2/§3 table. |
| 4 | **37/37 ablations fail-closed** | **AGREE** | my copy of `ablate_gates.py` run against **my own** receipts (`corpus/live/r78-verifier/ablation.json`): 51 rows (14 cells), **37 caught, 0 not caught, 0 tag absent, 0 base mismatches** — every mutated row flips to `anomaly`/row-fail, every base row still ok. |
| 5 | **pygame 80/80 + Godot-2D 88/88 unaffected** | **AGREE** | author's sibling runs corroborated: `pygame-20261014T21{0211318403Z,0706706131Z}` both `cases=80 pass=80 fail=0`; Godot `runs/20261014T210716859565Z/verdicts.json` → `summary: PASS`. The `1a03b7a` diff touches only `love_battery.py` + `love_phys_probe/main.lua`, so neither sibling runner sits on the changed surface. |
| 6 | **brief correction: fixture-drain member is `b2Assert(found)`, not `IsLocked()`** | **AGREE** | my re-derivation `n_depth2_fxdrain`: class `refused`, rc=0, detail `nested update from a fixture-drain EC: b2Assert(found)` — `b2Body::DestroyFixture`'s `b2Assert(found)` (`Box2D/Dynamics/b2Body.cpp:241`), a *different* member of the `refused` class than the r74 `IsLocked()` member. |
| 7 | **cited commits resolve and are ancestors of HEAD** | **AGREE** | `1a03b7a` = lane HEAD; `94356ce` (r76 closeout corrections: logs, boundary report, battery comment block), `aa4d567` (r76 report-last), `62201e5` (r77 work), `d48e0fd` (r77 folds), `d4aaa95` (r77 report-last) — `cat-file -t` = commit, `merge-base --is-ancestor … HEAD` exit=0 for all. |

## New claims re-derived (not in the author's table)

- **Row arithmetic** — 15 `CASES` + 4 `SPLICE_CELLS` + 73 `IW_CELLS` (56 prior + 17 r78) = 92. Re-counted in the live tracked battery. **AGREE.**
- **`n_depth2_seq` containment** — two sequential nests are contained at `depth=1`, not depth 2; the corruption is the drain-EC nest. Class `nested_lockclear`, stable bytes. **AGREE.**
- **`livelock_all` bound shape** — `aborts == drain_n == steps − fire_step + 1` (197 at 200), nothing destroyed. Class `livelock`, stable across reps. **AGREE.**
- **`94356ce` is comment-only on the battery** — diff is 6 changed lines, all inside the `iw_bc_jwatch` comment block (`−2/+4`), matching the author's disclosure. **AGREE.**

## Corroborating disclosures checked

- Author's "disclosed `91/92` provenance run" exists at `corpus/live/r78-author/runs/love-20261014T205937122136Z` → `92/91/1`. ✓
- Author's "`r78wpcall.srcline` is a probe line number, pinned nowhere" — my 11 line-token-only drift receipts are exactly those unpinned probe-line tokens. ✓
- Author's "no independent reproduction by another seat" (r78 scout's labrat had no execution tool) — this seat is that independent reproduction: two battery runs, 17-cell ×2 re-derivation, drift audit, ablation gate. ✓

## Remaining risks / not re-verified

- The two `corrupt` cells are `rc==−11`-keyed and host/loader-scoped; SIGABRT/SIGBUS on a different build would land `anomaly` (fail-loud — the claim is bounded, not disproven).
- All class verdicts and byte-stability are **this-host** measurements (LOVE 11.5, this host, these scenes); no claim about other builds/backends.
- The sibling-seat `wp_drain_throw_all` loop claim (every-entry arming on a resting contact) is §5 prose, not a pinned row — **not re-run by this seat**.
- The crashing frame of the depth-2 SIGSEGV is still **inferred, not observed** (no core/gdb here); the re-entrant `~World` destruction mechanism is source-anchored.
- Jitter receipts (`probe.stdout` dt, `splice-*` offsets, `verdicts.json` timestamps) are bounds-pinned by nature; "byte-stable" applies to the non-jitter receipts (my `stable_bytes=true` is over the parsed flat keys, not the raw byte streams of those files).
- My re-derivation ran **2 reps** per cell (author ≥3) and the ablation matrix is my copy of the author's deletion sets (independently executed, not independently designed) — "37/37 fail-closed" is a re-execution of the author's gate, not a second design.
- Both corrupt cells remain single-rep-classified only through the ×2 reps; the class is stable across them but the crashing *point* is not bisected.

## Errata (my own, disclosed)

- I ran the author's `drift_audit.py` once with `--post` pointing at my run-1 and it wrote its JSON into the **author's** scratch path (gitignored scratch, no tracked file). I restored that file by re-running the author's own comparison (`--pre` r77 closeout run, `--post` author final run `love-20261014T210635061798Z`) → 112 compared / 101 identical / 11 line-token-only / 0 semantic / 34 new, matching the author's §1. All of this seat's other receipts are under `corpus/live/r78-verifier/`.

## Evidence index

| artefact | content |
|---|---|
| `corpus/live/r78-verifier/runs/love-20261014T21{4247513502Z,4307020467Z}/verdicts.json` | my two independent 92/92 battery runs |
| `corpus/live/r78-verifier/cells/v1.<cell>.r{1,2}.{stdout,stderr}.txt` + `v1.summary.json` | 17-cell ×2 fresh-process re-derivation (34 processes), classes + stable-byte flags |
| `corpus/live/r78-verifier/ablate_gates.py` + `ablation.json` | my copy of the gate ablation + 37/37 caught run against my receipts |
| `corpus/live/r78-verifier/drift_audit.py` + `drift_audit.json` | my copy of the drift audit (my post receipts) |
| `corpus/live/r78-verifier/run_cells.py` | my copy of the cell runner |
| git plumbing | `git show --stat 1a03b7a`, `git cat-file -t`/`merge-base --is-ancestor` on 1a03b7a, 94356ce, aa4d567, 62201e5, d48e0fd, d4aaa95 |

## Blockers

None. No tracked file was edited, nothing was committed or pushed; the
landing decision remains with the operator/integrator.