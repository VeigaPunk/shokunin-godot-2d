#!/usr/bin/env python3
"""r90-scribe author-dossier recompute (read-only).

Checks (all against the committed tree at ee20575 + retained receipts):
  1. CASES tuple count / r90 row inventory / expected_errors r90 entries (AST)
  2. landed rows == emitted author-rows.py.txt block (byte-exact tuples)
  3. per-rep battery verdicts: rows, verdict, r90 pass count, fail classes
  4. rep9 census gate keys + r90 allowlist entries
  5. r90 arms: 6 fresh reps, out/err uniq, rc, pinned-signature hit
  6. fold fields present on every r90 motion row (eng=/tps=/pairing)
"""
import ast
import json
import os
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
AUTHOR = REPO / "corpus/live/r90-author"
BATTERY = pathlib.Path(os.environ.get("R90_BATTERY",
                                      REPO / "corpus/fixtures/run_battery.py"))


def ast_cases():
    tree = ast.parse(BATTERY.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("CASES not found")


def main() -> int:
    cases = ast_cases()
    r90 = [c for c in cases if c[0].startswith("r90_")]
    print(f"1. CASES={len(cases)} r90_rows={len(r90)}")
    for c in r90:
        sig = c[4]
        has_eng = "eng=PhysicsServer2D" in sig
        has_tps = "tps=60" in sig
        pairing = all(k in sig for k in ("cb0_rel=", "obs0_rel=", "pf_delta=", "tick_dh="))
        motion = c[0] not in ("r90_lattice_props", "r90_lattice_comread", "r90_lattice_comrefuse")
        print(f"   {c[0]:26s} eng={has_eng} tps={has_tps} pairing={pairing} motion={motion}")

    txt = (AUTHOR / "author-rows.py.txt").read_text()
    body = "\n".join(l for l in txt.splitlines() if not l.lstrip().startswith("#"))
    ns = {}
    exec("ROWS=[" + body + "]", ns)
    emitted = {c[0]: tuple(c) for c in ns["ROWS"]}
    landed = {c[0]: tuple(c) for c in r90}
    mm = [k for k in set(emitted) | set(landed) if emitted.get(k) != landed.get(k)]
    print(f"2. emitted_rows={len(emitted)} mismatches_vs_landed={mm}")

    print("3. battery reps:")
    total_r90_pass = 0
    for d in sorted(AUTHOR.glob("runs*")):
        if not d.is_dir():
            continue
        for stamp in sorted(p for p in d.iterdir() if p.is_dir()):
            vj = stamp / "verdicts.json"
            if not vj.exists():
                continue
            v = json.loads(vj.read_text())
            res = v["results"]
            fails = [r["case"] for r in res if r["verdict"] != "PASS"]
            r90res = [r for r in res if r["case"].startswith("r90_")]
            npass = sum(1 for r in r90res if r["verdict"] == "PASS")
            total_r90_pass += npass
            print(f"   {d.name}/{stamp.name}: rows={len(res)} verdict={v['verdict']} "
                  f"r90={npass}/{len(r90res)} fails={fails}")
    print(f"   total r90 PASS instances across stamps: {total_r90_pass}")

    rep9 = json.loads((AUTHOR / "runs9/20261015T212551992799Z/verdicts.json").read_text())
    for r in rep9["results"]:
        if r["case"] == "probe_error_clause_surface":
            c = r["census"]
            print(f"4. rep9 census rows_with_expected_errors={c['rows_with_expected_errors']} "
                  f"dead={c['dead_entry_count']}")
            for row in c["rows"]:
                if row["case"].startswith("r90_"):
                    print(f"   {row['case']}: bare_rejects={row['bare_classification_rejects']} "
                          f"allowlisted={row['allowlisted_classification_passes']} "
                          + " ".join(f"{e['entry'][:40]}..x{e['matched_lines']}dead={e['dead_in_run']}"
                                     for e in row["entries"]))

    print("5. fresh-arm reps:")
    for arm in sorted({p.name.split(".rep")[0] for p in (AUTHOR / "runs").glob("*.out")}):
        outs = sorted((AUTHOR / "runs").glob(f"{arm}.rep*.out"))
        errs = sorted((AUTHOR / "runs").glob(f"{arm}.rep*.err"))
        rcs = sorted((AUTHOR / "runs").glob(f"{arm}.rep*.rc"))
        if not outs:
            continue
        sig = None
        for c in r90:
            if c[0].endswith(arm) or c[0].split("_")[-1] == arm:
                sig = c[4]
        hits = sum(1 for o in outs if sig and sig in o.read_text(errors="replace"))
        print(f"   {arm:12s} reps={len(outs)} out_uniq={len({o.read_bytes() for o in outs})} "
              f"err_uniq={len({e.read_bytes() for e in errs})} "
              f"rc={sorted({r.read_text().strip() for r in rcs})} sig_hit={hits}/{len(outs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
