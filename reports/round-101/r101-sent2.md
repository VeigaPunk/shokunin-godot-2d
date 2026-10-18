# r101-sent2 — Evidence-discipline sentinel (SENT-2)

Load context (observation, one sample as instructed): `uptime` @ 16:21:55 → `up 1 day, 16:22, 1 user, load average: 42.10, 23.60, 14.72` (3D-lane r104 swarm + this round co-resident; slowness was expected, not failure).

Final census (observation): **64 shards**, **890,735 bytes**; last shard write **16:44:03** (`r101-scr4.md`); zero `r101-*.md` modifications after that through my snapshot **16:45:00**. `reports/round-101/mutations/` = **113 entries**. Later writes are outside this snapshot by definition.

## Method

- All 64 shards were processed by a claim/evidence extractor (`/var/tmp/r101-sent2/audit2.py`): per-line command citations, output-shaped bytes, observation/inference/unknown labels, and should/probably candidates.
- Full reads: `E0, E3, E5, E6, mut4, scr4`; targeted findings-section reads: `E17, crit2, crit5, simp1, simp3, scr2, ver5, ver8, connector`; digest review for the rest.
- Standard: a findings claim passes only with (a) a command/code-path citation and (b) observed bytes / quoted output / exit code in its immediate block. Flags: `E-CMD` (no command), `E-OUT` (command, no output), `LANG` ("should/probably/likely/presumably" in findings), `INF` (inference unlabeled), `STUB` (no results at end-time).
- I did **not** run `run_battery.py`, did not edit shared files, and created only this shard; scratch/tooling lives in `/var/tmp/r101-sent2/` (why not `/tmp`: below).

## Verdicts (summary)

1. **No "should work" evidence language found.** The strict pattern `(should|will|must|ought to) (work|pass|succeed|reject|produce|be stable|be reproducible|be byte)` returned 7 hits, all plans, row criteria, or counterfactuals (e.g. `mut8:215` "no row-level pin ... can or should reject it"; `ver9:94` "every new row must PASS" — a registration criterion). All 58 loose LANG candidates were inspected: recommendations ("seats should use /var/tmp"), counterfactuals ("would be vacuous"), or explicitly-labeled inference. No shard asserts an unverified result as likely/expected success.
2. **Four shards are STUBs at end-time** — plan/recon text only, no results, no receipts, no commands run in the shard. Their fixtures did land, so the gap is shard-level evidence, not missing artifacts: `E0-EXPORT-LEAD`, `E3`, `E5`, `E6`. Cross-confirmed by `scr4:32-33`, `scr4:235-236` (E3/E5/E6 "receipts missing"), and `ver14:5` (E0 spec absent at three timestamps).
3. **One unlabeled inference (minor):** `crit6:118` — "**Likely** entry-free rows → any gate is vacuous for them". A likelihood is stated in a findings section without an `[inference]` label; the surrounding context is otherwise measured.
4. **One broken evidence pointer (minor):** `planner:223` cites `reports/round-101/r101-E0-spec.md` as its "Evidence pointer"; that file is **ABSENT** (`ver14:5,17,21,145`; `scr4:42,232`).
5. **Cross-cutting hash staleness (caveat, not per-seat defect):** C1 shards cite mid-round fixture sha256s that no longer match the landed bytes — `scr4:168-172` discloses this; I independently confirmed s01 drift (below). Any "sha-pinned" claim written before the final edit is stale; integration must hash at commit.

## Independent spot-checks (my observations, not re-run of seat measurements)

| check | observed |
|---|---|
| `grep -c offy corpus/fixtures/r95b_order.gd` | `0` (matches E17:19,69-70) |
| `grep -o offy corpus/fixtures/run_battery.py \| wc -l` | `1` (matches E17:19-20,69) |
| `grep -c 'r101_' corpus/fixtures/run_battery.py` | `0` (matches scr4:262; rows unregistered as stated) |
| `sha256sum corpus/fixtures/export_prod_s01.gd` | `d6a2868d5a490240b37d88b5545a4020d6f685ac790ae3765c061c0e5768e7eb` — matches `scr4:146`, differs from `scr6`'s cited `4239ecec` (drift confirmed) |
| `sha256sum corpus/fixtures/export_prod_s08.gd` | `e6c6336199b0d19fa4139d334fd751485963c220192f678519ad3599bb955e28` — matches `E8` cite and `scr4:153` |
| `ls reports/round-101/mutations/ \| wc -l` | `113` (matches `scr4:264`) |
| `/tmp` write: `cat > /tmp/r101-sent2/detail.sh` | `cat: write error: Disk quota exceeded`; `df -h /tmp` showed `3.1G avail`, `80%` used → confirms the EDQUOT class reported by E7/E2/E10/crit4 (my tooling moved to `/var/tmp`) |

## Per-seat table (64 shards present at snapshot)

Counts are `lines / command-lines / output-lines / label-lines` from the extractor. `CLEAN` = no evidence-discipline flag found (digest + targeted read); it is not a re-execution of the seat's measurements.

| shard | L / cmd / out / lab | verdict | note |
|---|---|---|---|
| connector | 154 / 13 / 26 / 1 | CLEAN | evidence index with 9 exact commands; H2 reproduced |
| crit1 | 233 / 20 / 61 / 16 | CLEAN | attack matrix with measured bytes |
| crit2 | 231 / 4 / 86 / 15 | CLEAN | harness script + capture semantics cited; per-attack CLI not repeated (noted, not flagged) |
| crit3 | 249 / 8 / 32 / 8 | CLEAN | measured + labelled |
| crit4 | 269 / 16 / 56 / 10 | CLEAN | load envelopes, commands quoted |
| crit5 | 164 / 28 / 35 / 3 | CLEAN | command table + observed outputs; low label count but claims are measurements |
| crit6 | 270 / 14 / 38 / 6 | **INF-minor** | L118 "**Likely** entry-free rows" unlabeled |
| D1 | 264 / 8 / 57 / 14 | CLEAN | [D]/[O] legend; explicitly refuses to state inference (L256) |
| D2 | 183 / 10 / 29 / 13 | CLEAN | matrices + byte evidence |
| D3 | 99 / 12 / 23 / 5 | CLEAN | re-measured receipts |
| D4 | 290 / 7 / 50 / 15 | CLEAN | field grammar + mutation matrix |
| E0-EXPORT-LEAD | 10 / 2 / 2 / 1 | **STUB** | plan only; L10 "see uptime row below" has no row; spec absent |
| E1 | 181 / 24 / 42 / 9 | CLEAN | mutation table with observed first-fail lines |
| E2 | 246 / 20 / 60 / 12 | CLEAN | zip census + masks; re-run vs landed bytes |
| E3 | 21 / 1 / 3 / 2 | **STUB** | L14-20 all `- [ ]`; L21 "(progress appended below)" — nothing appended; s03 fixture landed (13,510 B) |
| E4 | 222 / 27 / 69 / 8 | CLEAN | main-scene swap + launch receipts |
| E5 | 14 / 2 / 1 / 0 | **STUB** | L13-14 "## Status / - [ ] recon"; s05 fixture landed (27,720 B) |
| E6 | 27 / 5 / 4 / 2 | **STUB** | L23 "scratch probe in progress"; L27 "(pending)"; s06 fixture landed (30,295 B) |
| E7 | 167 / 23 / 59 / 6 | CLEAN | refusal arms + mutant controls |
| E8 | 231 / 26 / 71 / 12 | CLEAN | templates-missing arm matrix with PASS receipts |
| E9 | 111 / 10 / 35 / 2 | CLEAN | arms + PASS lines; low label count, claims measured |
| E10 | 106 / 11 / 27 / 11 | CLEAN | icon/UID census with byte table |
| E11 | 202 / 35 / 78 / 5 | CLEAN | frame receipts, measured arms |
| E12 | 168 / 10 / 44 / 7 | CLEAN | seqfull fixture + verify output |
| E17 | 121 / 12 / 30 / 1 | CLEAN | retirement census + live measurement; commands and md5s quoted |
| mut1 | 249 / 12 / 59 / 10 | CLEAN | forged-line matrix, pre/post receipts |
| mut2 | 179 / 12 / 42 / 5 | CLEAN | forged receipt matrix |
| mut3 | 149 / 15 / 46 / 14 | CLEAN | dead-measure mutation; churn caveat disclosed |
| mut4 | 93 / 5 / 36 / 8 | CLEAN | three rigs, exact command shape, labelled inference |
| mut5 | 73 / 13 / 20 / 8 | CLEAN | wrong-magic mutant |
| mut6 | 183 / 18 / 41 / 9 | CLEAN | timeout-truncation probe |
| mut7 | 235 / 24 / 52 / 6 | CLEAN | harness-dead class |
| mut8 | 252 / 17 / 41 / 6 | CLEAN | CRLF seam matrix |
| mut9 | 190 / 22 / 34 / 7 | CLEAN | filter inversion matrix |
| planner | 302 / 38 / 74 / 17 | **E-CMD-minor** | L223 evidence pointer to absent `r101-E0-spec.md` |
| scout | 185 / 13 / 31 / 7 | CLEAN | census + read-only battery analysis |
| scr1 | 184 / 37 / 58 / 14 | CLEAN | lesson draft embedded; cites measured sources |
| scr2 | 178 / 13 / 49 / 2 | CLEAN | replay digests + demo script; claims measured |
| scr3 | 315 / 15 / 38 / 17 | CLEAN | 40-run phase census; unknowns labelled |
| scr4 | 276 / 20 / 65 / 5 | CLEAN | end-time skeleton; `[obs]/[seat]/[inf]` labels; hash caveat |
| scr5 | 263 / 26 / 38 / 16 | CLEAN | LOG draft; unresolved fields `⟨TBD⟩` |
| scr6 | 89 / 20 / 34 / 14 | CLEAN | verdict table + measured re-checks; cites pre-edit hashes (see caveat) |
| sent1 | 179 / 7 / 22 / 6 | CLEAN | scope sentinel; "likely verifier receipts" explicitly labeled inference (L161) |
| sent2 | this file | n/a | self |
| simp1 | 314 / 15 / 50 / 1 | CLEAN | 669 launches, 60-row tables, receipts path |
| simp2 | 90 / 13 / 15 / 2 | CLEAN | patch shard; targeted-row limits disclosed |
| simp3 | 300 / 23 / 39 / 2 | CLEAN | 365 receipts, lane tables, exact launch shape |
| ver1 | 81 / 9 / 30 / 14 | CLEAN | format derivation with O/D labels |
| ver2 | 399 / 32 / 92 / 11 | CLEAN | 25 KB matrix; `/tmp` EDQUOT disclosed |
| ver3 | 114 / 21 / 34 / 14 | CLEAN | refusal classes measured |
| ver4 | 384 / 39 / 101 / 18 | CLEAN | icon/main-pack semantics |
| ver5 | 194 / 8 / 25 / 6 | CLEAN | `[I]/[U]` labels; exact commands |
| ver6 | 197 / 14 / 32 / 5 | CLEAN | replay recomputation |
| ver7 | 269 / 8 / 54 / 12 | CLEAN | divergence recomputation |
| ver8 | 250 / 8 / 40 / 3 | CLEAN | Y math; `[O]` markers + md5s |
| ver9 | 223 / 15 / 44 / 10 | CLEAN | regression protocol + matrix |
| ver10 | 201 / 18 / 42 / 8 | CLEAN | receipt stability protocol |
| ver11 | 200 / 21 / 75 / 22 | CLEAN | forge-kill matrix |
| ver12 | 208 / 22 / 33 / 11 | CLEAN | floor-gate mutation matrix |
| ver13 | 132 / 11 / 42 / 11 | CLEAN | expected-errors census |
| ver14 | 169 / 20 / 60 / 20 | CLEAN | independent PCK/zip parser; observation/inference/unknown ledger |
| ver15 | 202 / 23 / 78 / 13 | CLEAN | launch-probe matrix |
| ver16 | 105 / 13 / 20 / 15 | CLEAN | determinism honesty; F5/F6 labeled |
| ver17 | 142 / 29 / 17 / 12 | CLEAN | environment pins with measured tokens |

## Flag detail (exact quotes)

- **E0 (STUB).** `r101-E0-EXPORT-LEAD.md:1-10` is only the plan; L10 reads "(load context: see uptime row below)" and no row follows. L8 promises `reports/round-101/r101-E0-spec.md`; that file is absent (`ver14:5` "Verdict: `r101-E0-spec.md` is ABSENT (checked 16:23:56, 16:25, 16:32:10)"; `scr4:232`). The consolidated `corpus/fixtures/export_prod.gd` exists (25,191 B, scr4:145) but is undocumented by its lead.
- **E3 (STUB).** L14-19: "## Status" + five unchecked boxes (`- [ ] discovery` … `- [ ] validation run`); L21: "(progress appended below)" with no appended text. `export_prod_s03.gd` exists (13,510 B; sha `d5e5314e…` per scr4:148), so the determinism measurement is unverified at shard level (`scr4:235`).
- **E5 (STUB).** L13-14: "## Status" / "- [ ] recon" — nothing further. s05 fixture exists (27,720 B, sha `8f16f47e…`, scr4:150); remap/UID census unverified at shard level.
- **E6 (STUB).** L23: "STATUS: recon complete, scratch probe in progress."; L27: "(pending)". s06 fixture exists (30,295 B, sha `772fb51e…`, scr4:151); filter measurements unverified at shard level.
- **crit6 (INF-minor).** L116-119: "…`corpus/live/r101-ver17/receipts/*.err` = 0 B. **Likely** entry-free rows → any gate is vacuous for them, but `cases_integrity` existence is still the needed pin." The likelihood is not labeled as inference; the rest of the shard does label observations.
- **planner (E-CMD-minor).** L223: "| headless production export | … | §2.1–§2.5 here + `reports/round-101/r101-E0-spec.md` (row receipts) | r101 (pending integration) |" — the pointer target does not exist (ver14 triple-check; scr4 §5). The row is marked pending, so severity is low.
- **Hash staleness (caveat).** `scr4:168-172`: "shard-cited hashes for `export_prod_s*` differ from the end-time files … Fixtures were edited after scr6's read; **hash at integration/commit**, do not treat shard cites as final." My check: s01 now `d6a2868d…` vs scr6's `4239ecec…` (drift real); s08 `e6c63361…` matches its citers. This affects any claim of the form "sha-pinned landed bytes" written before 16:43.

## Positive discipline observed (spot examples)

- `D1:256` explicitly refuses to state an inference: "the per-token values would be inference, so I do not state [them]".
- `ver5:16-17` declares "[I] (inference) / [U] (unknown)" and labels to them; `ver14:156-160` carries a full observation/inference/unknown ledger.
- `E17:61-76` pairs the static census (`offy` 0 reads) with a runtime leg (`diff` of two launches → byte-identical) and mutant rejection, rather than asserting the census alone.
- `mut3:135-137` and `mut2:165` disclose fixture churn / in-flight revisions at the time of their runs instead of presenting stale bytes as final.
- `E1:56-57` records a wrong first guess and the observed correction, not just the final number.

## Limits

- Verdicts are about **evidence presence and labeling**, not truth. I re-ran only the spot-checks above; I did not re-execute seats' Godot measurements or the battery (hard rule 1).
- Extractor `E-CMD/E-OUT` totals (662/25) are inflated by prose/table restatements; only the vetted flags above are asserted.
- Snapshot is point-in-time (16:45:00). Shards written later are out of scope; `scr4:127` correctly noted this seat was still running at its own 16:43 write.
- No shared files were edited; this shard is the only repo file written by SENT-2.
