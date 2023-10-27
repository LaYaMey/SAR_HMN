#!/bin/bash

#install the needed python libary
#sudo apt-get install gnome-terminal
python3 -m pip install -U watchdog



#start the server and the client
gnome-terminal -- python3 -q cloud_service/serv_fich.py
gnome-terminal -- python3 -q cloud_service/wach_hund.py
