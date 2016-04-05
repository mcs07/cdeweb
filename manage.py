# -*- coding: utf-8 -*-
"""
manage.py
~~~~~~~~~

cdeweb management commands.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from flask_script import Manager
from flask_migrate import MigrateCommand

from cdeweb import app, db
from cdeweb.tasks import celery


log = logging.getLogger(__name__)


manager = Manager(app)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('dicttoxml').setLevel(logging.WARN)


#: Perform database migrations
manager.add_command('db', MigrateCommand)


@manager.command
def celeryworker():
    """Run a celery worker."""
    argv = ['worker', '--loglevel=DEBUG', '-Q', 'batch,celery']
    celery.worker_main(argv)


if __name__ == '__main__':
    manager.run()
