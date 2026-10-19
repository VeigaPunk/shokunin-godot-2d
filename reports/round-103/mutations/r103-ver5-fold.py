#!/usr/bin/env python3
"""r103-ver5 — independent verification of S2's r100b SP2/SP3 fold (round 103).

Seat V5. Never runs run_battery.py. Replicates the battery launch shape
(godot --headless --path <proj> --script res://X.gd -- <flags>, 8 s bound,
stdout/stderr captured separately, output = stdout + stderr — the merge the
battery itself uses at every row) and the harness classifier (extracted
verbatim from run_battery.py via AST, `classify_process`).

REWRITE NOTE (V5, round 103 completion pass): the round-103 draft of this file
was never executed. Two defects fixed before first run:
  * scratch path moved to the mandated `/var/tmp/r103c-V5`;
  * the teeth mutant token `c0=(30.0, 14.0)` does not exist in the fixture
    (`grep -c` = 0 — the fixture builds that string at runtime from
    `str(root.get_mouse_position())`), so the draft aborted on its own assert
    before any measurement. Now mutates source tokens that do exist.
Backup of the unrun draft: /var/tmp/r103c-V5/r103-ver5-fold.py.orig

Steps:
 1. Reconstruct the fold INDEPENDENTLY from the r100-simplifier SP2/SP3 spec
    (delete `var arm := ""`, the 3-line `--arm=` parse, the `arm = a` carrier;
    `match arm:` -> `match a:`), asserting the exact deleted lines first.
 2. Byte-identity: my reconstruction vs the post-image of the landed patch
    `reports/round-103/mutations/r103-S0-E3-r100-SP2SP3-r100b_seq.patch`
    (applied by shell into /var/tmp/r103c-V5/wt) vs the `e77dc55c` claim in
    reports/round-100/r100-simplifier.md §5.
 3. Runs: 4 rows x {base, folded} x 2 reps; classify with production pins
    (CASES) + allowlists from run_battery.py; byte-compare stdout; diff stderr.
 4. SP2 dead-arg discrimination: the deleted `--arm=` parse must have been
    inert — `--arm=hover|--arm=cursor` on base and folded must leave stdout
    byte-identical to no-arg, with a positive control that flags DO act.
 5. Teeth: two one-token mutants of the folded fixture (semantic token in the
    pinned cell; the branch expression on the edited line) must FAIL the pin.
 6. Provenance: replay the r101-E12 generator against base (expect the landed
    r101_seqfull.gd digest to reproduce), against folded (expect the SRC_SHA
    tripwire), and with the tripwire bypassed (expect the transform anchors
    SP2/SP3 deleted to break the generator) — plus a static anchor census.
Writes receipts.json to /var/tmp/r103c-V5/.
"""
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
FIX = ROOT / "corpus" / "fixtures"
SCR = pathlib.Path("/var/tmp/r103c-V5")
GODOT = "/usr/bin/godot"
CLAIMED_FOLDED_SHA = "e77dc55c"  # r100-simplifier.md §5 claim (prefix)
E12 = ROOT / "reports" / "round-101" / "mutations" / "r101-E12-gen_seqfull.py"
S0E3 = ROOT / "reports" / "round-103" / "mutations" / "r103-S0-E3-r100-SP2SP3-r100b_seq.patch"


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---------- 1. independent fold (line surgery from the spec) ----------
base_bytes = (FIX / "r100b_seq.gd").read_bytes()
text = base_bytes.decode()
lines = text.split("\n")
def find_line(line):
    hits = [i for i, l in enumerate(lines) if l == line]
    assert len(hits) == 1, (line, hits)
    return hits[0]


def find_block(block):
    hits = [i for i in range(len(lines)) if lines[i:i + len(block)] == block]
    assert len(hits) == 1, (block, hits)
    return hits[0]


# SP2: dead `--arm=` parse in _initialize; SP3: `var arm` decl + `arm = a` carrier
decl = find_line('var arm := ""')
parse3 = find_block(['\tfor a in OS.get_cmdline_user_args():',
                     '\t\tif a.begins_with("--arm="):',
                     '\t\t\tarm = a.substr(6)'])
carrier = find_line('\t\tarm = a')
branch = find_line('\t\tmatch arm:')
# sites must land where the r100-simplifier spec puts them (decl L8, block L76-78, carrier L89)
assert parse3 == decl + 68 and carrier == branch - 1, (decl, parse3, carrier, branch)
drop = {decl, parse3, parse3 + 1, parse3 + 2, carrier}
folded_lines = [l for i, l in enumerate(lines) if i not in drop]
assert len(folded_lines) == len(lines) - 5, (len(folded_lines), len(lines))
shifted = branch - sum(1 for i in drop if i < branch)
assert folded_lines[shifted] == '\t\tmatch arm:', repr(folded_lines[shifted])
folded_lines[shifted] = '\t\tmatch a:'
folded_bytes = "\n".join(folded_lines).encode()

base_sha = sha(base_bytes)
folded_sha = sha(folded_bytes)
del_note = f"base {len(lines)-1} lines -> folded {len(folded_lines)-1} lines (-5)"

# stage trees
for tree in ("base", "folded"):
    (SCR / tree).mkdir(parents=True, exist_ok=True)
(SCR / "base" / "r100b_seq.gd").write_bytes(base_bytes)
(SCR / "folded" / "r100b_seq.gd").write_bytes(folded_bytes)
for extra in ("project.godot", "r101_seqfull.gd"):
    src = FIX / extra
    for tree in ("base", "folded"):
        (SCR / tree / extra).write_bytes(src.read_bytes())

# ---------- 2. landed patch post-image identity (worktree prepared by shell) ----------
wt_fixture = SCR / "wt" / "corpus" / "fixtures" / "r100b_seq.gd"
wt_bytes = wt_fixture.read_bytes() if wt_fixture.is_file() else None
patch_identity = {
    "patch": str(S0E3.relative_to(ROOT)),
    "patch_sha256": sha(S0E3.read_bytes()),
    "worktree": str(SCR / "wt"),
    "post_image_lines": wt_bytes.decode().count("\n") if wt_bytes else None,
    "post_image_sha256": sha(wt_bytes) if wt_bytes else None,
    "equals_my_reconstruction": wt_bytes == folded_bytes if wt_bytes else None,
    "equals_simplifier_e77dc55c_claim": (sha(wt_bytes).startswith(CLAIMED_FOLDED_SHA)
                                        if wt_bytes else None),
    "my_reconstruction_sha256": folded_sha,
}

# ---------- harness extraction (AST; run_battery.py is only read) ----------
harness_src = (FIX / "run_battery.py").read_text()
h_tree = ast.parse(harness_src)

def find_func(name):
    for node in ast.walk(h_tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(harness_src, node)
    sys.exit(f"{name} not found")

ns = {}
exec("import re\n" + find_func("classify_process"), ns)
classify_process = ns["classify_process"]

CASES = None
for node in h_tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        CASES = ast.literal_eval(node.value)
assert CASES, "CASES not found"
rows = {r[0]: r for r in CASES}

expected_errors = None
for node in ast.walk(h_tree):
    if isinstance(node, ast.Dict):
        try:
            d = ast.literal_eval(node)
        except Exception:
            continue
        if isinstance(d, dict) and "r100b_seq_clean" in d:
            expected_errors = d
            break
assert expected_errors is not None, "expected_errors dict not found"

# ---------- 3. runs ----------
def run(tree, script, flags, timeout=8):
    cmd = [GODOT, "--headless", "--path", str(SCR / tree),
           "--script", "res://" + script, "--", *flags]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return {"cmd": " ".join(cmd), "rc": p.returncode,
            "stdout": p.stdout, "stderr": p.stderr, "elapsed": round(time.time() - t0, 3)}


def pin_classify(r, name):
    pinned = rows[name]
    return classify_process(r["rc"], None, r["stdout"] + r["stderr"],
                            pinned[3], pinned[4], expected_errors.get(name, ()))


run_rows = [("r100b_seq_clean", "r100b_seq.gd", ["--clean=1"]),
            ("r100b_seq_noclean", "r100b_seq.gd", ["--clean=0"]),
            ("r101_seqfull_clean", "r101_seqfull.gd", ["--clean=1"]),
            ("r101_seqfull_noclean", "r101_seqfull.gd", ["--clean=0"])]

receipts = {}
for name, script, flags in run_rows:
    for tree in ("base", "folded"):
        for rep in (1, 2):
            r = run(tree, script, flags)
            r["classified"] = pin_classify(r, name)
            r["stdout_sha256"] = sha(r["stdout"].encode())
            r["stderr_sha256"] = sha(r["stderr"].encode())
            r["merged_sha256"] = sha((r["stdout"] + r["stderr"]).encode())
            r["stdout_lines"] = len(r["stdout"].splitlines())
            r["stderr_lines"] = len(r["stderr"].splitlines())
            receipts[f"{name}|{tree}|rep{rep}"] = r

# stderr diff for the seq rows (backtrace line-number class)
def stderr_lines(tree, name):
    return receipts[f"{name}|{tree}|rep1"]["stderr"].splitlines()

stderr_diffs = {}
for name in ("r100b_seq_clean", "r100b_seq_noclean"):
    a = stderr_lines("base", name)
    b = stderr_lines("folded", name)
    stderr_diffs[name] = {"len_base": len(a), "len_folded": len(b),
                          "diff_lines": [(x, y) for x, y in zip(a, b) if x != y]}

# stdout byte-identity base vs folded (both reps, all 4 rows)
stdout_identity = {}
for name, script, flags in run_rows:
    stdout_identity[name] = (
        receipts[f"{name}|base|rep1"]["stdout"] == receipts[f"{name}|folded|rep1"]["stdout"]
        and receipts[f"{name}|base|rep2"]["stdout"] == receipts[f"{name}|folded|rep2"]["stdout"]
        and receipts[f"{name}|base|rep1"]["stdout"] == receipts[f"{name}|base|rep2"]["stdout"]
        and receipts[f"{name}|folded|rep1"]["stdout"] == receipts[f"{name}|folded|rep2"]["stdout"])
    stdout_identity[name + "|rc"] = (receipts[f"{name}|base|rep1"]["rc"]
                                     == receipts[f"{name}|folded|rep1"]["rc"])

# ---------- 4. SP2 dead-arg discrimination ----------
deadarg = {}
for tree in ("base", "folded"):
    no_arm = receipts[f"r100b_seq_clean|{tree}|rep1"]["stdout"]
    for label, flags in (("arm=hover", ["--clean=1", "--arm=hover"]),
                         ("arm=cursor", ["--clean=1", "--arm=cursor"])):
        r = run(tree, "r100b_seq.gd", flags)
        deadarg[f"{tree}|{label}"] = {
            "cmd": r["cmd"], "rc": r["rc"],
            "stdout_sha256": sha(r["stdout"].encode()),
            "identical_to_no_arm": r["stdout"] == no_arm,
            "classified": pin_classify(r, "r100b_seq_clean"),
        }
# positive control: --clean= DOES act on the same binary/row
deadarg["control_clean_flag_changes_stdout"] = (
    receipts["r100b_seq_clean|base|rep1"]["stdout"]
    != receipts["r100b_seq_noclean|base|rep1"]["stdout"])
# no battery row feeds --arm= to either seq fixture
deadarg["battery_rows_passing_arm_to_seq_fixtures"] = [
    r[0] for r in CASES
    if r[1] in ("r100b_seq.gd", "r101_seqfull.gd") and any(f.startswith("--arm") for f in r[2])]

# ---------- 5. teeth: one-token mutants of the folded fixture ----------
teeth = {}
for tag, kind, old, new in (
        # headless DisplayServer does not move the cursor on push_input: this
        # mutant is byte-identical (recorded as an inert control, NOT a teeth)
        ("T1_inert_pushpos", "control", "Vector2(22, 22)", "Vector2(23, 23)"),
        # touch events DO move the headless cursor -> pinned value must break
        ("T2_touch_pos", "teeth", "st.position = Vector2(44, 44)",
         "st.position = Vector2(45, 45)"),
        # the branch expression on the edited line must be pinned by the row
        ("T3_branch_expr", "teeth", "\t\tmatch a:\n", "\t\tmatch a + \"x\":\n")):
    mut = SCR / ("folded_" + tag)
    mut.mkdir(parents=True, exist_ok=True)
    for extra in ("project.godot", "r101_seqfull.gd"):
        (mut / extra).write_bytes((FIX / extra).read_bytes())
    mtext = folded_bytes.decode()
    assert mtext.count(old) == 1, (tag, mtext.count(old))
    (mut / "r100b_seq.gd").write_bytes(mtext.replace(old, new).encode())
    r = run("folded_" + tag, "r100b_seq.gd", ["--clean=1"])
    teeth[tag] = {"kind": kind, "mutant": f"{old!r} -> {new!r}", "cmd": r["cmd"],
                  "rc": r["rc"], "stdout_sha256": sha(r["stdout"].encode()),
                  "classified": pin_classify(r, "r100b_seq_clean"),
                  "stdout_bytes_equal_to_folded": r["stdout"] == receipts["r100b_seq_clean|folded|rep1"]["stdout"],
                  "stdout_tail": r["stdout"].strip().splitlines()[-2:]}
teeth["summary"] = {
    "teeth_all_fail": all(v["classified"] is False for v in teeth.values()
                          if v.get("kind") == "teeth"),
    "inert_controls": [k for k, v in teeth.items() if v.get("kind") == "control"],
}

# ---------- 6. provenance: r101-E12 generator replay + static anchor census ----------
gen_src = E12.read_text()
g_tree = ast.parse(gen_src)
g_anchors = {}
for node in ast.walk(g_tree):  # the anchors are assigned inside main()
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        nm = node.targets[0].id
        if nm.startswith("anchor") or nm == "old_head":
            try:
                g_anchors[nm] = ast.literal_eval(node.value)
            except Exception:
                pass
assert "anchor_members" in g_anchors and "anchor_loop" in g_anchors, sorted(g_anchors)
g_anchors["cell_order_literal"] = "'census', 'routing', 'hover', 'motion', 'localpos', 'cursor', 'clip', 'drag', 'touch', 'subvp', 'warp', 'focus', 'render', 'osmeta'"
src_sha_lit = "4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd"

anchor_census = {k: {"in_base": v in text, "in_folded": v in folded_bytes.decode()}
                 for k, v in g_anchors.items()}


def replay(tree, name, src_text):
    g = SCR / "gen" / tree
    (g / "corpus" / "fixtures").mkdir(parents=True, exist_ok=True)
    (g / "reports" / "round-101" / "mutations").mkdir(parents=True, exist_ok=True)
    (g / "corpus" / "fixtures" / "r100b_seq.gd").write_bytes(
        base_bytes if tree.startswith("base") else folded_bytes)
    (g / "corpus" / "fixtures" / "run_battery.py").write_bytes(harness_src.encode())
    gen_path = g / "reports" / "round-101" / "mutations" / name
    gen_path.write_text(src_text)
    p = subprocess.run(["python3", str(gen_path)], capture_output=True, text=True)
    out_fixture = g / "corpus" / "fixtures" / "r101_seqfull.gd"
    return {"rc": p.returncode, "stdout": p.stdout.strip(),
            "stderr_tail": p.stderr.strip().splitlines()[-4:],
            "out_written": out_fixture.is_file(),
            "out_sha256": sha(out_fixture.read_bytes()) if out_fixture.is_file() else None}


prov = {
    "base": replay("base", "gen.py", gen_src),
    "folded": replay("folded", "gen.py", gen_src),
    "folded_guard_bypassed": replay("folded", "gen_bypass.py",
                                    gen_src.replace(src_sha_lit, folded_sha)),
    "landed_r101_seqfull_sha256": sha((FIX / "r101_seqfull.gd").read_bytes()),
    "generator_src_sha256": sha(gen_src.encode()),
    "anchor_census": anchor_census,
}

result = {
    "host": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
    "godot": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
    "head": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                           capture_output=True, text=True).stdout.strip(),
    "fold": {"base_sha256": base_sha, "folded_sha256": folded_sha, "lines": del_note,
             "claimed_folded_sha_prefix": CLAIMED_FOLDED_SHA,
             "claim_match": folded_sha.startswith(CLAIMED_FOLDED_SHA)},
    "patch_identity": patch_identity,
    "stdout_byte_identity_base_vs_folded": stdout_identity,
    "stderr_diffs": stderr_diffs,
    "receipts": {k: {kk: vv for kk, vv in v.items() if kk not in ("stdout", "stderr")}
                 for k, v in receipts.items()},
    "classify_all": {k: v["classified"] for k, v in receipts.items()},
    "deadarg": deadarg,
    "teeth": teeth,
    "provenance_generator": prov,
}
(SCR / "receipts.json").write_text(json.dumps(result, indent=1))
print(json.dumps({k: result[k] for k in
                  ("host", "godot", "head", "fold", "patch_identity",
                   "stdout_byte_identity_base_vs_folded", "stderr_diffs",
                   "classify_all", "deadarg", "teeth",
                   "provenance_generator")}, indent=1))
print("receipts ->", SCR / "receipts.json")
