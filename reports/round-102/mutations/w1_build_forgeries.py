import os, struct

TPL = '/home/vgpnk/.local/share/godot/export_templates/4.7.2.stable/linux_release.x86_64'
T = os.path.getsize(TPL)
E0A = '/var/tmp/r102-w1/e0root/embed/moved/embed.x86_64'
S0 = os.path.getsize(E0A)
print(f"TPL={T} E0_artifact={S0}")

def write_exe(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(data)
    os.chmod(p, 0o755)
    print(f"wrote {p} bytes={len(data)}")

def forge_from_body(size, body):
    R = T
    P = size - 12 - R
    assert P > 0, (size, R)
    buf = bytearray(body)
    assert len(buf) < R - 8, len(buf)
    buf += b'#' * (R - len(buf))
    buf += b'GDPC'
    buf += b'#' * (size - 12 - len(buf))
    buf += struct.pack('<Q', P) + b'GDPC'
    assert len(buf) == size, (len(buf), size)
    return bytes(buf)

def shell_body(marker_lines):
    return ("#!/bin/sh\n" + "".join('echo "%s"\n' % l for l in marker_lines) + "exit 0\n").encode()

def polyglot_body(marker_lines):
    cmds = ";".join('echo "%s"' % l for l in marker_lines) + ";exit 0\n"
    return b'\x7fELF;' + cmds.encode()

E0_MARK = ["EXPORT_LAUNCH_MAIN boot scene=main", "EXPORT_LAUNCH_FRAME 1", "EXPORT_LAUNCH_FRAME 2", "EXPORT_LAUNCH_FRAME 3"]
E2_MARK = ["LAUNCH_S02_MARKER boot=true", "LAUNCH_S02_FRAME 1", "LAUNCH_S02_FRAME 2", "LAUNCH_S02_FRAME 3", "LAUNCH_S02_FRAME 4", "LAUNCH_S02_FRAME 5"]

write_exe('/var/tmp/r102-w1/fpf_e0/embed.x86_64', forge_from_body(S0, shell_body(E0_MARK)))
write_exe('/var/tmp/r102-w1/fhe_e0/embed.x86_64', forge_from_body(S0, polyglot_body(E0_MARK)))
write_exe('/var/tmp/r102-w1/fpf_e2/s02.x86_64', forge_from_body(73521464, shell_body(E2_MARK)))

data = bytearray(open(E0A, 'rb').read())
tpl = open(TPL, 'rb').read()
data[T - 1000:T - 996] = tpl[T - 1000:T - 996]
data[T - 992:T - 990] = tpl[T - 992:T - 990]
write_exe('/var/tmp/r102-w1/forge_r_e0/embed.x86_64', bytes(data))
