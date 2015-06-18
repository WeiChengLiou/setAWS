#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join
import sys
from utils import call, loadparm, saveparm, chain
from shutil import copy


def loadhost():
    fi = 'hosts'
    ipboss, ips = None, []
    with open(fi, 'rb') as f:
        for li in f:
            ret = li.split(' ')
            if ipboss is None:
                ipboss = ret[0]
            else:
                ips.append(ret[0])
    return ipboss, ips


def chkparm(ipboss, slaves, **kwargs):
    parm = loadparm()

    parm['n_worker'] = len(slaves) + 1
    parm['roles']['master'] = [ipboss]
    parm['roles']['slave'] = slaves
    parm['roles']['all'] = list(chain([[ipboss], slaves]))
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


def comments(ip):
    li = [
        '1. ssh to master server',
        '    ssh hduser@{ip}',
        '    tmux',
        '    cd setCelery/deathrabbit',
        '    fab rsync',
        '    fab touch',
        '2. open another window',
        '    sh mainjob.sh',
        ]
    print '\n'.join(li).format(ip=ip)


if __name__ == '__main__':
    """"""
    ipboss, slaves = loadhost()
    print ipboss
    parm = chkparm(ipboss, slaves)

    if len(sys.argv) == 1:
        print 'main'
        call('fab -R all setDepPkg')
        call('fab -R master setMasPkg')
        call('fab -R master setMaster')

        comments(ipboss)
    else:
        x = 'b'
        cmds = [sys.argv[1], '(', ')']
        if len(sys.argv) > 2:
            [cmds.insert(-1, argv) for argv in sys.argv[2:]]
        eval(''.join(cmds))


