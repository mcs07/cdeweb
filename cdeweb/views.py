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

from flask import render_template, request, url_for, redirect
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


@app.route('/demo', methods=['GET', 'POST'])
def demo():

    if request.method == 'POST':
        log.info(request.form)
        job_id = six.text_type(uuid.uuid4())
        file = request.files['input-file']
        if '.' in file.filename:
            extension = file.filename.rsplit('.', 1)[1]
            if extension in app.config['ALLOWED_EXTENSIONS']:
                filename = '%s.%s' % (job_id, extension)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cde_job = CdeJob(file=filename, job_id=job_id)
                db.session.add(cde_job)
                db.session.commit()
                async_result = tasks.run_cde.apply_async([cde_job.id], task_id=job_id)
                return redirect(url_for('results', result_id=async_result.id))
    else:
        return render_template('demo.html')


@app.route('/results/<result_id>')
def results(result_id):
    task = celery.AsyncResult(result_id)
    job = CdeJob.query.filter_by(job_id=result_id).first()
    return render_template('results.html', task=task, job=job)
