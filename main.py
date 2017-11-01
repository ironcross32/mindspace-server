"""Server entry point."""

import logging
from time import time
from argparse import ArgumentParser, FileType, ArgumentDefaultsHelpFormatter
from twisted.internet import reactor, error
from server.server import server
from server.db import load_db, dump_db, ServerOptions
from server.program import build_context
from server.log_handler import LogHandler

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-o', '--options-id', type=int, default=1,
    help='The ID of the server options to run the server with'
)

parser.add_argument(
    '-l', '--log-file', type=FileType('w'), default='mindspace.log',
    help='Where to log server output'
)

if __name__ == '__main__':
    args = parser.parse_args()
    logging.basicConfig(
        level='INFO', format='%(name)s.%(levelname)s: %(message)s',
        stream=args.log_file
    )
    started = time()
    n = load_db()
    logging.info('Objects loaded: %d (%.2f seconds).', n, time() - started)
    ServerOptions.instance_id = args.options_id
    if ServerOptions.get() is None:
        logging.critical('Invalid ID for server options: %d.', args.options_id)
    else:
        logging.info(repr(ServerOptions.get()))
    from server import tasks  # noqa
    build_context()
    try:
        server.start_listening()
    except error.CannotListenError as e:
        logging.critical('Listening failed.')
        logging.exception(e)
        raise SystemExit
    logging.getLogger().addHandler(LogHandler())
    reactor.run()
    started = time()
    n = dump_db()
    logging.info('Objects dumped: %d (%.2f seconds).', n, time() - started)
