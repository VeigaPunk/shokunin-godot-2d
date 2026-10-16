#!/usr/bin/env python3
"""r93-scribe receipt census — signature binding + cross-arm collision + law
re-derivation over every committed r93 receipt (scout/boundary/author) plus
this seat's own runs.

Read-only over the committed corpus; writes JSON under
corpus/live/r93-scribe/audit/.
"""
import ast
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LIVE = REPO / "corpus/live"
OUT = REPO / "corpus/live/r93-scribe/audit/receipts_census.json"

src = subprocess.run(["git", "-C", str(REPO), "show",
                      "HEAD:corpus/fixtures/run_battery.py"],
                     capture_output=True, text=True).stdout
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        CASES = ast.literal_eval(node.value)
ROWS = [c for c in CASES if c[0].startswith("r93_")]
BY_CASE = {c[0]: {"fixture": c[1], "arm": c[2][0].split("=", 1)[1],
                  "signature": c[4]} for c in ROWS}


def armkey(fixture, arm):
    return f"{fixture.removesuffix('.gd')}:{arm}"

# ---------------------------------------------------------------- receipts
receipts = []  # (source, arm_key, path, text)


def add(source, arm_key, path, text):
    receipts.append({"source": source, "arm": arm_key,
                     "path": str(path.relative_to(REPO)), "text": text})


# scout canonical + loadtest
for p in sorted((LIVE / "r93-scout/runs").glob("r93_*.rep*.out")):
    cell = p.name.split(".rep")[0][len("r93_"):]
    add("scout", f"anim_lattice:{cell}", p, p.read_text(errors="replace"))
for p in sorted((LIVE / "r93-scout/runs/loadtest").glob("*.out")):
    cell = p.name.split(".rep")[0]
    if cell.startswith("r93_"):
        cell = cell[len("r93_"):]
    add("scout-load", f"anim_lattice:{cell}", p, p.read_text(errors="replace"))
# scout tps120 dirs if any
for d in sorted((LIVE / "r93-scout/runs").iterdir()):
    if d.is_dir() and d.name not in ("loadtest",):
        for p in sorted(d.glob("*.out")):
            cell = p.name.split(".rep")[0]
            if cell.startswith("r93_"):
                cell = cell[len("r93_"):]
            add(f"scout-{d.name}", f"anim_lattice:{cell}", p,
                p.read_text(errors="replace"))

# boundary batches
BOUND_BATCHES = ("q", "l", "f30", "f60", "f120", "f120l", "l32", "p")
for p in sorted((LIVE / "r93-boundary/runs").glob("*.out")):
    stem = p.name.split(".rep")[0]
    if "_" not in stem:
        continue
    batch, cell = stem.split("_", 1)
    if batch not in BOUND_BATCHES:
        continue
    if cell in ("clock", "manual_inv", "frame", "deferred", "purity", "blend"):
        arm_key = f"r93b_anim:{cell}"
    else:
        arm_key = f"anim_lattice:{cell}"
    add(f"boundary-{batch}", arm_key, p, p.read_text(errors="replace"))

# author fresh reps
for p in sorted((LIVE / "r93-author/fresh-reps").glob("*.rep*.out")):
    stem = p.name.split(".rep")[0]
    fixture, arm = stem.split(".", 1)
    add("author-fresh", f"{fixture}:{arm}", p, p.read_text(errors="replace"))

# author battery runs (verdicts.json outputs) + scribe runs
for runset in ("r93-author/runs1", "r93-author/runs2", "r93-author/runs3"):
    for vj in sorted((LIVE / runset).glob("*/verdicts.json")):
        try:
            data = json.loads(vj.read_text())
        except Exception as e:
            print("unreadable", vj, e)
            continue
        rows = data.get("rows") if isinstance(data, dict) else data
        if not isinstance(rows, list):
            continue
        for r in rows:
            if not r.get("case", "").startswith("r93_"):
                continue
            text = "\n".join(r.get("output") or [])
            add(f"author-{vj.parent.name}", f"author-battery:{r['case']}",
                vj.parent / f"row-{r['case']}.json", text)
for runset in ("r93-scribe/battery-runs", "r93-scribe/battery-committed"):
    for vj in sorted((LIVE / runset).glob("*/verdicts.json")):
        try:
            data = json.loads(vj.read_text())
        except Exception as e:
            print("unreadable", vj, e)
            continue
        rows = data.get("rows") if isinstance(data, dict) else data
        if not isinstance(rows, list):
            continue
        for r in rows:
            if not r.get("case", "").startswith("r93_"):
                continue
            text = "\n".join(r.get("output") or [])
            add(f"scribe-{vj.parent.name}", f"author-battery:{r['case']}",
                vj.parent / f"row-{r['case']}.json", text)

report = {"n_receipts": len(receipts),
          "receipts_by_source": {}, "binding": {}, "collisions": {}}
for r in receipts:
    report["receipts_by_source"][r["source"]] = \
        report["receipts_by_source"].get(r["source"], 0) + 1

# ---------------------------------------------------------------- binding
# For each row: the receipts of its own arm (all sources except author-battery
# synthetic rows) must contain the signature verbatim.
arm_receipts = defaultdict(list)
for r in receipts:
    if r["source"].startswith("author-") or r["source"].startswith("scribe-"):
        continue  # battery rows are keyed per case below
    arm_receipts[r["arm"]].append(r)

for case, spec in BY_CASE.items():
    arm = armkey(spec['fixture'], spec['arm'])
    recs = arm_receipts.get(arm, [])
    hits = [r for r in recs if spec["signature"] in r["text"]]
    misses = [r["path"] for r in recs if spec["signature"] not in r["text"]]
    report["binding"][case] = {
        "arm": arm, "receipts": len(recs), "hits": len(hits),
        "misses": misses[:6], "all_hit": len(misses) == 0 and len(recs) > 0}

# ---------------------------------------------------------------- collisions
# every r93 signature against every non-own-arm receipt
sig_index = {case: spec["signature"] for case, spec in BY_CASE.items()}
report["collisions"] = {}
for case, sig in sig_index.items():
    own = armkey(BY_CASE[case]["fixture"], BY_CASE[case]["arm"])
    hits = defaultdict(int)
    for r in receipts:
        if r["source"].startswith(("author-", "scribe-")):
            continue
        if r["arm"] != own and sig in r["text"]:
            hits[r["arm"]] += 1
    if hits:
        report["collisions"][case] = dict(hits)
# also: any OTHER r93 signature contained inside this row's own arm receipts?
report["own_arm_contains_other_signature"] = {}
for case, spec in BY_CASE.items():
    own = armkey(spec["fixture"], spec["arm"])
    recs = arm_receipts.get(own, [])
    others = []
    for other, osig in sig_index.items():
        if other == case or osig == spec["signature"]:
            continue
        if any(osig in r["text"] for r in recs):
            others.append(other)
    if others:
        report["own_arm_contains_other_signature"][case] = others

# ---------------------------------------------------------------- laws
def num(tok):
    return float(tok)

laws = {}

# 1. overshoot: BACK<start, SPRING>end (r93b purity, start scale:y=1.0 end=10.0)
pur = [r for r in receipts if r["arm"] == "r93b_anim:purity"
       and not r["source"].startswith(("author-", "scribe-"))]
ok_back = ok_spr = ok_ela = 0
vals = {"back025": set(), "back050": set(), "spr050": set(), "spr100": set(),
        "ela025": set()}
for r in pur:
    m = re.search(r"overshoot=\[back025=([-\d.e+]+),back050=([-\d.e+]+)\]", r["text"])
    m2 = re.search(r"overshoot2=\[spr050=([-\d.e+]+),spr100=([-\d.e+]+),ela025=([-\d.e+]+)\]", r["text"])
    if not (m and m2):
        continue
    b25, b50 = float(m.group(1)), float(m.group(2))
    s50, s100, e25 = float(m2.group(1)), float(m2.group(2)), float(m2.group(3))
    vals["back025"].add(b25); vals["back050"].add(b50)
    vals["spr050"].add(s50); vals["spr100"].add(s100); vals["ela025"].add(e25)
    ok_back += b25 < 1.0            # below the tween's start value (scale 1.0)
    ok_spr += s50 > 10.0            # above the tween's end value (10.0)
    ok_ela += 0.0 < e25 < 10.0      # elastic undershoot stays inside (start,end)
laws["overshoot"] = {
    "receipts": len(pur), "back025_below_start": ok_back,
    "spr050_above_end": ok_spr, "ela025_inside": ok_ela,
    "distinct_values": {k: sorted(v) for k, v in vals.items()}}

# 2. N-1 await law (r93b frame)
frm = [r for r in receipts if r["arm"] == "r93b_anim:frame"
       and not r["source"].startswith(("author-", "scribe-"))]
x1 = set(); pos10 = set(); applied10 = set(); phys = set(); pd = set()
per_batch = defaultdict(lambda: {"x1": set(), "pos10": set()})
for r in frm:
    m = re.search(r"idle=\[x1=([-\d.e+]+),", r["text"])
    if m:
        x1.add(float(m.group(1)))
    m = re.search(r"pos10=([-\d.e+]+)", r["text"])
    if m:
        pos10.add(float(m.group(1)))
        batch = r["source"].split("boundary-")[-1] if "boundary-" in r["source"] else r["source"]
        per_batch[batch]["pos10"].add(float(m.group(1)))
    m = re.search(r"mixer_applied_10=(\d+)", r["text"])
    if m:
        applied10.add(int(m.group(1)))
    m = re.search(r"phys=\[y1=([-\d.e+]+),y2=([-\d.e+]+),y3=([-\d.e+]+),y6=([-\d.e+]+)\]", r["text"])
    if m:
        phys.add(tuple(float(g) for g in m.groups()))
    m = re.search(r"phys_delta=([-\d.e+]+)", r["text"])
    if m:
        pd.add(float(m.group(1)))
laws["n_minus_1_await"] = {
    "receipts": len(frm), "x1_values": sorted(x1),
    "pos10_values": sorted(pos10), "pos10_per_batch": {k: sorted(v["pos10"]) for k, v in per_batch.items()},
    "mixer_applied_10": sorted(applied10), "phys_lattice": sorted(str(p) for p in phys),
    "phys_delta": sorted(pd),
    "pos10_vs_law": {k: sorted(
        f"pos10={v:.9g} 9*delta=" + (f"{9.0*(1.0/float(k[1:])):.9g} err={abs(v-9.0*(1.0/float(k[1:]))):.3g}"
                                     if k.startswith('f') and k[1:].isdigit() else "?")
        for v in vals["pos10"])
        for k, vals in per_batch.items()}}

# 3. crossfade weight law at three granularities
def parse_array(text, name):
    m = re.search(re.escape(name) + r"=\[([^\]]*)\]", text)
    return [float(x) for x in m.group(1).split(",")] if m else None

blend = [r for r in receipts if r["arm"] in ("anim_lattice:animblend",)
         and not r["source"].startswith(("author-", "scribe-"))]
r93b_blend = [r for r in receipts if r["arm"] == "r93b_anim:blend"
              and not r["source"].startswith(("author-", "scribe-"))]
law_sets = {}
for label, recs, names in (("animblend", blend,
                            ("finished_010", "finished_005", "finished_020")),
                           ("r93b-blend", r93b_blend,
                            ("finished_010", "finished_020"))):
    arrs = {n: set() for n in names}
    for r in recs:
        for n in names:
            a = parse_array(r["text"], n)
            if a:
                arrs[n].add(tuple(a))
    law_sets[label] = {"receipts": len(recs),
                       "arrays": {n: [list(t) for t in sorted(v)] for n, v in arrs.items()}}
# re-derive w_i=(i-1)/(N-1) for each pinned array
rederive = {}
for n, arrs in [("finished_010", law_sets["animblend"]["arrays"]["finished_010"]),
                ("finished_005", law_sets["animblend"]["arrays"]["finished_005"]),
                ("finished_020", law_sets["animblend"]["arrays"]["finished_020"])]:
    for arr in arrs:
        N = len(arr)
        expect = [100.0 + 400.0 * i / (N - 1) for i in range(N)]
        err = max(abs(a - b) for a, b in zip(arr, expect))
        rederive[f"animblend:{n}:N={N}"] = {"max_abs_err_vs_law": err,
                                            "first": arr[0], "last": arr[-1]}
for n, arrs in [("finished_010", law_sets["r93b-blend"]["arrays"]["finished_010"]),
                ("finished_020", law_sets["r93b-blend"]["arrays"]["finished_020"])]:
    for arr in arrs:
        N = len(arr)
        expect = [100.0 + 400.0 * i / (N - 1) for i in range(N)]
        err = max(abs(a - b) for a, b in zip(arr, expect))
        rederive[f"r93b:{n}:N={N}"] = {"max_abs_err_vs_law": err,
                                       "first": arr[0], "last": arr[-1]}
laws["crossfade"] = {"sets": law_sets, "rederived": rederive}

# interleaved == plain
inter = {}
for r in r93b_blend:
    inter[r["path"]] = "interleaved_eq_plain=true" in r["text"]
laws["crossfade"]["interleaved_eq_plain_all"] = all(inter.values())
laws["crossfade"]["interleaved_eq_plain_n"] = sum(inter.values())

# 4. DEFERRED routes (r93b deferred)
dfr = [r for r in receipts if r["arm"] == "r93b_anim:deferred"
       and not r["source"].startswith(("author-", "scribe-"))]
tokens = {"manual_def_after_adv_empty": 0, "next_proc_78": 0,
          "phys_flush_78": 0, "two_adv_queue_then_flush": 0,
          "immediate_in_adv": 0}
for r in dfr:
    t = r["text"]
    tokens["manual_def_after_adv_empty"] += "manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]]" in t
    tokens["next_proc_78"] += "next_proc=[7,8]" in t
    tokens["phys_flush_78"] += "manual_def_phys=[after_adv=[],after_phys=[7,8]]" in t
    tokens["two_adv_queue_then_flush"] += "two_adv=[after=[],flush=[7,8]]" in t
    tokens["immediate_in_adv"] += "immediate=[after_adv=[7,8],after_frame=[7,8]]" in t
laws["deferred"] = {"receipts": len(dfr), **tokens}

# 5. manual clock invariance (r93b manual_inv)
mi = [r for r in receipts if r["arm"] == "r93b_anim:manual_inv"
      and not r["source"].startswith(("author-", "scribe-"))]
inv_all = sum("inv=[paused_proc=true,paused_phys=true,manual_proc=true,manual_phys=true]" in r["text"]
              for r in mi)
step_all = sum("step_exact=[paused025=true,paused_done=true,manual025=true,manual_done=true]" in r["text"]
               for r in mi)
laws["manual_clock"] = {"receipts": len(mi), "inv_all_true": inv_all,
                        "step_exact_all_true": step_all}

report["laws"] = laws

# 6. mode-cell clause constancy (the only pinnable tokens of tweenproc/animproc)
clauses = {
    "anim_lattice:tweenproc": [
        "stable=[auto_advanced=true,paused_frozen=true,phys_advanced=true,manual_exact=true]",
        "phys_manual=[before=1.0,after_step025=2.0]"],
    "anim_lattice:animproc": [
        "stable=[manual_frame_frozen=true,manual_exact=true,speed0_frozen=true,inactive_advance=true,fin_fired=true,caches_once=true,mixer_updated_zero=true]",
        "manual=[x=25.0,after3frames=25.0] frozen=[0.0,true,0.0] inactive=[50.0,true]"],
    "r93b_anim:frame": [
        "mixer_applied_10=10 phys=[y1=0.0,y2=0.0,y3=1.66666674613953,y6=6.66666698455811]",
        "phys_delta=0.01666666666667"],
    "r93b_anim:deferred": [
        "manual_def=[after_adv=[],next_proc=[7,8],second_proc=[7,8]]",
        "manual_def_phys=[after_adv=[],after_phys=[7,8]]",
        "two_adv=[after=[],flush=[7,8]]",
        "immediate=[after_adv=[7,8],after_frame=[7,8]]"],
    "r93b_anim:purity": [
        "overshoot=[back025=0.10286344587803,back050=5.5]",
        "overshoot2=[spr050=10.510157585144,spr100=10.0,ela025=9.11611652374268]"],
    "r93b_anim:manual_inv": [
        "inv=[paused_proc=true,paused_phys=true,manual_proc=true,manual_phys=true]",
        "step_exact=[paused025=true,paused_done=true,manual025=true,manual_done=true]"],
    "r93b_anim:blend": [
        "interleaved_eq_plain=true", "hard_after_frame=500.0"],
}
report["clause_constancy"] = {}
for arm, toks in clauses.items():
    recs = [r for r in receipts if r["arm"] == arm
            and not r["source"].startswith(("author-", "scribe-"))]
    report["clause_constancy"][arm] = {
        "receipts": len(recs),
        "tokens": {t: sum(1 for r in recs if t in r["text"]) for t in toks}}

OUT.write_text(json.dumps(report, indent=1, sort_keys=True))
print(json.dumps({k: v for k, v in report.items() if k != "binding"},
                 indent=1, sort_keys=True)[:6000])
print("...")
print("binding all_hit:", sum(1 for v in report["binding"].values() if v["all_hit"]),
      "/", len(report["binding"]))
for c, v in report["binding"].items():
    if not v["all_hit"]:
        print("MISS", c, v["receipts"], v["hits"], v["misses"])
