#!/usr/bin/env python
"""Most functions need access to a similar set of objects.  Rather than
having to pass them all around individually or create a monolithic 'self'
object, let's point to them from a single context object.
"""
import json
import logging
import os
import time

from scriptworker.utils import makedirs

log = logging.getLogger(__name__)


class Context(object):
    """ Basic config object.

    Avoids putting everything in a big object, but allows for passing around
    config and easier overriding in tests.
    """
    config = None
    poll_task_urls = None
    session = None
    queue = None
    _task = None  # This assumes a single task per worker.
    _temp_credentials = None  # This assumes a single task per worker.
    _reclaim_task = None

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task
        path = os.path.join(self.config['work_dir'], "task.json")
        self.write_json(path, task, "Writing task file to {path}...")
        self.temp_credentials = task['credentials']
        self.reclaim_task = None
        # TODO payload.json ?

    @property
    def reclaim_task(self):
        return self._reclaim_task

    @reclaim_task.setter
    def reclaim_task(self, value):
        self._reclaim_task = value
        if value is not None:
            path = os.path.join(self.config['work_dir'],
                                "reclaim_task.{}.json".format(int(time.time())))
            self.write_json(path, value, "Writing reclaim_task file to {path}...")
            # TODO we may not need the reclaim_task.json or credentials.json...
            self.temp_credentials = value['credentials']

    @property
    def temp_credentials(self):
        return self._temp_credentials

    @temp_credentials.setter
    def temp_credentials(self, credentials):
        self._temp_credentials = credentials
        path = os.path.join(self.config['work_dir'],
                            "credentials.{}.json".format(int(time.time())))
        self.write_json(path, credentials, "Writing credentials file to {path}...")

    def write_json(self, path, contents, message):
        log.debug(message.format(path=path))
        parent_dir = os.path.dirname(path)
        if parent_dir:
            makedirs(os.path.dirname(path))
        with open(path, "w") as fh:
            json.dump(contents, fh, indent=2, sort_keys=True)