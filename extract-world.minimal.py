import os
import logging
import os.path
from time import time
from zipfile import ZipFile
from server.db import (
    session, load_db, dump_db, Action, Advert, CommunicationChannel,
    CommunicationChannelBan, CommunicationChannelListener,
    CommunicationChannelMessage, Direction, Entrance, Object, ObjectKey,
    Player, Revision, Room, Zone, ServerOptions, Rule, HelpTopic,
    HelpKeyword, HelpTopicKeyword, ObjectRandomSound, RoomRandomSound, Mobile,
    Social
)

output_dir = 'world.minimal'

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    started = time()
    logging.info('Loading database...')
    n = load_db()
    logging.info('Loaded objects: %d.', n)
    with session() as s:
        logging.info('Deleting unnecessary stuff:')
        for obj in s.query(ObjectKey):
            logging.info('Deleting %r.', obj.hotkey)
            s.delete(obj.hotkey)
            logging.info('Deleting %r.', obj)
            s.delete(obj)
        for cls in (
            Action, Advert, CommunicationChannel, CommunicationChannelBan,
            CommunicationChannelListener, CommunicationChannelMessage,
            Direction, Entrance, Object, Player, Revision, Room, Zone,
            ServerOptions, ObjectRandomSound, Rule, HelpTopic, HelpKeyword,
            HelpTopicKeyword, RoomRandomSound, Social, Mobile
        ):
            logging.info('Table: %s.', cls.__table__.name)
            n = s.query(cls).delete()
            logging.info('Rows affected: %d.', n)
    dump_db(output_dir)
    logging.info(
        'Dumped database to %s after %.2f seconds.', output_dir,
        time() - started
    )
    logging.info('Creating zipfile...')
    zf = ZipFile(f'{output_dir}.zip', 'w')
    for base, directories, files in os.walk(output_dir):
        for filename in files:
            zf.write(os.path.join(base, filename))
    zf.close()
    logging.info('Zipfile created.')
