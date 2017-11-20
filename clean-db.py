"""Removes unnecessary objects from the database to speed up load time."""

import os
import os.path
from shutil import rmtree

if __name__ == '__main__':
    folders = 0
    for name in ('Revision', 'CommunicationChannelMessage', 'LoggedCommand'):
        directory = os.path.join('world', name)
        if os.path.isdir(directory):
            print(f'Deleteing directory {directory}.')
            rmtree(directory)
            folders += 1
        else:
            print(f'No directory named {directory}.')
    print(f'Folders deleted: {folders}.')
