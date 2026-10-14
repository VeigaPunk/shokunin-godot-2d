"""r72-critic: build a patched COPY of the tracked pygame probe with the
round-72 reorder arm inserted (scratch only -- the tracked fixture is
untouched). Insertion point: immediately before `pygame.quit()`.
"""
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
HERE = Path(__file__).resolve().parent
SRC = LANE / "corpus/fixtures/pygame_probe.py"

src = SRC.read_text()
marker = "    pygame.quit()"
assert src.count(marker) == 1, src.count(marker)

ARM = r'''
    # --- reorder arm (r72-critic probe copy) ---------------------------
    # HEAD withheld in userspace; write-through descendant reaches fd1 now;
    # TAIL withheld too; the emit flush delivers HEAD+TAIL after CHILD.
    sys.stdout.write("REORDER-HEAD\n")
    os.system("printf 'REORDER-CHILD\\n'")
    sys.stdout.write("REORDER-TAIL\n")
    print("PYGAME-ARM reorder | child=printf markers=line", flush=True)
'''
patched = src.replace(marker, ARM + "\n" + marker)
dest = HERE / "pygame_probe_reorder.py"
dest.write_text(patched)
print(f"patched {SRC} -> {dest} (arm inserted before pygame.quit())")
