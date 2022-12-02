def initialize():
    global all_conns, active_conns, till, accept, server
    global host, port
    all_conns = {}
    active_conns = {}
    till, accept = False, False
    server = None
    host, port = '192.168.29.17', 3784
