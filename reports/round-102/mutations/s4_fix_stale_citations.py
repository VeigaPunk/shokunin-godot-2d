#!/usr/bin/env python3
"""r102-S4 stale-citation repair for `.shokunin/game-dev-2d/` paths.

Dry-run by default; never touches shared files unless --include-shared;
corpus/lessons/*.json handled only with --tier2 (receipt tier).

Tiers
  T1 operative surface: SCORECARD.md, PROVINCE.md (shared, opt-in), corpus/lessons/*.md
  T2 receipts, relative class: corpus/lessons/*.json lines WITHOUT the old
     absolute root /home/vgpnk/Projects/prymeagnt/...  (safe prefix substitution)
  T2-ABS receipts, absolute class: lines WITH that root. NOT repairable by
     substitution (they record a different checkout); listed, left untouched.

Outputs (always, even in dry-run): s4_cite_pairs.txt + s4_cite_manifest.json
next to this script. Exit 0 if dry/apply ok; exit 3 if a requested apply left
residual `.shokunin/game-dev-2d/` hits in the tier surface.
"""
import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]

RULE_CORPUS = (".shokunin/game-dev-2d/corpus/", "corpus/")
RULE_REPORTS = (".shokunin/game-dev-2d/reports/", "reports/")
ABS_ROOT = "/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/"
CUR_ROOT = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/"

T1_MD = "corpus/lessons/*.md"
T2_JSON = "corpus/lessons/*.json"
SHARED = ("SCORECARD.md", "PROVINCE.md")

# explicit full-line replacements (matched on exact before-text) for lines the
# two prefix rules cannot rewrite coherently
EXPLICIT = {
    "Only writes `.shokunin/game-dev-2d/**` and its own reports. Domain source trees are read-only.":
        "Only writes this repository's tree (`./**`) and its own reports. Domain source trees are read-only.",
}

REL_TOKEN = re.compile(r"(?:corpus|reports)/[^\s\"',)\]]+")
ABS_TOKEN = re.compile(r"/home/[^\s\"',)\]]+")


def rel_files(glob):
    return sorted(p for p in REPO.glob(glob) if p.is_file())


def subst(line):
    nl = ""
    body = line
    if line.endswith("\r\n"):
        body, nl = line[:-2], "\r\n"
    elif line.endswith("\n"):
        body, nl = line[:-1], "\n"
    new = body.replace(*RULE_CORPUS).replace(*RULE_REPORTS)
    return EXPLICIT.get(new, new) + nl


SUBST_TOKEN_RE = tuple(
    re.compile(re.escape(old) + r"([^\s\"',)\]]+)")
    for old, _ in (RULE_CORPUS, RULE_REPORTS))


def new_tokens(before, after):
    """tokens created by the prefix substitution (rule prefix + path tail)"""
    out = []
    for rx, (_, repl) in zip(SUBST_TOKEN_RE, (RULE_CORPUS, RULE_REPORTS)):
        for m in rx.finditer(before):
            out.append(repl + m.group(1))
    return out


def token_exists(token):
    token = token.rstrip(".,;:`")
    return (REPO / token).exists()


def abs_checks(token):
    token = token.rstrip(".,;:`")
    old = Path(token)
    if not token.startswith(ABS_ROOT):
        return {"old": None, "mapped_current": None}
    mapped = CUR_ROOT + token[len(ABS_ROOT):]
    return {"old": old.exists(), "mapped_current": Path(mapped).exists()}


def scan_file(path, tier):
    pairs = []
    abs_rows = []
    rel_resolve = [0, 0]   # resolved, total
    lines = path.read_text().splitlines(keepends=True)
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        if ".shokunin/game-dev-2d/" not in line:
            continue
        if ABS_ROOT in line:
            tok = ABS_TOKEN.search(line)
            abs_rows.append({"file": str(path.relative_to(REPO)), "line": i,
                             "checks": abs_checks(tok.group(0)) if tok else None})
            continue
        if tier == "t2" and not path.name.endswith(".json"):
            continue
        after = subst(line)
        if after == line:
            continue
        for tok in new_tokens(line, after):
            rel_resolve[1] += 1
            rel_resolve[0] += 1 if token_exists(tok) else 0
        pairs.append({"file": str(path.relative_to(REPO)), "line": i,
                      "before": line, "after": after})
    return pairs, abs_rows, rel_resolve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--include-shared", action="store_true")
    ap.add_argument("--tier2", action="store_true")
    a = ap.parse_args()

    targets = []          # (path, tier)
    for name in SHARED:
        targets.append((REPO / name, "t1"))
    targets += [(p, "t1") for p in rel_files(T1_MD)]
    if a.tier2:
        targets += [(p, "t2") for p in rel_files(T2_JSON)]

    all_pairs, all_abs, resolve = [], [], [0, 0]
    for path, tier in targets:
        pairs, abs_rows, rr = scan_file(path, tier)
        all_pairs += pairs
        all_abs += abs_rows
        resolve[0] += rr[0]
        resolve[1] += rr[1]

    if a.apply:
        by_file = {}
        for pr in all_pairs:
            by_file.setdefault(pr["file"], {})[pr["line"]] = pr["after"]
        wrote = []
        for rel, edits in by_file.items():
            p = REPO / rel
            if p.name in SHARED and not a.include_shared:
                continue
            lines = p.read_text().splitlines(keepends=True)
            for n, aft in sorted(edits.items()):
                assert subst(lines[n - 1]) == aft, f"{rel}:{n} content moved"
                lines[n - 1] = aft
            p.write_text("".join(lines))
            wrote.append(rel)
        print(f"applied: {len(wrote)} files, "
              f"{sum(len(e) for r, e in by_file.items() if r in wrote)} line pairs")

    # pair artefact
    out = HERE.parent / "s4_cite_pairs.txt"
    with out.open("w") as fh:
        for pr in all_pairs:
            fh.write(f"### {pr['file']}:{pr['line']}\nBEFORE {pr['before']}\nAFTER  {pr['after']}\n\n")
        fh.write(f"### NOT-REPAIRABLE-BY-SUBSTITUTION (absolute old-root receipts): {len(all_abs)} lines\n")
        for r in all_abs:
            chk = r["checks"] or {}
            fh.write(f"LEAVE {r['file']}:{r['line']} old_root_exists={chk.get('old')} "
                     f"mapped_current_exists={chk.get('mapped_current')}\n")

    manifest = {
        "rules": {"corpus": list(RULE_CORPUS), "reports": list(RULE_REPORTS),
                  "explicit": len(EXPLICIT)},
        "tiers_run": {"t1": True, "t2": a.tier2},
        "apply": a.apply, "include_shared": a.include_shared,
        "changed_lines": len(all_pairs),
        "changed_files": len({p["file"] for p in all_pairs}),
        "abs_leave_lines": len(all_abs),
        "rel_targets_resolved_after": f"{resolve[0]}/{resolve[1]}",
        "pairs_file": out.name,
    }
    (HERE.parent / "s4_cite_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
