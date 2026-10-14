"""r72-scout scratch — build a probe copy with the reorder arm inserted.

Copies the landed fixture corpus/fixtures/pygame_probe.py into this
scratch dir and inserts the own-fd1 reorder block just before
`pygame.quit()` — the insertion point the round-72 author would use.
Insertion-only; the fixture itself is untouched.

Run: python3 make_probe_copy.py
"""

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent.parent / "fixtures" / "pygame_probe.py"
DST = HERE / "probe_copy.py"

ARM_BLOCK = '''
    # --- reorder (r72-scout scratch pre-measurement; NOT landed) --------
    # own-fd1 variant: a spawned descendant writes into THIS process's
    # inherited fd1 mid-window. HEAD is deliberately unflushed.
    sys.stdout.write("R-HEAD\\n")                        # withheld (buffered)
    subprocess.run(["sh", "-c", "printf 'R-INJ\\\\n'"])  # inherits fd1
    time.sleep(0.20)                                     # hold window open
    sys.stdout.write("R-TAIL\\n")
    sys.stdout.flush()

'''

src = SRC.read_text()
needle = "    pygame.quit()\n"
assert src.count(needle) == 1, "insertion anchor not unique"
dst = src.replace(needle, ARM_BLOCK + needle)
DST.write_text(dst)
print(f"wrote {DST} ({len(dst.splitlines())} lines; "
      f"fixture was {len(src.splitlines())})")
