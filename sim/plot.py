"""Timeline of a sim run: telecommands sent (ground -> OBC) and the reply latency, plus heartbeat ticks. Usage: plot.py run.log out.png"""
import re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rx = re.compile(r"\[([\d.]+)s\] \(usart2 (←|→) ground\) (.*)")
tx, rep, hb = [], [], []
for line in open(sys.argv[1]):
    m = rx.match(line)
    if not m:
        continue
    t, d, s = float(m[1]), m[2], m[3]
    if d == "←":
        tx.append((t, s.split("(")[0].replace("CTS2+", "")))
    elif "HEARTBEAT" in s:
        hb.append(t)
    else:
        rep.append(t)

lat = []  # (send time, ms until first reply line)
for t, name in tx:
    first = next((r for r in rep if r >= t), None)
    lat.append((t, name, (first - t) * 1000))

fig, (a, b) = plt.subplots(2, 1, figsize=(9, 6), sharex=True, gridspec_kw={"height_ratios": [1, 2]})
a.vlines(hb, 0, 1, color="tab:green", lw=1)
a.set_yticks([]); a.set_ylabel(f"heartbeat\n({len(hb)} in {max(hb):.0f} s)")
b.bar([l[0] for l in lat], [l[2] for l in lat], width=0.5, color="tab:blue")
for t, n, ms in lat:
    b.text(t, ms + 1, n, rotation=60, fontsize=8, ha="left", va="bottom")
b.set_ylabel("telecommand to first reply (ms)"); b.set_xlabel("virtual time (s)")
b.set_ylim(0, max(l[2] for l in lat) * 1.6)
fig.suptitle("CTS-SAT-2 OBC firmware on simulated STM32L4R5ZI: telecommands over USART2")
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=110)
print(f"wrote {sys.argv[2]}")
