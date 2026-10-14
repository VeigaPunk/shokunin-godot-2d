"""r72-verifier scratch subject: reorder-fabrication probe child.

NOT a fixture (author arm absent at verification time). Reproduces the
xconnector X1 mechanism inside a real pygame process: this process's own
stdio block-buffer withholds HEAD while an os.system descendant writes to
inherited fd1 -> downstream reader sees descendant bytes FIRST
(prefix/reorder topology) unless the parent is unbuffered or flushes.

argv: reorder_subject.py <buffered|flushed> <pygame|bare>
  buffered : no flush before spawn (window open at spawn time)
  flushed  : sys.stdout.flush() before spawn (window collapsed)
  pygame   : import pygame + init + dummy set_mode first (in-engine run)
  bare     : plain interpreter control (language-layer isolation)
"""
import os
import sys
import time

mode = sys.argv[1]           # buffered | flushed
surface = sys.argv[2]        # pygame | bare

if surface == "pygame":
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))

sys.stdout.write("HEAD ")
if mode == "flushed":
    sys.stdout.flush()       # collapse the withhold window before spawn

# spawn-layer seam: grandchild (sh -> printf) inherits fd1, writes the
# kernel pipe directly -- never touches this process's userspace buffer.
os.system("printf 'INJECTED'")
time.sleep(0.05)

sys.stdout.write(" TAIL\n")
time.sleep(0.05)
# buffered mode: HEAD+TAIL sit in userspace until exit flush, landing
# AFTER the descendant's already-delivered bytes.
