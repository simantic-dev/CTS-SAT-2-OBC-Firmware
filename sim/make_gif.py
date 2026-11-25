"""Builds timeline.gif (a ground-station view) from run.log, the run's own UART capture. Pillow + ffmpeg only.
usage: python3 make_gif.py run.log timeline.gif <sim-version>      (run from sim/)"""
import os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gifkit import *

LOG, OUT, VER = sys.argv[1:4]
ev = []   # (t, direction, text)
for l in open(LOG, errors="replace"):
    m = re.match(r"\[([\d.]+)s\] \(usart2 (←|→) ground\) (.*)", l.rstrip("\n"))
    if m: ev.append((float(m[1]), "tx" if m[2] == "←" else "rx", m[3]))
cmds = []   # {t, name, args, replies [(t, text)]}
beats = []
for t, d, s in ev:
    if d == "tx":
        m = re.match(r"CTS2\+(\w+)\((.*)\)!", s)
        cmds.append(dict(t=t, name=m[1], args=m[2], rep=[]))
    elif s == "HEARTBEAT": beats.append(t)
    elif cmds and t - cmds[-1]["t"] < 0.9 and re.match(r"[\w ]*[:A-Z]", s): cmds[-1]["rep"].append((t, s))
boot = [(t, s) for t, d, s in ev if d == "rx" and t < 0.1 and s != "HEARTBEAT"]
con = [(t, "ERROR" if s.startswith("ERR") else "INFO", ("> " if d == "tx" else "") + s) for t, d, s in ev]

def rep(c, t): return [x for x in c["rep"] if x[0] <= t]
def find(name, pat, t, group=1):
    for c in cmds:
        for rt, s in rep(c, t):
            if c["name"] == name:
                m = re.search(pat, s)
                if m: return m[group], rt
    return None, None

def draw(c, t):
    c.header("CTS-SAT-2 OBC: flight firmware on a simulated STM32L4R5", "ground-station view of the run: telecommands up the umbilical UART, replies and heartbeat back, the OBC's own console", t)
    sync_t = next((rt for k in cmds for rt, s in k["rep"] if s == "Unix time synchronized"), None)
    c.panel(24, 84, 1232, 92, "Time-sync state (what get_unix_time answers: 'ERR: Unix time not synchronized' until set_unix_time)")
    synced = sync_t is not None and sync_t <= t
    c.chain(40, 112, 1200, 54, ["BOOTED, time NOT SYNCHRONIZED", "UNIX TIME SYNCHRONIZED"], 1 if synced else 0, [boot[0][0] if t >= boot[0][0] else None, sync_t if synced else None], [AMBER, GREEN], 17)
    c.panel(24, 188, 800, 330, "Telecommands from the ground and the OBC's replies")
    y = 222
    for k in cmds:
        if k["t"] > t: break
        r = rep(k, t)
        c.text(38, y, f"{k['t']:6.2f}s", 14, DIM, False, True)
        c.text(116, y, k["name"] + ("(..)" if k["args"] else "()"), 14, CYAN, False, True)
        if r:
            txt = r[0][1]; err = txt.startswith("ERR")
            c.text(310, y, f"{(r[0][0] - k['t']) * 1000:4.0f} ms", 14, DIM, False, True)
            c.text(385, y, txt[:50], 14, RED if err else GREEN, False, True)
        else: c.text(310, y, "waiting...", 14, AMBER, False, True)
        y += 24
    ver, _ = find("get_obc_info", r"Firmware Version: (\S+)", t); com, _ = find("get_obc_info", r"Commit Hash: (\w{7})", t)
    bts, _ = find("get_obc_info", r"Build Timestamp \(UNIX\): (\d+)", t)
    hb, _ = find("get_config", r"heartbeat_ms = U32\((\d+)\)", t); cv, _ = find("get_config", r"config_demo_variable1 = U32\((\d+)\)", t)
    ut, _ = find("get_unix_time", r"Unix time: (\d+) ms", t); up, _ = find("get_sys_uptime", r"System Uptime: (\d+) ms", t)
    nb = len([b for b in beats if b <= t])
    rc = next((s.replace("System reset cause: ", "") for tt, s in boot if "reset cause" in s and tt <= t), None)
    cards = [("OBC identity (get_obc_info)", f"firmware {ver}, commit {com}, built {time.strftime('%Y-%m-%d', time.gmtime(int(bts)))}" if ver else "no command yet", f"last reset cause: {rc}"),
             ("Config store", f"heartbeat_ms = {hb}" if hb else "-", f"config_demo_variable1 = {cv}" if cv else ""),
             ("Clock", ("synchronized" if synced else "not synchronized"), (time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(int(ut) / 1000)) + f".{int(ut) % 1000:03d}") if ut else ""),
             ("Uptime reply (get_sys_uptime)", f"{up} ms" if up else "no command yet", ""),
             ("Heartbeat task", f"{nb} HEARTBEAT lines so far", f"last at {[b for b in beats if b <= t][-1]:.3f} s, every 0.5 s" if nb else "")]
    for i, (nm, a, b) in enumerate(cards):
        yy = 188 + i * 66
        c.panel(836, yy, 420, 60)
        c.text(848, yy + 6, nm, 14, CYAN, True)
        c.text(848, yy + 24, a[:52], 14, FG, False, True); c.text(848, yy + 41, b[:52], 14, FG, False, True)
    c.log(24, 530, 1232, 156, con, t, "OBC umbilical UART (USART2): console lines, and the '>' telecommands the ground sent", 14)
    c.footer(VER, SPEED)

SPEED = 15.0 / 15
n = render(draw, 15.0, SPEED, OUT)
print("frames", n)
