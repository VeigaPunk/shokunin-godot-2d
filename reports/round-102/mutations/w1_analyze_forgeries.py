import os, hashlib, struct

TPL = '/home/vgpnk/.local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64'
T = os.path.getsize(TPL)

def sha_prefix(p, end):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        left = end
        while left > 0:
            ch = f.read(min(1 << 20, left))
            if not ch:
                break
            h.update(ch)
            left -= len(ch)
    return h.hexdigest()

tsha = sha_prefix(TPL, T - 1024)
print(f"template_bytes={T} sha256(template[0:{T - 1024}))={tsha}")

cases = [
    ('real_e0     ', '/var/tmp/r102-w1/e0root/embed/moved/embed.x86_64'),
    ('fpf_e0      ', '/var/tmp/r102-w1/fpf_e0/embed.x86_64'),
    ('fhe_e0      ', '/var/tmp/r102-w1/fhe_e0/embed.x86_64'),
    ('forge_r_e0  ', '/var/tmp/r102-w1/forge_r_e0/embed.x86_64'),
    ('fpf_e2      ', '/var/tmp/r102-w1/fpf_e2/s02.x86_64'),
    ('forge_w_naive', '/var/tmp/r102-w1/forge_w/launch_embed.x86_64'),
    ('forge_p_smug ', '/var/tmp/r102-w1/forge_p/launch_embed.x86_64'),
]

for name, p in cases:
    if not os.path.exists(p):
        print(f"{name} MISSING {p}")
        continue
    S = os.path.getsize(p)
    with open(p, 'rb') as f:
        head = f.read(4)
        f.seek(S - 12)
        foot = f.read(12)
    P = struct.unpack('<Q', foot[:8])[0]
    R = S - 12 - P
    trailer_gdpc = foot[8:12] == b'GDPC'
    region_head_ok = False
    if 0 <= R <= S - 12:
        with open(p, 'rb') as f:
            f.seek(S - 12 - P)
            region_head_ok = f.read(4) == b'GDPC'
    sha_ok = None
    patch = None
    if S >= T:
        sha_ok = sha_prefix(p, T - 1024) == tsha
        with open(p, 'rb') as f:
            f.seek(T - 1000)
            patch = (struct.unpack('<Q', f.read(8))[0], struct.unpack('<Q', f.read(8))[0])
    print(f"{name} S={S} head4={head.hex()} tail_gdpc={trailer_gdpc} P={P} R={R} R_eq_template={R == T} region_head_gdpc={region_head_ok} S_gt_T={S > T} prefix_sha_ok={sha_ok} patch={patch} patch_ok={patch == (T, P)}")
    print(f"{name} e0_replica: tail_magic={foot[8:12]!r} binary_bytes={S} | e2_replica: trailer_gdpc={trailer_gdpc} trailer_size_consistent={R == T} pack_magic_at_start={region_head_ok} bin_gt_template={S > T}")
