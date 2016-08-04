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

from flask import Blueprint, request
from flask_restplus import Api


log = logging.getLogger(__name__)


api_bp = Blueprint('api', __name__)


class CdeApi(Api):
    """Customized subclass of Flask-Restplus/Flask-Restful Api."""

    def make_response(self, data, *args, **kwargs):
        """Wrapper around make_response that uses 'format' querystring parameter as well as 'Accept' header."""
        # If querystring format, use that media type
        mediatypes = {
            'json': 'application/json',
            'xml': 'application/xml',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'sdf': 'chemical/x-mdl-sdfile'
        }
        mediatype = mediatypes.get(request.args.get('format'))
        if mediatype in self.representations:
            resp = self.representations[mediatype](data, *args, **kwargs)
            resp.headers['Content-Type'] = mediatype
            return resp
        # If text/html (i.e. browser default) make sure we return JSON not XML
        if 'text/html' in request.accept_mimetypes:
            resp = self.representations['application/json'](data, *args, **kwargs)
            resp.headers['Content-Type'] = 'application/json'
            return resp
        # Otherwise do default Flask-RestPlus/Flask-Restful content-negotiation via Accept Header
        return super(CdeApi, self).make_response(data, *args, **kwargs)



api = CdeApi(
    api_bp,
    version=b'1.0',
    title=b'ChemDataExtractor REST API',
    description=b'A web service for programmatically uploading documents to be processed using ChemDataExtractor on our servers.\n\n All endpoints are at constructed by appending to http://chemdataextractor.org/api'
)


from . import resources, representations



