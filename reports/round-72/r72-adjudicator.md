# R72 adjudicator (Sol) — reorder fabrication: fd1-inheritance × stdio-withholding

Round: 72. Wave: `shokunin-train-20261101-w12`. Work commit `fee5563`.

## Declared move (depth — xconnector X1 composed mechanism)

`reorder_*` arms on pygame_probe: a spawned descendant writes into the
fd1-owner's inherited stdout mid-window. Briefed claim: "buffered child
→ prefix_reorder; -u/flush child → midline_splice — ORDER is
language-layer, seam is spawn-layer."

## Claim adjudication

- Composition CONFIRMED (55/55, 4-seat independent repro — scout's
  pre-landing harness, scribe's raw-pipe harness ×10/×3, verifier's
  7/7 in-pygame cells, boundary's 27-cell matrix): buffered owner →
  `INJECTEDHEAD  TAIL` prefix_reorder; -u / flush=True /
  PYTHONUNBUFFERED=1 → `HEAD INJECTED TAIL` midline_splice; late
  descendant → append.
- Referent corrected mid-round (critic F1, converged by scout D1 +
  boundary F1): the discriminating variable is the **fd1-OWNER's**
  stdio mode, not the descendant's — a descendant-mode sweep lands a
  wrong-sign verdict. The landed arm sweeps the owner (the spawned
  python child carries HEAD/TAIL; descendant is a constant `printf`),
  so the pin is correct as implemented; the brief's "buffered child"
  wording is corrected here.
- Mechanism generality widened: identical 13-cell matrices on bare
  CPython 3.14.7 AND inside an initialized pygame process (byte-equal)
  — the ordering artifact is a CPython/libc writer-side property; SDL/
  pygame contributes nothing. C repro shows the class isn't even
  Python-specific.
- Window semantics (boundary F2–F4): reorder iff descendant write ∈
  (owner HEAD write, owner flush) — a **byte/buffer-lifetime** bound,
  not wall-time; a +300ms descendant still reorders if the owner never
  flushed. 4-valued topology family {prefix, infix, midline, append};
  paced mid-chunk child → infix (left un-pinned at fixture level —
  nondeterministic); SIGKILL/os._exit → loss class, not a topology.
- Witness caveat recorded (boundary F2): byte topology alone is NOT a
  fabrication witness — an honest-order cell can be byte-identical; the
  arm's write-order construction inside the owner is what makes it a
  witness.

## Defects found & folded

- **r71 verifier defect** (popen_arm ambient `PYTHONUNBUFFERED` leak →
  35/36, 2/2 repro): folded `env=CHILD_ENV` at `pygame_probe.py:93`.
- **critic F3**: ambient env leak on the probe side → battery
  `run_process` pops `PYTHONUNBUFFERED` (`pygame_battery.py:154`).
- **boundary F6**: anchored ARM parser misses a prefix-reordered
  receipt → `reorder_self` markers newline-terminated; raw-wire order
  pinned via new `RAW_CASES` (the parser hazard itself is the pinned
  finding — `REORDER-CHILD` precedes `REORDER-HEAD` at line 15<16 of
  captured stdout).
- pty capture is a false-negative regime (midline under both modes) —
  `fd1_isatty` recorded per receipt; battery pins pipe capture.

## Seat accounting

7/9 seats landed at adjudication: author `fee5563` (+171/−0
insertion-only); scout pre-measured + insertion pre-check on scratch
copy; critic F1 referent falsification + 13-cell cross-matrix; boundary
27-cell edge lattice (infix, loss class, 131072 splice-through,
parser-miss); scribe independent raw-pipe repro + knowledge drafts;
verifier **AGREE 5/5** on committed tree (55/55 ×3 +
PYTHONUNBUFFERED sweep + own 7/7); baseline zero-drift on pre-move
freeze `44127af` (88/88 + 89/89×3 + 19/19 + 36/36). Reviewer +
simplifier still in flight — their flags fold post-commit if
warranted.

## Verdict

**ADMIT** — the composed mechanism is real and now correctly
attributed: spawn-layer seam (POSIX fd1 inheritance, same as Godot
midlineforge / LOVE os.execute) × language-layer order (owner's stdio
buffering, CPython-general). Prior-arm key sets byte-stable; r71
defect repaired in the same commit.
