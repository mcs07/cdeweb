# -*- coding: utf-8 -*-
"""
cdeweb.models
~~~~~~~~~~~~~

Data models.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from . import db


log = logging.getLogger(__name__)


class CdeJob(db.Model):
    """A ChemDataExtractor job."""
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    text = db.Column(db.String, nullable=True)
    file = db.Column(db.String, nullable=True)
    url = db.Column(db.String, nullable=True)
    result = db.Column(JSONB, nullable=True)

    @property
    def status(self):
        from .tasks import celery
        return celery.AsyncResult(self.job_id).status
