# -*- coding: utf-8 -*-
"""
cdweb.wsgi
~~~~~~~~~~

wsgi script.

"""

import sys


# Ensure the main project directory is on the path
sys.path.insert(0, '/var/www/apps/cdeweb')

from cdeweb import app as application
