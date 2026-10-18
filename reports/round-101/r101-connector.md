# r101 CONNECTOR — sibling-overlap scan (2D lane ↔ 3D lane r104 in flight)

**Seat:** CONNECTOR · round 101 · lane `game-dev-2d-shokunin` · **READ-ONLY scan** — this shard is the only file written by this seat. No commits. Nothing copied out of the 3D lane tree.
**3D tree state:** r104 swarm mid-write (`.r104-seat17/`, `trace.*`, modified `run_gate.sh` `+85/−4` per `3d/reports/round-104/r104-report.md`). The 3D files cited below were read at 16:21–16:24 local; shas marked **[moving]** were changing under the other session. No 3D content was modified, copied, or committed.

## Load context (recorded once, host shared)

```
$ uptime
 16:21:06 up 1 day, 16:21, 1 user,  load average: 33.42, 19.05, 12.84
$ uptime   # 2 min later, still climbing
 16:23:19 up 1 day, 16:23, 1 user,  load average: 54.55, 32.63, 18.67
$ df -h /tmp
 tmpfs  16G  13G  3.1G  80% /tmp
```
The 3D r104 and 2D r101 swarms are both active; load 54.5 at last reading.

## Plan (5 lines, kept from seat start)
1. Read 2D push-forward state + index: which of the 100 pushes in `reports/round-100/` are registered, complete, or incomplete (grep `LOG.md`, `SCORECARD.md`, `PROVINCE.md`).
2. Cross-reference the 2D index against the 3D lane `LOG.md` tail / `SCORECARD.md` head / `PROVINCE.md` + `../MANIFEST.json` last rounds for shared rows, naming, and coverage overlap.
3. Itemize any push/company the 2D lane should import as routed cited references (XConnector proposals, fold-specs, tree-timeout mechanism) and any contested scope between the lanes.
4. Resolve contests by explicit lane-ownership rule (2D lane owns the 2D-side citation; name the exact row/col it lands in); flag what cannot be resolved by ownership alone.
5. Write shard with citations (exact line refs and observed output) and routed proposal list.

**STATUS: complete.** Findings below; no work items were executed because this seat is read-only.

---

## 0. Verdict in one line

Of the three named candidate imports, **tree-timeout is still open and valuable**, **XConnector's while-live gate is already closed on the 2D side (landed r64, dual landed r65)**, and **fold-spec has no substantive 2D content**. Two *new* live cross-lane hazards dominate: **/tmp per-uid quota exhaustion (measured)** and the **shared export-templates directory** (safe redirect mechanism measured).

---

## 1. Routed import list (3D → 2D), priority order

### I1 — tree-timeout / process-group termination mechanism — **OPEN, highest value**

**2D gap (measured):**
```
$ grep -n "setsid\|killpg\|getpgid\|start_new_session\|process.group\|pkill" corpus/fixtures/run_battery.py
(no matches; the only "tree" hits are expected-string text)
```
* `corpus/lessons/r22-real-timeout.md`: "there is explicitly **no process-tree cleanup claim**"; only the direct child is killed/reaped.
* `corpus/lessons/r62-pipe-eof-timeout.md`: "CPython POSIX kills the **direct child pid only** … never a process-group signal"; "an fd-detached descendant … lives on as an orphan"; recheck clause names `start_new_session`/`os.killpg` as the trigger for re-measurement.
* `corpus/README.md:24` and `corpus/lessons/r19-stream-attribution.md:32`: "process-tree timeout remain[s] unprobed".
* Registered as a pending import since r63/r64: `SCORECARD.md` planned line — "port of 3d's tree-timeout mechanism is a proposed sibling import".

**3D mechanism (the import target), all read-only:**
* `3d/corpus/fixtures/timeout_tree3d.gd` — clean arm + `--hold-open` arm spawning `timeout_descendant.py`, 2 s witness-pidfile deadline, 30 s hold.
* `3d/corpus/fixtures/run_battery.py:1101-1215` `probe_tree_timeout` — `subprocess.Popen(..., start_new_session=True)` (:1145); on 3 s timeout `os.killpg(process.pid, SIGKILL)` (:1168); `/proc/<pid>/stat` identity = cmdline + state not `Z/X` + `ppid` + `pgid` + `starttime` (:1121-1138); witness verified detached (`ppid == godot pid`, `pgid == witness_pid`); SIGTERM → 3 s grace → SIGKILL (:1170-1181); pass conjunction at :1211-1215 = normal clean **and** timed_out **and** `actual_exit=None` **and** marker exactly once **and** `classified is False` **and** witness verified **and** `witness_gone` **and** cleanup string exact.
* `3d/corpus/fixtures/README.md:83-97` documents the user-facing contract ("runner confirms the `/proc` identity and start time of the one detached witness, kills/reaps Godot and sends SIGTERM to that verified witness *before* waiting for pipe EOF").

**Import spec for a 2D owner round (does not exist yet; needs a coverage seat):** copy the two-arm fixture pattern with a `Node2D` marker and the same verdict conjunction; keep it an **uncounted meta row** (the record carries `error` on the hold arm, so it cannot be a CASES tuple — same reason as the r62 pipe-EOF meta). Traps to inherit: (a) the relative-`--runs` tree-timeout trap from `3d/reports/round-72/r72-verifier.md` (relative scratch prefix vs globalized `/proc` cmdline → fails closed; only relevant *once the mechanism lands* — 2D has no `/proc` prefix matching today); (b) **do not put the probe in `/tmp`** — see I4/H2; (c) wall-clock: 2 Godot boots ≈ 2 s here, but serial boot floor is ~0.9 s each (`3d` r103 calibration), so do not scale this into a serial battery arm.

### I2 — XConnector while-live marker gate — **CLOSED; no import**

* 3D proposal: `3d/reports/round-72/r72-adjudicator.md:48` — "2d could adopt 3d-style liveness-gated acceptance for marker reads"; `3d/SCORECARD.md:12` planned line — "XConnector while-live marker gate port to 2d".
* 2D already landed it at r64: `corpus/fixtures/run_battery.py:2721` ("r64 meta: while-live signature gate — the XConnector wave-3 synthesis"), implementation at `:2940`, `LOG.md:610-612`, `SCORECARD.md:20` (poll() at marker-completing read; forged post-death rejects; `kill(pid,0)` false-accepts through zombies; live-window forge defeated by construction).
* The proposed dual also landed: r65 XConnector wave-4 Arm 1 (`LOG.md:620-624`) — post-death un-allowlisted `ERROR:` flips a genuine PASS→FAIL.
* **Disposition:** remove both items from the 2D `planned` queue; cite r64/r65 as the closure. No 3D→2D action.

### I3 — fold-spec — **NOT substantive for 2D; two process rules are transferable**

* `3d/reports/round-102/fold-spec.md` is the r103 fold queue for the 3D lane's Unreal-MCP gate (A1 range-tail pointer regex, A2 prose-hijack, A3 card-name set, A4 network-blocked vs byte mismatch). It has no 2D fixture or gate in scope.
* Transferable **process** rules only (propose for r102+/2D templates, not code):
  1. Attack/falsification verdicts must name the **target hash** — 3D r103 `LOG.md:1376-1381` records a seat that attacked a 249-line intermediate while the final was 347 lines.
  2. Distinguish pinned fixture **CODE** from repairable fixture **DOCS** — 3D r103 conformance defect and its ruling (`LOG.md:1393-1397`).
  3. A bare line-number citation rots — cite structurally with a dated parenthetical (`LOG.md:1376`).

### I4 — NEW host/workdir laws from 3D r101–r104 (actionable for r101 itself)

* **`GATE_WORKDIR` > `TMPDIR` > `/tmp`** pattern: 3D r104 gate `run_gate.sh:37-71` `WORK_ROOT=${GATE_WORKDIR:-${TMPDIR:-/tmp}}` with **up-front, loud validation** (unset/typo'd dir no longer fails late as an empty `$WORK`). File is **[moving]** (modified in-flight `+85/−4`, not committed at read time), so cite it as an r104-in-flight pattern, not a landed 3D law.
* **/tmp is a shared, quota-limited resource** — 3D r103 `LOG.md:1382-1383` ("`/tmp` is a shared 16G tmpfs near quota — mktemp/clone workdirs there flake silently"); measured live on the 2D side in §H2.
* **`--path .` against the seed tree stray-writes fixture dirs** — 3D r103 `LOG.md:1387-1388` (`stray r90bt_*` hazard). 2D's battery already copies seeds to scratch (`corpus/README.md:3`), so the hazard is contained *for the battery*, but any r101 seat running `godot --path corpus/fixtures` directly would reintroduce it. Recommend an integration-time `git status --porcelain corpus/fixtures` check.
* **Serial-child wall-clock scales by boot floor, not cores** — 21 serial boots ≈ 19 s vs 21 concurrent ≈ 1.0 s (3D r103 calibration, `LOG.md:1381-1382`). Relevant to any 2D timing-bounded arm.

### I5 — low-priority calibration laws (cite, do not land)

* **Pointer counts are scanner-relative** — three scanners read 40/41/43 on one tree; never cite a bare `POINTERS=` without its scanner (`3d/LOG.md:1341-1343`). Only relevant if a 2D seat adds a pointer census.
* **Pinned-env markers are host receipts, not timeless truths** — 3D battery's node-v24 markers go red on the host's v26 (`3d/LOG.md` ROUND 103 LAWS). No 2D Node runner today; no action.

---

## 2. Contested scope / cross-lane hazards

### H1 — shared export-templates directory — **LIVE hazard for r101 C1**

* 12 r101 shards cite `~/.local/share/godot/export_templates/4.7.2.stable/` (E1/E2/E3/E6/E8/E9/E10/E11, crit1, mut5, ver3, plus mine). E8's plan (`r101-E8.md:5`) is to "run Godot … with the export-templates dir redirected to an empty path". **A rename/move of the shared directory would break every concurrent exporter in both lanes** (E1–E11 now, and any 3D r104 run that exports).
* **Safe mechanism, measured by this seat [O]:** Godot resolves templates under `$XDG_DATA_HOME/godot/export_templates/<version>/`. Probe under `/var/tmp/r101-connector/proj` (minimal project + `LinuxProbe` preset):

```
$ XDG_DATA_HOME=$P/xdg-empty godot --headless --path $P --export-release "LinuxProbe" $P/out.x86_64
ERROR: Cannot export project with preset "LinuxProbe" due to configuration errors:
No export template found at the expected path:
/var/tmp/r101-connector/proj/xdg-empty/godot/export_templates/4.7.2.stable/linux_debug.x86_64
No export template found at the expected path:
/var/tmp/r101-connector/proj/xdg-empty/godot/export_templates/4.7.2.stable/linux_release.x86_64
ERROR: Project export for preset "LinuxProbe" failed.
EXPORT_EXIT=1
--- control (default XDG_DATA_HOME) ---
CTRL_EXIT=0 ; out2.x86_64  73,519,416 bytes
```
* **Rule:** E8 and any templates-missing arm must use `XDG_DATA_HOME=<private empty dir>` (or a per-run `HOME`), never mutate `~/.local/share/godot/`. Caveat: the probe preset was deliberately minimal, so the four `Couldn't find … export_filter/include_filter/exclude_filter/options` ERROR lines are **probe noise**, not the templates error class; the class is the `No export template found at the expected path:` pair + exit 1.

### H2 — `/tmp` per-uid quota exhaustion — **LIVE, measured twice by different seats**

* My measurement at 16:23 (16:23:19 uptime above):
```
$ printf 'x' > /tmp/r101-connector/probe2b.txt   # 1 byte
$ dd if=/dev/zero of=/tmp/r101-connector/probe1m.bin bs=1M count=1
dd: error writing 'probe1m.bin': Disk quota exceeded
0 bytes copied
DD_EXIT=1
```
  Tiny writes can succeed while 1 MiB writes fail — this is the "flake silently" shape, not a clean ENOSPC.
* E7 independently recorded it and moved scratch: `r101-E7.md:5` — "`/tmp` is quota-blocked on this host — EDQUOT even for 2-byte writes"; scratch is `/var/tmp/r101-E7/proj/`.
* **Routed:** r101 seats with multi-MB scratch (exports, zips, main-pack runs) should use `/var/tmp/r101-<key>/`, and the integration battery should not assume `/tmp` capacity. E7 already complies; E1–E6/E8–E11/E12/E17 were still targeting `/tmp` at read time.

### H3 — surface boundary between lanes (semantic, not contested in practice)

* 2D `PROVINCE.md`: owns "2D game production … loop, input, physics, scenes, camera, UI, levels, juice, **export readiness**"; refuses engine source, publishing, rights, harness auditing, narrative canon. No sibling-lane clause.
* 3D `PROVINCE.md`: refuses "2D production scope (game-dev-2d — shared fixture patterns are inherited, 2D product surfaces are not)" and lists "export templates for 3D" as unprobed coverage (`3d/SCORECARD.md:12` planned/coverage text).
* **Boundary rule to state (not to edit — PROVINCE is orchestrator-owned):** patterns (export lattice shape, tree-timeout mechanics, citation discipline) inherit freely; **evidence does not cross lanes** — a 2D export row never proves a 3D export claim, and r101 C1's `export_prod` lattice is 2D-only. Similarly, 2D r100 GUI/Viewport input covers 2D input; 3D's "GUI/viewport embedding" remains a 3D camera/viewport surface. No overlap found that changes either lane's claims.

### H4 — fleet MANIFEST lag (informational; no action taken)

`../MANIFEST.json` holds only **8** game-dev entries: last 2D closure is **r64** (`commit game-dev-2d-shokunin@a32920b+5265da6`), last 3D closure is **r73** (`game-dev-3d-shokunin@b41fb33`) — read at 16:22. So 2D r65–r101 and 3D r74–r104 are invisible to anything reading the fleet manifest. If r101 close is expected to append a manifest row, that is orchestrator-owned; I did not touch the file.

---

## 3. Evidence index (exact commands run)

| # | command | result |
|---|---|---|
| 1 | `uptime` ×2 | load 33.42 then 54.55 (19:21Z, 19:23Z) |
| 2 | `df -h /tmp`; `df -i /tmp` | 13G/16G used (80%, 3.1G free); inodes 63% |
| 3 | `printf 'x' > /tmp/.../probe2b.txt` | 1 byte written, OK |
| 4 | `dd if=/dev/zero of=/tmp/.../probe1m.bin bs=1M count=1` | `Disk quota exceeded`, 0 bytes, exit 1 |
| 5 | `grep -n "setsid\|killpg\|getpgid\|start_new_session" corpus/fixtures/run_battery.py` | no matches (2D lacks process-group kill) |
| 6 | `XDG_DATA_HOME=<empty> godot --headless --export-release LinuxProbe` | exit 1; `No export template found at …/xdg-empty/godot/export_templates/4.7.2.stable/linux_{debug,release}.x86_64` |
| 7 | same, default `XDG_DATA_HOME` | exit 0; 73,519,416-byte x86_64 |
| 8 | `python3` filter over `../MANIFEST.json` | 8 game-dev rows; last 2D r64, last 3D r73 |
| 9 | `grep -rn "XConnector" game-dev-3d-shokunin/` | proposals at r71/r72/r75; plan line at `SCORECARD.md:12` |

Scratch created under `/var/tmp/r101-connector/` was deleted after the probe (`rm -rf`); `/tmp/r101-connector/` holds no files.

## 4. Not done / follow-ups for the parent

* **I1 tree-timeout import is unimplemented** — needs an owner round with fixture budget; spec above. This is the only substantive open import.
* **H1 must be enforced on E8** (and any templates arm): `XDG_DATA_HOME` redirect, never a move of the shared dir. If E8 already wrote a different mechanism after 16:24, re-check `r101-E8.md`.
* **H2:** seats still on `/tmp` for multi-MB artefacts should be moved to `/var/tmp`; disk headroom was 3.1 GB at 16:23 and shrinking (12G→13G used in 2 min).
* **H3/H4 are proposals only** — `PROVINCE.md` and fleet `MANIFEST.json` are outside seat write scope.
* 3D r104 artifacts were read mid-flight; the only 3D hash I cite is the moved-file caveat, deliberately not a stable hash.
