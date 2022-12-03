import platform
import subprocess


def clear_screen():
    if platform.system() == 'Windows':
        subprocess.run('cls', shell=True)
    else:
        subprocess.run('clear', shell=True)
