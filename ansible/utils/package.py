''' '''

import argparse
import os


SCRIPT_INTRO = '''#!/bin/bash

set -x

PIDS=""
'''

SCRIPT_ZOOKEEPER = '''
ansible-playbook  --key-file "~/.ssh/fabric"  autogen_package_zookeeper{org}.yml &> log_package_zookeeper{org}  &
PIDS="$PIDS $!"'''

SCRIPT_KAFKA = '''
sleep 5
ansible-playbook  --key-file "~/.ssh/fabric"  autogen_package_kafka{org}.yml &> log_package_kafka{org}  &
PIDS="$PIDS $!"'''

SCRIPT_FABRICCA = '''
sleep 5
ansible-playbook  --key-file "~/.ssh/fabric"  autogen_package_fabricca{org}.yml &> log_package_fabricca{org}  &
PIDS="$PIDS $!"'''

SCRIPT_PEER = '''
sleep 5
ansible-playbook  --key-file "~/.ssh/fabric"  autogen_package_peer{peer}org{org}.yml &> log_package_peer{peer}org{org}  &
PIDS="$PIDS $!"'''

SCRIPT_ORDERER = '''
sleep 5
ansible-playbook  --key-file "~/.ssh/fabric"  autogen_package_orderer{org}.yml &> log_package_orderer{org}  &
PIDS="$PIDS $!"'''

SCRIPT_CLI = '''
sleep 5
ansible-playbook  --key-file "~/.ssh/fabric"  autogen_package_cli{org}.yml &> log_package_cli{org}  &
PIDS="$PIDS $!"'''

SCRIPT_FINISH = '''
sleep 5

for PID in $PIDS; do
    wait $PID
done

tail -n 5 log_package_*
'''


def script_package(peer_count):

    fname = 'autogen_package.sh'
    with open(fname, 'w') as ffile:
        ffile.write(SCRIPT_INTRO)

        org_count = len(peer_count)
        for org in range(0, org_count):
            ffile.write(SCRIPT_ZOOKEEPER.format(org=org))
            ffile.write(SCRIPT_KAFKA.format(org=org))
            ffile.write(SCRIPT_FABRICCA.format(org=org))

            for peer in range(0, peer_count[org]):
                ffile.write(SCRIPT_PEER.format(peer=peer, org=org))

            ffile.write(SCRIPT_ORDERER.format(org=org))
            ffile.write(SCRIPT_CLI.format(org=org))

        ffile.write(SCRIPT_FINISH)
    os.chmod(fname, 0o755)


def script_yml_zookeeper(org_id, org_count, vars_file):

    template_zookeeper = '''---
- hosts: z{org_id}
  remote_user: "{{{{ fabric.user }}}}"
  gather_facts: yes
  vars_files:
  - "{vars_file}"
  vars:
    org_id: {org_id}
    servers:
{server}
    zk_id: {zoo_id}
  roles:
  - zookeeper
    '''

    tmp = ['    - server.{}=z{}:2182:2183:participant'.format(x+1, x) for x in range(0, org_count)]
    server = '\n'.join(tmp)

    zoo_id = org_id + 1
    fname = 'autogen_package_zookeeper{}.yml'.format(org_id)
    with open(fname, 'w') as ffile:
        ffile.write(template_zookeeper.format(org_id=org_id, zoo_id=zoo_id, server=server, vars_file=vars_file))


def script_yml_kafka(org_id, org_count, vars_file):

    template_kafka = '''---
- hosts: k{org_id}
  remote_user: "{{{{ fabric.user }}}}"
  gather_facts: yes
  vars_files:
  - "{vars_file}"
  vars:
    org_id: {org_id}
    kafka_id: {kafka_id}
    zookeeper_connect: "{zookeeper_connect}"
  roles:
  - kafka
    '''

    tmp = ['z{}:2181'.format(x) for x in range(0, org_count)]
    zookeeper_connect = ','.join(tmp)
    kafka_id = org_id + 1
    fname = 'autogen_package_kafka{}.yml'.format(org_id)
    with open(fname, 'w') as ffile:
        ffile.write(template_kafka.format(org_id=org_id, kafka_id=kafka_id, zookeeper_connect=zookeeper_connect, vars_file=vars_file))


def script_yml_fabricca(org_id, vars_file):

    template_fabricca = '''---
- hosts: fabric-ca{org_id}
  remote_user: "{{{{ fabric.user }}}}"
  gather_facts: yes
  vars_files:
  - "{vars_file}"
  vars:
    org_id: {org_id}
  roles:
  - fabricca
    '''

    fname = 'autogen_package_fabricca{}.yml'.format(org_id)
    with open(fname, 'w') as ffile:
        ffile.write(template_fabricca.format(org_id=org_id, vars_file=vars_file))


def script_yml_peer(peer_id, org_id, vars_file):

    template_peer = '''---
- hosts: peer{peer_id}.org{org_id}
  remote_user: "{{{{ fabric.user }}}}"
  gather_facts: yes
  vars_files:
  - "{vars_file}"
  vars:
    peer_id: {peer_id}
    org_id: {org_id}
  roles:
  - docker
  - peer
    '''

    fname = 'autogen_package_peer{peer_id}org{org_id}.yml'.format(peer_id=peer_id, org_id=org_id)
    with open(fname, 'w') as ffile:
        ffile.write(template_peer.format(peer_id=peer_id, org_id=org_id, vars_file=vars_file))


def script_yml_orderer(org_id, vars_file):

    template_orderer = '''---
- hosts: orderer{org_id}
  remote_user: "{{{{ fabric.user }}}}"
  gather_facts: yes
  vars_files:
  - "{vars_file}"
  vars:
    org_id: {org_id}
  roles:
  - orderer
    '''

    fname = 'autogen_package_orderer{}.yml'.format(org_id)
    with open(fname, 'w') as ffile:
        ffile.write(template_orderer.format(org_id=org_id, vars_file=vars_file))


def script_yml_cli(org_id, vars_file):

    template_cli = '''---
- hosts: cli{org_id}
  remote_user: "{{{{ fabric.user }}}}"
  gather_facts: yes
  vars_files:
  - "{vars_file}"
  vars:
    org_id: {org_id}
  roles:
  - docker
  - golang
  - cli
    '''

    fname = 'autogen_package_cli{}.yml'.format(org_id)
    with open(fname, 'w') as ffile:
        ffile.write(template_cli.format(org_id=org_id, vars_file=vars_file))


def script_yml(peer_count, vars_file):
    
    org_count = len(peer_count)
    for org in range(0, org_count):
        script_yml_zookeeper(org, org_count, vars_file)
        script_yml_kafka(org, org_count, vars_file)
        script_yml_fabricca(org, vars_file)

        for peer in range(0, peer_count[org]):
            script_yml_peer(peer, org, vars_file)

        script_yml_orderer(org, vars_file)
        script_yml_cli(org, vars_file)


def main():
    '''parse cmdline args and print script'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--peer_count',
                        nargs='+',
                        type=int,
                        help='number of peers per org')
    parser.add_argument('-v', '--vars_file', help='ansible vars_file location')
    args = parser.parse_args()

    script_package(args.peer_count)
    script_yml(args.peer_count, args.vars_file)


if __name__ == '__main__':
    main()
