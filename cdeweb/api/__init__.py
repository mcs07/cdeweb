# -*- coding: utf-8 -*-
"""
cdeweb.api
~~~~~~~~~~

REST API for ChemDataExtractor.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from flask import Blueprint
from flask_restplus import Api, apidoc


log = logging.getLogger(__name__)


api_bp = Blueprint('api', __name__)


api = Api(
    api_bp,
    version=b'1.0',
    title=b'ChemDataExtractor REST API',
    description=b'A web service for programmatically uploading documents to be processed using ChemDataExtractor on our servers.',
)


from . import resources



