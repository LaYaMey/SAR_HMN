#!/usr/bin/env python3

import socket
import sys
import os
import szasar

class SarClient:
    def __init__(self, server='localhost', port=6012):
        self.SERVER = server
        self.PORT = port
        
        self.List, self.Download, self.Upload, self.Delete, self.Exit = range(1, 6)
        self.Options = ("File list", "Download file", "Upload file", "Delete file", "Exit")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.SERVER, self.PORT))

        self.ER_MSG = [
            "Correct.",
            "Unknown or unexpected command.",
            "Unknown user.",
            "Incorrect passphrase or password.",
            "Error creating file list.",
            "File does not exist.",
            "Error downloading the file.",
            "Anonymous user does not have permission for this operation.",
            "The file is too large.",
            "Error preparing the file for upload.",
            "Error uploading the file.",
            "Error deleting the file."
        ]


    def iserror(self, message):
        if message.startswith("ER"):
            code = int(message[2:])
            print(self.ER_MSG[code])
            return True
        else:
            return False

    def int2bytes(self, n):
        if n < 1 << 10:
            return str(n) + " B  "
        elif n < 1 << 20:
            return str(round(n / (1 << 10))) + " KiB"
        elif n < 1 << 30:
            return str(round(n / (1 << 20))) + " MiB"
        else:
            return str(round(n / (1 << 30))) + " GiB"
        
    def login(self, user, password):
        #returns False if failed, True if successful

        message = f"{szasar.Command.User}{user}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        if self.iserror(message):
            return False

        message = f"{szasar.Command.Password}{password}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        if not self.iserror(message):
            return True
        
    def listfiles(self):
        message = f"{szasar.Command.List}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        if self.iserror(message):
            return
        filecount = 0
        print("List of available files")
        print("-------------------------------")
        while True:
            line = szasar.recvline(self.socket).decode("ascii")
            if line:
                filecount += 1
                fileinfo = line.split('?')
                print("{:<20} {:>8}".format(fileinfo[0], self.int2bytes(int(fileinfo[1]))))
            else:
                break
        print("-------------------------------")
        if filecount == 0:
            print("No files available.")
        else:
            plural = "s" if filecount > 1 else ""
            print("{0} file{1} available{1}.".format(filecount, plural))
        return

        
    def download(self, filename):
        message = f"{szasar.Command.Download}{os.path.split(filename)[1]}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        if self.iserror(message):
            return
        filesize = int(message[2:])
        message = f"{szasar.Command.Download2}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        if self.iserror(message):
            return
        filedata = szasar.recvall(self.socket, filesize)
        try:
            with open(filename, "wb") as f:
                f.write(filedata)
        except:
            print("Could not save the file to disk.")
        else:
            print("File {} downloaded successfully.".format(os.path.split(filename)[1]))
        return
    
    def upload(self, filename):
        try:
            filesize = os.path.getsize(filename)
            with open(filename, "rb") as f:
                filedata = f.read()
        except:
            print("Could not access the file {}.".format(filename))
            return

        message = f"{szasar.Command.Upload}{os.path.split(filename)[1]}?{filesize}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        if self.iserror(message):
            return

        message = f"{szasar.Command.Upload2}\r\n"
        self.socket.sendall(message.encode("ascii"))
        self.socket.sendall(filedata)
        message = szasar.recvline(self.socket).decode("ascii")
        if not self.iserror(message):
            print("File {} uploaded successfully.".format(os.path.split(filename)[1]))
        return
    
    def delete(self, filename):
        message = f"{szasar.Command.Delete}{os.path.split(filename)[1]}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        if not self.iserror(message):
            print("File {} deleted successfully.".format(os.path.split(filename)[1]))
        return

    def exit(self):
        message = f"{szasar.Command.Exit}\r\n"
        self.socket.sendall(message.encode("ascii"))
        message = szasar.recvline(self.socket).decode("ascii")
        self.socket.close()
        return


    def run_ui(self):
        
        while True:
            user = input("Enter the username: ")
            message = f"{szasar.Command.User}{user}\r\n"
            self.socket.sendall(message.encode("ascii"))
            message = szasar.recvline(self.socket).decode("ascii")
            if self.iserror(message):
                continue

            password = input("Enter the password: ")
            message = f"{szasar.Command.Password}{password}\r\n"
            self.socket.sendall(message.encode("ascii"))
            message = szasar.recvline(self.socket).decode("ascii")
            if not self.iserror(message):
                break

        while True:
            option = self.menu()

            if option == self.List:
                self.listfiles()
                continue

            elif option == self.Download:
                filename = input("Enter the file you want to download: ")
                self.download(filename)
                continue 

            elif option == self.Upload:
                filename = input("Enter the file you want to upload: ")
                self.upload(filename)
                continue

            elif option == self.Delete:
                filename = input("Enter the file you want to delete: ")
                self.delete(filename)
                continue

            elif option == self.Exit:
                self.exit()
                break
        self.socket.close()


    def menu(self):
        print("+{}+".format('-' * 30))
        for i, option in enumerate(self.Options, 1):
            print("| {}.- {:<25}|".format(i, option))
        print("+{}+".format('-' * 30))

        while True:
            try:
                selected = int(input("Select an option: "))
            except:
                print("Invalid option.")
                continue
            if 0 < selected <= len(self.Options):
                return selected
            else:
                print("Invalid option.")

if __name__ == "__main__":
    sar_client = SarClient()
    sar_client.run_ui()
