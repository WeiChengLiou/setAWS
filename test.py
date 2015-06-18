#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

def test(x):
    print 'execute %s' % x


if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) > 1:
        test(sys.argv[1])
    else:
        test('main')
