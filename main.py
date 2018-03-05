"""Server entry point."""

import logging
from time import time
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from twisted.internet import reactor, error
from server.server import server
from server.db import load_db, dump_db, ServerOptions, Task, session, Base
from server.program import build_context
from server.log_handler import LogHandler
from server.tasks import tasks_task, tasks_errback

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-o', '--options-id', type=int, default=1,
    help='The ID of the server options to run the server with'
)

parser.add_argument(
    '-l', '--log-file', type=FileType('w'), default='mindspace.log',
    metavar='FILENAME', help='Where to log server output'
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


if __name__ == '__main__':
    started = time()
    args = parser.parse_args()
    logging.basicConfig(
        level='INFO', format='%(name)s.%(levelname)s: %(message)s',
        stream=args.log_file
    )
    started = time()
    load_db()
    logging.info(
        'Objects loaded: %d (%.2f seconds).', Base.number_of_objects(),
        time() - started
    )
    if args.test_db:
        logging.info('Database loaded successfully.')
        raise SystemExit
    ServerOptions.instance_id = args.options_id
    if ServerOptions.get() is None:
        logging.critical('Invalid ID for server options: %d.', args.options_id)
    else:
        logging.info(repr(ServerOptions.get()))
    build_context()
    try:
        server.start_listening(args.private_key, args.cert_key)
        tasks_task.start(1.0, now=False).addErrback(tasks_errback)
    except error.CannotListenError as e:
        logging.critical('Listening failed.')
        logging.exception(e)
        raise SystemExit
    logging.getLogger().addHandler(LogHandler())
    with session() as s:
        for t in Task.query():
            t.next_run = time() + t.interval
            s.add(t)
    logging.info('Initialisation completed in %.2f seconds.', time() - started)
    reactor.run()
    started = time()
    n = dump_db()
    logging.info(
        'Objects dumped: %d (%.2f seconds).', Base.number_of_objects(),
        time() - started
    )
