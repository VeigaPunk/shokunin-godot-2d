"""Child for flush_edge_pygame.py: unflushed 3-slot writer, optional pygame import."""
import sys
import time

if "--import-pygame" in sys.argv:
    import pygame  # noqa: F401  (banner suppressed by env)

n = int(sys.argv[1])
sys.stdout.write("A1\n")
time.sleep(0.30)
sys.stdout.write("B" * n + "\n")
time.sleep(0.30)
sys.stdout.write("A3\n")
