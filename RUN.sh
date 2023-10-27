#!/bin/bash

# Start the server in a new terminal
wsl bash -c "python3 /path/to/serv_fich.py; exec bash"



# Start the client in the same terminal (foreground)
python3 cli_fich.py
