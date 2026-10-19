# r105 seat report — R105Planner (planner)

Verbatim final output of L2 `W2RoundGameDev2d.R105Planner` (round 105, batched swarm; transcript `history://W2RoundGameDev2d.R105Planner` is session-scoped and not evidence — this file is).

---

## Observations — measured at `e8990516`; read-only

- **[OBS] C1:** the CASES AST count is **21** `res_uid_` rows. The in-file r104 comment says “23 … remain green” (`run_battery.py:1756–1762`); the measured base count is 21, so use the L1-declared 21→28 baseline.
- **[OBS] C2:** neither `corpus/QUALITY.md` nor `corpus/lessons/round-105.md` exists at base; the STATE dossier records no mined class captured by a criterion (§4).
- **[OBS] C3:** base has **2** knowledge entries, **0** required header lines, and no `corpus/SOURCES.md`.
- **[OBS]** The base runner exposes no reverse-order option (`run_battery.py:2318–2331`). Reversed-order receipts therefore require an explicit harness mechanism.
- **[OBS]** D3/D4 counts: README map rows 0, Frontier headings 0; PROVINCE Core/Frontier/Adjacent headings 0. D8 counts: `planned: r64` once; Saturation headings twice.
- No Godot or battery verification was run and no files were changed.

## Falsifier checklist

| Claim | Counting command (from lane root) | Before | After threshold | Refuter |
|---|---|---:|---|---|
| **C1 — res_uid row isolation** | Base: `python3 -c 'import ast,subprocess; s=subprocess.check_output(["git","show","e8990516:corpus/fixtures/run_battery.py"],text=True); t=ast.parse(s); c=next(n.value.elts for n in ast.walk(t) if isinstance(n,ast.Assign) and any(getattr(x,"id",None)=="CASES" for x in n.targets) and isinstance(n.value,ast.List)); print(sum(r.elts[0].value.startswith("res_uid_") for r in c))'` → 21. Receipts: `grep -c '^PASS res_uid' <forward.log>` and the same command for `<reverse.log>`. | **21** CASES rows | **≥28 PASS rows in each order**, plus shared-scratch negative control reproducing the Unrecognized-UID failure class. | Either order has <28 green rows; the negative control passes or does not reproduce that failure class; or the “rev…
| **C2 — mistakes captured by QUALITY** | Base: `python3 -c 'import subprocess; r="e8990516"; p=subprocess.check_output(["git","ls-tree","-r","--name-only",r,"--","corpus/QUALITY.md","corpus/lessons/round-105.md"],text=True).splitlines(); print(len(p))'` → 0. After, with `M` rows shaped `| M01 | evidence-pointer | Q01-or-none | fix |`: `python3 -c 'from pathlib import Path; split=lambda p:[x.split(chr(124)) for x in Path(p).read_text().splitlines() if x.startswith(chr(124))]; m=[r for r in split("corpus/lessons/round-105.md") if r[1].strip().startswith("M")]; q=[r for r in split("corpus/QUALITY.md") if r[1].strip().startswith("Q")]; ids={r[1].strip() for r in q}; print(len(m),sum(r[3].strip() in ids for r in m),len(q))'` | **0** files; **0** captured classes…
| **C3 — SOURCES and three knowledge entries** | Base: `python3 -c 'import re,subprocess; r="e8990516"; ps=subprocess.check_output(["git","ls-tree","-r","--name-only",r,"--","corpus/knowledge"],text=True).splitlines(); bs=[subprocess.check_output(["git","show",f"{r}:{p}"],text=True) for p in ps if p.endswith(".md")]; print(len(bs),sum(len(re.findall(r"^(?:source|verified-at|recheck):",b,re.M)) for b in bs),int(subprocess.run(["git","cat-file","-e",f"{r}:corpus/SOURCES.md"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0))'` → `2 0 0`. After: `grep -cE '^[[:space:]]*S[0-9]{3,}[[:space:]]*' corpus/SOURCES.md` is **not** the registry-row census; use the contract census `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`. Co…

C2’s **14/14** threshold is a proposed bar, not an L1-declared number. For C3, the K3 control is not specified in the supplied contract; **[INFERENCE]** define it before execution as an input-omission replay that must fail the declared gameplay invariant. K1’s collision-disabled control and K2’s sidecar-only control are grounded in ART C1 and the r104 lesson/fixture respectively.

## Proposed `SCORECARD.md` `planned:` block for r106

```text
planned: r106
- depth — ART C3 clean-checkout import→export→launch: `clean_checkout_` CASES 0→2 (positive pipeline + missing-preset negative); count with the CASES AST prefix count; gate with serial full-battery receipts and an observed launch of the exported artifact.
- coverage — D3/D4: README family-map rows 0→51, README Frontier 0→1, PROVINCE Core/Frontier/Adjacent headings 0→3; count map rows as `| \`family\` | ...`, plus `grep -c '^## Frontier$' corpus/README.md` and the three PROVINCE heading counts.
- calibration — D8: `planned: r64` 1→0, `planned: r106` 0→1, Saturation headings 2→1; count with `grep -c '^planned: r106' SCORECARD.md` and `grep -c '^## Saturation' SCORECARD.md`.
```

The coverage target’s 51 families is recorded in STATE §3; the current README has no family-map rows. The depth gate is ART C3. The calibration repair is STATE D8.

## Rubric proposal for the L0 question — no scores assigned

Use **q = verified-complete units / eligible units**; apply the same bands separately to each axis: **0** = 0%; **1–2** = 1–20%; **3–4** = 21–40%; **5–6** = 41–60%; **7–8** = 61–80%; **9** = 81–99%; **10** = 100%.

- **Depth units:** entries with all required headers and Claim/Evidence/Decision/Limits, whose recheck command and discriminating negative were actually rerun. Structural census: `python3 -c 'from pathlib import Path; ps=list(Path("corpus/knowledge").glob("*.md")); ok=sum(all(x in p.read_text() for x in ("source: ","verified-at: ","recheck: ","## Claim","## Evidence","## Decision","## Limits")) for p in ps); print(ok,len(ps))'`
- **Coverage units:** CASES script paths represented in the structured README map. Compare intersection/total via an AST census of CASES paths against code-formatted map rows; score only after checking the mapped domain surfaces and frontier.
- **Calibration units:** mined mistake rows whose `captured-by` ID resolves to a QUALITY criterion with a lesson/LOG pointer. Recount M rows and matching Q IDs from `corpus/lessons/round-*.md` and `corpus/QUALITY.md`; spot-check at least one admit and one reject, per LEARNING.md.
- These commands count candidate units; only source-resolving, executed evidence qualifies. This is a proposal, not a claim about current scores.

**Blockers / contract note:** No blocker to this read-only plan. C1 needs a real reverse-order mechanism before its gate is executable. Also, canonical Shokunin `AXES.md` defines `planned` as a *single* next axis-move; treat the three requested r106 lines as candidates for L1 to select from unless that contract is explicitly overridden.

[Some lines truncated to 768 chars. Use agent://W2RoundGameDev2d.R105Planner:raw:14-14 to read line 14 whole; cut lines run to line 16, each read the same way]
