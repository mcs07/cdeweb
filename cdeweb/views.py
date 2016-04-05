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
import re
import uuid

import requests
from flask import render_template, request, url_for, redirect, abort, flash
from flask_mail import Message
import natsort
import six

from . import app, tasks, db, mail
from .forms import ContactForm
from .models import CdeJob
from .tasks import celery


log = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/download')
def download():
    return render_template('download.html')


@app.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')


@app.route('/citing')
def citing():
    return render_template('citing.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(
            subject='ChemDataExtractor contact message',
            recipients=app.config['MAIL_RECIPIENTS'],
            body='From: %s <%s>\n\n%s' % (form.name.data, form.email.data, form.message.data)
        )
        mail.send(msg)
        flash('Your message was sent successfully.')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)


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
        elif 'input-url' in request.form:
            url = request.form['input-url']
            r = requests.get(url)
            extension = None
            if 'Content-Type' in r.headers:
                t = r.headers['Content-Type']
                if 'text/html' in t:
                    extension = 'html'
                elif '/xml' in t:
                    extension = 'xml'
                elif '/pdf' in t:
                    extension = 'pdf'
            elif 'Content-Disposition' in r.headers:
                d = r.headers['Content-Disposition']
                m = re.search('filename=(.+)\.([^\.]+)', d)
                if m:
                    extension = m.group(2)
            else:
                m = re.search('\.([a-z]+)$', url)
                if m:
                    extension = m.group(1)
            if not extension:
                abort(400, 'Could not determine file type!')
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                abort(400, 'Disallowed file extension!')
            filename = '%s.%s' % (job_id, extension)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
                f.write(r.content)
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
    job = CdeJob.query.filter_by(job_id=result_id).first_or_404()
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
        other_records = natsort.natsorted(other_records, lambda x: x.get('labels', ['ZZZ%s' % (99 - len(x.get('names', [])))])[0])
    return render_template('results.html', task=task, job=job, important_records=important_records, other_records=other_records)


@app.route('/n2s/<name>')
def n2s(name):
    """Attempt to resolve structure for name."""
    pass  # TODO.. ChemSpiPy and CIRpy... return SMILES. Use ChemDoodle Web Components for depiction
