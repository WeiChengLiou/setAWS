#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pprint
import subprocess
import shlex
import yaml
import itertools as it
from os.path import join
from shutil import copy


chain = it.chain.from_iterable


def dprint(li):
    for r in li:
        pprint(r.__dict__)


def call(cmd):
    return subprocess.call(shlex.split(cmd))


def loadparm():
    return yaml.load(open('parm.yaml', 'rb'))


def saveparm(parm):
    yaml.dump(parm, open('parm.yaml', 'wb'))


def loadhost():
    fi = 'hosts'
    ips = []
    with open(fi, 'rb') as f:
        for li in f:
            ret = li.split(' ')
            ips.append(ret[0])
        ipboss = ips.pop(0)
    return ipboss, ips


def chkparm(ipboss, slaves, **kwargs):
    # Update parameters
    parm = loadparm()

    parm['n_worker'] = len(slaves) + 1
    parm['roles']['master'] = [ipboss]
    parm['roles']['slave'] = slaves
    parm['roles']['all'] = list(it.chain([[ipboss], slaves]))
    parm['celeryuri'] = 'amqp://{USER}:{PWD}@{IP}:5672/'.format(
        USER=parm['CELERY_USER'],
        PWD=parm['CELERY_PWD'],
        IP=ipboss)
    for k, v in kwargs.iteritems():
        parm[k] = v
    saveparm(parm)

    for fi1 in ('hosts.py', 'parm.yaml'):
        copy(fi1, join(parm['programdir'], fi1))
    return parm


def renewHost():
    # Update worker list in parm.yaml manually
    chkparm(*loadhost())


