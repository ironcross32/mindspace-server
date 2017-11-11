"""Contains classes and functions related to the tasks framework."""

import logging
from time import time
from sqlalchemy import or_
from twisted.internet import task
from .db import Session, Task
from .program import run_program

logger = logging.getLogger(__name__)


def do_tasks():
    """Run through all the tasks."""
    now = time()
    for t in Task.query(
        Task.disabled.isnot(True),
        or_(Task.next_run.is_(None), Task.next_run <= now)
    ):
        print(t)
        logger.info('Running %r.', t)
        try:
            run_program(None, Session, t)
        except Exception as e:
            Session.rollback()
            t.disabled = True
            logger.warning('Error in %r. Task disabled.', t)
            Session.add(t)
            Session.commit()
            logger.exception(e)


def tasks_errback(err):
    """A task threw an error."""
    logger.exception(err.getTraceback())


tasks_task = task.LoopingCall(do_tasks)
