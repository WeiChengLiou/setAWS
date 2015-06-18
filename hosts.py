from fabric.api import env
import yaml

parm = yaml.load(open('parm.yaml', 'rb'))

n_worker = parm['n_worker']
for role, ips in parm['roles'].iteritems():
    env.roledefs[role] = ips

USER = parm['CELERY_USER']
PWD = parm['CELERY_PWD']
env.user = parm['USER']
if 'keyfile' in parm:
    env.key_filename = parm['keyfile']
else:
    env.password = parm['PWD']
