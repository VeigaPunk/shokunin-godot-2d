# r102-E0-spec — export_launch CASES registration spec (C1 launch matrix)

Seat: **E0-LAUNCH-LEAD** (owner of `corpus/fixtures/export_launch.gd` only).
Engine: `godot 4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`); templates at
`~/.local/share/godot/export_templates/4.7.2.stable/` (`linux_release.x86_64`
73,519,416 B on disk). Host: load 7–9 during the session, `uptime` 17:40 load
7.13/8.55/9.21. `run_battery.py` was never executed by this seat.

All receipts are **observed bytes** from targeted runs of the exact command
shape the battery uses:

```
godot --headless --path corpus/fixtures --script res://export_launch.gd -- --arm=<arm>
```

against the live fixture project (read-only) with scratch under
`EXPORT_LAUNCH_ROOT=/var/tmp/r102-E0/fx` (rounds A/B, byte-identical PASS lines,
exit 0, stderr 0 bytes) and once with **no env override** (battery default root
selected: `~/.local/share/godot/app_userdata/MechanicOneShotTest/export_launch`;
every pinned prefix byte-identical; only the trailing `stderr_bytes` field
drifted 283→341 with the path length, as designed).

## 1. Rows to register (exact CASES tuples, r101 tuple shape)

```python
    # r102 — C1: export_launch launch matrix (see reports/round-102/r102-E0-spec.md).
    ('export_launch_embed_boot', 'export_launch.gd', ["--arm=embed"], 0,
     'PASS export_launch embed_boot boot=true frames=[1,2,3] extra=false exit=0 cwd=isolated'),
    ('export_launch_embed_self_contained', 'export_launch.gd', ["--arm=embed"], 0,
     'PASS export_launch embed_census artifacts=1 sidecar_pck=0 tail_magic=47445043'),
    ('export_launch_embed_mainpack_refusal', 'export_launch.gd', ["--arm=embed"], 0,
     'PASS export_launch embed_refusal rc=1 class=path_overrides_disabled hint=disable_path_overrides_no'),
    ('export_launch_stock_boot', 'export_launch.gd', ["--arm=stock"], 0,
     'PASS export_launch stock_boot boot=true frames=[1,2,3] extra=false exit=0 sidecar=cwd'),
    ('export_launch_stock_sidecar_census', 'export_launch.gd', ["--arm=stock"], 0,
     'PASS export_launch stock_census artifacts=2 pck_exists=true pck_magic=47445043'),
    ('export_launch_stock_mainpack_refusal', 'export_launch.gd', ["--arm=probe"], 0,
     'PASS export_launch refusal rc=1 class=path_overrides_disabled hint=disable_path_overrides_no'),
    ('export_launch_editor_mainpack_contrast', 'export_launch.gd', ["--arm=probe"], 0,
     'PASS export_launch editor_boot boot=true frames=[1,2,3] extra=false exit=0'),
    ('export_launch_stock_missing_sidecar', 'export_launch.gd', ["--arm=probe"], 0,
     'PASS export_launch hole rc=124 class=project_data_missing pck_hint=true stdout_bytes=0'),
```

* No ordering constraints between rows: each arm is self-contained (own variant
  dir, own export). No `expected_errors` entries: the fixture's own stdout and
  stderr never contain `ERROR:`/`SCRIPT ERROR:`/`Parse Error:` (nested
  diagnostics go to scratch logs; fixture stderr measured 0 bytes on every run).
* `tail_magic=47445043` / `pck_magic=47445043` are hex for `GDPC` (ASCII form is
  never emitted, so non-magic tails stay printable under mutants).
* Trailing unpinned fields (per line, after the pinned text): `binary_bytes`,
  `bin_bytes`, `pck_bytes`, `log_bytes`, `stderr_bytes` — host/engine-version
  dependent by design.
* Minimal subset if battery time is tight (4 rows ≈ 19 s): embed_boot,
  embed_self_contained, stock_sidecar_census, stock_mainpack_refusal.

## 2. What each row measures (and its measured discriminator)

| row | measured mechanism (observed) | counterfactual (measured output) |
|---|---|---|
| embed_boot | embedded binary exported to an isolated dir (no project, no pck beside it) boots `./embed.x86_64 --headless --quit-after 3`: marker seen, `frames=[1,2,3]`, `extra=false`, exit 0 | m1 (preset flips to embed_pck=false): still boots via the sidecar (row survives — the census row below is the embed/stock discriminator) |
| embed_self_contained | `--export-release` under embed_pck=true writes **one** artifact; `artifacts=1 sidecar_pck=0`; binary ends with the appended pack trailer, last 4 B = `47445043` | m1: `artifacts=2 sidecar_pck=1 tail_magic=00000000` — row FAILs |
| embed_mainpack_refusal | the embedded build is the same template build: `--main-pack` (path need not exist — refusal is at arg parse) → rc=1, verbatim class | engine rebuild with path overrides → class flips |
| stock_boot | stock binary + adjacent `stock.pck` boots with marker + `frames=[1,2,3]` exit 0 | missing sidecar → separate `hole` row |
| stock_sidecar_census | embed_pck=false writes **two** artifacts: binary + sidecar `stock.pck` (head magic `47445043` == GDPC) | m2 (preset flips to embed_pck=true): `artifacts=1 pck_exists=false pck_magic=missing pck_bytes=-1` — row FAILs (boot row still passes: embedded pack boots) |
| stock_mainpack_refusal | exported template build + `--main-pack probe.pck` → rc=1, `class=path_overrides_disabled`, `hint=disable_path_overrides_no` | m3 (refusal command runs the editor binary instead): `rc=0 class=other hint=missing` — row FAILs |
| editor_mainpack_contrast | `/usr/bin/godot --headless --main-pack <same pck>` → marker + `frames=[1,2,3]`, exit 0 — proves the pack itself is loadable and the refusal is a property of the exported build | broken pack/export → boot=false |
| stock_missing_sidecar | same binary copied to a dir without its pck → empty stdout, stderr class `Couldn't load project data at path` + `Is the .pck file missing?`, process **keeps running** (rc=124 under the fixture's `timeout 2` wrapper) | sidecar present → boots instead of the error class |

Fixture-side mutants (scripts in `reports/round-102/mutations/`, outputs in §4):
`r102-E0-m1_embed_off.sh`, `r102-E0-m2_stock_embed_on.sh`,
`r102-E0-m3_refuse_with_editor.sh` — each is a one-token sed over
`corpus/fixtures/export_launch.gd` run on a scratch project.

## 3. Environment notes the integration must know

1. **/tmp EDQUOT hazard (r101 finding, still guarded).** The 4.7.2 packer
   serializes `project.binary` through a fixed `/tmp/tmpproject.binary-<rand>`
   path ($TMPDIR not honored). Every export here runs under
   `unshare -m --map-root-user sh -c 'mount -t tmpfs … /tmp; …'` when user
   namespaces are available; `EXPORT_LAUNCH_DIAG <arm> userns_tmp_isolation=true`
   recorded on every run this session. Without unshare the arms still run and a
   broken pack shows up as a failed boot, never as a silent PASS.
2. **Scratch root policy.** `EXPORT_LAUNCH_ROOT` → `$TMPDIR/export_launch` →
   `<engine user-data dir>/export_launch` → `/tmp/export_launch`, each accepted
   only after a 4096-byte write+readback probe. Battery default (no env var)
   selected `~/.local/share/godot/app_userdata/MechanicOneShotTest/export_launch`
   and every pinned prefix reproduced byte-identically. Host paths appear only
   in `EXPORT_LAUNCH_DIAG` lines.
3. **Cost** (measured, loaded host, per arm process): `embed` 3.77–4.18 s,
   `stock` 3.74–4.32 s, `probe` 5.57–6.12 s (includes the fixed 2 s
   missing-sidecar timeout). Registering all 8 rows re-runs arms per row
   ≈ 42 s battery wall time; the 4-row subset ≈ 19 s. Every arm ≤ 6.2 s
   against the 8 s fixture bound.
4. **Host dependency:** `timeout` (GNU coreutils, `/usr/bin/timeout`) must exist
   for the `hole` arm; rc=124 is timeout(1)'s exit status, not the game's.
5. **Overlap with sibling seats (do not double-register):** E1 `export_launch_s01.gd`
   and E2 `export_launch_s02.gd` target the embedded-binary boot/frames path;
   E3 `export_launch_s03.gd` targets the stock `--main-pack` refusal + editor
   contrast. The rows above are the lead-harness canonical set; the orchestrator
   may register either family, but should avoid two rows pinning the same
   mechanism from both.

## 4. Verbatim refusal / error classes (observed, scratch /var/tmp/r102-E0)

Refusal, both exported template binaries, rc=1, 265 B stderr, stdout empty
(sha256 of the 265 bytes: `785a6ba9162e8c9dc7fce07fbf129bec30a30de29c992d938b37eaffa867ad28`;
path-free text):

```
ERROR: `--main-pack` was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.
To be able to use it, use the `disable_path_overrides=no` SCons option when compiling Godot.

   at: setup (main/main.cpp:1892)
```

Missing sidecar, rc=124 (timeout-wrapped; process idles), 283 B stderr at the
scratch root, stdout empty:

```
ERROR: Error: Couldn't load project data at path "/var/tmp/r102-E0/nopck2". Is the .pck file missing?

If you've renamed the executable, the associated .pck file should also be renamed to match the executable's name (without the extension).

   at: setup (main/main.cpp:2130)
```

## 5. Residual risk

* `artifact=1/2` counts and magic pins are engine-version conditional; sizes are
  deliberately unpinned. A future engine that emits an extra sidecar or stops
  appending the pack trailer fails the census rows — that is the intended
  tripwire, verify the engine change before re-pinning.
* The `hole` arm's rc=124 depends on `timeout(1)`; if `timeout` is absent the
  row fails loudly with `rc=127 class=other`.
* Cross-root: only magic strings and booleans are pinned (no shas, no byte
  counts inside pinned text), so root-path drift cannot flake these rows.
