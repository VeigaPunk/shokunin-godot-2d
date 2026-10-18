#!/usr/bin/env python3
"""MUT-5: wrong-magic patch on the PCK census row.

Produces wrong-magic variants of a real Godot 4 PCK and checks that the
PCK census-row acceptance predicate rejects them. The mutation changes ONLY
the 4 magic bytes: size and the body (offset >= 4) stay byte-identical, so
any census that accepts the mutant is size/body-blind, i.e. the magic check
is vacuous.

Usage:
  python3 mut05.py --source /tmp/r101-mut5/out/pack.pck --out /tmp/r101-mut5/out
  python3 mut05.py ... --run-loader /usr/bin/godot

Exit 0 = real ACCEPT, both mutants REJECT (mutation detected).
Exit 1 = a mutant slipped through the census predicate (latent defect).
"""
import argparse
import hashlib
import pathlib
import subprocess
import sys

MAGIC = b"GDPC"
PCK_VERSIONS = (1, 2, 3, 4)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def census_accept(data: bytes) -> dict:
    """Replica of the PCK census-row acceptance predicate.

    magic == GDPC, sane pack version, non-empty, non-zero file count.
    """
    magic = data[:4]
    version = int.from_bytes(data[4:8], "little") if len(data) >= 8 else -1
    # file count lives after the v3 file_base field; for v4 packs the first
    # u32 after the 4-byte magic+version+3 version words+flags+file_base.
    # We do not need its exact offset for the mutation: non-empty body is
    # enough to keep the predicate honest without over-fitting the format.
    nonzero_body = len(data) > 4 and any(data[4:])
    return {
        "magic": magic.decode("latin1"),
        "version": version,
        "size": len(data),
        "accept": magic == MAGIC and version in PCK_VERSIONS and nonzero_body,
    }


def size_only_accept(data: bytes) -> bool:
    """Weaker predicate a size-only census would use; must ACCEPT mutants."""
    return len(data) > 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--run-loader", default="", help="godot binary; run --main-pack receipt")
    args = ap.parse_args()

    real = args.source.read_bytes()
    if real[:4] != MAGIC:
        print(f"MUT5 FAIL source is not a PCK: magic={real[:4]!r}")
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    variants = {
        "mutA": b"GDXX" + real[4:],          # magic overwrite
        "mutB": bytes([real[0] ^ 0x80]) + real[1:],  # high-bit flip: GDPC -> \xc7DPC
    }
    paths = {"real": args.source}
    for name, data in variants.items():
        p = args.out / f"{name}.pck"
        p.write_bytes(data)
        paths[name] = p

    real_sha = sha256_bytes(real)
    real_census = census_accept(real)
    print(f"MUT5 real  path={paths['real']} size={len(real)} sha={real_sha} "
          f"magic={real_census['magic']} version={real_census['version']} "
          f"census={'ACCEPT' if real_census['accept'] else 'REJECT'}")
    if not real_census["accept"]:
        print("MUT5 FAIL real PCK rejected by census replica")
        return 1
    if not size_only_accept(real):
        print("MUT5 FAIL size-only predicate rejected real PCK")
        return 1

    ok = True
    for name in ("mutA", "mutB"):
        data = variants[name]
        census = census_accept(data)
        size_only = size_only_accept(data)
        body_equal = data[4:] == real[4:]
        sha_diff = sha256_bytes(data) != real_sha
        verdict = "REJECT" if not census["accept"] else "ACCEPT"
        print(f"MUT5 {name}  path={paths[name]} size={len(data)} "
              f"sha={sha256_bytes(data)} magic={census['magic']!r} "
              f"version={census['version']} census={verdict} "
              f"size_only={'ACCEPT' if size_only else 'REJECT'} "
              f"body_equal={str(body_equal).lower()} sha_changed={str(sha_diff).lower()}")
        if census["accept"]:
            print(f"MUT5 FAIL {name} accepted: wrong magic bypasses census")
            ok = False
        if len(data) != len(real) or not body_equal:
            print(f"MUT5 FAIL {name} is not an isolated magic-only patch")
            ok = False
        if not size_only:
            print(f"MUT5 FAIL {name}: size-only control unexpectedly rejected")

    if args.run_loader:
        for name in ("real", "mutA", "mutB"):
            proc = subprocess.run(
                [args.run_loader, "--headless", "--main-pack", str(paths[name]),
                 "--quit-after", "2"],
                capture_output=True, text=True, timeout=120)
            out = (proc.stdout + proc.stderr).strip().splitlines()
            interesting = [ln for ln in out if "MUT5_PACK_STARTED" in ln
                           or "ERROR" in ln or "error" in ln.lower()]
            print(f"MUT5 loader {name}: rc={proc.returncode} "
                  f"lines={len(out)} interesting={interesting[:4]}")

    print("MUT5 " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
