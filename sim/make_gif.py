"""Animates run.log (the sim's own UART capture) into timeline.gif. Usage: make_gif.py run.log out.gif "tag" (matplotlib, pillow)"""
import re, sys, io
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
rx = re.compile(r"\[([\d.]+)s\] \(usart2 (←|→) ground\) (.*)")
tx, rep, hb = [], [], []
for line in open(sys.argv[1]):
    m = rx.match(line)
    if not m: continue
    t, d, s = float(m[1]), m[2], m[3]
    if d == "←": tx.append((t, s.split("(")[0].replace("CTS2+", "")))
    elif "HEARTBEAT" in s: hb.append(t)
    else: rep.append(t)
lat = [(t, n, (next(r for r in rep if r >= t) - t) * 1000) for t, n in tx]
end = max(hb); frames = []
for k in range(1, 41):
    tc = end * k / 40
    fig, (a, b) = plt.subplots(2, 1, figsize=(7, 4.6), dpi=70, sharex=True, gridspec_kw={"height_ratios": [1, 2]})
    h = [x for x in hb if x <= tc]
    a.vlines(h, 0, 1, color="tab:green", lw=1); a.set_yticks([]); a.set_ylabel(f"heartbeat\n({len(h)})", fontsize=7)
    l = [x for x in lat if x[0] <= tc]
    b.bar([x[0] for x in l], [x[2] for x in l], width=.5, color="tab:blue")
    for t, n, ms in l: b.text(t, ms + 1, n, rotation=60, fontsize=6, ha="left", va="bottom")
    b.set_xlim(0, end + 1); b.set_ylim(0, max(x[2] for x in lat) * 1.8)
    b.set_ylabel("telecommand to first reply, ms", fontsize=7); b.set_xlabel("virtual time, s")
    a.set_title(f"CTS-SAT-2 OBC firmware on simulated L4R5, t={tc:.1f} s virtual, {sys.argv[3]}", fontsize=8)
    fig.tight_layout(); bf = io.BytesIO(); fig.savefig(bf, format="png"); plt.close(fig)
    frames.append(Image.open(bf).convert("RGB").quantize(colors=64, dither=Image.Dither.NONE))
frames[0].save(sys.argv[2], save_all=True, append_images=frames[1:], duration=[120] * 39 + [1500], loop=0, optimize=True)
