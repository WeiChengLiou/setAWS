#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import Celery

app = Celery('tasks', broker='amqp://gilbert:~AMPQxpkp5168@106.187.49.17//')

@app.task
def add(x, y):
    return x + y
