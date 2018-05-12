"""Server entry point."""

import os.path
import logging
from time import time
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from twisted.internet import reactor, error
from twisted.internet.task import LoopingCall
from server.server import server
from server.db import load_db, dump_db, ServerOptions, Task, session, Base
from server.program import build_context
from server.log_handler import LogHandler
from server.tasks import start_tasks

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
    'private_key', nargs='?', metavar='PRIVATE-KEY',
    default=os.path.join('certs', 'privkey.pem'), help='Private key file'
)

parser.add_argument(
    'cert_key', nargs='?', metavar='CERTIFICATE-KEY',
    default=os.path.join('certs', 'fullchain.pem'), help='Certificate key file'
)


if __name__ == '__main__':
    started = time()
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level, format=args.log_format,
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
    if ServerOptions.instance() is None:
        logging.critical('Invalid ID for server options: %d.', args.options_id)
    else:
        logging.info('Using server options: %s.', ServerOptions.instance())
    build_context()
    try:
        server.start_listening(args.private_key, args.cert_key)
    except error.CannotListenError as e:
        logging.critical('Listening failed.')
        logging.exception(e)
        raise SystemExit
    handler = LogHandler()
    logger = logging.getLogger()
    logger.addHandler(handler)
    with session():
        Task.query(Task.next_run.isnot(None)).update({Task.next_run: None})
    start_tasks_task = LoopingCall(start_tasks)
    start_tasks_task.start(
        ServerOptions.get().auto_start_tasks, now=True
    ).addErrback(
        lambda err: logging.exception(err.getTraceback())
    )
    logging.info('Initialisation completed in %.2f seconds.', time() - started)
    reactor.run()
    started = time()
    # Reactor has finished, let's stop writing to the database.
    logger.removeHandler(handler)
    dump_db()
    logging.info(
        'Objects dumped: %d (%.2f seconds).', Base.number_of_objects(),
        time() - started
    )
