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
import subprocess
import tempfile
import zipfile

import cirpy
from chemdataextractor import Document
from chemdataextractor.scrape import DocumentEntity, NlmXmlDocument, Selector
from chemdataextractor.text.normalize import chem_normalize
from natsort import natsort

from . import app, db, make_celery
from .models import CdeJob, ChemDict

log = logging.getLogger(__name__)

celery = make_celery(app)


def get_result(f, fname):
    try:
        document = Document.from_file(f, fname=fname)
    except Exception:
        return {}
    records = document.records.serialize()
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


def add_structures(result):
    # Run OPSIN
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        for record in result['records']:
            for name in record.get('names', []):
                tf.write(('%s\n' % name).encode('utf-8'))
    subprocess.call([app.config['OPSIN_PATH'], '--allowRadicals', '--wildcardRadicals', '--allowAcidsWithoutAcid', '--allowUninterpretableStereo', tf.name, '%s.result' % tf.name])
    with open('%s.result' % tf.name) as res:
        structures = [line.strip() for line in res]
        i = 0
        for record in result['records']:
            for name in record.get('names', []):
                if 'smiles' not in record and structures[i]:
                    log.debug('Resolved with OPSIN: %s = %s', name, structures[i])
                    record['smiles'] = structures[i]
                i += 1
    os.remove(tf.name)
    os.remove('%s.result' % tf.name)
    # For failures, use NCI CIR (with local cache of results)
    for record in result['records']:
        for name in record.get('names', []):
            if 'smiles' not in record:
                local_entry = ChemDict.query.filter_by(name=name).first()
                if local_entry:
                    log.debug('Resolved with local dict: %s = %s', name, local_entry.smiles)
                    if local_entry.smiles:
                        record['smiles'] = local_entry.smiles
                else:
                    smiles = cirpy.resolve(chem_normalize(name).encode('utf-8'), 'smiles')
                    log.debug('Resolved with CIR: %s = %s', name, smiles)
                    db.session.add(ChemDict(name=name, smiles=smiles))
                    if smiles:
                        record['smiles'] = smiles
    return result


@celery.task()
def run_cde(job_id):
    cde_job = CdeJob.query.get(job_id)
    job_result = []
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
                result = add_structures(result)
            with zf.open(zipname) as f:
                result['biblio'] = get_biblio(f, zipname)
            if result:
                job_result.append(result)
    else:
        with open(filepath) as f:
            result = get_result(f, filepath)
            result = add_structures(result)
        with open(filepath) as f:
            result['biblio'] = get_biblio(f, os.path.basename(filepath))
        job_result.append(result)
    cde_job.result = job_result
    db.session.commit()
