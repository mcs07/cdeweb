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
from cde.scrape.entity import DocumentEntity
from cde.scrape.pub.nlm import NlmXmlDocument
from cde.scrape.selector import Selector

from . import app, db, make_celery
from .models import CdeJob


log = logging.getLogger(__name__)

celery = make_celery(app)


@celery.task()
def run_cde(job_id):
    cde_job = CdeJob.query.get(job_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], cde_job.file)
    with open(filepath) as f:
        if filepath.endswith('.html'):
            cde_job.biblio = DocumentEntity(Selector.from_html_text(f.read())).serialize()
        elif filepath.endswith('.xml') or filepath.endswith('.nxml'):
            cde_job.biblio = NlmXmlDocument(Selector.from_xml_text(f.read(), namespaces={'xlink': 'http://www.w3.org/1999/xlink'})).serialize()
    with open(filepath) as f:
        document = Document.from_file(f, fname=cde_job.file)
    cde_job.result = [r.to_primitive() for r in document.records]
    cde_job.abbreviations = {'abbreviations': document.abbreviation_definitions}
    db.session.commit()
