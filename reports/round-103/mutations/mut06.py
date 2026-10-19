#!/usr/bin/env python3
"""r103-mut06 (KEY=M6) — fold-regression driver for the 3 landed C3 fold patches.

Question: for each landed fold patch (E1 r97 F6, E2 r99 F2, E3 r100 SP2/SP3),
does the FOLD-REVERTED source (the regression mutant = HEAD bytes) behave
identically to the FOLDED source (the landing candidate) on every row/arm that
can observe it — and does the folded source keep its teeth? A fold whose
revert drifts the classified evidence, or whose folded form stops
discriminating, is a regression.

ACCEPTANCE CONTRACT (fixed before the sweep; every clause is measured):
  A  patch bytes == independent string-derivation bytes (and the published
     line/sha anchors hold).
  B  per probed row/arm, on identical env:
     B1 the row's production classifier verdict is identical across variants
        and True (direct arms with no registered row use the row classifier of
        the row they replicate, or a strict rc/ERROR check when none exists);
     B2 every `k=v` token of the probed PASS line whose value set differs
        between variants is UNSTABLE within at least one variant at the same
        sample size (measured noise floor), or — for a stdout-identical probe —
        the stderr difference is only engine GDScript-backtrace source-line
        citations, byte-equal after normalising `res://…:<N>`, displaced by
        exactly the fold's removed-line count (citations carry no `ERROR:`
        token, so they are not the classified unit).
  C  teeth: a minimal semantic mutant of the FOLDED bytes must (i) drift the
     probed capture and (ii) be observable in the mutant capture — an added
     token present, a removed token absent from a NON-EMPTY capture, or the row
     classifier flipping.
  D  no `k=v` token is single-valued in BOTH variants yet different between
     them, and no token is present on one side only (both would be an
     unattributed fold signal) — subsumed by B2's "every diff key unstable".

Method (never runs run_battery.py; the repo is read-only from here):
  1. stage /var/tmp/r103c-m6/scratch as a battery-faithful copy of
     corpus/fixtures (staging ops mirrored from run_battery.py main(); that
     file is excluded and never executed — the staging anchors assert).
  2. Row contracts (script/flags/expected_exit/signature + the EXPECTED_ERRORS
     allowlist) are AST-extracted from the live battery; battery sha is stored.
  3. Per target: folded bytes = the landed patch applied with patch(1) in a
     throwaway tree, cross-checked against an independent derivation.
  4. Sweep folded vs regression, N reps per probe, stdout/stderr kept separate
     and merged exactly as the production classifier consumes them.
  5. Analysis: token-level comparison of the PASS line(s), timing-noise floor,
     stderr citation attribution, teeth observability, refined verdict.

Receipts: /var/tmp/r103c-m6/receipts/<target>.json (+ summary.json). Raw
captures: /var/tmp/r103c-m6/captures/. Scratch: /var/tmp/r103c-m6 (NOT /tmp:
EDQUOT on this host).

Usage:
  python3 reports/round-103/mutations/mut06.py            # setup + full sweep
  python3 reports/round-103/mutations/mut06.py setup       # staging only
"""

import ast
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURES = REPO / "corpus" / "fixtures"
BATTERY = FIXTURES / "run_battery.py"
MUT = REPO / "reports" / "round-103" / "mutations"
ROOT = Path("/var/tmp/r103c-m6")
SCRATCH = ROOT / "scratch"
CAPTURES = ROOT / "captures"
RECEIPTS = ROOT / "receipts"
APPLY = ROOT / "apply"
TIMEOUT = 30  # every swept row's production bound is 8 s (run_battery.py execute())
CITE_RE = re.compile(r"res://([A-Za-z0-9_./-]+):(\d+)")
TIMING_ALPHABET = set('.,-[] "@usµ%')

TARGETS = [
    {
        "id": "E1-r97-F6-scene_marker",
        "fixture": "r97_scene_marker.gd",
        "patch": "r103-S0-E1-r97-F6-scene_marker.patch",
        "expect_folded_lines": 3,
        "rows": [("stree_lattice_scene_probe", 3)],
        "direct": [],
        "teeth": [
            {
                "name": "export_rename_tag_to_tagx",
                "probe": ("row", "stree_lattice_scene_probe", 1),
                "edit": ('@export var tag := "?"', '@export var tagx := "?"'),
            },
            {
                "name": "liveness_ready_print",
                "probe": ("row", "stree_lattice_scene_probe", 1),
                "edit": (
                    '@export var tag := "?"\n',
                    '@export var tag := "?"\n\n\nfunc _ready() -> void:\n'
                    '\tprint("R103_MUT06_READY_LIVE")\n',
                ),
                "expect_substring": "R103_MUT06_READY_LIVE",
            },
        ],
    },
    {
        "id": "E2-r99-F2-r99b_modes",
        "fixture": "r99b_modes.gd",
        "patch": "r103-S0-E2-r99-F2-r99b_modes.patch",
        "expect_folded_lines": 452,
        "rows": [
            ("r99b_startphase", 5),
            ("r99b_mixfree", 5),
            ("r99b_finfree_played", 5),
        ],
        # `--arm=splitcycle` is the ONLY way to reach the folded site
        # (r99b_modes.gd:91) and NO battery row passes it -> no registered row
        # covers this fold; run it directly under a strict rc/ERROR check.
        "direct": [("splitcycle", ["--arm=splitcycle"], 5, None)],
        "teeth": [
            {
                "name": "splitcycle_label_token",
                "probe": ("direct", "splitcycle", 1),
                "edit": ("changes=%d seq=%s", "changesX=%d seq=%s"),
            }
        ],
    },
    {
        "id": "E3-r100-SP2SP3-r100b_seq",
        "fixture": "r100b_seq.gd",
        "patch": "r103-S0-E3-r100-SP2SP3-r100b_seq.patch",
        "expect_folded_lines": None,  # 785 = HEAD 790 - 5
        "expect_folded_sha_prefix": "e77dc55c",
        "rows": [
            ("r100b_seq_clean", 3),
            ("r100b_seq_noclean", 3),
        ],
        # direct arm: the deleted `--arm=` parse is handed a value. The arm
        # reproduces the r100b_seq_clean transcript, so it is graded with THAT
        # row's production classifier (incl. its allowlisted dummy-renderer
        # ERROR), not with a strict check.
        "direct": [("clean_armflag_cursor", ["--clean=1", "--arm=cursor"], 3, "r100b_seq_clean")],
        "teeth": [
            {
                "name": "seq_arms_drop_census",
                "probe": ("row", "r100b_seq_clean", 1),
                "edit": ("['census', 'routing',", "['routing',"),
            }
        ],
    },
]


# --------------------------------------------------------------------------
# helpers


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path):
    return sha256(p.read_bytes()) if p.is_file() else None


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def run_cmd(cmd, timeout=TIMEOUT):
    env = os.environ.copy()
    for d in ("tmp", "xdg-data", "xdg-cache"):
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    env["TMPDIR"] = str(ROOT / "tmp")
    env["XDG_DATA_HOME"] = str(ROOT / "xdg-data")
    env["XDG_CACHE_HOME"] = str(ROOT / "xdg-cache")
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env)
        stdout = p.stdout.decode("utf-8", "replace")
        stderr = p.stderr.decode("utf-8", "replace")
        rc, error = p.returncode, None
    except subprocess.TimeoutExpired as exc:
        fb, sb = exc.stdout or b"", exc.stderr or b""
        stdout = fb.decode("utf-8", "replace") if isinstance(fb, (bytes, bytearray)) else (fb or "")
        stderr = sb.decode("utf-8", "replace") if isinstance(sb, (bytes, bytearray)) else (sb or "")
        rc, error = None, f"TIMEOUT after {timeout} seconds"
    except OSError as exc:
        stdout, stderr, rc, error = "", str(exc), None, f"launch error: {exc}"
    return {
        "command": " ".join(cmd),
        "rc": rc,
        "error": error,
        "wall_seconds": round(time.monotonic() - t0, 3),
        "stdout": stdout,
        "stderr": stderr,
    }


def write_capture(tag, run):
    CAPTURES.mkdir(parents=True, exist_ok=True)
    (CAPTURES / f"{tag}.out").write_text(run["stdout"])
    (CAPTURES / f"{tag}.err").write_text(run["stderr"])


def capture_record(tag, run):
    merged = run["stdout"] + run["stderr"]
    return {
        "tag": tag,
        "command": run["command"],
        "rc": run["rc"],
        "error": run["error"],
        "wall_seconds": run["wall_seconds"],
        "production_timeout_fits": None if run["error"] else run["wall_seconds"] < 8,
        "stdout_sha256": sha256(run["stdout"].encode()),
        "stderr_sha256": sha256(run["stderr"].encode()),
        "merged_sha256": sha256(merged.encode()),
        "merged_bytes": len(merged.encode()),
        "stdout_bytes": len(run["stdout"].encode()),
        "stderr_bytes": len(run["stderr"].encode()),
        "merged_tail": merged.splitlines()[-3:] if merged.strip() else [],
    }


# --- production classifier, body copied VERBATIM from run_battery.py ---------


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def direct_clean(run):
    """Strict check for direct arms with no row to replicate (mine, not the battery's)."""
    merged = run["stdout"] + run["stderr"]
    return (run["rc"] == 0 and run["error"] is None
            and "SCRIPT ERROR:" not in merged and "Parse Error:" not in merged
            and "ERROR:" not in merged)


# --- battery source contracts (AST, never executed) -------------------------


def battery_contracts():
    tree = ast.parse(BATTERY.read_text())
    cases = None
    expected = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            cases = ast.literal_eval(node.value)
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            if "r100b_seq_clean" in keys:
                expected = ast.literal_eval(node)
    if cases is None or expected is None:
        raise SystemExit("battery contract extraction failed")
    rows = {}
    for r in cases:
        if isinstance(r, (list, tuple)) and len(r) >= 5:
            rows[r[0]] = {
                "name": r[0], "script": r[1], "flags": list(r[2]),
                "expected_exit": r[3], "signature": r[4],
                "allowed_errors": list(r[5]) if len(r) > 5 and isinstance(r[5], (list, tuple)) else [],
            }
    return rows, {k: list(v) for k, v in expected.items()}


# --- staging (mirrors run_battery.py main(); that file is never executed) ---


def stage_scratch():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    copied, skipped = 0, []
    for item in sorted(FIXTURES.iterdir(), key=lambda p: p.name):
        if item.name == "run_battery.py" or item.name.startswith(".") or item.name == "__pycache__":
            skipped.append(item.name)
            continue
        if item.is_dir():
            shutil.copytree(item, SCRATCH / item.name)
        else:
            shutil.copy2(item, SCRATCH / item.name)
        copied += 1
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    project_file = SCRATCH / "project.godot"
    text = project_file.read_text()
    assert 'config/name="MechanicOneShotTest"' in text, "staging drift: app-name anchor"
    project_file.write_text(text.replace('config/name="MechanicOneShotTest"',
                                         f'config/name="MechanicOneShotTest-{stamp}"', 1))
    shutil.copy2(SCRATCH / "controls" / "pickup.tscn", SCRATCH / "pickup.tscn")
    chain = SCRATCH / "causal_chain.gd"
    anchor = "    await process_frame\n    var old := current_scene"
    ctext = chain.read_text()
    assert anchor in ctext, "staging drift: causal_chain anchor"
    chain.write_text(ctext.replace(anchor, "    await process_frame\n    await process_frame\n"
                                  "    var old := current_scene", 1))
    imp = run_cmd(["godot", "--headless", "--path", str(SCRATCH), "--import"], timeout=300)
    info = {"scratch": str(SCRATCH), "copied": copied, "skipped": skipped,
            "import_rc": imp["rc"], "import_tail": (imp["stdout"] + imp["stderr"]).strip().splitlines()[-3:]}
    assert imp["rc"] == 0, f"scratch import failed: {info}"
    return info


# --- fold derivation + patch application ------------------------------------


def derive_folded(fixture, head_bytes):
    text = head_bytes.decode()

    def once(old, new, label):
        nonlocal text
        n = text.count(old)
        assert n == 1, f"{label}: expected 1 occurrence, got {n}"
        text = text.replace(old, new, 1)

    if fixture == "r97_scene_marker.gd":
        once('@export var tag := "?"\nvar ready_ticks := 0\n\nfunc _ready() -> void:\n'
             '\tready_ticks += 1\n', '@export var tag := "?"\n', "E1")
    elif fixture == "r99b_modes.gd":
        once("\tvar pairs: Dictionary = {}\n", "", "E2")
    elif fixture == "r100b_seq.gd":
        once('func _initialize() -> void:\n'
             '\tfor a in OS.get_cmdline_user_args():\n'
             '\t\tif a.begins_with("--arm="):\n'
             '\t\t\tarm = a.substr(6)\n'
             '\tcall_deferred("_run")\n',
             'func _initialize() -> void:\n\tcall_deferred("_run")\n', "SP2")
        once('var arm := ""\n', "", "SP3a")
        once("\t\tarm = a\n\t\tmatch arm:\n", "\t\tmatch a:\n", "SP3b")
    else:
        raise SystemExit(f"no derivation for {fixture}")
    return text.encode()


def apply_patch_bytes(target, head_bytes):
    tree = APPLY / target["fixture"]
    if tree.exists():
        shutil.rmtree(tree)
    dst = tree / "corpus" / "fixtures" / target["fixture"]
    dst.parent.mkdir(parents=True)
    dst.write_bytes(head_bytes)
    patch_file = MUT / target["patch"]
    with open(patch_file) as fh:
        proc = subprocess.run(["patch", "-p1", "-s", "-d", str(tree)],
                              stdin=fh, capture_output=True, text=True)
    assert proc.returncode == 0, f"patch failed: {proc.stdout}{proc.stderr}"
    return dst.read_bytes(), f"patch -p1 -s -d {tree} < {patch_file}"


# --- analysis helpers -------------------------------------------------------


def timing_like(value: str) -> bool:
    return all(c.isdigit() or c in TIMING_ALPHABET for c in value)


def pass_tokens(merged: str):
    toks = {}
    for line in merged.splitlines():
        if line.startswith("PASS "):
            for t in line.split():
                if "=" in t:
                    k, v = t.split("=", 1)
                    toks.setdefault(k, set()).add(v)
    return toks


def words(s: str):
    return set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", s))


def capture_texts(target_id, stage, name):
    """stage ∈ {folded, regression_unfolded, teeth, teeth_control}; rep-ordered."""
    paths = sorted(CAPTURES.glob(f"{target_id}__{stage}__{name}__r*.out"),
                   key=lambda p: int(p.stem.rsplit("r", 1)[1]))
    out = []
    for p in paths:
        e = p.with_suffix(".err")
        out.append({"stdout": p.read_text(), "stderr": e.read_text() if e.is_file() else ""})
    return out


def citation_report(folded_texts, reg_texts, fold_delta):
    """Attributed iff stderr is byte-equal after normalising citations, and every
    citation's line number is displaced by exactly the fold's removed lines."""

    def norm(t):
        return CITE_RE.sub(lambda m: f"res://{m.group(1)}:#", t)

    f_norm = {norm(t) for t in folded_texts}
    r_norm = {norm(t) for t in reg_texts}
    shifts, counts_match = set(), True
    for f, r in zip(sorted(folded_texts), sorted(reg_texts)):
        fc = [int(n) for _p, n in CITE_RE.findall(f)]
        rc = [int(n) for _p, n in CITE_RE.findall(r)]
        if len(fc) != len(rc):
            counts_match = False
            continue
        shifts.update(b - a for a, b in zip(fc, rc))
    no_citations = not shifts
    return {
        "normalized_stderr_identical": f_norm == r_norm,
        "citation_counts_match": counts_match,
        "shifts": sorted(shifts),
        "fold_line_delta": fold_delta,
        "all_shifts_equal_fold_delta": bool(shifts) and shifts == {fold_delta},
        "attributed": f_norm == r_norm and counts_match
                      and (no_citations or shifts == {fold_delta}),
    }


def field_analysis(target_id, comparison_entry, fold_delta):
    probe = comparison_entry["probe"]
    folded = capture_texts(target_id, "folded", probe)
    reg = capture_texts(target_id, "regression_unfolded", probe)
    f_stdout = {sha256(c["stdout"].encode()) for c in folded}
    r_stdout = {sha256(c["stdout"].encode()) for c in reg}
    f_stderr = {sha256(c["stderr"].encode()) for c in folded}
    r_stderr = {sha256(c["stderr"].encode()) for c in reg}
    f_toks, r_toks = {}, {}
    for c in folded:
        for k, vs in pass_tokens(c["stdout"] + c["stderr"]).items():
            f_toks.setdefault(k, set()).update(vs)
    for c in reg:
        for k, vs in pass_tokens(c["stdout"] + c["stderr"]).items():
            r_toks.setdefault(k, set()).update(vs)
    keys = sorted(set(f_toks) | set(r_toks))
    unstable_f = sorted(k for k in keys if len(f_toks.get(k, set())) > 1)
    unstable_r = sorted(k for k in keys if len(r_toks.get(k, set())) > 1)
    unstable_any = set(unstable_f) | set(unstable_r)
    diff_keys = sorted(k for k in keys if f_toks.get(k, set()) != r_toks.get(k, set()))
    disjoint_keys = sorted(k for k in diff_keys
                           if f_toks.get(k, set()).isdisjoint(r_toks.get(k, set())))
    one_sided = sorted(k for k in diff_keys if k not in f_toks or k not in r_toks)
    stable_both = [k for k in keys
                   if len(f_toks.get(k, set())) == 1 and len(r_toks.get(k, set())) == 1]
    stable_diff = sorted(k for k in stable_both if f_toks.get(k) != r_toks.get(k))
    unattributed = sorted(k for k in diff_keys if k not in unstable_any)
    diff_timing_like = all(all(timing_like(v) for v in (f_toks.get(k, set()) | r_toks.get(k, set())))
                           for k in diff_keys)
    noise_attributed = bool(diff_keys) and not unattributed
    return {
        "probe": probe,
        "kind": comparison_entry["kind"],
        "classifier": comparison_entry["classifier"],
        "reps_folded": len(folded),
        "reps_regression": len(reg),
        "stdout_sets_equal": f_stdout == r_stdout,
        "stderr_sets_equal": f_stderr == r_stderr,
        "merged_sets_equal": comparison_entry["byte_identical"],
        "token_keys": len(keys),
        "stable_and_equal_tokens": len([k for k in stable_both if f_toks.get(k) == r_toks.get(k)]),
        "unstable_within_folded": unstable_f,
        "unstable_within_regression": unstable_r,
        "diff_keys": diff_keys,
        "disjoint_keys": disjoint_keys,
        "one_sided_keys": one_sided,
        "stable_separated_between_variants": stable_diff,
        "unattributed_diff_keys": unattributed,
        "diff_keys_all_timing_like": diff_timing_like,
        "noise_attributed": noise_attributed,
        "citation": citation_report([c["stderr"] for c in folded], [c["stderr"] for c in reg],
                                    fold_delta) if f_stderr != r_stderr else None,
        "classify_folded": comparison_entry["folded_evidence"],
        "classify_regression": comparison_entry["regression_evidence"],
        "rc_folded": comparison_entry["rc_set_folded"],
        "rc_regression": comparison_entry["rc_set_regression"],
    }


def teeth_observability(tooth, captures_control, captures_mutant, control_cls, mutant_cls):
    old_edit, new_edit = tooth["edit"]
    added = words(new_edit) - words(old_edit)
    removed = words(old_edit) - words(new_edit)
    control_text = "".join(c["stdout"] for c in captures_control)
    mutant_text = "".join(c["stdout"] + c["stderr"] for c in captures_mutant)
    non_empty = bool(mutant_text.strip())
    checks = []
    for tok in sorted(added):
        checks.append({"token": tok, "expect": "present",
                       "action": "present_not_in_control" if tok not in control_text else "unverified",
                       "observed": tok in mutant_text and tok not in control_text})
    for tok in sorted(removed):
        # non-vacuity guard: 'absent' only counts against a NON-EMPTY capture
        checks.append({"token": tok, "expect": "absent",
                       "action": "absent_but_in_control" if tok in control_text else "unverified",
                       "observed": non_empty and tok not in mutant_text and tok in control_text})
    token_channel = non_empty and any(c["observed"] for c in checks)
    flip = bool(control_cls) and all(control_cls) and not any(mutant_cls)
    return {"added_words": sorted(added), "removed_words": sorted(removed),
            "checks": checks,
            "mutant_captures": len(captures_mutant),
            "mutant_capture_non_empty": non_empty,
            "classifier_flip": flip,
            "observable": token_channel or flip,
            "observable_channel": ("token:" + ",".join(c["token"] for c in checks if c["observed"]))
            if token_channel else ("classifier_flip" if flip else "none")}


# --- sweep ------------------------------------------------------------------


def sweep_target(target, rows, expected_errors):
    fixture = target["fixture"]
    head_bytes = (FIXTURES / fixture).read_bytes()
    folded_bytes = derive_folded(fixture, head_bytes)
    patched_bytes, patch_cmd = apply_patch_bytes(target, head_bytes)

    fold_delta = len(head_bytes.decode().splitlines()) - len(folded_bytes.decode().splitlines())
    patch_derivation_identical = patched_bytes == folded_bytes
    folded_lines = len(folded_bytes.decode().splitlines())
    head_lines = len(head_bytes.decode().splitlines())
    if target.get("expect_folded_lines") is not None:
        assert folded_lines == target["expect_folded_lines"], \
            f"{fixture}: folded lines {folded_lines} != {target['expect_folded_lines']}"
    if target.get("expect_folded_sha_prefix"):
        assert sha256(folded_bytes).startswith(target["expect_folded_sha_prefix"]), \
            f"{fixture}: folded sha {sha256(folded_bytes)[:8]} != {target['expect_folded_sha_prefix']}"

    run_plan = []
    for row_name, reps in target["rows"]:
        spec = rows[row_name]
        run_plan.append({"kind": "row", "probe": row_name, "script": spec["script"],
                         "flags": spec["flags"], "reps": reps, "spec": spec,
                         "classifier": f"production:{row_name}"})
    for name, flags, reps, classify_as in target["direct"]:
        spec = rows[classify_as] if classify_as else None
        run_plan.append({"kind": "direct", "probe": name, "script": fixture, "flags": flags,
                         "reps": reps, "spec": spec,
                         "classifier": f"production:{classify_as}" if classify_as else "strict:direct_clean"})

    def grade(item, run):
        if item["spec"] is not None:
            allowed = list(expected_errors.get(item["spec"]["name"], ()))
            return classify_process(run["rc"], run["error"], run["stdout"] + run["stderr"],
                                    item["spec"]["expected_exit"], item["spec"]["signature"], allowed)
        return direct_clean(run)

    variants = {"folded": folded_bytes, "regression_unfolded": head_bytes}
    measurements, by_probe = [], {}
    for variant, data in variants.items():
        (SCRATCH / fixture).write_bytes(data)
        for item in run_plan:
            for rep in range(1, item["reps"] + 1):
                cmd = ["godot", "--headless", "--path", str(SCRATCH),
                       "--script", "res://" + item["script"], "--", *item["flags"]]
                tag = f"{target['id']}__{variant}__{item['probe']}__r{rep}"
                run = run_cmd(cmd)
                write_capture(tag, run)
                rec = capture_record(tag, run)
                rec.update({"variant": variant, "probe": item["probe"], "kind": item["kind"],
                            "rep": rep, "flags": item["flags"],
                            "evidence": grade(item, run)})
                measurements.append(rec)
                by_probe.setdefault(item["probe"], {}).setdefault(variant, []).append(rec)
                print(f"  [{target['id']}] {variant:20s} {item['probe']:26s} r{rep} rc={run['rc']} "
                      f"wall={run['wall_seconds']}s evidence={rec['evidence']} "
                      f"stdout={rec['stdout_sha256'][:12]} merged={rec['merged_sha256'][:12]}", flush=True)

    comparison = []
    for item in run_plan:
        probe = item["probe"]
        arms = by_probe[probe]
        folded_shas = [m["merged_sha256"] for m in arms["folded"]]
        reg_shas = [m["merged_sha256"] for m in arms["regression_unfolded"]]
        comparison.append({
            "probe": probe,
            "kind": item["kind"],
            "classifier": item["classifier"],
            "reps": item["reps"],
            "folded_shas": folded_shas,
            "regression_shas": reg_shas,
            "within_folded_distinct": len(set(folded_shas)),
            "within_regression_distinct": len(set(reg_shas)),
            "byte_identical": set(folded_shas) == set(reg_shas),
            "strict_per_rep_identical": folded_shas == reg_shas,
            "folded_evidence": sorted({m["evidence"] for m in arms["folded"]}, key=str),
            "regression_evidence": sorted({m["evidence"] for m in arms["regression_unfolded"]}, key=str),
            "rc_set_folded": sorted({str(m["rc"]) for m in arms["folded"]}),
            "rc_set_regression": sorted({str(m["rc"]) for m in arms["regression_unfolded"]}),
            "max_wall_seconds": max(m["wall_seconds"] for m in arms["folded"] + arms["regression_unfolded"]),
            "mean_wall_seconds": round(sum(m["wall_seconds"] for m in arms["folded"] + arms["regression_unfolded"])
                                       / (len(arms["folded"]) + len(arms["regression_unfolded"])), 3),
            "production_timeout_fits": all(m["production_timeout_fits"] is not False
                                           for m in arms["folded"] + arms["regression_unfolded"]),
        })

    analysis = [field_analysis(target["id"], c, fold_delta) for c in comparison]

    # --- teeth: minimal semantic mutant of the FOLDED bytes -----------------
    teeth_results = []
    for tooth in target["teeth"]:
        old, new = tooth["edit"]
        n = folded_bytes.decode().count(old)
        mutant = folded_bytes.decode().replace(old, new, 1).encode() if n == 1 else None
        kind, probe, reps = tooth["probe"]
        item = next(i for i in run_plan if i["probe"] == probe)
        cmd = ["godot", "--headless", "--path", str(SCRATCH), "--script",
               "res://" + item["script"], "--", *item["flags"]]
        ctrl_recs, mut_recs, ctrl_cls, mut_cls = [], [], [], []
        for rep in range(1, reps + 1):
            (SCRATCH / fixture).write_bytes(folded_bytes)
            run = run_cmd(cmd)
            tag = f"{target['id']}__teeth_control__{tooth['name']}__r{rep}"
            write_capture(tag, run)
            ctrl_recs.append(capture_record(tag, run))
            ctrl_cls.append(grade(item, run))
            if mutant is not None:
                (SCRATCH / fixture).write_bytes(mutant)
                run_m = run_cmd(cmd)
                tag_m = f"{target['id']}__teeth__{tooth['name']}__r{rep}"
                write_capture(tag_m, run_m)
                mut_recs.append(capture_record(tag_m, run_m))
                mut_cls.append(grade(item, run_m))
        ctrl_shas = {c["merged_sha256"] for c in ctrl_recs}
        mut_shas = {m["merged_sha256"] for m in mut_recs}
        obs = teeth_observability(tooth,
                                  capture_texts(target["id"], "teeth_control", tooth["name"]),
                                  capture_texts(target["id"], "teeth", tooth["name"]),
                                  ctrl_cls, mut_cls)
        entry = {
            "name": tooth["name"],
            "edit": {"old": old, "new": new, "occurrences_at_head": n},
            "applied": mutant is not None,
            "probe": probe,
            "control_shas": sorted(ctrl_shas),
            "mutant_shas": sorted(mut_shas),
            "teeth_detected_byte_drift": bool(mut_shas) and mut_shas != ctrl_shas,
            "control_classify": ctrl_cls,
            "mutant_classify": mut_cls,
            "observability": obs,
            "teeth_fire": bool(mut_shas) and mut_shas != ctrl_shas and obs["observable"],
        }
        teeth_results.append(entry)
        print(f"  [{target['id']}] teeth {tooth['name']}: drift="
              f"{entry['teeth_detected_byte_drift']} observable={obs['observable']} "
              f"channel={obs['observable_channel']} cls={ctrl_cls}->{mut_cls}", flush=True)

    liveness = []
    for tooth in target["teeth"]:
        if "expect_substring" not in tooth:
            continue
        needle = tooth["expect_substring"]
        mut = capture_texts(target["id"], "teeth", tooth["name"])
        seen = sum(1 for c in mut if needle in c["stdout"] + c["stderr"])
        liveness.append({"needle": needle, "tooth": tooth["name"], "mutant_runs": len(mut),
                         "observed_in_mutant_captures": seen, "observed": seen > 0})

    (SCRATCH / fixture).write_bytes(head_bytes)
    result = {
        "target": target["id"], "fixture": fixture, "patch": target["patch"],
        "patch_command": patch_cmd,
        "head_sha256": sha256(head_bytes), "folded_sha256": sha256(folded_bytes),
        "head_lines": head_lines, "folded_lines": folded_lines, "fold_line_delta": fold_delta,
        "patch_derivation_identical": patch_derivation_identical,
        "comparison": comparison, "analysis": analysis, "teeth": teeth_results,
        "liveness": liveness, "measurements": measurements,
    }
    result["refined_verdict"], result["refined_problems"] = refined(result, analysis)
    return result


def refined(result, analysis):
    problems = []
    if not result["patch_derivation_identical"]:
        problems.append("A: patch bytes != independent derivation")
    for a in analysis:
        if a["classify_folded"] != [True] or a["classify_regression"] != [True]:
            problems.append(f"B1: {a['probe']} classifier not True in both variants "
                            f"(folded={a['classify_folded']} regression={a['classify_regression']})")
        if a["merged_sets_equal"]:
            continue
        if a["stdout_sets_equal"] and a["citation"] and a["citation"]["attributed"]:
            continue  # B2b: stderr differs only by fold-displaced line citations
        if a["noise_attributed"]:
            continue  # B2a: every diff token is unstable within a variant (noise floor)
        problems.append(f"B2: {a['probe']} transcript difference NOT attributed "
                        f"(stdout_equal={a['stdout_sets_equal']}, diff_keys={a['diff_keys']}, "
                        f"unattributed={a['unattributed_diff_keys']}, citation="
                        f"{a['citation'] and a['citation']['attributed']})")
    for a in analysis:
        if a["stable_separated_between_variants"]:
            problems.append(f"D: {a['probe']} stable-separated tokens "
                            f"{a['stable_separated_between_variants']}")
    for t in result["teeth"]:
        if not t["teeth_fire"]:
            problems.append(f"C: teeth {t['name']} (drift={t['teeth_detected_byte_drift']}, "
                            f"observable={t['observability']['observable']}, "
                            f"channel={t['observability']['observable_channel']})")
    if result["liveness"] and not all(l["observed"] for l in result["liveness"]):
        problems.append("C: liveness probe not observed in mutant captures")
    return ("PASS" if not problems else "FAIL"), problems


def main():
    t_start = time.monotonic()
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        print(json.dumps(stage_scratch(), indent=2))
        return 0
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    rows, expected_errors = battery_contracts()
    host = {"uptime": subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(),
            "loadavg": list(os.getloadavg()),
            "godot": subprocess.run(["godot", "--version"], capture_output=True, text=True).stdout.strip(),
            "head": head, "started": now_iso(),
            "env": "XDG_DATA_HOME/XDG_CACHE_HOME/TMPDIR redirected into scratch for every run; "
                   "both variants run under the identical env, so comparisons are unaffected"}
    staged = stage_scratch()
    summary = {"seat": "r103-mut6 (KEY=M6)", "date": "2026-10-18", "host": host, "staging": staged,
               "battery_sha256": sha256_file(BATTERY), "battery_bytes": BATTERY.stat().st_size,
               "rows_extracted": len(rows), "expected_error_rows": len(expected_errors),
               "acceptance": "A patch==derivation; B1 classifier identical+True; B2 every diff token "
                             "unstable within a variant or stderr differences = citations displaced by "
                             "the fold delta; C teeth fire+observable (non-vacuity guarded); D no "
                             "stable-separated token",
               "targets": []}
    for target in TARGETS:
        print(f"[{target['id']}] sweeping...", flush=True)
        result = sweep_target(target, rows, expected_errors)
        summary["targets"].append(result)
        (RECEIPTS / f"{target['id']}.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"[{target['id']}] refined_verdict={result['refined_verdict']} "
              f"problems={result['refined_problems']}", flush=True)
    summary["verdict"] = "PASS" if all(t["refined_verdict"] == "PASS" for t in summary["targets"]) else "FAIL"
    summary["replay_seconds"] = round(time.monotonic() - t_start, 1)
    summary["finished"] = now_iso()
    (RECEIPTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"verdict": summary["verdict"], "seconds": summary["replay_seconds"],
                      "per_target": [{"target": t["target"], "verdict": t["refined_verdict"],
                                      "problems": t["refined_problems"],
                                      "folded_sha256": t["folded_sha256"],
                                      "head_sha256": t["head_sha256"],
                                      "patch_derivation_identical": t["patch_derivation_identical"],
                                      "probes": [{"probe": a["probe"], "classifier": a["classifier"],
                                                  "stdout_sets_equal": a["stdout_sets_equal"],
                                                  "stderr_sets_equal": a["stderr_sets_equal"],
                                                  "diff_keys": a["diff_keys"],
                                                  "unattributed": a["unattributed_diff_keys"],
                                                  "noise_attributed": a["noise_attributed"],
                                                  "citation_attributed": bool(a["citation"]
                                                                              and a["citation"]["attributed"]),
                                                  "citation_shifts": a["citation"]["shifts"] if a["citation"] else None,
                                                  "stable_separated": a["stable_separated_between_variants"],
                                                  "folded_stdout_shas": sorted({sha256(c["stdout"].encode())
                                                                                for c in capture_texts(t["target"], "folded", a["probe"])}),
                                                  "regression_stdout_shas": sorted({sha256(c["stdout"].encode())
                                                                                    for c in capture_texts(t["target"], "regression_unfolded", a["probe"])})}
                                                 for a in t["analysis"]],
                                      "teeth": [{"name": x["name"], "fire": x["teeth_fire"],
                                                 "channel": x["observability"]["observable_channel"]}
                                                for x in t["teeth"]]}
                                     for t in summary["targets"]]}, indent=2))
    return 0 if summary["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
