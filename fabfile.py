#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join, basename, realpath, expanduser
from fabric.api import task, run, sudo, execute
from fabric.contrib.files import append, exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import *
from fabric.operations import put
import hosts # <<-- Added an import line!
from hosts import *


def read_key_file(key_file):
    key_file = expanduser(key_file)
    if not key_file.endswith('pub'):
        raise RuntimeWarning('Trying to push non-public part of key pair')
    with open(key_file) as f:
        return f.read()


@task
def push_key(key_file='~/.ssh/id_rsa.pub'):
    key_text = read_key_file(key_file)
    append('~/.ssh/authorized_keys', key_text)


@task
def genkey():
    base = basename(realpath('.'))
    home = '/home/{0}'.format(parm['USER'])
    sudo('cp {base}/{keyfile} {home}/.ssh/id_rsa'.format(
        base=base, keyfile=parm['keyfile'], home=home))
    sudo('ssh-keygen -y -f .ssh/id_rsa > .ssh/id_rsa.pub')
    with open('hosts', 'rb') as f:
        for li in f:
            for host in li.replace('\n', '').split(' '):
                # sudo('ssh-keygen -R {0}'.format(host))
                sudo('ssh-keyscan -H {0} >> {1}/.ssh/known_hosts'.format(
                    host, home))


@task
def msg(msg):
    run('echo %s' % msg)


@task
def ls(path=''):
    run('ls %s' % path)


@task
def cat(path=''):
    run('cat %s' % path)


@task
def setDepPkg():
    sudo('export LC_ALL="en_US.UTF-8"')
    sudo('apt-get update')
    sudo('apt-get install -y --force-yes build-essential python-dev gfortran python-pip')
    sudo('apt-get install -y --force-yes libblas-dev liblapack-dev liblapacke-dev')
    sudo('apt-get -y --force-yes upgrade')
    sudo('apt-get -y --force-yes install python-numpy python-scipy')
    sudo('pip install celery pyyaml')


@task
def setMasPkg():
    sudo('export LC_ALL="en_US.UTF-8"')
    sudo('apt-get update')
    sudo('apt-get install tmux')
    run('wget https://raw.githubusercontent.com/tsung/config/master/shell/tmux.conf')
    sudo('mv tmux.conf ~/.tmux.conf')

    sudo('apt-get install -y python-dev')
    sudo('apt-get install -y python-pip')
    sudo('echo "deb http://www.rabbitmq.com/debian/ testing main"|sudo tee -a /etc/apt/sources.list')
    run('wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc')
    sudo('apt-key add rabbitmq-signing-key-public.asc')
    sudo('apt-get install -y rabbitmq-server')
    sudo('rabbitmqctl delete_user guest')
    sudo('rabbitmqctl add_user {USER} {PWD}'.format(**globals()))
    sudo('rabbitmqctl set_permissions {USER} ".*" ".*" ".*"'.format(**globals()))
    sudo('pip install celery fabric')

    put('~/.boto')
    sudo('pip install boto')
    # sudo('apt-get -y upgrade')


@task
def setMaster():
    if exists('/etc/hosts0'):
        print 'etc/hosts0 exists'
    else:
        sudo('cp /etc/hosts /etc/hosts0')

    sudo('rm /etc/hosts')
    sudo('cp /etc/hosts0 /etc/hosts')
    put('hosts')
    sudo('cat hosts|sudo tee -a /etc/hosts')
    run('rm hosts')

    run('cat /etc/hosts')

    path1 = '/home/{0}'.format(parm['USER'])
    rsync_project(path1, exclude=['result'])

    path2 = join(path1, basename(realpath('.')))
    path3 = join(path2, parm['programdir'])
    for dst in (path2, path3):
        fi = '{0}/{1}'.format(dst, parm['keyfile'])
        if not exists(fi, use_sudo=True):
            put(parm['keyfile'], dst)
            sudo('chmod 400 {0}'.format(fi))
    execute('genkey')

