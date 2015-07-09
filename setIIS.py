#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from utils import call, loadhost, chkparm


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


