#!/usr/bin/env python3
"""r93 verifier — discrimination matrix for the 23 r93 rows.

For each row: take this seat's fresh receipt for the row's arm, classify it with
the AST-extracted production classify_process (must be True), then mutate the
observed output on the row's own load-bearing tokens and re-classify.  Every
semantic mutation must REJECT; a mutation that still classifies PASS marks a
token that is not actually pinned by the signature.

Also runs the three global rejection axes on every row (rc flip, timeout error,
unrelated ERROR: injection).
"""
import ast
import pathlib
import re
import sys

V = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r93-verifier")
FIX = V / "freeze" / "x" / "corpus" / "fixtures"
src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)

seg = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        break
ns = {"re": re}
exec("import re\n" + seg, ns)  # noqa: S102 - frozen committed source
classify_process = ns["classify_process"]

cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
        break
rows = [ast.literal_eval(e) for e in cases if ast.literal_eval(e)[0].startswith("r93_")]

MUT = {
    "r93_tween_census": ["ap_is_mixer=true", "TYPE_BEZIER=6", "proc=1,"],
    "r93_tween_interp_value": ["clamp_neg=-5.0", "int_050=5", "expo_out_10=10.0"],
    "r93_tween_interp_grid_a": ["lin in=0.0,2.5", "io=0.0,0.15625,5.0"],
    "r93_tween_interp_grid_b": ["io=0.0,-0.99681839346886,5.0", "out=0.0,6.6333669424057"],
    "r93_anim_track_interp": ["two_default_interp=1", "t10=10.0", "bezier_key_count=2"],
    "r93_tween_manual_step": ["step10=[10.0,false,1.0,1,1]", "paused=[5.0,false,true,0.25,0]"],
    "r93_tween_chain": ["seq=[20.0,30.0,40.0]", "cb_at_050=0", "after=[false,false]"],
    "r93_tween_process_stable": ["auto_advanced=true", "manual_exact=true"],
    "r93_tween_phys_manual_step": ["after_step025=2.0"],
    "r93_anim_seek": ["seek_noup=[75.0,0.5]", "manual_frames=[0.0,0.0]"],
    "r93_anim_method_callback": ["deferred_adv=[]", "immediate_adv=[7,8]", "disabled_track=[]"],
    "r93_anim_blend_finished": ["finished_020=[100.0,200.0,300.0,400.0,500.0]",
                                "finished_010=[100.0,144.444442749023"],
    "r93_anim_blend_running": ["after_025=500.0", "default_blend_mid=100.0"],
    "r93_anim_process_manual": ["after3frames=25.0", "frozen=[0.0,true,0.0]"],
    "r93_anim_process_stable": ["caches_once=true", "mixer_updated_zero=true"],
    "r93_anim_overshoot": ["back025=0.10286344587803", "spr050=10.510157585144",
                           "neg=-5.0", "neg_elapsed=-0.5"],
    "r93_anim_manual_clock_interleaved": ["e=10.0]", "m=100.0]"],
    "r93_anim_manual_clock_control": ["unpaused_moved=true", "paused_proc=true"],
    "r93_anim_deferred_flush": ["after_adv=[]", "after_phys=[7,8]"],
    "r93_anim_await_offbyone": [],  # handled as an explicit prefix-pin boundary sweep below
    "r93_anim_physics_tick": ["mixer_applied_10=10", "y6=6.66666698455811"],
    "r93_anim_phys_delta": ["phys_delta=0.01666666666667"],
    "r93_anim_blend_interleaved": ["interleaved_eq_plain=true", "hard_after_frame=500.0"],
}

# The await row pins a PREFIX of the first field (`idle=[x1=0.0` with no
# trailing comma).  Sweep the admitted boundary explicitly: x1 in [0.0,0.1)
# satisfies the prefix, x1 >= 0.1 does not.
SPECIAL = {
    "r93_anim_await_offbyone": [
        ("idle=[x1=0.0,", "idle=[x1=0.01,"),
        ("idle=[x1=0.0,", "idle=[x1=0.05,"),
        ("idle=[x1=0.0,", "idle=[x1=0.099,"),
        ("idle=[x1=0.0,", "idle=[x1=0.1,"),
        ("idle=[x1=0.0,", "idle=[x1=1.0,"),
    ],
}

# mutation replacement: perturb the token's own bytes in a semantics-changing way
def mutate(text, token):
    m = re.search(re.escape(token), text)
    if not m:
        return None
    chunk = m.group(0)
    if "=[]" in chunk:
        new_chunk = chunk.replace("=[]", "=[7,8]", 1)
    elif "true" in chunk or "false" in chunk:
        new_chunk = (chunk.replace("true", "false", 1) if "true" in chunk
                     else chunk.replace("false", "true", 1))
    else:
        nums = list(re.finditer(r"[-0-9]+(?:\.[0-9]+)?", chunk))
        if nums:
            last = nums[-1]
            val = last.group(0)
            newval = f"{float(val) + 1.0!r}" if "." in val else str(int(val) + 1)
            new_chunk = chunk[:last.start()] + newval + chunk[last.end():]
        else:
            new_chunk = chunk + "X"
    return text[:m.start()] + new_chunk + text[m.end():], f"{chunk} => {new_chunk}"


lines = []
admitted = []
rejected = 0
for r in rows:
    name, script, flags, sig = r[0], r[1], r[2], r[4]
    stem, arm = script[:-3], flags[0].split("=", 1)[1]
    out = (V / "arms" / f"{stem}.{arm}.rep1.out").read_text()
    err = (V / "arms" / f"{stem}.{arm}.rep1.err").read_text()
    merged = out + err
    assert classify_process(0, None, merged, r[3], sig, ()) is True, f"baseline not PASS: {name}"
    lines.append(f"{name}: baseline PASS (receipt {stem}.{arm}.rep1)")
    for token in MUT.get(name, []):
        res = mutate(merged, token)
        if res is None:
            lines.append(f"  !! token not found in observed output: {token}")
            continue
        mutated, label = res
        v = classify_process(0, None, mutated, r[3], sig, ())
        if v:
            admitted.append((name, label))
            lines.append(f"  ADMITTED {label}")
        else:
            rejected += 1
            lines.append(f"  rejected {label}")
    for old, repl in SPECIAL.get(name, []):
        if old not in merged:
            lines.append(f"  !! special token not found: {old}")
            continue
        mutated = merged.replace(old, repl, 1)
        v = classify_process(0, None, mutated, r[3], sig, ())
        label = f"{old}->{repl}"
        if v:
            admitted.append((name, label))
            lines.append(f"  ADMITTED {label}")
        else:
            rejected += 1
            lines.append(f"  rejected {label}")
    # global axes
    if classify_process(1, None, merged, r[3], sig, ()):
        admitted.append((name, "rc-flip"))
        lines.append("  ADMITTED rc-flip")
    else:
        rejected += 1
        lines.append("  rejected rc-flip")
    if classify_process(None, "TIMEOUT after 8 seconds", merged, r[3], sig, ()):
        admitted.append((name, "timeout"))
        lines.append("  ADMITTED timeout")
    else:
        rejected += 1
        lines.append("  rejected timeout")
    if classify_process(0, None, merged + "\nERROR: unrelated injected diagnostic\n", r[3], sig, ()):
        admitted.append((name, "unrelated-error"))
        lines.append("  ADMITTED unrelated-error")
    else:
        rejected += 1
        lines.append("  rejected unrelated-error")

lines.append("")
lines.append(f"mutations rejected={rejected} admitted={len(admitted)}")
for a in admitted:
    lines.append(f"  ADMITTED {a}")
(V / "probes" / "discrimination.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if not admitted else 1)
