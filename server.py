import socket
# this is the main function: in here, the client creates the communication.
import string
import sys
import time
import os
import watchdog
import random


# this function checks validation of the input. if valid, file name is returned to main function.
def check_validation(argv):
    # in case the number of arguments (first one is script path, second-port of server) isn't 2, terminate program.
    if len(argv) != 2:
        print("number of arguments incorrect: enter 1 argument, a valid port number-terminating")
        sys.exit(1)
    # if the port number is not valid, terminate the program. the cases are- its not an integer\its not in the range.
    # only if the first condition is met, the int casting happens and thus the whole statement passes interpretation.
    if not argv[1].isdigit() or not (1 <= int(argv[1]) <= 65535):
        print("port number isn't valid-terminating")
        sys.exit(1)


def create_file(path):
    directory_list = path.split("\\")
    for directory in directory_list[:-1]:
        if not os.path.isdir(directory):
            os.mkdir(directory)
        os.chdir(directory)
    file = open(directory_list[-1],"wb")
    return file


def receive_all_files(client_socket):
    # sign in and receive
    # send 128 random id
    id_dir = ''.join(random.choices(string.ascii_uppercase + string.digits, k=128))
    client_socket.send(bytes(id_dir))
    os.mkdir(id_dir)
    os.chdir(id_dir)
    while True:
        path_length = client_socket.recv(8)
        if (path_length == -1):
            break
        path = client_socket.recv(int(path_length))
        # initiate new file in the specified path
        file = create_file(path)
        file_length = client_socket.recv(8)
        file_bytes = client_socket.recv(int(file_length))
        file.write(file_bytes)
        # write the information into the new file


def send_all_files(id, s):
    os.chdir(id)
    # push all files to server
    # we shall store all the file names in this list
    filelist = []
    for root, dirs, files in os.walk():
        for file in files:
            # append the file name to the list
            filelist.append(os.path.join(root, file))
    for path in filelist:
        try:
            # check that the given file name exists in our directory,
            # and open the file given as arguments and read its bytes into byte-type variable 'file'.
            file = open(path, "rb")
            # check that the given ip argument is valid using a specific function in python 3:
            socket.inet_aton(path)
        except IOError:
            print("file name isn't valid: file doesn't exist, or ip address isn't valid- terminating")
            sys.exit(1)
        s.send(int.to_bytes(len(path), 8, 'little') + path)
        s.send(int.to_bytes(len(file.read()), 8, 'little') + file.read())
    s.send(int.to_bytes(-1, 8, 'little'))


def on_created(client_socket):
    path_len = client_socket.recv(8)
    path = client_socket.recv(int(path_len))
    create_file(path)


def on_deleted(client_socket):
    path_len = client_socket.recv(8)
    path = client_socket.recv(int(path_len))
    os.remove(path)


##############
def on_modified(client_socket):
    pass


def on_moved(client_socket):
    src_path_len = client_socket.recv(8)
    src_path = client_socket.recv(int(src_path_len))
    dest_path_len = client_socket.recv(8)
    dest_path = client_socket.recv(int(dest_path_len))
    create_file(dest_path)
    #now move all data from src to dest
    src_file = open(src_path, 'rb')
    dest_file = open(dest_path, 'wb')
    all_data = src_file.read()
    dest_file.write(all_data)
    os.remove(src_path)


def main(argv):
    check_validation(argv)
    #make sure in relevant directory
    if not os.path.isdir("mother_dir"):
        os.mkdir("mother_dir")
    os.chdir("mother_dir")
    # check validation of arguments in another function: this will terminate program politely for invalid inputs.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tie up a port to this port. if the port wouldn't be specified, os would choose the port independently.
    # as a server program, the port must be specified, in order for clients' request to know which port to
    # use as the destination port when trying to communicate with the server application.
    server.bind(('', int(argv[1])))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()
        data = client_socket.recv(128)
        if data == 0:
            receive_all_files(client_socket)
        else:
            send_all_files(data, client_socket)
        while True:
            action = client_socket.recv(5)
            if action == b'create':
                on_created(client_socket)
            elif action == b'delete':
                on_deleted()
            elif action == b'modify':
                on_modified()
            elif action == b'moveee':
                on_moved()

        client_socket.close()


# this is a call to the main function.
if __name__ == '__main__':
    main(sys.argv)

    # for root, dirs, files in os.walk(path):
    #     name = root.split('\\')[-1]
    #     s.send(name.encode('utf-8'))
    #     for file in files:
    #         # append the file name to the list
    #         name = os.path.basename(os.path.join(root, file))
