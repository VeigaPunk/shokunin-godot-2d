#!/usr/bin/env python3
"""r92-scribe: nav 2-payload envelope audit over every committed nav receipt.

Recomputes, from receipts on disk only:
  * the two whitelisted payloads of r92_tilemap_nav (AST from HEAD harness)
  * every committed receipt line of the landed nav arm, partitioned into
    payload[0] / payload[1] / neither
  * the single-valuedness of every non-envelope nav field
  * the settled-form (regions_f2) value across all receipts
Sources: corpus/live/r92-scout/runs, r92-boundary/runs, r92-author/fresh-reps,
r92-author/runs{1..5}. Only stdout files are read.
"""
import ast
import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LIVE = REPO / "corpus" / "live"
src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
                     capture_output=True, check=True).stdout.decode()
tree = ast.parse(src)
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
nav = next(c for c in cases if c[0] == "r92_tilemap_nav")
payloads = list(nav[4])
assert len(payloads) == 2, "not an envelope"

LINE = re.compile(r"^PASS tilemap_lattice nav .*$")


def scan(paths):
    hits = []
    for p in paths:
        if p.suffix not in (".out", ""):
            continue
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if LINE.match(line):
                hits.append((p, line))
    return hits


def scan_verdicts(paths):
    hits = []
    for p in paths:
        try:
            data = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data = data.get("results", [])
        if not isinstance(data, list):
            continue
        for rec in data:
            if not isinstance(rec, dict) or rec.get("case") != "r92_tilemap_nav":
                continue
            for line in rec.get("output") or []:
                if LINE.match(line):
                    hits.append((p, line))
    return hits


groups = {
    "scout": scan(sorted((LIVE / "r92-scout" / "runs").rglob("*"))),
    "boundary": scan(sorted((LIVE / "r92-boundary" / "runs").rglob("*"))),
    "author-fresh": scan(sorted((LIVE / "r92-author" / "fresh-reps").glob("*.out"))),
    "author-runs": scan_verdicts(sorted((LIVE / "r92-author").glob("runs*/**/verdicts.json"))),
    "scribe-runs": scan_verdicts(sorted((LIVE / "r92-scribe").glob("battery-runs*/**/verdicts.json"))),
}
summary = {}
allhits = []
for g, hits in groups.items():
    c = {"receipts": len(hits), "payload0": 0, "payload1": 0, "neither": 0,
         "dupes": 0}
    seen = set()
    for p, line in hits:
        allhits.append((g, p, line))
        if line in seen:
            c["dupes"] += 1
        seen.add(line)
        if line == payloads[0]:
            c["payload0"] += 1
        elif line == payloads[1]:
            c["payload1"] += 1
        else:
            c["neither"] += 1
    summary[g] = c

# field-level single-valuedness across every distinct emitted line
fields = {}
distinct = {}
for g, p, line in allhits:
    toks = line.split()
    body = toks[3:]
    distinct.setdefault(line, 0)
    distinct[line] += 1
    for kv in body:
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        fields.setdefault(k, set()).add(v)

payload_diff = []
a, b = payloads[0].split(), payloads[1].split()
for i, (x, y) in enumerate(zip(a, b)):
    if x != y:
        payload_diff.append({"index": i, "payload0": x, "payload1": y})
assert len(a) == len(b), "payload token counts differ"

out = {
    "payload0_sha256_prefix": payloads[0][:80],
    "payload1_sha256_prefix": payloads[1][:80],
    "payload_token_counts": [len(a), len(b)],
    "payload_diff": payload_diff,
    "groups": summary,
    "distinct_lines": {str(k)[:60]: v for k, v in
                       sorted(distinct.items(), key=lambda kv: -kv[1])},
    "distinct_line_count": len(distinct),
    "field_value_sets": {k: sorted(v) for k, v in sorted(fields.items())},
    "multi_valued_fields": {k: sorted(v) for k, v in fields.items() if len(v) > 1},
    "neither_examples": [str(p) + " :: " + l[:120] for g, p, l in allhits
                         if l not in payloads][:5],
}
print(json.dumps(out, indent=1))
(Path(__file__).parent / "nav_envelope.json").write_text(json.dumps(out, indent=1))
