import socket as sock


def initialize():
    global p, c, d, bl, g, y, r, b, u, e, fix, info, error
    p = '\033[95m'
    c = '\033[96m'
    d = '\033[36m'
    bl = '\033[94m'
    g = '\033[92m'
    y = '\033[93m'
    r = '\033[91m'
    b = '\033[1m'
    u = '\033[4m'
    e = '\033[0m'
    fix = f'[{bl}Fix{e}]'
    info = f'[{g}Info{e}]'
    error = f'[{r}Error{e}]'
    global all_conns, active_conns, till, accept, server
    global host, port
    all_conns = {}
    active_conns = {}
    till, accept = False, False
    server = None
    hostname = sock.gethostname()
    host, port = sock.gethostbyname(hostname), 4348
