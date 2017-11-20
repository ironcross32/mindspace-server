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
        Task.paused.isnot(True),
        or_(Task.next_run.is_(None), Task.next_run <= now)
    ):
        logger.debug('Running %r.', t)
        try:
            run_program(None, Session, t)
            t.next_run = now + t.interval
            Session.add(t)
            Session.commit()
        except Exception as e:
            Session.rollback()
            t.paused = True
            logger.warning('Error in %r. Task paused.', t)
            Session.add(t)
            Session.commit()
            logger.exception(e)


def tasks_errback(err):
    """A task threw an error."""
    logger.exception(err.getTraceback())


tasks_task = task.LoopingCall(do_tasks)
