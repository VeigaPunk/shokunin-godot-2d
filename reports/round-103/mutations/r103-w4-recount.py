#!/usr/bin/env python3
"""r103-W4 independent recount: fresh census of r102 verdicts.json vs the stored
reports/round-103/mutations/r103-w4-census.json (multi-PASS allowlist baseline).

Independence from r103-w4-census.py:
  - PASS matcher here is `startswith("PASS")` (loose) AND `re.match(r'^PASS\\b')` (strict);
    the census script used a single regex `^PASS(\\b|$|[:=])`. Equality of the three
    matchers on this data is asserted, not assumed.
  - row_index is recomputed by positional scan AND re-derived from case->index map.
  - every stored multi row's pass_lines list is compared element-wise.
Read-only on all inputs; writes nothing except stdout.
"""
import json, re, hashlib, sys

RUNS = [("run1", "corpus/live/runs/20261018T212500022987Z/verdicts.json"),
        ("run2", "corpus/live/runs/20261018T213443471189Z/verdicts.json")]
STORED = "reports/round-103/mutations/r103-w4-census.json"
RE_STRICT = re.compile(r"^PASS\b")
RE_CENSUS = re.compile(r"^PASS(\b|$|[:=])")

fails = []
def check(name, ok, detail=""):
    print(f"{'OK  ' if ok else 'FAIL'} {name}" + (f" :: {detail}" if detail else ""))
    if not ok:
        fails.append(name)

stored = json.load(open(STORED))
print(f"stored {STORED} sha256={hashlib.sha256(open(STORED,'rb').read()).hexdigest()}")

for key, path in RUNS:
    raw = open(path, "rb").read()
    print(f"\n=== {key} {path}")
    print(f"    bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()}")
    j = json.loads(raw)
    res = j["results"]
    check(f"{key}: rows==554", len(res) == 554, f"n={len(res)}")
    check(f"{key}: all verdict PASS", {r.get("verdict") for r in res} == {"PASS"})
    check(f"{key}: top-level verdict PASS", j.get("verdict") == "PASS", repr(j.get("verdict")))

    cases = [r.get("case") for r in res]
    check(f"{key}: distinct cases == rows (keys usable)", len(set(cases)) == len(cases))
    cmap = {c: i for i, c in enumerate(cases)}

    multi_loose, multi_strict, multi_census = {}, {}, {}
    n_out = n_zero = 0
    for i, r in enumerate(res):
        out = r.get("output")
        if out is None:
            continue
        n_out += 1
        ls = out if isinstance(out, list) else str(out).splitlines()
        pl = [x for x in ls if x.startswith("PASS")]
        ps = [x for x in ls if RE_STRICT.match(x)]
        pc = [x for x in ls if RE_CENSUS.match(x)]
        if pl != ps or ps != pc:
            check(f"{key}: matcher agreement row {i} ({r.get('case')})", False,
                  f"loose={len(pl)} strict={len(ps)} census={len(pc)}")
        if not pl:
            n_zero += 1
        if len(pl) > 1:
            multi_loose[r.get("case")] = pl
            multi_strict[r.get("case")] = ps
            multi_census[r.get("case")] = pc

    check(f"{key}: rows_with_output == stored", n_out == stored[key]["rows_with_output"],
          f"fresh={n_out} stored={stored[key]['rows_with_output']}")
    check(f"{key}: zero-pass rows == stored", n_zero == stored[key]["rows_zero_pass"],
          f"fresh={n_zero} stored={stored[key]['rows_zero_pass']}")
    check(f"{key}: matchers identical sets",
          set(multi_loose) == set(multi_strict) == set(multi_census))
    check(f"{key}: multi count == stored", len(multi_census) == stored[key]["multi_count"],
          f"fresh={len(multi_census)} stored={stored[key]['multi_count']}")

    # structural compare against stored multi list (order + counts + lines + row_index)
    s_multi = stored[key]["multi"]
    s_cases = [m["case"] for m in s_multi]
    check(f"{key}: multi order identical", s_cases == list(multi_census))
    for m in s_multi:
        c = m["case"]
        fresh = multi_census.get(c)
        check(f"{key}: {c} pass_lines elementwise", fresh == m["pass_lines"],
              "" if fresh == m["pass_lines"] else f"stored={m['pass_lines']} fresh={fresh}")
        check(f"{key}: {c} count", m["count"] == len(m["pass_lines"]),
              f"count={m['count']} len={len(m['pass_lines'])}")
        check(f"{key}: {c} row_index", m["row_index"] == cmap[c],
              f"stored={m['row_index']} fresh={cmap[c]}")
        check(f"{key}: {c} verdict PASS", m["verdict"] == "PASS")
        check(f"{key}: {c} has_raw_output False", m["has_raw_output"] is False)

    total = sum(1 for r in res if r.get("output") is not None
                for x in (r["output"] if isinstance(r["output"], list) else str(r["output"]).splitlines())
                if x.startswith("PASS"))
    stored_total = stored[key]["shape_first_tokens"].get("PASS")
    check(f"{key}: total PASS-lines == stored", total == stored_total,
          f"fresh={total} stored={stored_total}")

    # identity: set of multi cases + their line counts, expressed as a fingerprint
    fp = hashlib.sha256("\n".join(
        f"{c}\t{len(multi_census[c])}\t{'|'.join(multi_census[c])}"
        for c in sorted(multi_census)).encode()).hexdigest()
    print(f"    multi-set fingerprint sha256={fp}")

    if key == "run1":
        r1_cases = list(multi_census)
    else:
        check("cross-run: multi case sets identical", r1_cases == list(multi_census))
        check("cross-run: multi pass_lines byte-identical",
              all(stored["run1"]["multi"][i]["pass_lines"] == m["pass_lines"]
                  for i, m in enumerate(stored["run2"]["multi"])))

# cross-run: row order alignment (strictness note: compare cases positionally)
a = json.load(open(RUNS[0][1]))["results"]
b = json.load(open(RUNS[1][1]))["results"]
mis = [i for i, (x, y) in enumerate(zip(a, b)) if x.get("case") != y.get("case")]
check("cross-run: case order 554/554 aligned", not mis, f"mismatch idx={mis[:5]}")

# counts digest of the 19 allowlist rows (for the shard table)
print("\nallowlist (fresh, run1): case nPASS first-two-tokens")
for c in r1_cases:
    pl = next(m["pass_lines"] for m in stored["run1"]["multi"] if m["case"] == c)
    tags = {}
    for ln in pl:
        t = " ".join(ln.split()[:2])
        tags[t] = tags.get(t, 0) + 1
    print(f"  {c:34s} {len(pl):2d}  {tags}")

print(f"\nTOTAL CHECKS FAILED: {len(fails)} {fails}")
sys.exit(1 if fails else 0)
