"""Contains classes and functions related to the tasks framework."""

import logging
from time import time
from sqlalchemy import or_
from twisted.internet.task import LoopingCall
from .db import session, Task
from .program import run_program, handle_traceback

logger = logging.getLogger(__name__)

tasks = {}


def task_errback(err):
    """A task threw an error."""
    logger.exception(err.getTraceback())


class TaskLoopingCall(LoopingCall):
    """A LoopingCall specifically for Task instances."""

    def __init__(self, task):
        self.task_id = task.id
        super().__init__(self.run)

    def run(self):
        """Run this task."""
        now = time()
        with session() as s:
            t = Task.get(self.task_id)
            if t is None:
                logger.info('Task %d has since been deleted.', self.task_id)
                self.stop()
                return
            logger.debug('Running task %s.', t)
            try:
                run_program(None, s, t)
                t.next_run = now + t.interval
                if t.interval != self.interval:
                    logger.debug(
                        'Adjusting task for task %s with interval %g.', t,
                        t.interval
                    )
                    self.start(t.interval)
            except Exception as e:
                s.rollback()
                t.paused = True
                self.stop()
                s.add(t)
                task_name = str(t)
                handle_traceback(e, task_name, 'Task Scheduler', __name__)

    def start(self, *args, **kwargs):
        """Start this task."""
        return super().start(*args, **kwargs).addErrback(task_errback)

    def stop(self, *args, **kwargs):
        """Stop this task."""
        if self.task_id in tasks:
            del tasks[self.task_id]
        return super().stop(*args, **kwargs)


def start_tasks():
    """Call queue_task for each Task instance."""
    now = time()
    ids = [Task.id.isnot(id) for id in tasks]
    for t in Task.query(Task.paused.isnot(True), *ids):
        task = TaskLoopingCall(t)
        tasks[t.id] = task
        task.start(t.interval, now=False)
