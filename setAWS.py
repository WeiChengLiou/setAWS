#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import boto.s3
import boto.ec2
import boto.vpc
from traceback import print_exc
from pdb import set_trace
from os.path import basename, realpath, exists, join
import os
import time
import cPickle
from utils import chkparm, loadparm, saveparm, call
import itertools as it

# AMI: https://aws.amazon.com/marketplace/ordering?productId=ecd5575e-d805-450e-843e-f2a9872b8c80&ref_=dtl_psb_continue&region=us-east-1

grpname = 'testiis'
ami = 'ami-1b471c2b'  # c3
cpu = 'c3.2xlarge'
ami = 'ami-17471c27'  # t1.micro
cpu = 't1.micro'
keyname = 'testiis'
regionname = 'us-west-2'
cidr_rng = '192.168.0.0/20'
cidr_rng1 = '192.168.0.0/21'
cidr_all = '0.0.0.0/0'
grprules = [
    ('tcp', 22, 22, cidr_all),
    ('tcp', 5672, 5672, cidr_all),
    ('tcp', 1, 65535, cidr_all),
    ('icmp', 1, 102, cidr_all),
    ]
n_instances = 2
parm = loadparm()


def get_region(name):
    for x in boto.vpc.regions():
        if x.name == name:
            return x
    return None


path = realpath('.')
region = get_region(regionname)
c = boto.vpc.VPCConnection(region=region)
ec2 = boto.ec2.connect_to_region(regionname)
s3 = boto.s3.connect_to_region(regionname)


def def_vpc():
    vpc = c.create_vpc(cidr_rng)
    c.modify_vpc_attribute(vpc.id, enable_dns_support=True)
    c.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)
    igw = c.create_internet_gateway()
    c.attach_internet_gateway(igw.id, vpc.id)
    subnet = c.create_subnet(vpc.id, cidr_rng1)
    c.get_status(
        'ModifySubnetAttribute',
        {'SubnetId': subnet.id, 'MapPublicIpOnLaunch.Value': 'true'},
        verb='POST')
    return vpc, igw, subnet


def def_keypair(keyname):
    key = ec2.create_key_pair(keyname)
    key.save(path)
    return key


def def_pgrp(grpname):
    try:
        ec2.create_placement_group(grpname)
    except:
        """"""


def def_secgrp(vpc):
    grp = c.get_all_security_groups(filters={'vpc_id': vpc.id})[0]
    cols = ('ip_protocol', 'from_port', 'to_port', 'cidr_ip')
    for rule in grprules:
        grp.authorize(**{k: v for k, v in zip(cols, rule)})

    return [grp]


def def_route(vpc, igw):
    rtbl = c.get_all_route_tables(filters={'vpc_id': vpc.id})[0]
    c.create_route(rtbl.id, cidr_all, igw.id)


def get_state(resv):
    return [x.update() for x in resv.instances]


def inst_attr(resv, attr):
    return [x.__getattribute__(attr) for x in resv.instances]


def run_instance(ami, vpc, grps, subnet, n_inst):
    resv = c.run_instances(
        ami, min_count=n_inst, max_count=n_inst, key_name=keyname,
        instance_type=cpu,
        subnet_id=subnet.id,
        instance_initiated_shutdown_behavior='stop',
        security_group_ids=[x.id for x in grps])

    while any([(x != 'running') for x in get_state(resv)]):
        time.sleep(5)
    return resv


def SetUp():
    global key, vpc, igw, subnet, grps, resv
    key = def_keypair(keyname)
    print 'generate key-pair'

    vpc, igw, subnet = def_vpc()
    print 'vpc, internet gateway, subnet generated'

    grps = def_secgrp(vpc)
    print 'security group modified'

    def_route(vpc, igw)
    print 'route table modified'

    cPickle.dump(vpc, open('EC2info.pkl', 'wb'))


def get_resv(vpcid):
    for resv in c.get_all_instances():
        for inst in resv.instances:
            if inst.vpc_id == vpcid:
                yield resv
                break


def get_igw(vpcid):
    for igw in c.get_all_internet_gateways():
        for x in igw.attachments:
            if x.vpc_id == vpcid:
                return igw


def chkstate(resv, state):
    states = [x.update() for x in resv.instances]
    print states
    return [(x == state) for x in states]


def clear(vpc, img):
    vpcid = vpc.id
    fildic = {'filters': {'vpc_id': vpcid}}

    shutdown(vpc)
    subnet = c.get_all_subnets(**fildic)[0]
    while (subnet and 1):
        try:
            c.delete_subnet(subnet.id)
            break
        except:
            time.sleep(3)
    print 'subnet deleted.'

    igw = get_igw(vpcid)
    c.detach_internet_gateway(igw.id, vpcid)
    c.delete_internet_gateway(igw.id)
    print 'internet gateway deleted.'

    vpc = c.get_all_vpcs(**fildic)[0]
    vpc.delete()
    print 'vpc deleted.'

    c.delete_key_pair(keyname)

    fis = [
        '{0}/{1}.pem'.format(path, keyname),
        'EC2info.pkl',
        'resv0.pkl'
        ]
    for fi in fis:
        if exists(fi):
            os.remove(fi)
    print 'key-pair deleted'

    if img is not None:
        delImage(img)
        print 'image deleted'

    parm.pop('keyfile')
    saveparm(parm)
    print 'clean parm'


def makeHosts(vpc, resv0, ipboss, n_inst):
    # Write hosts

    def appip(resv):
        for ip in inst_attr(resv, 'private_ip_address'):
            yield str(ip)

    ips = []
    for resv in get_resv(vpc.id):
        if resv.id != resv0.id:
            map(ips.append, appip(resv))

    hosts = '\n'.join(
        ['{0} worker{1:03}'.format(ip, i)
            for i, ip in enumerate(it.chain([ipboss], ips))])
    print hosts
    with open('hosts', 'wb') as f:
        f.write(hosts)
    print 'hosts file saved'

    return ipboss, ips


def comments(ip):
    base = basename(realpath('.'))
    li = [
        'Do the following steps manually:',
        '1. ssh to master server',
        '    ssh -i {key}.pem ubuntu@{ip}',
        '    tmux',
        '    cd {base}/{programdir}',
        '    fab rsync',
        '    fab touch',
        '2. open another window',
        '    sh mainjob.sh',
        ]
    print '\n'.join(li).format(
        base=base,
        programdir=parm['programdir'],
        ip=ip,
        key=keyname)


def makeImage(inst):
    print 'creating image'
    name = parm['programdir']
    id = c.create_image(inst.id, name, "temp", False)
    for ami in c.get_all_images(owners=['self'], filters={'name': name}):
        while ami.update() != 'available':
            time.sleep(3)
        print 'image available'
        break
    return [x for x in c.get_all_images(owners=['self']) if x.id == id][0]


def delImage(ami):
    c.deregister_image(ami.id, True)


def main(reset=False):
    print 'main'
    fi = 'resv0.pkl'
    if (exists(fi)) and (not reset):
        return loadInst(fi)
    else:
        return createInst(fi)


def loadInst(fi):
    print 'load instance'
    global vpc, grps, subnet
    vpc = cPickle.load(open('EC2info.pkl', 'rb'))
    grps = c.get_all_security_groups(filters={'vpc_id': vpc.id})
    subnet = c.get_all_subnets(filters={'vpc_id': vpc.id})[0]
    resv0, img = cPickle.load(open(fi, 'rb'))
    return resv0, img


def surecall(cmd):
    for i in xrange(10):
        ret = call(cmd)
        if ret == 0:
            return
        time.sleep(10)
    raise Exception('Error running command: %s' % cmd)


def createInst(fi):
    print 'create instance'
    global parm
    SetUp()
    resv0 = run_instance(ami, vpc, grps, subnet, 1)
    # resv0 = getresv0()

    ipboss = str(inst_attr(resv0, 'ip_address')[0])
    ipboss, slaves = makeHosts(vpc, resv0, ipboss, 1)
    parm = chkparm(
        ipboss, slaves,
        keyfile='%s.pem' % keyname)

    surecall('fab -R master setDepPkg')

    img = makeImage(resv0.instances[0])
    cPickle.dump((resv0, img), open(fi, 'wb'))

    run_instance(img.id, vpc, grps, subnet, n_instances-1)
    ipboss, slaves = makeHosts(vpc, resv0, ipboss, n_instances)

    parm = chkparm(
        ipboss, slaves,
        keyfile='%s.pem' % keyname)

    surecall('fab -R master setMasPkg')
    surecall('fab -R master setMaster')

    return resv0, img


def getAllstate():
    recvs = c.get_all_instances()
    print map(get_state, recvs)


def shutdown(vpc):
    vpcid = vpc.id
    for resv in get_resv(vpcid):
        fcnt = lambda state: sum(chkstate(resv, state))

        n = len(resv.instances)
        if fcnt('terminated') != n:
            resv.stop_all()
            while fcnt('stopped') != n:
                time.sleep(3)
            print 'instances stopped.'

            for inst in resv.instances:
                inst.terminate()

            while fcnt('terminated') != n:
                time.sleep(3)
    print 'instances terminated.'


def getKeys():
    bkt = s3.get_bucket(parm['s3_bucket'])
    keys = bkt.get_all_keys()
    li = sorted([(k.last_modified, k.name) for k in keys])
    for x in li:
        print x
    return keys


def saveFile(keys):
    dst = 'result'
    for k in keys:
        fi = join(dst, k.name)
        if not exists(fi):
            k.get_contents_to_filename(fi)
            print fi


def getresv0():
    # find initial reserved instance temporarily
    resv0 = None
    for r in c.get_all_instances():
        for inst in r.instances:
            if inst.update() == 'running':
                resv0 = r
        if resv0 is not None:
            break
    return resv0


if __name__ == '__main__':
    """"""
    if len(sys.argv) == 1:
        resv0, img = main()
        ipboss = str(inst_attr(resv0, 'ip_address')[0])
        comments(ipboss)
    else:
        x = 'b'
        cmds = [sys.argv[1], '(', ')']
        if len(sys.argv) > 2:
            [cmds.insert(-1, argv) for argv in sys.argv[2:]]
        eval(''.join(cmds))


