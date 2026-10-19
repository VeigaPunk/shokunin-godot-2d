import json,statistics,collections
rows=[json.loads(l) for l in open('census-raw.jsonl')]
ok=[r for r in rows if 'wall_ms' in r]
w=sorted(r['wall_ms'] for r in ok)
print(f"MEASURED ROWS: {len(ok)} of 554 (export-class rows skipped by design: 2)")
print(f"wall_ms  min={w[0]:.0f}  p25={w[len(w)//4]:.0f}  p50={statistics.median(w):.0f}  p75={w[3*len(w)//4]:.0f}  p90={w[int(len(w)*.9)]:.0f}  p99={w[int(len(w)*.99)]:.0f}  max={w[-1]:.0f}  mean={statistics.mean(w):.0f}")
print()
print("ROWS OVER THE 5s MARK:")
over=[r for r in ok if r['wall_ms']>5000]
for r in sorted(over,key=lambda x:-x['wall_ms']):
    print(f"  {r['wall_ms']:8.0f} ms  {r['case']:42s} {r['script']:28s} {r['flags']}")
print(f"  count={len(over)} / {len(ok)}  = {100*len(over)/len(ok):.2f}%")
print()
print("ROWS OVER 3s (meta-probe bound):")
o3=sorted([r for r in ok if r['wall_ms']>3000],key=lambda x:-x['wall_ms'])
for r in o3: print(f"  {r['wall_ms']:8.0f} ms  {r['case']:42s} {r['script']}")
print(f"  count={len(o3)}")
print()
# per-script aggregate
by=collections.defaultdict(list)
for r in ok: by[r['script']].append(r['wall_ms'])
print("TOP SCRIPTS BY TOTAL COST:")
tot=sum(w)
for s,v in sorted(by.items(),key=lambda x:-sum(x[1]))[:12]:
    print(f"  {sum(v):9.0f} ms  n={len(v):3d}  mean={statistics.mean(v):7.0f}  {s}")
print(f"  TOTAL ALL MEASURED = {tot/1000:.1f} s")
