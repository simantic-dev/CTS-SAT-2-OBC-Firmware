#!/usr/bin/env python3
"""Turn the console that `sim run --ascii usart2` prints on stdin into one line per telecommand: command, then the
firmware's reply. HEARTBEAT lines are counted, not printed."""
import re, sys

LOG = re.compile(r"^\[([\d.]+)s\] \(usart2 → ground\) (.*)$")
cur, replies, beats = None, [], 0


def flush():
    if cur:
        cmd = cur if len(cur) <= 40 else cur[:37] + "..."
        print(f"{cmd:<40}  {' | '.join(replies)}", flush=True)


for line in sys.stdin:
    line = line.rstrip("\n")
    if line.startswith("[ground] GROUND TX CTS2+"):
        flush()
        cur, replies = line[len("[ground] GROUND TX CTS2+"):].rstrip("!"), []
        continue
    m = LOG.match(line)
    if not m:
        continue
    text = m[2]
    if text == "HEARTBEAT":
        beats += 1
    elif cur is None:
        print(f"boot: {text}", flush=True)
    else:
        text = re.sub(r"^(Variable|Unix time|System Uptime|Firmware Version|Build Timestamp \(UNIX\)|Commit Hash): ?", r"\1 ", text)
        replies.append(re.sub(r"commit (\w{7})\w+", r"commit \1", text.replace("Commit Hash ", "commit ").replace("Build Timestamp (UNIX) ", "build "))[:70])
flush()
print(f"HEARTBEAT lines from the firmware: {beats}")
