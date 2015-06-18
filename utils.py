#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pprint
import subprocess
import shlex
import yaml
import itertools as it


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
