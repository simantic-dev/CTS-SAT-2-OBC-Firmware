"""Ground station on the OBC umbilical UART (USART2 PD5 TX / PD6 RX, 115200 8N1): sends each telecommand in TCMDS at
its virtual time (seconds). The firmware's replies are plain text on the same UART, logged as `(usart2) ...`."""

TIMEA = "#TIMEA,USB1,0,50.5,FINESTEERING,2209,515163.000,02000020,9924,16809;VALID,-2.501488425e-09,6.133312031e-10,-17.99999999630,2026,10,3,16,36,45000,VALID*1100ad64"

TCMDS = [
    (2.0, "CTS2+hello_world()!"),
    (3.0, "CTS2+get_obc_info()!"),
    (4.0, "CTS2+get_config(heartbeat_ms)!"),
    (5.0, "CTS2+set_config(config_demo_variable1,u32(456))!"),
    (6.0, "CTS2+get_config(config_demo_variable1)!"),
    (7.0, "CTS2+get_unix_time()!"),
    (8.0, "CTS2+set_unix_time(1791045405000)!"),
    (9.0, "CTS2+get_unix_time()!"),
    (10.0, "CTS2+get_timestamp(" + TIMEA + ")!"),
    (11.0, "CTS2+get_sys_uptime()!"),
    (12.0, "CTS2+no_such_command()!"),
]


class Peer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.todo = sorted(TCMDS)
        self._arm()

    def _arm(self):
        if self.todo:
            self.ctx.schedule_oneshot_ns(max(1, int(self.todo[0][0] * 1e9) - self.ctx.now_ns))

    def on_timer(self):
        while self.todo and int(self.todo[0][0] * 1e9) <= self.ctx.now_ns:
            cmd = self.todo.pop(0)[1]
            self.ctx.info(f"GROUND TX {cmd}")
            self.ctx.send(cmd.encode())
        self._arm()

    def on_byte(self, b):
        pass
