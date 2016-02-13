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
import os

from cde.doc.document import Document

from . import app, db, make_celery
from .models import CdeJob


log = logging.getLogger(__name__)

celery = make_celery(app)


@celery.task()
def run_cde(job_id):
    cde_job = CdeJob.query.get(job_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], cde_job.file)
    with open(filepath) as f:
        document = Document.from_file(f, fname=cde_job.file)
    cde_job.result = [r.to_primitive() for r in document.records]
    db.session.commit()
