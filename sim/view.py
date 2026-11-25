#!/usr/bin/env python3
"""Show the console that `sim run --ascii usart2` prints on stdin, live and unchanged (lines cut at 120 columns).
Only the sim's own `[ground] GROUND TX` peer log lines and its banner are dropped. On a terminal the last ROWS lines are
redrawn in place instead of scrolling."""
import collections, re, sys

ROWS = 28
shown = collections.deque(maxlen=ROWS)
LINE = re.compile(r"^\[[\d.]+s\] \(usart2 [←→] ground\)")


def emit(line):
    line = line[:120]
    if not sys.stdout.isatty():
        print(line, flush=True)
        return
    shown.append(line)
    sys.stdout.write("\033[H\033[J" + "\n".join(shown) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    if LINE.match(line):
        emit(line.rstrip("\n"))
