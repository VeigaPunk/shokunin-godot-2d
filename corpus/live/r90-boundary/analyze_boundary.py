#!/usr/bin/env python3
"""r90-boundary analyzer — per-cell rc/uniq/at-lines plus claim-level classification.

Reads runs/*.rep*.{out,err,rc,wall}, emits:
  - analyze_boundary.json : machine-readable per-cell + per-claim data
  - stdout                : the boundary table used for the report
"""
import json
import os
import re
import sys
from collections import defaultdict

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
G = 980.0

# scout r90 canonical pins (substrings of the PASS line; from reports/round-90/r90-scout.md)
SCOUT_PINS = {
    "sv_order": [
        "ncb=60",
        "cb0=st=0.016667 ty=0.2722 vy=16.3333",
        "f1=y=0.2722,vy=16.3333",
        "f60=y=482.2250,vy=933.3325",
    ],
    "sv_damp": [
        "tld=default=0.1000|rep0=0.0000|rep05=0.5000|comb05=0.6000",
        "f30=default[y=124.5675,vy=478.3405]|rep0[y=126.5834,vy=490.0001]",
        "f60=default[y=482.2250,vy=933.3325]|rep0[y=498.1666,vy=979.9996]",
    ],
    "sv_write": [
        "f30=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=118.4167,vy=490.0001]",
        "f60=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=481.8333,vy=979.9996]",
    ],
    "sv_impulse": [
        "c_central[v=0.0000,-60.0000,w=0.0000,iI=0.031250,im=1.0000]",
        "c_off[v=0.0000,-60.0000,w=-15.0000,iI=0.031250,im=1.0000]",
        "c_tq[v=0.0000,0.0000,w=15.0000,iI=0.031250,im=1.0000]",
        "r_tq[v=0.0000,0.0000,w=11.5200,iI=0.024000,im=1.0000]",
        "r_off[v=0.0000,-60.0000,w=-11.5200,iI=0.024000,im=1.0000]",
    ],
    "sv_freezelock": [
        "f30=f_normal[y=-7.6969,vy=0.0000,w=0.0000,fz=false]",
        "f_static[y=-100.0000,vy=0.0000,w=0.0000,fz=true]",
        "f_kin[y=-100.0000,vy=-30.0000,w=0.0000,fz=true]",
        "f_lock[y=-128.0000,vy=-60.0000,w=0.0000,fz=false]",
        "sleep=s_off[sl=false,y=-7.7000,vy=0.0000] s_on[sl=true,y=-7.7000,vy=0.0000]",
    ],
    "sv_contacts": [
        "rest=y=-7.7000,vy=0.0000",
        "cb=count=1 y=-7.7000 pos=0.0000,0.3000 cvel=0.0000,16.3333",
        "entered=1",
    ],
    "sv_gravity": [
        "g05[y=62.2838,vy=239.1703]",
        "g1[y=124.5675,vy=478.3405]",
        "g2[y=249.1351,vy=956.6811]",
        "g1[y=482.2250,vy=933.3325]",
        "zv0[y=-30.0000,vy=-30.0000]",
    ],
    "sv_gravity_t120": [
        "g1[y=478.1452,vy=932.9641]",
        "g1[y=122.5250,vy=478.1458]",
        "zv0[y=-30.0000,vy=-30.0000]",
    ],
    "sv_comrefuse": [
        "auto_set4=com=0.0000,0.0000 mode=0",
        "custom_set4=com=4.0000,0.0000 mode=1",
        "back_auto=com=0.0000,0.0000 mode=0",
    ],
}

# scout pins expected in my own instrumented cells
SELF_PINS = {
    "b_order": ["ncb=60", "cb0=st=0.016667 ty=0.2722 vy=16.3333", "f1=y=0.2722,vy=16.3333",
                "f60=y=482.2250,vy=933.3325", "pf_delta=60", "tick_dh=1:59"],
    "b_order_t120": ["ncb=60", "cb0=st=0.008333 ty=0.0681 vy=8.1667",
                     "f60=y=122.5250,vy=478.1458", "pf_delta=60", "tick_dh=1:59"],
    "b_write": ["step=0.016667", "f30=wzero[y=0.0000,vy=0.0000]|whold[y=-50.0000,vy=0.0000]|wman[y=118.4167,vy=490.0001]"],
    "b_damp": ["tld=default=0.1000|rep0=0.0000|rep05=0.5000|comb05=0.6000"],
    "b_impulse": ["c_auto" if False else "auto[v=0.0000,-60.0000,w=15.0000,iI=0.031250"],
}


def cells():
    names = set()
    for f in os.listdir(RUNS):
        m = re.match(r"(.+)\.rep(\d+)\.(out|err|rc|wall)$", f)
        if m:
            names.add(m.group(1))
    return sorted(names)


def read_cell(name):
    reps, i = [], 1
    while True:
        rc = os.path.join(RUNS, "%s.rep%d.rc" % (name, i))
        if not os.path.exists(rc):
            break
        out = open(os.path.join(RUNS, "%s.rep%d.out" % (name, i)), "rb").read()
        err = open(os.path.join(RUNS, "%s.rep%d.err" % (name, i)), "rb").read()
        rc_v = int(open(rc).read().strip())
        wallp = os.path.join(RUNS, "%s.rep%d.wall" % (name, i))
        wall = float(open(wallp).read().strip()) if os.path.exists(wallp) else 0.0
        reps.append({"rc": rc_v, "out": out, "err": err, "wall": wall})
        i += 1
    return reps


def pass_lines(reps):
    return [ln.decode() for r in reps for ln in r["out"].splitlines() if ln.startswith(b"PASS ")]


def first_pass(name):
    return pass_lines(read_cell(name))[0]


def kv(pass_line):
    toks = pass_line.split()
    d = {}
    for t in toks[3:]:
        if "=" in t:
            k, v = t.split("=", 1)
            d[k] = v
    return d


def at_lines(err_bytes):
    return sorted(set(re.findall(r"at: (\S+ \([^)]*\))", err_bytes.decode(errors="replace"))))


def err_class(err_bytes):
    return sorted(set(re.findall(r"ERROR: (.*)", err_bytes.decode(errors="replace"))))


def uniq(xs):
    return len(set(xs))


def frames_of(pl):
    ms = re.findall(r" f(\d+)=", pl)
    if ms:
        return max(int(x) for x in ms)
    m = re.search(r"tick_dh=([\w:,]+)", pl)
    if m:
        return sum(int(n) for _, n in (x.split(":") for x in m.group(1).split(",") if ":" in x)) + 1
    return None


def tps_of(name):
    for t in (240, 120, 60, 30):
        if "t%d" % t in name:
            return t
    return 60


def dh_ok(pl, frames):
    m = re.search(r"tick_dh=([\w:,]+)", pl)
    if not m:
        return None
    pairs = [x.split(":") for x in m.group(1).split(",") if ":" in x]
    total = sum(int(n) for _, n in pairs)
    ones = sum(int(n) for d, n in pairs if int(d) == 1)
    return {"ok": total == frames - 1 and ones == total,
            "total": total, "ones": ones, "dh": m.group(1)}


def classify_pair(pl):
    """Pairing of first callback vs first await observation (race-robust ordering)."""
    mcb = re.search(r"cb0_rel=(\d+)", pl)
    mobs = re.search(r"obs0_rel=(\d+)", pl)
    if mcb and mobs:
        a, b = int(mcb.group(1)), int(mobs.group(1))
        if a == b:
            return "sync0"
        if a > b:
            return "late_body"
        return "early_body"
    return "?"


def main():
    out = {"cells": {}, "claims": {}}
    rows = []
    for name in cells():
        reps = read_cell(name)
        pls = pass_lines(reps)
        errs = [r["err"] for r in reps]
        rcs = [r["rc"] for r in reps]
        walls = [round(r["wall"], 2) for r in reps]
        ats = sorted(set(a for e in errs for a in at_lines(e)))
        ecls = sorted(set(c for e in errs for c in err_class(e)))
        arm = pls[0].split()[2] if pls else "?"
        rec = {
            "arm": arm,
            "reps": len(reps),
            "rc": rcs,
            "pass_uniq": uniq(pls),
            "raw_uniq": uniq([r["out"] for r in reps]),
            "err_uniq": uniq(errs),
            "err_bytes": [len(e) for e in errs],
            "at": ats,
            "err_class": ecls,
            "wall": walls,
            "pair": sorted(set(classify_pair(p) for p in pls)),
            "keys": kv(pls[0]) if pls else {},
            "pass": pls[0] if pls else "",
        }
        out["cells"][name] = rec
        rows.append((name, rec))

    C = out["claims"]

    # scout-pin equality for verbatim and instrumented cells
    pin = {}
    for name, rec in rows:
        exp = SCOUT_PINS.get(name) or SELF_PINS.get(name)
        if not exp:
            continue
        per_rep = []
        for r in read_cell(name):
            pl = [ln.decode() for ln in r["out"].splitlines() if ln.startswith(b"PASS ")]
            pl = pl[0] if pl else ""
            per_rep.append(all(s in pl for s in exp))
        pin[name] = {"pins": exp, "per_rep": per_rep, "all_ok": all(per_rep)}
    C["pins"] = pin

    # C1 ordering: ncb == frames, pf_delta == frames, per-await step 1:1, cb0==f1 when synced
    for name, rec in rows:
        if rec["arm"] != "order":
            continue
        pl = first_pass(name)
        try:
            frames = frames_of(pl)
            ncb = int(re.search(r"ncb=(\d+)", pl).group(1))
            pfd = int(re.search(r"pf_delta=(\d+)", pl).group(1))
            cb0 = re.search(r"cb0=st=([\d.]+) ty=([-\d.]+) vy=([-\d.]+)", pl)
            f1 = re.search(r" f1=y=([-\d.]+),vy=([-\d.]+)", pl)
            dh = dh_ok(pl, frames)
            pair = classify_pair(pl)
            checks = {
                "frames": frames, "ncb": ncb, "pf_delta": pfd,
                "ncb_eq_frames": ncb == frames,
                "pf_delta_eq_frames": pfd == frames,
                "tick_1to1": dh["ok"] if dh else None,
                "pair": pair,
                "cb0_step": cb0.group(1),
                "cb0_ty": cb0.group(2), "cb0_vy": cb0.group(3),
                "f1": f1.group(0).strip(),
                "cb0_eq_f1": (abs(float(cb0.group(2)) - float(f1.group(1))) < 5e-5
                              and abs(float(cb0.group(3)) - float(f1.group(2))) < 5e-5) if pair == "sync0" else None,
                "cb0_eq_f2": None,
            }
            if pair != "sync0":
                f2 = re.search(r" f2=y=([-\d.]+),vy=([-\d.]+)", pl)
                if f2:
                    checks["cb0_eq_f2"] = (abs(float(cb0.group(2)) - float(f2.group(1))) < 5e-5
                                           and abs(float(cb0.group(3)) - float(f2.group(2))) < 5e-5)
            C.setdefault("order", {})[name] = checks
        except Exception as e:
            C.setdefault("order", {})[name] = {"parse_error": str(e)}

    # C3 lag: d.dy == n*g*dt^2 (n = executed callbacks); positions closed-form
    for name, rec in rows:
        if rec["arm"] != "lag":
            continue
        pl = first_pass(name)
        dt = 1.0 / tps_of(name)
        n = int(re.search(r"an=(\d+)", kv(pl)["acc"]).group(1))
        dy = float(re.search(r"dy=([-\d.]+)", kv(pl)["d"]).group(1))
        dvy = float(re.search(r"dvy=([-\d.]+)", kv(pl)["d"]).group(1))
        a_y = float(re.search(r"y=([-\d.]+)", kv(pl)["a"]).group(1))
        b_y = float(re.search(r"y=([-\d.]+)", kv(pl)["b"]).group(1))
        a_vy = float(re.search(r"vy=([-\d.]+)", kv(pl)["a"]).group(1))
        exp_dy = n * G * dt * dt
        a_y_cf = G * dt * dt * n * (n + 1) / 2.0
        b_y_cf = G * dt * dt * n * (n - 1) / 2.0
        pre = float(re.search(r"bpre=([-\d.]+)", kv(pl)["acc"]).group(1))
        post = float(re.search(r"bpost=([-\d.]+)", kv(pl)["acc"]).group(1))
        C.setdefault("lag", {})[name] = {
            "tps": tps_of(name), "dt": round(dt, 8), "n": n, "frames": frames_of(pl),
            "dy": dy, "exp_dy": round(exp_dy, 4), "dy_ok": abs(dy - exp_dy) < 2e-4,
            "dvy": dvy,
            "a_y": a_y, "a_y_cf": round(a_y_cf, 4), "a_ok": abs(a_y - a_y_cf) < 3e-4,
            "b_y": b_y, "b_y_cf": round(b_y_cf, 4), "b_ok": abs(b_y - b_y_cf) < 3e-4,
            "a_vy": a_vy, "a_vy_cf": round(n * G * dt, 4), "a_vy_ok": abs(a_vy - n * G * dt) < 3e-4,
            "bpre": pre, "bpre_cf": round((n - 1) * G * dt, 4),
            "bpost": post, "bpost_cf": round(n * G * dt, 4),
            "pf_delta": kv(pl).get("pf_delta"),
            "tick_dh": kv(pl).get("tick_dh"),
        }

    # C2 damp: tld oracle + recurrence per lane
    def damp_recurrence(n, tld, dt):
        v, y = 0.0, 0.0
        for _ in range(n):
            v = v * (1.0 - tld * dt) + G * dt
            y += v * dt
        return y, v

    for name, rec in rows:
        if rec["arm"] != "damp":
            continue
        pl = first_pass(name)
        tps = tps_of(name)
        dt = 1.0 / tps
        frames = frames_of(pl)
        m_n = re.search(r"ncb=(\d+)", pl)
        n = int(m_n.group(1)) if m_n else frames
        tlds = dict(p.split("=") for p in kv(pl)["tld"].split("|"))
        exp_tld = {"default": 0.1, "rep0": 0.0, "rep05": 0.5, "comb05": 0.6}
        checks = {"tps": tps, "frames": frames, "ncb": n,
                  "tld_ok": all(abs(float(tlds[l]) - exp_tld[l]) < 1e-9 for l in exp_tld),
                  "tld": kv(pl)["tld"], "pf_delta": kv(pl).get("pf_delta"),
                  "tick_dh": kv(pl).get("tick_dh"), "lanes": {}}
        for half_k, full_k in (("f%d" % (frames // 2), "f%d" % frames),):
            half = dict()
            for lane in kv(pl).get(half_k, "").split("|"):
                m = re.match(r"(\w+)\[y=([-\d.]+),vy=([-\d.]+)\]", lane)
                if m:
                    half[m.group(1)] = (float(m.group(2)), float(m.group(3)))
            full = dict()
            for lane in kv(pl).get(full_k, "").split("|"):
                m = re.match(r"(\w+)\[y=([-\d.]+),vy=([-\d.]+)\]", lane)
                if m:
                    full[m.group(1)] = (float(m.group(2)), float(m.group(3)))
        for lane in exp_tld:
            y_cf, v_cf = damp_recurrence(n, exp_tld[lane], dt)
            y_h, v_h = damp_recurrence(n // 2, exp_tld[lane], dt)
            got, got_h = full.get(lane), half.get(lane)
            checks["lanes"][lane] = {
                "y": got[0] if got else None, "y_cf": round(y_cf, 4),
                "ok": bool(got) and abs(got[0] - y_cf) < 5e-4,
                "y_half": got_h[0] if got_h else None, "y_half_cf": round(y_h, 4),
                "half_ok": bool(got_h) and abs(got_h[0] - y_h) < 5e-4,
            }
        C.setdefault("damp", {})[name] = checks

    # C4 impulse: w == 480*iI for torque lanes; v == -60*im for central lanes
    for name, rec in rows:
        if rec["arm"] != "impulse":
            continue
        pl = first_pass(name)
        lanes = {}
        for lane in kv(pl)["post"].split("|"):
            m = re.match(r"(\w+)\[v=([-\d.]+),([-\d.]+),w=([-\d.]+),iI=([-\d.]+),im=([-\d.]+),inertia=([^,]+),mass=([^\]]+)\]", lane)
            if not m:
                m = re.match(r"(\w+)\[v=([-\d.]+),([-\d.]+),w=([-\d.]+),iI=([-\d.]+),im=([-\d.]+)\]", lane)
                if m:
                    lanes[m.group(1)] = {"vx": float(m.group(2)), "vy": float(m.group(3)),
                                         "w": float(m.group(4)), "iI": float(m.group(5)),
                                         "im": float(m.group(6)), "inertia": None, "mass": None}
            else:
                lanes[m.group(1)] = {"vx": float(m.group(2)), "vy": float(m.group(3)),
                                     "w": float(m.group(4)), "iI": float(m.group(5)),
                                     "im": float(m.group(6)), "inertia": m.group(7),
                                     "mass": m.group(8)}
        checks = {}
        scout_exp = {"c_central": (-60.0, 0.0), "c_off": (-60.0, -15.0), "c_tq": (0.0, 15.0),
                     "r_tq": (0.0, 11.52), "r_off": (-60.0, -11.52)}
        for ln, d in lanes.items():
            if d["inertia"] is None:  # scout verbatim lane set: one impulse per lane
                ev, ew = scout_exp[ln]
                checks[ln] = {"w": d["w"], "exp_w": ew, "w_ok": abs(d["w"] - ew) < 5e-5,
                              "vy": d["vy"], "exp_v": ev, "v_ok": abs(d["vy"] - ev) < 5e-5,
                              "iI": d["iI"], "im": d["im"], "inertia": None, "mass": None}
                continue
            if ln in ("s_offneg", "s_up"):
                continue
            sign = -1.0 if ln == "s_tqneg" else 1.0
            exp_w = sign * 480.0 * d["iI"]
            exp_v = -60.0 * d["im"]
            checks[ln] = {"w": d["w"], "exp_w": exp_w,
                          "w_ok": abs(d["w"] - exp_w) <= max(1e-4, abs(exp_w) * 1e-6),
                          "vy": d["vy"], "exp_v": exp_v,
                          "v_ok": abs(d["vy"] - exp_v) <= max(1e-4, abs(exp_v) * 1e-6),
                          "iI": d["iI"], "im": d["im"], "inertia": d["inertia"], "mass": d["mass"]}
        if "s_offneg" in lanes:
            checks["s_offneg"] = {"w": lanes["s_offneg"]["w"], "exp_w": 15.0,
                                  "w_ok": abs(lanes["s_offneg"]["w"] - 15.0) < 1e-4}
        if "s_up" in lanes:
            checks["s_up"] = {"vy": lanes["s_up"]["vy"], "exp_v": 60.0,
                              "v_ok": abs(lanes["s_up"]["vy"] - 60.0) < 1e-4}
        C.setdefault("impulse", {})[name] = checks

    # C5 comcase: error count per case
    com = {}
    for name, rec in rows:
        if rec["arm"] != "comcase":
            continue
        case = kv(rec["pass"]).get("case", name) if rec["pass"] else name
        err_counts = [len(err_class(r["err"])) for r in read_cell(name)]
        com[case] = {"err_counts": err_counts, "at": rec["at"], "err_class": rec["err_class"],
                     "rc": rec["rc"], "pass": rec["pass"], "pass_uniq": rec["pass_uniq"]}
    C["comcase"] = com

    # C2 backend: engine identity + drop
    for name, rec in rows:
        if rec["arm"] != "backend":
            continue
        k = kv(first_pass(name))
        C.setdefault("backend", {})[name] = {
            "cfg2d": k.get("cfg2d"), "id2d": k.get("id2d"), "dss2d": k.get("dss2d"),
            "cls_exists": k.get("cls_exists"), "drop": k.get("drop"), "ncb": k.get("ncb"),
            "tld": k.get("tld"), "pf_delta": k.get("pf_delta"), "hint2d": k.get("hint2d")}

    # C6 stall: step accounting
    for name, rec in rows:
        if rec["arm"] != "stall":
            continue
        pl = first_pass(name)
        frames = frames_of(pl)
        dh = dh_ok(pl, frames)
        k = kv(pl)
        C.setdefault("stall", {})[name] = {
            "stall": k.get("stall"), "ncb": k.get("ncb"), "frames": frames,
            "ncb_eq_frames": int(k["ncb"]) == frames, "tick_1to1": dh["ok"] if dh else None,
            "tick_dh": dh["dh"] if dh else None, "near": k.get("near"), "fN": k.get("fN"),
            "wall": rec["wall"]}

    # C6 settle: window margin (parse raw PASS line)
    for name, rec in rows:
        if rec["arm"] != "settle":
            continue
        pl = first_pass(name)
        samples = {}
        for m in re.finditer(
                r"f(\d+)=n\[y=([-\d.]+),vy=([-\d.]+)\] c\[y=([-\d.]+),cnt=(\d+),ent=(\d+)\] "
                r"so\[y=([-\d.]+),sl=(\w+)\] sf\[y=([-\d.]+),sl=(\w+)\]", pl):
            samples[int(m.group(1))] = {
                "n_y": float(m.group(2)), "c_y": float(m.group(4)), "cnt": int(m.group(5)),
                "ent": int(m.group(6)), "so_y": float(m.group(7)), "so_sl": m.group(8),
                "sf_y": float(m.group(9)), "sf_sl": m.group(10)}
        k = kv(pl)
        C.setdefault("settle", {})[name] = {
            "samples": samples, "ncb": k.get("ncb"), "pf_delta": k.get("pf_delta"),
            "tick_dh": k.get("tick_dh"), "wall": rec["wall"],
            "n_rest_margin": samples.get(60, {}).get("n_y") == samples.get(120, {}).get("n_y")
            if 60 in samples and 120 in samples else None,
        }

    with open("analyze_boundary.json", "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)

    # ---- table --------------------------------------------------------------
    print("%-34s %-10s %3s %-14s %-14s %-9s %s" % ("cell", "arm", "reps", "rc", "pass/err u", "pair", "at/err"))
    for name, rec in rows:
        print("%-34s %-10s %3d %-14s %-14s %-9s %s" % (
            name, rec["arm"], rec["reps"], "".join(str(r) for r in rec["rc"]),
            "%d/%d" % (rec["pass_uniq"], rec["err_uniq"]), ",".join(rec["pair"]),
            (";".join(a.split(" ")[0] for a in rec["at"])[:30]) + (" e=%d" % len(rec["err_class"]) if rec["err_class"] else "")))
    print()
    print("== pins ==")
    for name, d in sorted(C["pins"].items()):
        print("%-30s all_ok=%s per_rep=%s" % (name, d["all_ok"], d["per_rep"]))
    print()
    print("== claims ==")
    for claim in ("order", "lag", "damp", "impulse", "backend", "stall", "settle"):
        for name, cd in sorted(C.get(claim, {}).items()):
            if claim in ("order",):
                print("%s %-28s ncb=%s/%s pfd=%s/%s 1to1=%s pair=%s cb0=%s,%s f1=%s cb0eq1=%s cb0eq2=%s" % (
                    claim, name, cd.get("ncb"), cd.get("frames"), cd.get("pf_delta"), cd.get("frames"),
                    cd.get("tick_1to1"), cd.get("pair"), cd.get("cb0_ty"), cd.get("cb0_vy"),
                    cd.get("f1"), cd.get("cb0_eq_f1"), cd.get("cb0_eq_f2")))
            elif claim == "lag":
                print("lag %-28s tps=%s n=%s/%s dy=%s cf=%s ok=%s dvy=%s a_y=%s cf=%s ok=%s b_y=%s cf=%s ok=%s pre=%s/%s post=%s/%s" % (
                    name, cd["tps"], cd["n"], cd["frames"], cd["dy"], cd["exp_dy"], cd["dy_ok"],
                    cd["dvy"], cd["a_y"], cd["a_y_cf"], cd["a_ok"], cd["b_y"], cd["b_y_cf"], cd["b_ok"],
                    cd["bpre"], cd["bpre_cf"], cd["bpost"], cd["bpost_cf"]))
            elif claim == "damp":
                lanes = " ".join("%s:%s/%s%s" % (l, v["y"], v["y_cf"], "" if v["ok"] else "!FAIL")
                                 for l, v in cd["lanes"].items())
                print("damp %-28s tps=%s ncb=%s tld_ok=%s | %s" % (name, cd["tps"], cd["ncb"], cd["tld_ok"], lanes))
            elif claim == "impulse":
                bad = {l: v for l, v in cd.items() if v.get("w_ok") is False or v.get("v_ok") is False}
                print("impulse %-28s lanes=%d failing=%s" % (name, len(cd), json.dumps(bad, sort_keys=True)))
            elif claim == "backend":
                print("backend %-28s cfg2d=%-10s id2d=%-22s dss2d=%-32s drop=%s ncb=%s tld=%s" % (
                    name, cd["cfg2d"], cd["id2d"], cd["dss2d"], cd["drop"], cd["ncb"], cd["tld"]))
            elif claim == "stall":
                print("stall %-28s %s ncb=%s/%s 1to1=%s dh=%s wall=%s" % (
                    name, cd["stall"], cd["ncb"], cd["frames"], cd["tick_1to1"], cd["tick_dh"], cd["wall"]))
            elif claim == "settle":
                print("settle %-28s ncb=%s pf=%s samples=%s margin=%s wall=%s" % (
                    name, cd["ncb"], cd["pf_delta"], json.dumps(cd["samples"], sort_keys=True), cd["n_rest_margin"], cd["wall"]))
    print()
    print("== comcase ==")
    for case, cd in sorted(C["comcase"].items()):
        print("%-34s err=%s rc=%s at=%s uniq=%s" % (case, cd["err_counts"], cd["rc"], cd["at"], cd["pass_uniq"]))


if __name__ == "__main__":
    main()
