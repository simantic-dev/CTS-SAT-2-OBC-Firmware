#!/bin/sh
# Runs the committed CTS-SAT-2 OBC firmware (STM32L4R5ZI) with a scripted ground station over USART2.
# Pass = boot banner, heartbeat, telecommand replies (config set/get, time sync, error paths) all appear; no fault.
cd "$(dirname "$0")/.." || exit 1
log=$(mktemp)
trap 'rm -f "$log"' EXIT
${SIM:-sim} run --scenario sim/scenario.yaml --ascii usart2 --timeout 15 >"$log" 2>&1
rc=0
for s in "USART2 ready. Buffered RX active." HEARTBEAT "HELLO WORLD" "Firmware Version: 0.1.0" \
  "Variable: config_demo_variable1 = U32(456)" "Unix time synchronized" "ERR: Unknown telecommand" "System Uptime: "; do
  if grep -qF "$s" "$log"; then echo "ok   $s"; else echo "FAIL $s"; rc=1; fi
done
if grep -qiE "HardFault|panic|Guru" "$log"; then echo "FAIL fault in log"; rc=1; else echo "ok   no fault"; fi
exit $rc
