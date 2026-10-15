# r100-boundary receipts

Frozen replay probe:  proj/r100_gui.gd        dd826f6e7b74ba62fcfd175ab7a1cf0c40fd9712de4b33a18554930cf6dad073
Artifact probe:        probes/r100b_phase.gd  49298e6cc18c4e0de627105b9d95ff28ed2ccfa52bb1cc2da364b76d5430d4b7
Sequencing probe:      probes/r100b_seq.gd    4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd
Mode/state one-offs:   probes/r100b_meta.gd   457dd2e1e3b5c056dfbbdd27be36b490884caf6a45849a8bb9d8209327400f29
                       probes/r100b_emul.gd   31087e7821eb4d2d5cf4bd28d9e5d8ca11bd52f83057fcd41889ecfecdbd4960
Drivers/analysis:      run_matrix.sh c6d3fa3b1163222287e4d9f6489ee873824a3d1b18f5649f398b7c02b9800cb2
                       run_probes.sh d9849a4502cf2d8b8a6c1762c283dffa8057ba23bac21e3fa2a869792ae6c9fc
                       analyze_r100b.py 8fd0310215248b978c884e0f1bd278668e460f2c796def4f0aafe41002f7cbea
                       make_seq.py 3542ee802489e6e1922bebcba95a4b229eaa72a352cad38c8e2d6395a4e26ff5
Launch projects:       proj/project.godot      8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9 (fixture byte-copy)
                       proj_thr/project.godot  eb2bda39ce82cd5a09c0b67003f5437417acb6a215617c4485a62c240304e489 (+ 2d/run_on_separate_thread=true)
Reference rows:        ../r100-scout/author-rows.py.txt  c32d7a2f24ab1a619d0fc10914d3141b004d9ccccbf302769ae2a64ce33ab2ff
Report:                ../../../reports/round-100/r100-boundary.md  92451b06ee571c3ba4978948d1fda6190d3f176376cb8d5ad19b544601f3c917

matrix receipts:  210  (quiet 42, load 42, ff30 28, ff60 28, ff120 28, thr 28, ff1 14)
probe receipts:   143  (quiet 33, load/ff30/ff60/ff120/thr 22 each)
one-off receipts:   3  (meta proj/thr, emul)
total .out files: 356, every .rc=0, 0 timeouts

classifier: production `classify_process` (segment sha256 749fa0607e7707e6…, AST-extracted
from corpus/fixtures/run_battery.py) over all 210 matrix receipts + merged stdout/stderr:
210/210 accepted, rejected=[].
replay: all 14 quiet rep1 receipts byte-identical (stdout+stderr) to
../r100-scout/runs/r100_gui_<cell>.rep1.{out,err}.
portability: one distinct PASS payload per cell across all 7 modes (and the full stdout,
banner included, is one distinct hash).

cells: census routing hover motion localpos cursor clip drag touch subvp warp focus render osmeta
probe arms: cursorphase hoverphase dragphase coalesce velphase startup flushpos orderin dblclick
            seq_noclean seq_clean (+ meta, emul)
