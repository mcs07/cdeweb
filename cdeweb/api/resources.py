# -*- coding: utf-8 -*-
"""
cdeweb.api.resources
~~~~~~~~~~~~~~~~~~~~

API resources.

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

import six
from flask import current_app, make_response
from flask_restplus import Resource, abort, fields
import werkzeug

from .. import db
from ..models import CdeJob
from ..tasks import run_cde
from . import api


log = logging.getLogger(__name__)


jobs = api.namespace('Jobs', path='/job', description='Submit jobs and retrieve results')


cdejob_schema = api.model('CdeJob', {
    'job_id': fields.String(required=True, description='Unique job ID'),
    'created_at': fields.DateTime(required=True, description='Job creation timestamp'),
    'status': fields.String(required=True, description='Current job status'),
    'result': fields.Raw(required=False, description='Job results')
})


submit_parser = api.parser()
submit_parser.add_argument('file', type=werkzeug.datastructures.FileStorage, required=True, help='The input file.', location='files')

result_parser = api.parser()
result_parser.add_argument('format', help='Response format', location='query', choices=['json', 'xml', 'xlsx', 'sdf'])


@jobs.route('/')
# @api.doc(responses={400: 'Disallowed file type'})
class CdeJobSubmitResource(Resource):
    """Submit a new ChemDataExtractor job and get the job ID."""

    @api.doc(description='Submit a new ChemDataExtractor job.', parser=submit_parser)
    @api.marshal_with(cdejob_schema, code=201)
    def post(self):
        """Submit a new job."""
        args = submit_parser.parse_args()
        file = args['file']
        job_id = six.text_type(uuid.uuid4())
        if '.' not in file.filename:
            abort(400, b'No file extension!')
        extension = file.filename.rsplit('.', 1)[1]
        if extension not in current_app.config['ALLOWED_EXTENSIONS']:
            abort(400, b'Disallowed file extension!')
        filename = '%s.%s' % (job_id, extension)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        cde_job = CdeJob(file=filename, job_id=job_id)
        db.session.add(cde_job)
        db.session.commit()
        run_cde.apply_async([cde_job.id], task_id=job_id)
        return cde_job, 201


@jobs.route('/<string:job_id>')
@api.doc(params={'job_id': 'The job ID'})  # responses={404: 'Job not found'},
class CdeJobResource(Resource):
    """View the status and results of a specific ChemDataExtractor job."""

    @api.doc(description='View the status and results of a specific ChemDataExtractor job. \n\n Use the `Accept` header or the `format` query parameter to specify JSON, XML, or Excel response format.', parser=result_parser)
    @api.marshal_with(cdejob_schema)
    def get(self, job_id):
        """Get the results of a job."""
        return CdeJob.query.filter_by(job_id=job_id).first_or_404()
