"""r71-boundary scratch: pygame headless pump-free loop + event-queue cap.

Arms:
  - pump_free: frame loop with zero event calls; event queue census after.
  - queue_cap: post USEREVENTs without get() until post() fails; pin the cap.
  - get_without_pump: a posted event is retrievable with get() and no pump.
  - drain: get() count vs posted count.

Run under dummy env (env set inside).
"""

import os
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))
clock = pygame.time.Clock()


def main():
    # pump-free frame loop
    t0 = time.perf_counter()
    for _ in range(300):
        clock.tick(120)
    loop_ms = (time.perf_counter() - t0) * 1e3
    queued = len(pygame.event.get())
    print(f"PYGAME-ARM pump_free | frames=300 tick120 total_ms={loop_ms:.1f} "
          f"queued_after={queued}")

    # posted event survives without pump
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, tag="probe"))
    found = [e for e in pygame.event.get() if e.type == pygame.USEREVENT]
    print(f"PYGAME-ARM pump_free_post | retrieved_without_pump={len(found)}")

    # queue cap: post until failure (raises pygame.error at 65535)
    n_ok = 0
    fail_msg = None
    t0 = time.perf_counter()
    for i in range(200000):
        ev = pygame.event.Event(pygame.USEREVENT, seq=i)
        try:
            ok = pygame.event.post(ev)
        except pygame.error as exc:
            fail_msg = str(exc)
            break
        if ok:
            n_ok += 1
        else:
            fail_msg = "post returned False"
            break
    post_ms = (time.perf_counter() - t0) * 1e3
    drained = 0
    while True:
        batch = pygame.event.get()
        if not batch:
            break
        drained += len(batch)
    print(f"PYGAME-ARM queue_cap | posted_ok={n_ok} fail_at={n_ok} "
          f"fail_msg={fail_msg!r} post_ms={post_ms:.1f} drained={drained}")

    # after drain, post works again?
    again = pygame.event.post(pygame.event.Event(pygame.USEREVENT, seq=-1))
    print(f"PYGAME-ARM queue_cap_repost | post_after_drain={again}")

    print("PUMP_PROBE_DONE")


if __name__ == "__main__":
    main()
