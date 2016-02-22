# -*- coding: utf-8 -*-
"""
cdeweb.forms
~~~~~~~~~~~~



:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email


log = logging.getLogger(__name__)


class ContactForm(Form):
    """Form to contact us."""
    name = StringField('Your name:', validators=[DataRequired()])
    email = StringField('Your email:', validators=[DataRequired(), Email()])
    message = TextAreaField('Message:', validators=[DataRequired()])
    submit = SubmitField('Send Message')