"""Removes unnecessary objects from the database to speed up load time."""

from server.server import server  # noqa
from server.db import (
    load_db, dump_db, CommunicationChannelMessage, Revision, LoggedCommand,
    session
)

if __name__ == '__main__':
    load_db()
    with session() as s:
        objects = 0
        for cls in (Revision, CommunicationChannelMessage, LoggedCommand):
            objects += cls.query().delete()
    if objects:
        dump_db()
        print('Cleaned objects: %d.' % objects)
    else:
        print('Nothing to do.')
