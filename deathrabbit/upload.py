#!/usr/bin/env python
# -*- coding: utf-8 -*-
import boto.s3
import os
import sys
import yaml
from pdb import set_trace
from traceback import print_exc


regionname = 'us-west-2'
parm = yaml.load(open('parm.yaml', 'rb'))


def get_region(name):
    for x in boto.s3.regions():
        if x.name == name:
            return x
    return None


path = os.path.realpath('.')
region = get_region(regionname)
s3 = boto.s3.connect_to_region(regionname)


def loadbkt(bktname):
    try:
        bkt = s3.get_bucket(bktname)
    except:
        bkt = s3.create_bucket(bktname, location=regionname)
    return bkt


def upload(bkt, fi):
    key = bkt.get_key(fi)
    if not key:
        key = bkt.new_key(fi)
    key.set_contents_from_filename(fi)
    print fi, 'uploaded'


def chkbkt():
    return loadbkt(parm['s3_bucket'])


if __name__ == '__main__':
    if len(sys.argv) == 1:
        bkt = loadbkt(parm['s3_bucket'])
        for fi in os.listdir('.'):
            if 'pkl' in fi:
                key = bkt.get_key(fi)
                if not key:
                    key = bkt.new_key(fi)
                key.set_contents_from_filename(fi)
                print fi, 'uploaded'
    else:
        if sys.argv[1] == 'chkbkt':
            chkbkt()
        else:
            bkt = loadbkt(parm['s3_bucket'])
            upload(bkt, sys.argv[1])


