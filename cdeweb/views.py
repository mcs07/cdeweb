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

from flask import render_template

from . import app


log = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('index.html')
