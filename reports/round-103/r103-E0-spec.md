# r103-E0-spec — C1 export_div ROW-TUPLE SPEC (seat KEY=E0-SPEC-LEAD)

## Plan (5 lines)
1. Read landed `corpus/fixtures/export_div_s02.gd` + `mutations/w5_export_div.patch` for row names/registration shape; read E1/E3/E4/E5 shards for the sibling row intents.
2. Run s02 targeted in `/var/tmp/r103c-E0` (arm=iso, arm=xdg, 8 s bound) and take row tuples/expected values FROM MY OWN RECEIPT BYTES.
3. Emit FINAL row tuples: s02 = measured; s01/s03/s04/s05 = PENDING-fixture with intended shape + expected values + expected_errors need.
4. Fix ordering constraints (CASES insertion point vs gates; contiguity of the family) and the expected_errors field needs per row.
5. Keep this shard <=400 lines; no shared-file edits; no run_battery.py execution.

Host: load `1.82 1.76 1.62`, uptime `1 day, 20:55` (20:55 local). Godot `4.7.2.stable.arch_linux.ed1daf0bf`.
Scratch: `/var/tmp/r103c-E0` (never /tmp — EDQUOT). No device-census tokens pinned.

Owner note: this seat owns **no fixture**. All repo writes by this seat: this shard only.
HEAD `6e3e87f7b34252b1fd1deaeb8f8adef85efac849`; `run_battery.py` sha256
`40440356f0bf04481f518adc332d1ebb7ba79213878a9f3836421a512828a5c4` (== W5 `PINNED_SHA`,
verified). `run_battery.py` was never executed by this seat. No git worktrees created
(scratch only: `/var/tmp/r103c-E0/`).

## Status log
- [x] shard opened; recon starting.
- [x] s02 measured on the pre-fix revision (`sha256 50b56438…`, 457 lines): both arms PASS round 1.
- [x] **Defect found (C1 blocker):** `arm=xdg` FAILs on the 2nd run against the same scratch root
      (`reason=run4_read_not_none:[run4]`, `store_c=[run4,run4]`) — `_wipe_dir` blind to dot-dirs.
      Reproduced 2×; mechanism isolated by a 5-line probe; fix verified end-to-end.
- [x] E2 completion seat fixed the repo fixture concurrently (mtime `20:57:06`, `sha256 c08792c1…`,
      468 lines). Current revision: 2 rounds × 2 arms = 4 × PASS, exit 0, stderr 0 B,
      stdout byte-identical per arm across rounds (full-file sha256 below).
- [x] Row tuples FINAL for s02 (pins verified as exact substrings of the current-revision receipts).
- [x] s01/s03 fixtures landed mid-run (still being written at spec time → PENDING-measurement);
      s04/s05 absent → PENDING-fixture.

---

# 1. Measured evidence (s02)

Battery command shape (`run_battery.py:1929`:
`[godot, "--headless", "--path", <fixtures>, "--script", "res://"+script, "--", *flags]`,
8 s per-row bound at `:1930`) reproduced verbatim:

```
cd <repo>
EXPORT_DIV_ROOT=/var/tmp/r103c-E0/scratch /usr/bin/godot --headless \
  --path "$PWD/corpus/fixtures" --script res://export_div_s02.gd -- --arm=iso   # then --arm=xdg
```

Round 1 (pre-fix rev `50b56438…`), 20:55 — observation, exit 0 both, stderr 0 B both:

```
PASS export_div s02 arm=iso r1_read=none r1_exit=0 r2_read=run1 r2_exit=0 store=[run1,run2] store_under_xdg=true userdir_under_xdg=true home_store_absent=true proj=<root>/div_s02/proj
PASS export_div s02 arm=xdg r3_read=none r3_exit=0 store_b=[run3] store_b_under_xdg=true r3_userdir_under_xdg=true r4_read=none r4_exit=0 store_c=[run4] r4_userdir_under_home=true xdg_a_store=[run1,run2] proj=<root>/div_s02/proj
```

Rounds 1+2 on the **current** revision (`c08792c1…`), root `/var/tmp/r103c-E0/scratchC`
(control block of `sweep2.sh`), 20:58 — observation, same two lines verbatim in both rounds,
exit 0 for all 4 processes, stderr 0 B for all 4:

- whole-stdout sha256, round1 == round2: iso `e0951d8252a8f3f6…`, xdg `900b59f62f2c6c20…`
- `grep -c 'ERROR:\|SCRIPT ERROR:\|Parse Error:'` over all 4 stdout files = **0** (the
  classifier's `unrelated_errors` / stream clauses have nothing to trip on)
- harness-side store tree after round 2 (independent of the fixture's own assertions):
  `xdgA/godot/app_userdata/ExportDivS02/div_s02_state.txt = run1,run2`;
  `xdgB/… = run3`; `homeC/.local/share/godot/app_userdata/ExportDivS02/div_s02_state.txt = run4`
  (exactly one write, i.e. round 2 read `<none>`); `homeA` contains nothing (no `.local`).
- wall time per arm (`time`, load spiked to 11.59 during measurement): iso (cold: wipe + 73 MB
  export + 2 child boots) **4.795 s**; xdg (binary reused) **2.342 s**. Post-fix control, per-arm
  durations from log mtimes: xdg1 2.563 s, iso2 **4.794 s**, xdg2 2.537 s (iso1 not bracketed).
  Slowest row ≈ 4.8 s vs the 8 s bound → ~1.67× headroom. Host load at shard close
  (`21:00:16`): `11.51 7.65 4.17` — measurement conditions were already loaded, so 4.8 s is a
  realistic worst case rather than an idle-host number.

# 2. FINAL row tuples — s02 (measured, register verbatim)

Pins are exact substrings of the current-revision receipts (hit counts 1/1, cross-arm hits 0/0),
and each pin stops **before** the host-dependent tail (`proj=`, `xdg_a_store=`), so both rows are
order- and root-robust:

```python
    # r103 — C1: export_div divergence/isolation family (see reports/round-103/r103-E0-spec.md).
    # Insert immediately after export_launch_stock_missing_sidecar and BEFORE the
    # crash/descendant tail (run_battery.py:1710/1711). iso MUST precede xdg.
    ('export_div_s02_user_iso', 'export_div_s02.gd', ["--arm=iso"], 0,
     'PASS export_div s02 arm=iso r1_read=none r1_exit=0 r2_read=run1 r2_exit=0 store=[run1,run2] store_under_xdg=true userdir_under_xdg=true home_store_absent=true'),
    ('export_div_s02_xdg_override', 'export_div_s02.gd', ["--arm=xdg"], 0,
     'PASS export_div s02 arm=xdg r3_read=none r3_exit=0 store_b=[run3] store_b_under_xdg=true r3_userdir_under_xdg=true r4_read=none r4_exit=0 store_c=[run4] r4_userdir_under_home=true'),
```

`expected_errors`: **none** for both rows (§5). Discrimination of the pin boundary: the iso pin
does not occur in the xdg receipt and vice versa; a fixture that skipped the `run2` read-back,
honoured HOME instead of XDG, or leaked the store across roots changes a pinned literal
(`r2_read=` / `store_under_xdg=` / `home_store_absent=` / `r4_userdir_under_home=`).

# 3. Idempotence defect found, mechanism, and its fix (C1 correctness)

**Observation (pre-fix rev `50b56438…`, 20:56):** second run of the *same* root:
`FAIL export_div s02 arm=xdg reason=run4_read_not_none:[run4] … store_c=[run4,run4]` — the
battery runs every CASES row twice (two batteries per round), so `export_div_s02_xdg_override`
would have been red on battery run 2 while run 1 was green.

**Mechanism (probe, verbatim, `/var/tmp/r103c-E0/probe/wipe_probe.gd`, subject = live
`homeC` holding a leftover store):**

```
PROBE_WIPE home_c_exists=true dot_local_exists=true
PROBE_WIPE static_listing_dirs=0 static_listing_files=0      <-- get_directories_at(get_files_at) hide dot-entries
PROBE_WIPE store_before=[run4,run4,run4]
PROBE_WIPE v0_as_landed home_c_exists=true store_after=[run4,run4,run4]   <-- landed _wipe_dir was a NO-OP
PROBE_WIPE v1_include_hidden home_c_exists=false dot_local_exists=false   <-- fix removes the tree
```

Godot 4.7.2 `DirAccess.get_directories_at()/get_files_at()` skip dot-entries
(`include_hidden` defaults false on the instance API), so the old `_wipe_dir` never descended
into `homeC/.local` and the final `remove_absolute(homeC)` failed on a non-empty dir.

**State now:** the E2 completion seat applied exactly this fix at 20:57:06 (`sha256 c08792c1…`,
468 lines; `_wipe_dir` at `corpus/fixtures/export_div_s02.gd:202` opens a `DirAccess` instance
and sets `include_hidden = true`). My "fixed copy" step was a no-op by construction (anchor
count 0; fixed-copy sha == landed sha), so control == fixed; the standing evidence is the
2-round × 2-arm control in §1 (4 PASS, byte-identical stdout per arm). **No further action
needed on the fixture**; the residual risk is a regression only — the failure mode is
detectable only on run 2, so any future edit to that fixture must be validated with 2 rounds.

# 4. PENDING rows (intended shape only — no invented pins)

Naming law (from the s02 fixture's own arm→row mapping): `export_div_s0N_<arm>[_<aspect>]`,
always keeping the `export_div_` prefix — both W5 gates key on it
(`r["case"].startswith("export_div_")`, `w5_export_div.patch`).

| row set | fixture state @ spec time | intended shape | pin source |
|---|---|---|---|
| `export_div_s01_*` (preset-vs-`--export-pack`) | landed 20:59, **still being written** (sha `ffb5c5a6…`→`fb9c8d08…` inside 60 s) | `PASS export_div s01 arm=<pack\|…> <derived literals>`; default arm `pack`; must carry a class literal that only a real two-path export can produce (artifact census of BOTH paths), nested engine output redirected | author's frozen receipt |
| `export_div_s03_seq_*` (multi-preset sequential) | landed 20:59 | default arm `seq`; emits `pack_exit/embed_exit`, `pack_magic=%08X`, `pack_ver`, `pack_flags`, `pack_file_base`, `pack_dir_offset`, `pack_entries`, `pack_md5_ok`, `pack_size`, `pack_footer_marker`, `embed_elf` | author's frozen receipt |
| `export_div_s04_*` (PCK extended header census) | **missing** | struct-decoded header fields as literals + independent byte-level re-parse cross-check; magic hex (`47445043`-style), engine-version-conditional pins like r102 | fixture → author |
| `export_div_s05_*` (editor-settings override probe) | **missing** | per-probe derived booleans with the supported/refused *class* as a literal; refusal arms must NOT echo engine `ERROR:` lines verbatim, else they need an `expected_errors` entry (§5) | fixture → author |

Rule: a pin may only be quoted from the authoring/validating seat's actual receipt bytes; do not
copy the shapes above into CASES with invented literals.

# 5. `expected_errors` needs

- s02 rows: **none**. Evidence: §1 scan (0 `ERROR:` / `SCRIPT ERROR:` / `Parse Error:` lines,
  stderr 0 B). Matches the W5 comment that the family ships allowlist-free; the
  `r103_expected_errors_all_matched` gate is then vacuous-but-honest (`all([]) is True`).
- Mechanism if ever needed (`run_battery.py:2038`-region dict lookup `.get(name, ())`, record
  field at `:2369`): the entry must be keyed by the **exact case name** and be the verbatim
  observed line (shape `exact`); a `dead_in_run` entry fails the new gate.
- Trigger condition to watch: any export_div arm that *echoes* a nested Godot `ERROR:` line onto
  its own stdout/stderr (most likely s05's refusal probes, or an s01 path that prints a nested
  preset/pack refusal). Then `classify_process`'s `unrelated_errors` clause rejects the row even
  though the PASS line is right — so the author must either redirect that output to scratch logs
  (r102/`export_prod.gd` evidence rule) or register the entry in the same splice.

# 6. Ordering / registration constraints (for the orchestrator)

1. **Insertion point:** immediately after `('export_launch_stock_missing_sidecar', …, :1710)` and
   before `("crash_spontaneous_sigabrt", …, :1711)` — i.e. *ahead* of the crash/descendant tail.
   The r79/r88/r101/r102 rule stands: no CASES row may sit between
   `descendant_pipe_detached_control` and the meta probes (`:99-102`, `:442-444`); appending at the
   end of CASES violates it. CASES closes at `:1719`.
2. **Within the family:** `export_div_s02_user_iso` **before** `export_div_s02_xdg_override`
   (the xdg arm reuses `<root>/div_s02/out/div_s02.x86_64` and the iso arm wipes that dir; both
   pins are order-robust, but reversing costs a redundant ~2.5 s export and destroys the
   cross-arm `xdg_a_store` evidence). Keep the family contiguous, s01→s05.
3. **No parallel execution of these rows:** they share the mutable variant dir `<root>/div_s02`
   (battery is sequential today, `:2376`).
4. **Atomic splice:** W5 H1 (`cases_integrity` prefix tuple + `"export_div_"`) + H2
   (`r103_expected_errors_all_matched`, `r103_export_div_count_floor`) + the CASES rows must land
   in ONE splice. `reports/round-103/mutations/w5_export_div.patch` `git apply --check` = OK on
   HEAD; `run_battery.py` sha256 == the splice script's `PINNED_SHA`. A gate-only splice turns the
   next battery red (w5 self-test cells M/P); a rows-only splice leaves the family floorless.
5. **Freeze the count floor:** with only the two s02 rows registered, splice with `--min-rows 2`
   (the default `>= 1` cannot see a partial drop once ≥2 rows exist). Raise it in the same splice
   that registers any s01..s05 rows, and never below the number of registered rows.
   *Unknown:* the final row count depends on how many arms s01/s03/s04/s05 land with (each
   `--arm=<x>` that prints its own PASS line = one row); freeze after those fixtures stop changing.
6. **Do not pin** `EXPORT_DIV_DIAG …` lines, `proj=`, `xdg_a_store=`, byte sizes, or any path.
7. **Budget:** 8 s per row vs measured 4.8 s worst case (iso, cold export) — fits, but the iso row
   is the family's tightest; on a saturated 64-seat host re-measure rather than assume.

# 7. Residual risk / unknowns

- Environment precondition for the whole family: a `linux_release.x86_64` template for
  `4.7.2.stable` must be reachable from `$XDG_DATA_HOME/godot/export_templates/…`,
  `$HOME/.local/share/godot/export_templates/…`, `/usr/local/share/…`, or `/usr/share/…`
  (`export_div_s02.gd` `_template_exists()`); otherwise the fixture FAILs closed with
  `reason=template_binary_not_found`. Present on this host under `$HOME/.local/share/…` (observed).
  Rows run with `env=None` (`run_battery.py:1933-1936`), so they inherit the battery's `HOME`.
- `/tmp` isolation: `EXPORT_DIV_DIAG … userns_tmp_isolation=true` observed on every run here; if a
  host lacks user namespaces the packer's fixed `/tmp/tmpproject.binary` temp runs against the
  (EDQUOT-prone) host `/tmp` — the r101 hazard, unchanged by this family.
- Pre-fix FAIL receipts exist only for revision `50b56438…` (logs kept at
  `/var/tmp/r103c-E0/logs/{s02_iso_r2.out,s02_xdg_r2.out}`); they are the regression witness, not
  current behaviour. Current revision sha must be re-read at integration time (the file was
  edited by another seat during this run).
- s01/s03 shas were still drifting when this shard was written (`ffb5c5a6…` → `fb9c8d08…` for
  s01); their row tuples remain PENDING until their authors' receipts freeze.
