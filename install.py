#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Reference: https://www.rabbitmq.com/install-debian.html

import os

cmds = [
    'echo "deb http://www.rabbitmq.com/debian/ testing main"|sudo tee /etc/apt/sources.list',
    'wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc',
    'sudo apt-key add rabbitmq-signing-key-public.asc',
    'sudo apt-get update',
    'sudo apt-get install rabbitmq-server',
    'sudo rabbitmqctl delete_user guest',
#'sudo rabbitmqctl add_user gilbert ',
    ]

map(os.system, cmds)

user, pwd = raw_input()

os.system('sudo rabbitmqctl add_user {user} {pwd}'.format(locals()))

cmds = [
    'sudo rabbitmqctl set_permissions {user} ".*" ".*" ".*"'.format(locals()),
    'sudo pip install celery',
    ]



