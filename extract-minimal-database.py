"""A program to extract a minimal database from the database provided as
input."""

import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from time import time
from server.db import (
    load_db, dump_db, get_classes, session, Hotkey, Command, Credit, Base
)

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    'infile', nargs='?', default='world.yaml', help='The database file to load'
)
parser.add_argument(
    'outfile', nargs='?', default='minimal.yaml', help='The file to write to'
)


def main():
    """Do stuff."""
    args = parser.parse_args()
    logging.basicConfig(level='INFO')
    started = time()
    load_db(args.infile)
    logging.info(
        'Objects loaded: %d (%.2f seconds).', Base.number_of_objects(),
        time() - started
    )
    with session() as s:
        for cls in get_classes():
            if cls in (Hotkey, Command, Credit):
                continue  # Don't delete those.
            q = cls.query()
            logging.info(
                'Deleting %d objects from table %s.', q.count(),
                cls.__table__.name
            )
            q.delete()
            s.commit()
    started = time()
    dump_db(args.outfile)
    logging.info(
        'Objects dumped: %d (%.2f seconds).', Base.number_of_objects(),
        time() - started
    )


if __name__ == '__main__':
    main()
