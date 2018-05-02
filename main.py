"""Server entry point."""

import logging
from time import time
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from twisted.internet import reactor, error
from server.server import server
from server.db import ServerOptions, Task, session, Base, load_db, finalise_db
from server.program import build_context
from server.log_handler import LogHandler
from server.tasks import tasks_task, tasks_errback

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-i', '--import-yaml', default=None,
    help='Import a previously-dumped database'
)

parser.add_argument(
    '-o', '--options-id', type=int, default=1,
    help='The ID of the server options to run the server with'
)

parser.add_argument(
    '-l', '--log-file', type=FileType('w'), default='mindspace.log',
    metavar='FILENAME', help='Where to log server output'
)

parser.add_argument(
    '-L', '--log-level', default='INFO', help='The default logging level'
)

parser.add_argument(
    '-F', '--log-format',
    default='[%(asctime)s] %(name)s.%(levelname)s: %(message)s',
    help='The format of log messages'
)

parser.add_argument(
    '-t',
    '--test-db',
    action='store_true',
    help='Try and load the database then exit'
)

parser.add_argument(
    'private_key', metavar='PRIVATE-KEY', help='Private key file'
)

parser.add_argument(
    'cert_key', metavar='CERTIFICATE-KEY', help='Certificate key file'
)


def log_number_of_objects():
    """Log the number of objects in the base."""
    logging.info('Objects in database: %d.', Base.number_of_objects())


if __name__ == '__main__':
    started = time()
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level, format=args.log_format,
        stream=args.log_file
    )
    started = time()
    logging.info('Creating database tables...')
    Base.metadata.create_all()
    if args.import_yaml:
        if Base.number_of_objects():
            logging.critical('Refusing to import while there are objects present in the database.')
        else:
            load_db(args.import_yaml)
    finalise_db()
    log_number_of_objects()
    if args.test_db:
        logging.info('Database loaded successfully.')
        raise SystemExit
    ServerOptions.instance_id = args.options_id
    if ServerOptions.get() is None:
        logging.critical('Invalid ID for server options: %d.', args.options_id)
    else:
        logging.info('Using server options: %s.', ServerOptions.get())
    build_context()
    try:
        server.start_listening(args.private_key, args.cert_key)
        tasks_task.start(1.0, now=False).addErrback(tasks_errback)
    except error.CannotListenError as e:
        logging.critical('Listening failed.')
        logging.exception(e)
        raise SystemExit
    handler = LogHandler()
    logger = logging.getLogger()
    logger.addHandler(handler)
    with session() as s:
        for t in Task.query():
            t.next_run = time() + t.interval
            s.add(t)
    logging.info('Initialisation completed in %.2f seconds.', time() - started)
    reactor.run()
    logging.info('Server quitting.')
    log_number_of_objects()
