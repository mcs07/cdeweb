# -*- coding: utf-8 -*-
"""
cdeweb fabric deployment tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
"""

from fabric.api import *
from fabric.operations import prompt
from fabtools import require
from fabtools.postgres import database_exists, create_database, create_user
from fabtools.python import install_requirements

from . import db
from . import rabbitmq


#: Production server ssh login username
env.user = 'root'
# Production server
env.hosts = ['chemdataextractor.org']
# Application name
env.app_name = 'cdeweb'
# Application user
env.app_user = env.app_name
# App installation directory
env.app_dir = '/var/www/apps/%(app_name)s' % env
# Config file to use
env.config_file = 'deploy/config.py'
# Git remote to clone/pull from
env.git_remote = 'git@github_cdeweb:mcs07/cdeweb.git'
# Database user
env.database_user = env.app_name
# Database name
env.database_name = env.app_name
# RabbitMQ user
env.rabbitmq_user = env.app_name
# RabbitMQ vhost
env.rabbitmq_vhost = '%(app_name)s_vhost' % env


@task
def setup():
    """Initial setup - create application user, database, install package dependencies."""
    require.user(env.app_user, group='www-data', system=True, create_home=True)
    require.postgres.server()
    require.nginx.server()
    require.deb.packages(['libxml2-dev', 'libxslt1-dev', 'python-dev'])
    setup_postgres()
    setup_rabbitmq()


@task
def setup_postgres():
    """Initial postgres setup."""
    if not db.user_exists(env.database_user):
        if not env.database_pw:
            prompt('PostgreSQL database password:', key='database_pw')
        create_user(env.database_user, password=env.database_pw, encrypted_password=True)
    if not database_exists(env.database_name):
        create_database(env.database_name, env.database_user, locale='en_GB.UTF-8')


@task
def setup_rabbitmq():
    """Initial RabbitMQ setup."""
    if not env.rabbitmq_pw:
        prompt('RabbitMQ password:', key='rabbitmq_pw')
    rabbitmq.require_user(env.rabbitmq_user, env.rabbitmq_pw)
    rabbitmq.require_vhost(env.rabbitmq_vhost)
    sudo('rabbitmqctl set_permissions -p %(rabbitmq_vhost)s %(rabbitmq_user)s ".*" ".*" ".*"' % env)
    require.service.started('rabbitmq-server')


@task
def deploy():
    """Deploy everything."""
    deploy_app()
    install_dependencies()
    deploy_config()
    deploy_nginx()
    deploy_celery()


@task
def deploy_app():
    """Deploy app by cloning from github repository."""
    require.git.working_copy(env.git_remote, path=env.app_dir, update=True, use_sudo=True)
    require.files.directory(env.app_dir, group='www-data', use_sudo=True)


@task
def install_dependencies():
    """Ensure all dependencies listed in requirements.txt are installed."""
    with cd(env.app_dir):
        install_requirements('requirements.txt', use_sudo=True)


@task
def deploy_config():
    """Deploy config file to Flask instance folder."""
    require.files.directory('%s/instance' % env.app_dir, use_sudo=True)
    require.file('%(app_dir)s/instance/config.py' % env, source='%(config_file)s' % env, use_sudo=True, group='www-data')


@task
def deploy_gunicorn():
    """Deploy gunicorn service."""
    # TODO: Maybe ensure wsgi.py permissions are set to executable
    # require.file('%(wsgi_dir)s/%(app_name)s.wsgi' % env, source='deploy/%(app_name)s.wsgi' % env, use_sudo=True, group='www-data', mode='654')
    require.files.template_file(
        '/etc/init/%(app_name)s.conf' % env,
        template_source='deploy/gunicorn.conf',
        context=dict(app_user=env.app_user, app_name=env.app_name, app_dir=env.app_dir)
    )
    require.service.started(env.app_name)


@task
def deploy_nginx():
    """Deploy nginx site configuration and enable site."""
    require.nginx.site(
        env.app_name,
        template_source='deploy/nginx.conf',
        host='chemdataextractor.org',
        app_name=env.app_name,
        docroot=env.app_dir
    )
    require.nginx.enabled(env.app_name)


@task
def deploy_celery():
    """Deploy celery service scripts to appropriate location."""
    require.file('/etc/init.d/%(app_name)s-celeryd' % env, source='deploy/celeryd' % env, use_sudo=True, mode='755')
    require.files.template_file(
        '/etc/default/%(app_name)s-celeryd' % env,
        template_source='deploy/celeryd-default' % env,
        context=dict(app_name=env.app_name, app_dir=env.app_dir),
        use_sudo=True
    )
    sudo('update-rc.d %(app_name)s-celeryd defaults' % env)
    require.directory('/var/log/%(app_name)s' % env, use_sudo=True, owner=env.app_user, group='www-data')
    require.directory('/var/run/%(app_name)s' % env, use_sudo=True, owner=env.app_user, group='www-data')


@task
def start():
    """Start services for gunicorn, nginx, and celeryd."""
    require.service.started(env.app_name)
    require.service.started('nginx' % env)
    require.service.started('%(app_name)s-celeryd' % env)


@task
def restart():
    """Restart services for gunicorn, nginx, and celeryd."""
    require.service.restarted(env.app_name)
    require.service.restarted('nginx' % env)
    require.service.restarted('%(app_name)s-celeryd' % env)
