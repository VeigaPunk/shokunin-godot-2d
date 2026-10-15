import os, subprocess, sys, time
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
pygame.init(); pygame.display.set_mode((64,64)); clock = pygame.time.Clock()
n = int(os.cpu_count() or 4)
loads = [subprocess.Popen([sys.executable, "-c", "while True: pass"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
         for _ in range(n)]
try:
    for rep in range(2):
        dts = []
        for _ in range(150):
            t0 = time.perf_counter(); clock.tick(60); dts.append((time.perf_counter()-t0)*1e3)
        print(f"PYGAME-ARM cadence_loaded | rep={rep} nproc_load={n} n=150 "
              f"dt_mean_ms={sum(dts)/len(dts):.4f} dt_min_ms={min(dts):.4f} "
              f"dt_max_ms={max(dts):.4f} hz={1000/(sum(dts)/len(dts)):.2f}")
finally:
    for p in loads: p.kill()
print("LOADED_DONE")
