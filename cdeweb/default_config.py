# -*- coding: utf-8 -*-
"""
cdeweb.default_config
~~~~~~~~~~~~~~~~~~~~~

Default configuration. Should be overridden when deployed.

"""

DEBUG = True
SECRET_KEY = '4ef582f317d50e0c0c36a512aa45282c9259f4c1ac634cf2'
SQLALCHEMY_DATABASE_URI = 'postgresql://cdeweb:cdeweb@localhost/cdeweb'
SQLALCHEMY_TRACK_MODIFICATIONS = False

CELERY_BROKER_URL = 'amqp://cdeweb:cdeweb@localhost:5672/cdeweb_vhost'
CELERY_RESULT_BACKEND = 'db+postgresql://cdeweb:cdeweb@localhost:5432/cdeweb'
CELERYD_TASK_TIME_LIMIT = 1000
