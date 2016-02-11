# -*- coding: utf-8 -*-
"""
cdeweb.tasks
~~~~~~~~~~~~

Celery tasks.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from . import app, db, make_celery


log = logging.getLogger(__name__)

celery = make_celery(app)


@celery.task()
def add(x, y):
    return x + y
