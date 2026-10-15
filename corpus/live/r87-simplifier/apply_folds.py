#!/usr/bin/env python3
"""r87-simplifier: apply the proven fold set to a *copy* of input_lattice.gd.

Never run against the tracked tree. Target: corpus/live/r87-simplifier/fixtures-after/input_lattice.gd
"""
import sys
from pathlib import Path

src = Path(sys.argv[1])
text = src.read_text()
orig = text

EDITS = [
    # F1: uncalled formatter (no call sites anywhere in repo; grep fallback,
    # no LSP device available on this host/dispatch).
    (
        '\treturn "pre=%s post_ph=[%s] post_pr=[%s]" % [pre, " ".join(post_ph), " ".join(post_pr)]\n'
        '\n'
        'func _fmt_ticks_d(mask_ph: bool = false) -> String:\n'
        '\tvar out: Array = []\n'
        '\tfor t in ticks:\n'
        '\t\tif t.k == "EV":\n'
        '\t\t\tout.append("EV%d@pr+%d/ph%s" % [t.seq, t.prd,\n'
        '\t\t\t\t"~" if mask_ph else "+%d" % t.d])\n'
        '\t\telse:\n'
        '\t\t\tout.append("%s%d{%s}" % [t.k, t.d, t.st])\n'
        '\treturn "[" + " ".join(out) + "]"\n',
        '\treturn "pre=%s post_ph=[%s] post_pr=[%s]" % [pre, " ".join(post_ph), " ".join(post_pr)]\n',
    ),
    # F2: first _mark() in ui_ns is overwritten by the second with no reads
    # (no ticks recorded, no events) between them.
    (
        '\tvar ua_n := InputMap.action_get_events(&"ui_accept").size()\n'
        '\t_mark()\n'
        '\tawait _pr_frames(2)\n'
        '\t_mark()\n',
        '\tvar ua_n := InputMap.action_get_events(&"ui_accept").size()\n'
        '\tawait _pr_frames(2)\n'
        '\t_mark()\n',
    ),
    # F3: pre_frame re-assigns ph0/pr0 to exactly the values _mark() just set
    # (no await between).
    (
        '\tInput.parse_input_event(_act(&"pf0", true))\n'
        '\tflags["ph0"] = phys_no\n'
        '\tflags["pr0"] = proc_no\n'
        '\tvar imm0 := _st(&"pf0")\n',
        '\tInput.parse_input_event(_act(&"pf0", true))\n'
        '\tvar imm0 := _st(&"pf0")\n',
    ),
    # F4: imap_erase prints r.desc only; ev_watch map is never printed.
    (
        '\t_bind(&"er", _key(KEY_Z))\n'
        '\twatch = [&"er"]\n'
        '\tev_watch = true\n'
        '\tawait _pr_frames(2)\n',
        '\t_bind(&"er", _key(KEY_Z))\n'
        '\tawait _pr_frames(2)\n',
    ),
    # F5: imap_mid_cb prints via/tag/desc only; ev_watch map never printed.
    (
        '\t_mk_sink("s0")\n'
        '\twatch = [&"cb_b"]\n'
        '\tev_watch = true\n'
        '\t# During delivery of the F5 event',
        '\t_mk_sink("s0")\n'
        '\t# During delivery of the F5 event',
    ),
    # F6: reentrant prints seq/via/tag/desc only; ev_watch map never printed.
    (
        '\tInputMap.add_action(&"rb")\n'
        '\twatch = [&"ra", &"rb"]\n'
        '\tev_watch = true\n',
        '\tInputMap.add_action(&"rb")\n',
    ),
    # F7: dispatch_order prints seq/via/tag only; the "do" binding and watch
    # are never read (no _st/_pl/_fmt_recv in the arm).
    (
        '\t_mk_sink("s1")\n'
        '\t_bind(&"do", _key(KEY_F8))\n'
        '\twatch = [&"do"]\n'
        '\tawait _pr_frames(2)\n'
        '\tInput.parse_input_event(_key(KEY_F8, true))\n',
        '\t_mk_sink("s1")\n'
        '\tawait _pr_frames(2)\n'
        '\tInput.parse_input_event(_key(KEY_F8, true))\n',
    ),
]

for i, (old, new) in enumerate(EDITS, 1):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"F{i}: anchor count {n} != 1")
    text = text.replace(old, new)

src.write_text(text)
print(f"applied {len(EDITS)} edits: {len(orig.splitlines())} -> {len(text.splitlines())} lines "
      f"(-{len(orig.splitlines()) - len(text.splitlines())})")
