#!/usr/bin/env bash
# Run the firmware in the simulator, check the expected output, and draw the timeline PNG.
# Needs `sim` (https://simantic.com) on PATH and python3 with matplotlib for the plot.
set -euo pipefail
cd "$(dirname "$0")"
sim run --scenario scenario.yaml --ascii usart2 --timeout 15 | tee run.log
for s in "USART2 ready. Buffered RX active." HEARTBEAT "HELLO WORLD" "Firmware Version: 0.1.0" \
  "Commit Hash: 0515f868369790b7517db6b6191616c27b17233a" "Variable: heartbeat_ms = U32(1000)" \
  "Variable: config_demo_variable1 = U32(456)" "ERR: Unix time not synchronized" "Unix time synchronized" \
  "ERR: Unknown telecommand" "System Uptime: "; do
  grep -qF "$s" run.log && echo "PASS  $s" || { echo "FAIL  $s"; exit 1; }
done
! grep -qE "HardFault|panicked" run.log && echo "PASS  no HardFault/panic"
python3 plot.py run.log timeline.png
