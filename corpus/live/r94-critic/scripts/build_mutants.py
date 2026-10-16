#!/usr/bin/env python3
"""r94-critic mutant builder: patch the frozen committed fixture into mutant proj dirs.

Each mutant gets corpus/live/r94-critic/mutants/<name>/{project.godot,particles_lattice.gd}
plus a mutation.json recording the exact substitution applied.
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = "/tmp/r94crit-frozen/corpus/fixtures/particles_lattice.gd"
PROJ = "/tmp/r94crit-frozen/corpus/fixtures/project.godot"
BASE = open(FIX).read()

CONTAM_OLD_START = "func _arm_cpu_contam() -> void:"
CONTAM_OLD_END = "func _arm_cpu_oneshot_off() -> void:"

CONTAM_NEW = '''func _arm_cpu_contam() -> void:
	# CRITIC MUTANT (r94-critic M1): the never nodes are created in frame 0
	# (add_pf=0) BEFORE the prior emitter, so the first-idle-frame rule
	# predicts they stay clean (fin_delta=-1 n=0). The shipped row pins
	# `ok=true n_never=2` only; if it still PASSes here the row is vacuous.
	var nodes: Array = []
	for label in ["never1", "never2"]:
		var n := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
		root.add_child(n)
		var st := {"fin_ph": -1, "n_fin": 0}
		_watch(n, st)
		n.emitting = false
		nodes.append([label, n, st])
	var pre := _new_cpu({"one_shot": false, "lifetime": 0.5, "amount": 8, "explosiveness": 1.0})
	root.add_child(pre)
	pre.emitting = true
	await _wait_ph(5)
	_free_node(pre)
	var out: Array[String] = []
	for e in nodes:
		var b: int = PH
		while PH < b + 20 and e[2]["fin_ph"] < 0:
			await process_frame
		out.append("%s[fin_delta=%d n=%d]" % [e[0], (int(e[2]["fin_ph"]) - b) if int(e[2]["fin_ph"]) >= 0 else -1, e[2]["n_fin"]])
		_free_node(e[1])
	print("PASS particles_lattice cpu_contam",
		" ok=%s n_never=%d" % [str(out.size() == 2), out.size()],
		" | " + " ".join(out))

'''

MUTANTS = {
    # name: list of (old, new, note)
    "m1_contam_addpf0": [
        (BASE[BASE.index(CONTAM_OLD_START):BASE.index(CONTAM_OLD_END)], CONTAM_NEW,
         "cpu_contam: never nodes created in frame 0 (add_pf=0) before the prior emitter; predicted fin_delta=-1 n=0 (clean)"),
    ],
    "m2_pause_parent_nofreeze": [
        ("	p.visible = false\n", "	p.visible = true  # CRITIC MUTANT: parent lever no longer freezes\n",
         "cpu_pause: parent-visibility lever hides nothing (no freeze); predicted vis_parent fin_after_show=-25"),
    ],
    "m3_pause_pm_nofreeze": [
        ("	n3.process_mode = Node.PROCESS_MODE_DISABLED\n",
         "	n3.process_mode = Node.PROCESS_MODE_INHERIT  # CRITIC MUTANT: no disable\n",
         "cpu_pause: process_mode lever never disables; predicted pm_disabled fin_after_enable=-25"),
    ],
    "m4_request_round": [
        ("		var expected: int = int(floor(0.5 / spec)) + 1",
         "		var expected: int = int(round(0.5 / spec)) + 1  # CRITIC MUTANT: pre-fold form",
         "cpu_request: floor reverted to round (the falsified scout form); expected values unchanged at 0.10/0.05 -> row cannot discriminate"),
    ],
    "m5_request_noplus1": [
        ("		var expected: int = int(floor(0.5 / spec)) + 1",
         "		var expected: int = int(floor(0.5 / spec))  # CRITIC MUTANT: +1 removed",
         "cpu_request: +1 removed from the closed form; predicted fin_call1=6 vs expected=5 -> FAIL"),
    ],
    "m6_never_addpf1": [
        ("func _arm_cpu_never() -> void:\n	var n := _new_cpu(",
         "func _arm_cpu_never() -> void:\n	await process_frame  # CRITIC MUTANT: node now added at add_pf=1\n	var n := _new_cpu(",
         "cpu_never: node added after the first idle frame (add_pf=1); predicted the node fires -> ok=false"),
    ],
}

def build():
    made = []
    for name, subs in MUTANTS.items():
        text = BASE
        applied = []
        for old, new, note in subs:
            if text.count(old) != 1:
                raise SystemExit(f"{name}: pattern count {text.count(old)} for {old[:60]!r}")
            text = text.replace(old, new, 1)
            applied.append({"old": old, "new": new, "note": note})
        d = os.path.join(ROOT, "mutants", name)
        os.makedirs(d, exist_ok=True)
        shutil.copy2(PROJ, os.path.join(d, "project.godot"))
        open(os.path.join(d, "particles_lattice.gd"), "w").write(text)
        json.dump({"mutant": name, "substitutions": applied,
                   "source": FIX, "source_sha256_note": "0701e813e50cdb50e05f0df0194d0baf94c1240f361e941949414dd5c52c00a9"},
                  open(os.path.join(d, "mutation.json"), "w"), indent=2)
        made.append(name)
    print("built:", made)

if __name__ == "__main__":
    build()
