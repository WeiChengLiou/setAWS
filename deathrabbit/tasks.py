#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
import cPickle
from celery import Celery
import time
import yaml


parms = yaml.load(open('parm.yaml', 'rb'))
ln = np.log
pow = np.power
app = Celery('tasks', backend='amqp', broker=parms['celeryuri'])


@app.task
def primeNum(num):
    if num % 2 == 0:
        return None
    else:
        for v in xrange(3, num, 2):
            if num % v == 0:
                return None
        return num


def dotask_local(N):
    # For local only
    ret0 = []
    for i in xrange(N):
        ret0.append(primeNum(i))
    return [x for x in ret0 if x is not None]


def dotask(N):
    # For celery distribute jobs
    ret0 = []
    for i in xrange(N):
        ret0.append(primeNum.delay(i))

    ret = [x.get() for x in ret0]
    return [x for x in ret if x is not None]


def upload(fi):
    os.system('python upload.py %s' % fi)


def main():
    ret = dotask(100)
    print ret
    fi = 'result.pkl'
    cPickle.dump(ret, open(fi, 'wb'))
    upload(fi)


if __name__ == '__main__':
    main()


