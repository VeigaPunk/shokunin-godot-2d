import ast, json, sys, os
sys.path.insert(0, '/var/tmp/r101-simp3/scripts')
REPO = '/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin'
src = open(f'{REPO}/corpus/fixtures/run_battery.py').read()
tree = ast.parse(src)
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == 'CASES' for t in node.targets):
        cases = ast.literal_eval(node.value)
assert cases is not None
scripts = set(sys.argv[1:])
rows = [[c[0], c[1], c[2]] for c in cases if c[1] in scripts]
os.makedirs('/var/tmp/r101-simp3', exist_ok=True)
json.dump(rows, open('/var/tmp/r101-simp3/rows.json', 'w'), indent=1)
from collections import Counter
print(f"{len(rows)} rows:", dict(Counter(r[1] for r in rows)))
