import socket
# this is the main function: in here, the client creates the communication.
import sys
import time
import os
import socket
# this function checks validation of the input. if valid, file name is returned to main function.
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


def check_validation(argv):
    # in case the number of arguments (first one is script path, second-port of server, third- ip address, fourth-
    # name of txt placed in our folder) isn't 4, terminate program.
    if not len(argv) in {5, 6}:
        sys.exit(1)
    # if the port number is not valid, terminate the program. the cases are- its not an integer\its not in the range.
    # only if the first condition is met, the int casting happens and thus the whole statement passes interpretation.
    if not argv[1].isdigit() or not (1 <= int(argv[1]) <= 65535):
        print("port number isn't valid- terminating")
        sys.exit(1)
    # check validation of other arguments using try-except logic:
    try:
        # check that the given file name exists in our directory,
        # and open the file given as arguments and read its bytes into byte-type variable 'file'.
        file = open(argv[3], "rb")
        # check that the given ip argument is valid using a specific function in python 3:
        socket.inet_aton(argv[2])
    except IOError:
        print("file name isn't valid: file doesn't exist, or ip address isn't valid- terminating")
        sys.exit(1)
    return file


def create_file(path):
    directory_list = path.split("\\")
    for directory in directory_list[:-1]:
        if not os.path.isdir(directory):
            os.mkdir(directory)
        os.chdir(directory)
    file = open(directory_list[-1], "wb")
    return file


def send_all_files(s, path):
    s.send(b'0' * 128)
    s.recv(128)
    # push all files to server
    # we shall store all the file names in this list
    filelist = []
    for root, dirs, files in os.walk(path):
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


def receive_all_files(argv, s):
    id = argv[6]
    s.send(id)
    while True:
        path_length = s.recv(8)
        if path_length == -1:
            break
        path = s.recv(int(path_length))
        # initiate new file in the specified path
        file = create_file(path)
        file_length = s.recv(8)
        file_bytes = s.recv(int(file_length))
        file.write(file_bytes)


def on_created(event, s):
    s.send(b'create' + int.to_bytes(len(event.src_path), 8, 'little') + event.src_path)


def on_deleted(event, s):
    s.send(b'delete' + int.to_bytes(len(event.src_path), 8, 'little') + event.src_path)


def on_modified(event, s):
    s.send(b'modify' + int.to_bytes(len(event.src_path), 8, 'little') + event.src_path)


def on_moved(event, s):
    s.send(b'moveee' + int.to_bytes(len(event.src_path), 8, 'little') + event.src_path +
           int.to_bytes(len(event.dest_path), 8, 'little') + event.dest_path)


def monitor_files(argv, s):
    # set watchdog up
    patterns = ["*"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved
    path = "."
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(argv[5])
            #now observer synchronizes the server triggering event handler
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()


def main(argv):
    # check validation of arguments in another function: this will terminate program politely for invalid inputs.
    # also, if passed all tests, the file in bytes is returned.
    # file = check_validation(argv)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((argv[1], argv[2]))
    # if we didn't receive id- save my id from the server for all future connections.
    path = argv[3]
    if len(argv) is 5:
        send_all_files(s, path)
    else:
        receive_all_files(argv, s)
    monitor_files(argv, s)
    s.close()


# this is a call to the main function.
if __name__ == '__main__':
    main(sys.argv)
