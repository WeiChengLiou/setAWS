#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import *
from fabric.context_managers import cd
from fabric.contrib.project import rsync_project
import os
from os.path import join
from hosts import *


localdir = os.path.realpath(os.curdir)

env.warn_only = True
env.forward_agent = True
env.disable_known_hosts = True


def mul():
    env.hosts = list(env.roledefs['all'])


@parallel
@roles('all')
def touch():
    with cd(parm['programdir']):
        run('celery -A tasks worker --loglevel=info')


@parallel
@roles('slave')
def shutdown1():
    sudo('shutdown -h 0')


@parallel
@roles('all')
def rsync():
    rsync_project(join('/home', parm['USER']))


@parallel
@roles('master')
def shutdown():
    execute(shutdown1)
    sudo('shutdown -h 1')


