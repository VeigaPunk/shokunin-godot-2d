#!/bin/sh
# r105 counting commands — run from the lane root; $1 = git rev (default HEAD)
R=${1:-HEAD}
echo "== rev $(git rev-parse --short "$R")"
echo "-- C1 coverage: res_uid CASES rows / total CASES (AST)"
git show "$R:corpus/fixtures/run_battery.py" | python3 -c "import ast,sys;t=ast.parse(sys.stdin.read());c=[n.value.elts for n in ast.walk(t) if isinstance(n,ast.Assign) and any(getattr(x,'id',None)=='CASES' for x in n.targets) and isinstance(n.value,ast.List)][0];print('res_uid',sum(e.elts[0].value.startswith('res_uid_') for e in c),'r105',sum(e.elts[0].value.startswith('r105_') for e in c),'total',len(c))"
echo "-- C2 calibration: QUALITY criteria / inherited baseline / lesson-derived criteria / mapped rows"
python3 reports/round-105/r105-mapped-criteria.py "$R"
echo "-- C3 depth: knowledge entries / entries with all 3 headers / SOURCES rows"
git ls-tree --name-only "$R" corpus/knowledge/ | grep -c '\.md$'
for f in $(git ls-tree --name-only "$R" corpus/knowledge/ | grep '\.md$'); do git show "$R:$f" | grep -cE '^(source|verified-at|recheck):' ; done | grep -c '^3$'
git show "$R:corpus/SOURCES.md" 2>/dev/null | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' || true
