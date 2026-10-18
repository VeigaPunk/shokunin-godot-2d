# r102-crit1 — adversarial audit of the C1 export-launch receipts (KEY=C1)

Seat: critic for claim C1. No shared file touched; `run_battery.py` never run; no fixture modified.
Owned output: this shard + `reports/round-102/mutations/r102-crit1-attack.sh`. Scratch: `/var/tmp/r102-crit1/`.
Host: `uptime` 2026-10-18 20:40:58Z — load 6.55/8.32/9.12 (1d17h41m up). Engine
`godot 4.7.2.stable.arch_linux.ed1daf0bf`; template `linux_release.x86_64` 73,519,416 B
sha256 `d9f79ab89b5ae369aeed11c6052d402e8218cd503bf85b4a235f9c30c46a7c63`; editor 182,015,704 B.
Labels: [obs] = this seat's measured bytes; [inf] = inference; [unk] = unknown.

## Attack verdicts (summary)

| attack class | verdict | strongest evidence |
|---|---|---|
| forged embed marker (wrapper script) | DEMONSTRATED against rc+substring pins; landed arms carry provenance (launch the export just written) — closed only where boot+boundary/identity legs co-registered | `forge/fake_marker.x86_64` rc=0 prints marker; `forge/fake_refusal.x86_64` rc=1 prints the refusal verbatim |
| size-bound vacuity / forged trailer | **OPEN in E0 `export_launch_embed_self_contained`** (pinned fields all pass on `template+"GDPC"`); CLOSED in s01/s02 (identity + boundary magic) | forged artifact 73,519,420 B passes `artifacts=1 sidecar_pck=0 tail_magic=47445043`; cannot boot |
| refusal-class spoofing via stderr subject injection | DEMONSTRATED live: `--path` refusal has the byte-identical class tail; E0 `embed_refusal`/`refusal` rows (tail-only `class=`) are spoofable; s03 pins the full flag sentence (good) | 5 subject variants in template strings; live `--path` rc=1 run |
| census echo-pins | landed censuses are artifact/runtime-derived (good); case ground truth established; E5 `tmpl` dir census is install-inventory; E0 census vacuous (see row 2) | engine-side pack listing `up.TXT=true down.txt=true`; forged trailer eval |
| missing-sidecar linger (host-state, NEW) | mechanism = spawned `zenity` alert child + `wait4`; rc=124 bound-safe at ≥17 s margin; PATH-less env flips to rc=1 in **15–44 ms**; orphan-zenity leak (intermittent) | strace fork/exec/wait4; phase table; PATH-neutral control |

## F1 — forged marker / forged refusal (attack 1)

Attack artifacts (shell scripts, in scratch; reproduced by the mutation script):
* `forge/fake_marker.x86_64` — prints `CRIT1_MARKER=1`, `CRIT1_EXE=$0`, 3 frame lines, exit 0. [obs] rc=0; a pin of `rc==0 && contains(marker)` accepts a **non-ELF** wrapper. Self-report does not save it: the wrapper truthfully prints its own path.
* `forge/fake_refusal.x86_64` — prints E0's exact 265-B refusal text to stderr, exit 1. Any pin of `rc!=0 && contains("compiled without support for path overrides")` accepts it (dtto `hint` + `log_bytes` shape).

Why the landed fixtures are (mostly) immune: every boot/refusal arm runs the artifact path **that the same fixture just exported** (`export_launch.gd:253/272/331/341`, `export_launch_s02.gd:378/438`), with scratch dirs wiped (`s02:352`). Required discriminator (per row, register-or-fail):
1. the launched path must be this run's export output (all landed arms OK);
2. embed arms must carry `sidecar_pck=0` in the **same** arm receipt (s02 in-row; E0 only in the separate census row — acceptable only if both rows are registered);
3. ≥1 structural leg that a non-boot artifact cannot satisfy: s02 `trailer_size_consistent`/`pack_magic_at_start` (`s02:369-377,398`); s01 `accounting_exact`+`pck_at_template_boundary` (`s01:316-321,341`);
4. do not rely on binary self-report (`OS.get_executable_path`) as sole provenance — forgeable by wrappers; it is fine as a secondary field.

## F2 — size-bound vacuity + forged trailer (attack 2)

Measured layout [obs] (same engine/template as the lane): template 73,519,416 B;
non-embed export `plain.x86_64` is **byte-identical** to the template (`cmp` clean, sha `d9f79ab8…`) + sidecar `plain.pck` 2,200 B; embed export `emb.x86_64` 73,521,624 B = template + 2,208; trailer last 12 B = u64 `0x894`=2,196 + ASCII `GDPC`; embedded payload = sidecar − 4 B (file_base field; matches s02 F3); `bin − 12 − pack_size == template` exactly, `GDPC` at pack start. E0's arithmetic (delta = pck+8; `embed` 2,064 = 2,056+8) is the same law with their project.
Consequences:
* `binary >= template` is **vacuous** (the non-embed byte-copy satisfies it with `==`); only `>` plus `sidecar_pck=0`/identity discriminates. s02 uses `>` (`s02:388`) and the identity — correct. s01's `ge_template_plus_pck` (`s01:318,321`) is implied by its own identity (12-B slack; 8-B slack against the sidecar variant) — harmless only because `accounting_exact` is also required.
* **Forged trailer counterexample [obs]**: `cat <template> > fake; printf GDPC >> fake` → 73,519,420 B, tail magic `47445043`, no sidecar, single file. E0's pinned row 2 fields (`r102-E0-spec.md:29-30`: `artifacts=1 sidecar_pck=0 tail_magic=47445043`) **all pass**; boot fails (rc=124 under `timeout 3`, no marker). s02's algebra on the same file rejects it (`trailer_gdpc=true`, `pack_size=0`, `trailer_size_consistent=false`). ⇒ **E0 census row must adopt the three s02/s01 legs** (trailer_size_consistent, pack_magic_at_start, bin_gt_template) or stay unregistered; the pair `embed_boot`+`embed_census` in one battery run does not close it — only the same-row legs do, because rows are pinned independently.
* E0 shard's "trailer last 8 B" description and s02's "last 12 B" decode are both consistent with the bytes; the 12-B decode with the size-consistency equation is the one that discriminates. Registering both E0 and s02 embed families doubles spending on the same mechanism (E0 spec §3.5 warns); recommend E0 boot + s02 embed rows, E0 census upgraded or dropped.

## F3 — refusal-class spoofing via stderr subject-tail (attack 3)

[obs] strings census, `linux_release.x86_64`: **five** distinct refusals share the tail
`…but this Godot binary was compiled without support for path overrides. Aborting.` +
hint `…use the disable_path_overrides=no SCons option…`:
``--test`` (unit tests variant), ```--scene```, `Scene path`, ```--path```, `project.godot path`,
```--main-pack```, plus CWD-`.pck`/`project.godot` variants (lines 53085/54769/54771/177236/177239/177245/177257-177260 of `strings -n 8`). The editor binary contains **0** occurrences.
[obs] live: `./plain.x86_64 --headless --path <dir> --quit-after 3` → rc=1, stderr =
``ERROR: `--path` was specified on the command line, but this Godot binary was compiled without support for path overrides. Aborting.`` + same hint + `at: setup (main/main.cpp:1782)` (vs `:1892` for `--main-pack`).
⇒ A row pinning only `class=path_overrides_disabled hint=disable_path_overrides_no rc=1` (E0 spec rows `export_launch_embed_mainpack_refusal`, `export_launch_stock_mainpack_refusal`, `r102-E0-spec.md:31-32,37-38`) stays green for a mutant that passes `--path`/`--scene` instead of `--main-pack` — the subject is not pinned. The forged refusal wrapper (F1) also passes it.
Required: pin the flag-specific full first sentence — **s03 does exactly that** (`export_launch_s03.gd:79` ``REFUSAL_FRAG = "`--main-pack` was specified on the command line, …"`` + hint `:80` + `REFUSAL_AT :81`), plus its template byte-identity receipt (`s03:451-452`) and nonexistent-path arm. Recommendation: register s03's refusal row; upgrade or drop E0's tail-only rows (no double-register).

## F4 — missing-sidecar linger is a zenity alert child (attack 4, host-state, NEW)

[obs] strace of the exact bare-binary shape (`/var/tmp/r102-crit1/iso6`, `strace -f -tt`, 24 s cap):
```
2518743 execve("./t.x86_64", ["./t.x86_64","--headless","--quit-after","2"]) = 0
2518743 clone3(...) -> /bin/sh -c `-- "xdg-user-dir" "DESKTOP" 2>/dev/null`
2518748 execve("/usr/bin/zenity", ["zenity","--warning","--width","500","--title","ALERT!",
         "--text","Error: Couldn't load project dat..."]) = 0
2518743 wait4(2518748 <unfinished ...     <-- game blocked here for the whole run
```
Phase table for "stock binary without sidecar" [obs]: (a) self-exit rc=1 after ~17.05 s
(err/rc mtimes 17:44:57.591→17:45:14.639); (b) SIGKILL after 210.2 s, still in `do_wait` (rc=137);
(c) rc=124 at 2,002 ms under `timeout 2` (this seat ×2; E0 ×2 rounds; E2 hand probes 6 s/10 s).
PATH-neutral control [obs]: `env PATH=<empty-dir> /usr/bin/timeout 6 ./p.x86_64 --headless --quit-after 2`
→ **rc=1 in 44 ms** (15 ms on the reproducer re-run), identical stderr class. Orphan leak [obs]:
zenity pid 2340417 (`ALERT! …iso2`) survived SIGKILL of its parent 6+ min → one leaked dialog
helper per bare run in the hanging phase; the leak is intermittent (1 orphan over ≥6 bare-binary
runs; the `timeout 2` runs left none in the reproducer re-run). `timeout` kills only the direct child.
Impact on landed rows:
* E0 `export_launch_stock_missing_sidecar` pins `rc=124` (`r102-E0-spec.md:41-42,68`) and s02 contrast gates on `killed==124` (`s02:442,457`). They are **bound-safe in practice** (min self-exit latency observed 17 s vs a 2 s bound) but host-state dependent; the wording "process keeps running"/"non-self-exiting" (`r102-E0-spec.md:68`, `r102-E2.md:132-134`, `s01:33-34`, `s02:13-16`) is false without "within the bound" — the process does self-exit once zenity dies or when zenity/PATH is absent. `rc=124` is the watchdog's status, not the game's.
* Recommend: (i) keep rc=124 but add an envelope note naming the zenity mechanism and the measured latencies; or better (ii) add the PATH-neutralized variant (deterministic rc=1, 15–44 ms, same class; also removes the 2-s battery cost and the leak) — new pin text `rc=1 class=project_data_missing pck_hint=true`; (iii) arms that keep the timeout should kill the process group and the orchestrator should prune `zenity` ALERT processes between battery runs (this leak is new to r102 fixtures).

## F5 — census echo-pins + case ground truth (attack 5)

Positive ground truth [obs] (my scratch `casep` preset, `include_filter="*.txt"`, files `up.TXT` + `down.txt`): engine-side listing of the exported pack (editor `--main-pack out/casep.pck` running the exported project's own main.gd):
`CRIT1_EXISTS up.TXT=true down.txt=true`; `CRIT1_ROOTFILES down.txt,main.gd.remap,main.gdc,main.tscn.remap,project.binary,up.TXT`; no-filter `plain.pck` contains neither. ⇒ `*.txt` matched the uppercase extension `up.TXT` (case-insensitive for this pair); E4's measured case-permutation byte-identity (`s04:26-27`) corroborates. Census consequences: the entry census must be derived from the artifact/runtime list (E4 `_census_pck :242-265`, s05 `_census_pck`), not from the filter string; strict-identity pin sets are brittle because exported scripts appear as `.gdc`+`.remap` names — use membership booleans (`present in pack`).
Byte-level [obs] (reproducer artifact): inside the pack, the filter-added extra-file entries are stored as length-prefixed **bare** names (`up.TXT`/`down.txt` at offsets 2332/2068), with no `res://up.TXT` byte run, while resources are stored as `res://…` paths — a census written as a `res://`+name byte grep silently misses filter-added files; parse the entry table (E4/s05 do).
Echo-pin rule applied to landed rows: E0 `stock_census`/`embed_census` fields are file-system/artifact reads (OK); E5 `tmpl` arm (dir listing + version.txt, `s05:16`) is **install inventory, not a capability** — its PASS text must not read as "feature supported"; E5's behavior legs (editor in-process feature vector + template runs + pack-entry census, `s05:40-43,546-561`) are the capability evidence. No echo-pin hole found in E6's patch design (patches are applied at runtime via `ProjectSettings.load_resource_pack`, `s06:60-62` — behavior, not census).

## Required discriminators per row (register-or-fail)

| row | requirement beyond current landed text |
|---|---|
| E0 `embed_boot` (`spec:27-28`) | OK; keep `cwd=isolated`; pair with (upgraded) census or s02 identity row |
| E0 `embed_self_contained` (`spec:29-30`) | **ADD** `trailer_size_consistent=true pack_magic_at_start=true bin_gt_template=true` (s02 form) or drop row (forgery in F2) |
| E0 `embed_mainpack_refusal` (`spec:31-32`) | **ADD** subject pin (s03 `REFUSAL_FRAG` + hint), else spoofable by `--path` (F3) |
| E0 `stock_boot` (`spec:33-34`) | OK |
| E0 `stock_sidecar_census` (`spec:35-36`) | OK (pck head magic from artifact); optionally add `bin_eq_template=true` (size identity measured: byte-identical) |
| E0 `stock_mainpack_refusal` (`spec:37-38`) | subject pin (as above); s03 covers it — prefer s03 row, avoid double-register |
| E0 `editor_mainpack_contrast` (`spec:39-40`) | OK (editor build boots the same pack) |
| E0 `stock_missing_sidecar` (`spec:41-42`) | keep rc=124 **with** envelope note (zenity wait4, self-exit latencies 17 s–210 s+, PATH-less rc=1/15–44 ms) or switch to PATH-neutral deterministic rc=1 |
| s02 `embedded_quit_frames` (`s02:82-84`) | OK as gated (pck_sibling/trailer/identity/`>`); `bin_bytes>template_bytes` strict ✓; wants env note only |
| s02 `nonembed_contrast` (`s02:85-87`) | replace `bin_eq_template` size equality with byte/sha equality (measured byte-identical; template sha is root-independent) if cheap; else keep; add zenity note |
| s01 (`s01:313-321,341`) | OK (identity + boundary); keep `accounting_exact`; treat `ge_template_plus_pck` as secondary; neg arm rc=124 inherits F4 fragility |
| s03 (`s03:79-81,451-452`) | OK — the only refusal family that closes F3; recommend as the registered refusal row |
| s04 | OK (artifact census + case-permutation byte-identity); keep membership booleans |
| s05 | OK (behavior legs); label `tmpl` inventory row as inventory, not capability |
| s06 | design is behavior-first (patch pck delta + runtime apply + refusal classes `s06:50-52`); critic did not re-run its arms — ceded to E6 receipts |

## Evidence index (exact commands; logs under /var/tmp/r102-crit1/logs/)

* `strings -n 8 $TPL | grep -n "path overrides"` → 5 subject variants (template); `grep -ac … /usr/bin/godot` → 0.
* exports (unshare+tmpfs /tmp): `godot --headless --path proj --export-release plain|emb …x86_64`, `--export-pack casep …casep.pck` → rc 0; sizes/shas in F2.
* launches: `emb_iso_q3|q1` (rc 0, frames [1,2,3]/[1], banner `.official`), `plain_iso` (error class, rc 1 after ~17 s / ≥210 s phases), `plain_sidecar` rc 0, `plain_mainpack` rc 1 (:1892), `plain_pathrefuse` rc 1 (:1782), `editor_mainpack` rc 0 (`.arch_linux`), forged wrappers rc 0/1.
* forged trailer: `trailer_fake.x86_64` (73,519,420 B) field eval + `timeout 3` boot rc=124.
* linger: strace `/var/tmp/r102-crit1/logs/strace_probe.txt` (32,931 lines); zenity census `ps -eo pid,ppid,etime,args | grep zenity`; PATH-neutral `env PATH=/var/tmp/r102-crit1/nobin /usr/bin/timeout 6 …` rc=1 15–44 ms.
* case census: `godot --headless --main-pack out/casep.pck --quit-after 3` → `CRIT1_EXISTS …`, `CRIT1_ROOTFILES …`; raw-byte form: `grep -abo "up\.TXT" out/casep.pck` (bare-name entry).
* Reproduce: `reports/round-102/mutations/r102-crit1-attack.sh` (scratch root default `/var/tmp/r102-crit1-attack`); validated end-to-end from a clean root 2026-10-18 (~18 s): [A]–[E] reproduced ([D] bare rc=124, PATH-neutral rc=1 15 ms; [E] `up.TXT=true down.txt=true`).

## Unknowns / open

* [unk] what phase variable gates zenity's lifetime (dbus/X display autolaunch suspected; not read from source, not reproduced by phase control) — same class as the C2 r62 probe and the r101 tri-red joys rows.
* [unk] whether the 17-s self-exit phase recurs in battery context; the 2-s bound margin (≥8.5×) is one-sided evidence.
* Not re-verified by this seat: s06 patch artifacts (E6 owns receipts), E5 runtime-vector values, cross-host behaviour (single host, one engine build).
