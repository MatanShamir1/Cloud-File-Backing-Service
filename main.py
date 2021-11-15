# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    import os

    path = "C:/workspace/python"
    # we shall store all the file names in this list
    filelist = []

    for root, dirs, files in os.walk(path):
        for file in files:
            # append the file name to the list
            filelist.append(os.path.join(root, file))

    # print all the file names
    for name in filelist:
        print(name)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
