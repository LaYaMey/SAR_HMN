import time
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import tkinter as tk
from tkinter import filedialog

from cli_class import SarClient
# Define your event handler class
class WachHundClient(FileSystemEventHandler):
    def __init__(self, user="sar", password="sar"):
        super().__init__()
        # Start SAR client and login
        self.sar_client = SarClient()
        self.sar_client.login(user, password)


        
    def on_any_event(self, event):

        if event.event_type == "closed":
            #current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            #print(f"[{current_time}] Event key: {event.key}")

            self.sar_client.upload(event.src_path)
            return
        
        if event.event_type == "deleted":
            #current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            #print(f"[{current_time}] Event key: {event.key}")

            self.sar_client.delete(event.src_path)
            return
        
        if event.event_type == "created":
            #current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            #print(f"[{current_time}] Event key: {event.key}")

            self.sar_client.upload(event.src_path)
            return
        
        if event.event_type == "moved":
            #current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            #print(f"[{current_time}] Event key: {event.key}")

            self.sar_client.delete(event.src_path)
            if os.path.split(event.dest_path)[0] == os.path.split(event.src_path)[0]:
                self.sar_client.upload(event.dest_path)
            return
        


def select_folder_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    folder_path = filedialog.askdirectory()
    
    return folder_path



if __name__ == "__main__":
    # Set the directory to monitor
    path_to_monitor = select_folder_dialog()
    # Start monitoring the directory for file system events
    print(f"Monitoring directory at: {path_to_monitor}")
    event_handler = WachHundClient()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_monitor, recursive=True)
    observer.start()
    

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()



    

