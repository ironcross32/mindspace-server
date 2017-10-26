"""Removes unnecessary objects from the database to speed up load time."""

from server.db import (
    load_db, dump_db, CommunicationChannelMessage, Revision, LoggedCommand,
    session
)

if __name__ == '__main__':
    load_db()
    with session() as s:
        objects = 0
        for cls in (Revision, CommunicationChannelMessage, LoggedCommand):
            for obj in cls.query():
                objects += 1
                s.delete(obj)
    if objects:
        dump_db()
        print('Cleaned objects: %d.' % objects)
    else:
        print('Nothing to do.')
