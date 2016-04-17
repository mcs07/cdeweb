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
import zipfile

from chemdataextractor import Document
from chemdataextractor.scrape import DocumentEntity, NlmXmlDocument, Selector
from natsort import natsort

from . import app, db, make_celery
from .models import CdeJob


log = logging.getLogger(__name__)

celery = make_celery(app)


def get_result(f, fname):
    try:
        document = Document.from_file(f, fname=fname)
    except Exception:
        return {}
    records = [r.to_primitive() for r in document.records]
    records = natsort.natsorted(records, lambda x: x.get('labels', ['ZZZ%s' % (99 - len(x.get('names', [])))])[0])
    result = {
        'records': records,
        'abbreviations': document.abbreviation_definitions
    }
    return result


def get_biblio(f, fname):
    biblio = {'filename': fname}
    try:
        if fname.endswith('.html'):
            biblio.update(DocumentEntity(Selector.from_html_text(f.read())).serialize())
        elif fname.endswith('.xml') or fname.endswith('.nxml'):
            biblio.update(NlmXmlDocument(Selector.from_xml_text(f.read(), namespaces={'xlink': 'http://www.w3.org/1999/xlink'})).serialize())
    except Exception:
        pass
    return biblio


@celery.task()
def run_cde(job_id):
    cde_job = CdeJob.query.get(job_id)
    cde_job.result = []
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], cde_job.file)
    if filepath.endswith('.zip'):
        zf = zipfile.ZipFile(filepath)
        for zipname in zf.namelist():
            if '.' not in zipname:
                continue
            extension = zipname.rsplit('.', 1)[1]
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                continue
            with zf.open(zipname) as f:
                result = get_result(f, zipname)
            with zf.open(zipname) as f:
                result['biblio'] = get_biblio(f, zipname)
            if result:
                cde_job.result.append(result)
    else:
        with open(filepath) as f:
            result = get_result(f, filepath)
        with open(filepath) as f:
            result['biblio'] = get_biblio(f, os.path.basename(filepath))
        cde_job.result.append(result)

    db.session.commit()
