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

import copy
import logging
import os
import re
import uuid

from flask import render_template, request, url_for, redirect, abort, flash, Response
import hoedown
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
import requests
import six

from . import app, tasks, db
from .forms import RegisterForm
from .models import CdeJob, User
from .tasks import celery


log = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/download', methods=['GET', 'POST'])
def download():
    registered = request.args.get('registered', False)
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=request.form['email'], name=request.form['name'], affiliation=request.form['affiliation'])
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('download', registered=True))
    return render_template('download.html', form=form, registered=registered)


@app.route('/evaluation')
def evaluation():
    return redirect(url_for('download'))


@app.route('/citing')
def citing():
    return render_template('citing.html')


@app.route('/docs')
def docs_index():
    return redirect(url_for('docs', docfile='intro'))


@app.route('/docs/<docfile>')
def docs(docfile):

    toc = [
        'intro', 'install', 'gettingstarted', 'reading', 'records', 'tokenization', 'pos', 'cem', 'lexicon',
        'abbreviations', 'cli', 'scrape', 'contributing'
    ]

    titles = {
        'intro': 'Introduction',
        'install': 'Installation',
        'gettingstarted': 'Getting Started',
        'reading': 'Reading Documents',
        'records': 'Chemical Records',
        'tokenization': 'Tokenization',
        'pos': 'Part-of-speech Tagging',
        'cem': 'Chemical Named Entities',
        'lexicon': 'Lexicon',
        'abbreviations': 'Abbreviation Detection',
        'cli': 'Command Line Interface',
        'scrape': 'Scraping Structured Data',
        'contributing': 'Contributing'
    }

    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'docs'))
    source_path = os.path.abspath(os.path.join(docs_dir, '%s.md' % docfile))
    # Check just in case somehow a path outside docs dir is constructed
    if not source_path.startswith(docs_dir):
        abort(404)
    try:
        with open(source_path) as mf:
            content = hoedown.html(mf.read().decode('utf-8'))
            prev_i = toc.index(docfile) - 1
            prev = toc[prev_i] if prev_i >= 0 else None
            next_i = toc.index(docfile) + 1
            next = toc[next_i] if next_i < len(toc) else None
            return render_template('docs.html', current=docfile, prev=prev, next=next, content=content, toc=toc, titles=titles)
    except IOError:
        abort(404)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        log.info(request.form)
        job_id = six.text_type(uuid.uuid4())
        if 'input-file' in request.files:
            file = request.files['input-file']
            if '.' not in file.filename:
                abort(400, 'No file extension!')
            extension = file.filename.rsplit('.', 1)[1].lower()
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
                    extension = m.group(2).lower()
            else:
                m = re.search('\.([a-z]+)$', url)
                if m:
                    extension = m.group(1).lower()
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
                f.write(input_text.encode('utf-8'))
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

    prop_keys = {'nmr_spectra', 'ir_spectra', 'uvvis_spectra', 'melting_points', 'electrochemical_potentials', 'quantum_yields', 'fluorescence_lifetimes'}

    has_result = False
    has_important = False
    has_other = False
    if job.result:
        for result in job.result:
            for record in result.get('records', []):
                has_result = True
                if any(k in prop_keys for k in record.keys()):
                    has_important = True
                elif 'labels' in record or 'smiles' in record:
                    has_other = True
                else:
                    has_important = True

    return render_template(
        'results.html',
        task=task,
        job=job,
        has_result=has_result,
        has_important=has_important,
        has_other=has_other
    )


@app.route('/depict/<path:smiles>')
def depict(smiles):
    """Depict structure"""
    mol = Chem.MolFromSmiles(smiles)

    mc = copy.deepcopy(mol)
    try:
        img = Draw.MolToImage(mc, size=(180, 180), kekulize=True, highlightAtoms=[])
    except ValueError:  # <- can happen on a kekulization failure
        mc = copy.deepcopy(mol)
        img = Draw.MolToImage(mc, size=(180, 180), kekulize=False, highlightAtoms=[])
    img_io = six.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return Response(response=img_io.getvalue(), status=200, mimetype='image/png')


@app.route('/mol/<path:smiles>')
def mol(smiles):
    """Return MOL for SMILES."""
    mol = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol)
    mb = Chem.MolToMolBlock(mol)
    return Response(response=mb, status=200, mimetype='chemical/x-mdl-molfile', headers={'Content-Disposition': 'attachment;filename=structure.mol'})

