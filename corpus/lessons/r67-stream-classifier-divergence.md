# R67 — classify_streams ↔ classify_process per-channel divergence map (Godot 4.7.2 headless)

Sources: `reports/round-67/r67-{author,critic,reviewer,scribe,...}.md`;
`corpus/fixtures/run_battery.py` classifiers :160–177 / :179–208,
`run_process` :149–158, `run_process_streams` :2200–2209, meta arm in the
`--probe-stream-attribution` block (commits `d44ba86` work + `9e946c9`
load-bearing `sd_sig_head` pin); `corpus/fixtures/
stream_attribution_probe.gd` `streamdiv_*` byte-placement arms;
author receipt `corpus/live/r67-author/runs/…/stream-attribution-
verdicts.json`; scribe independent receipt `corpus/live/r67-scribe/
stream-verdicts.json` (sha256 `c12f76e352cd…`, 54 real-pipe records,
driver `b54e564a5e5d…`) + landed replay `runs/20261014T095922857280Z/`
(89/89, 20/20 discriminations); critic matrix + e2e receipts under
`corpus/live/r67-critic/`.
Prior lessons extended: `r19-stream-attribution.md` (the pair's origin),
`r66-rejection-clause-surface.md` (merged-clause surface map).

verified-at: 2026-10-14, Godot `4.7.2.stable.arch_linux.ed1daf0bf`,
Python 3.14.7, Linux x86_64; classifier segments byte-identical
worktree↔HEAD (`classify_process 749fa060`, `classify_streams a886968f`);
verdicts driven through `ast.get_source_segment`-extracted production
functions on real captured pipe bytes — never fed strings.

## The asymmetry, precisely

`classify_process` sees one concat blob (`stdout` then `stderr`);
`classify_streams` sees the channels separately. Every divergence is a
clause whose byte-view differs:

- ABSORB side (streams=T, merged=F): stdout is examined ONLY for
  signature-presence and the `SCRIPT ERROR:`/`Parse Error:` blob tokens.
  A stdout `ERROR:` line is invisible — absorbed PASS-shaped, with or
  without a matching allowlist entry.
- STRICT side (merged=T, streams=F): (a) EVERY non-empty stderr line
  must match `allowed_stderr` — non-`ERROR:` chatter (`WARNING:`,
  `STREAM_STDERR:`, banner noise) is verdict-inert under merged but
  rejects under streams; (b) the signature is channel-pinned to stdout —
  a stderr-only signature satisfies merged's blob test, never streams',
  and exempting it in `allowed_stderr` cannot redirect the pin; (c) the
  merged concat's stdout-tail→stderr-head seam fabricates substrings
  (signatures, `ERROR:` lines, blob tokens) present in NEITHER stream —
  merged can be forged to a verdict either way, streams cannot see the
  seam; (d) the structured `chain incomplete` allowlist entry is
  merged-only — `line_allowed` has exact + `,`-prefix shapes only.
- SEAM×ALLOWLIST side (merged=F, streams=T): an allowlisted stderr
  fragment completes a phantom `ERROR:`/`SCRIPT ERROR:` line that exists
  only in the concat — merged rejects the fabrication; streams sees an
  exempted stderr line and accepts.
- AGREE shapes: stderr `ERROR:` rejects under both (same verdict,
  different clause); allowlist absorbs matching stderr lines under both;
  blob tokens reject under both in either stream; exit/error mismatches
  short-circuit first in both.

## Notable pins

- The shipped `--probe-stream-attribution` REJECT arm already diverges:
  `STREAM_STDERR: unrelated attribution diagnostic` has no `ERROR:`
  token → merged=True / streams=False. The divergence was production
  behavior since r19, un-named.
- `line_allowed`'s exact/`,`-prefix matcher (:191–198) is live only for
  `allowed_stderr` — sole caller passes `()`, so it is dead machinery
  until a non-empty allowlist arm exercises it (r66 census: same
  finding).
- Only stdout-tail→stderr-head seam order fabricates in merged; stderr
  bytes always land after all stdout, so the reversed seam cannot.
- Latency bound: the 88-row battery never calls `classify_streams` —
  divergence lives only where a caller captures streams separately.
