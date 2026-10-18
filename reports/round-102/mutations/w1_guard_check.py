import os, struct, sys

def check(p):
    S = os.path.getsize(p)
    with open(p, 'rb') as f:
        head = f.read(4)
        f.seek(S - 12)
        foot = f.read(12)
    P = struct.unpack('<Q', foot[:8])[0]
    m1 = head == b'\x7fELF'
    m2 = (foot[8:12] == b'GDPC') and (16 <= P < S - 12)
    R = (S - 12 - P) if m2 else -1
    m3 = False
    if m2 and R > 0:
        with open(p, 'rb') as f:
            f.seek(R)
            ph = f.read(8)
        ver = struct.unpack('<I', ph[4:8])[0]
        m3 = ph[:4] == b'GDPC' and 1 <= ver <= 4
    verdict = 'ACCEPT' if (m1 and m2 and m3) else 'REJECT'
    print(f"{verdict} path={p} size={S} head_elf={m1} trailer_gdpc={foot[8:12] == b'GDPC'} P={P} region={R} pack_head_ok={m3} last12={foot.hex()}")

for p in sys.argv[1:]:
    check(p)
