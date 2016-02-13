# -*- coding: utf-8 -*-
"""
cdeweb.views
~~~~~~~~~~~~

Main website views.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import os
import uuid

from cde.doc.document import Document
import natsort
from flask import render_template, request, url_for, redirect, abort
import six

from . import app, tasks, db
from .models import CdeJob
from .tasks import celery


log = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/citing')
def citing():
    return render_template('citing.html')


@app.route('/demo', methods=['GET', 'POST'])
def demo():

    if request.method == 'POST':
        log.info(request.form)
        job_id = six.text_type(uuid.uuid4())
        if 'input-file' in request.files:
            file = request.files['input-file']
            if '.' not in file.filename:
                abort(400, 'No file extension!')
            extension = file.filename.rsplit('.', 1)[1]
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                abort(400, 'Disallowed file extension!')
            filename = '%s.%s' % (job_id, extension)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cde_job = CdeJob(file=filename, job_id=job_id)
            db.session.add(cde_job)
            db.session.commit()
            async_result = tasks.run_cde.apply_async([cde_job.id], task_id=job_id)
            return redirect(url_for('results', result_id=async_result.id))
        elif 'input-text' in request.form:
            # save text file from request.form
            input_text = request.form['input-text']
            filename = '%s.txt' % job_id
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'w') as f:
                f.write(input_text)
            cde_job = CdeJob(file=filename, job_id=job_id)
            db.session.add(cde_job)
            db.session.commit()
            async_result = tasks.run_cde.apply_async([cde_job.id], task_id=job_id)
            return redirect(url_for('results', result_id=async_result.id))

        # Something must have been wrong...
        abort(400)

    else:
        return render_template('demo.html')


@app.route('/results/<result_id>')
def results(result_id):
    task = celery.AsyncResult(result_id)
    job = CdeJob.query.filter_by(job_id=result_id).first()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], job.file)
    with open(filepath) as f:
        document = Document.from_file(f)
    # Divide the results:
    important_records = []
    other_records = []
    if job.result:
        for record in job.result:
            if record.keys() == ['names'] or record.keys() == ['labels']:
                other_records.append(record)
            else:
                important_records.append(record)
        important_records = natsort.natsorted(important_records, lambda x: x.get('labels', ['ZZZ%s' % (99 - len(x.get('names', [])))])[0])
    return render_template('results.html', task=task, job=job, document=document, important_records=important_records, other_records=other_records)


@app.route('/n2s/<name>')
def n2s(name):
    """Attempt to resolve structure for name."""
    pass  # TODO.. ChemSpiPy and CIRpy... return SMILES. Use ChemDoodle Web Components for depiction
