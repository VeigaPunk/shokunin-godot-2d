#!/usr/bin/env python3
"""r101 fold: re-pin the 3 phase-bimodal ytrans rows to the invariant PASS
lines measured on the folded fixture (quiet host, 2/2 byte-identical reps).
The order-sensitive fields moved to R101Y diagnostics in r101_ytrans.gd."""
import py_compile
BAT = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/run_battery.py"
NEW = {
 "r101_ytrans_y1000": "PASS r101_ytrans ytrans offy=1000.0000 add_order=[a,b,c,d,e] dy_resid=0.0000 distinct_ticks=7 last_change_tick=64 t2_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000] n_at_y=5 n_at_0=0 t64_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000]",
 "r101_ytrans_ym1000": "PASS r101_ytrans ytrans offy=-1000.0000 add_order=[a,b,c,d,e] dy_resid=0.0000 distinct_ticks=7 last_change_tick=64 t2_absy=[-1000.0000|-1000.0000|-1000.0000|-1000.0000|-1000.0000] n_at_y=5 n_at_0=0 t64_absy=[-1000.0000|-1000.0000|-1000.0000|-1000.0000|-1000.0000]",
 "r101_ytrans_ycop": "PASS r101_ytrans ycop offy=1000.0000 a_t2_absy=[0.0000|0.0000|0.0000|0.0000|0.0000] a_t2_cross_clean=true dy_meas=0.0000 a_t4_absy=[0.0000|0.0000|0.0000|0.0000|0.0000] a_t4_cross_clean=true b_t2_absy=[1000.0000|1000.0000|1000.0000|1000.0000|1000.0000] b_t2_cross_clean=true n_between=0 n_origin=5 n_at_b=5",
}
lines = open(BAT).read().splitlines(keepends=True)
count = 0
for i, l in enumerate(lines):
    for name, sig in NEW.items():
        if l.startswith("    ('%s'," % name):
            # tuple: ('name', 'script', [flags], 0,\n     'SIG'),\n
            nxt = lines[i + 1]
            assert nxt.lstrip().startswith("'PASS r101_ytrans"), nxt[:80]
            assert nxt.rstrip().endswith("),"), nxt[-40:]
            indent = nxt[: len(nxt) - len(nxt.lstrip())]
            lines[i + 1] = "%s'%s'),\n" % (indent, sig)
            count += 1
assert count == 3, count
open(BAT, "w").write("".join(lines))
py_compile.compile(BAT, doraise=True)
print("fold splice OK: 3 pins re-pinned; py_compile OK")
