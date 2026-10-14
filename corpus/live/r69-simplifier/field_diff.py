import json, sys
def rows(p):
    d = json.load(open(p))
    return {r.get("case", f"row{i}"): r for i, r in enumerate(d["results"])}
a, b = rows(sys.argv[1]), rows(sys.argv[2])
shared = sorted(set(a) & set(b))
print(f"shared={len(shared)}, new_only={sorted(set(b)-set(a))}, base_only={sorted(set(a)-set(b))}")
diffs = [k for k in shared if a[k].get("verdict") != b[k].get("verdict")]
print("verdict_diffs:", diffs)
