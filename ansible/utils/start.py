''' '''

import argparse
import os

INTRO = '''#!/bin/bash

set -x

'''

PIDS_NEW = '''PIDS=""
'''
PIDS_WAIT = '''
for PID in $PIDS; do
  wait $PID
done

'''

ZOOKEEPER = '''ansible-playbook  --key-file "~/.ssh/fabric"  autogen_start_zookeeper{org}.yml  &>  log_autogenstart_zookeeper{org}   &
PIDS="$PIDS $!" 
'''

KAFKA = '''ansible-playbook  --key-file "~/.ssh/fabric"  autogen_start_kafka{org}.yml  &>  log_autogen_start_kafka{org}   &
PIDS="$PIDS $!"
'''

FABRICCA = '''ansible-playbook  --key-file "~/.ssh/fabric"  autogen_start_fabricca{org}.yml  &>  log_autogen_start_fabricca{org}.log   &
PIDS="$PIDS $!" 
'''

ORDERER = '''ansible-playbook  --key-file "~/.ssh/fabric"  autogen_start_orderer{org}.yml  &>  log_autogen_start_orderer{org}.log   &
PIDS="$PIDS $!" 
'''

PEER = '''ansible-playbook  --key-file "~/.ssh/fabric"  autogen_start_peer{peer}org{org}.yml  &>  log_autogen_start_peer{peer}org{org}.log   &
PIDS="$PIDS $!" 
'''

def start(fp, body, org_count):
    fp.write(PIDS_NEW)
    for org in range(0, org_count):
        fp.write(body.format(org=org))
    fp.write(PIDS_WAIT)


def script_start(peer_count):
    org_count = len(peer_count)

    filename = 'autogen_start.sh'
    with open(filename, 'w') as fp:
        fp.write(INTRO)
        start(fp, ZOOKEEPER, org_count)
        start(fp, KAFKA, org_count)
        start(fp, FABRICCA, org_count)
        start(fp, ORDERER, org_count)

        fp.write(PIDS_NEW)
        for org in range(0, org_count):
            for peer in range(0, peer_count[org]):
                fp.write(PEER.format(peer=peer, org=org))
        fp.write(PIDS_WAIT)
    os.chmod(filename, 0o755)


def script_template(host, service, vars_file, filename):

    template = '''---
- hosts: {host}
  remote_user: root
  gather_facts: yes
  vars_files:
  - "{vars_file}"
  vars:
    service_name: "{service}"
  roles:
  - start
    '''

    with open(filename, 'w') as ffile:
        ffile.write(template.format(host=host, service=service, vars_file=vars_file))


def script_yml(peer_count, vars_file):

    org_count = len(peer_count)
    for org in range(0, org_count):
        script_template('z{}'.format(org), 'zookeeper.service', vars_file, 'autogen_start_zookeeper{}.yml'.format(org))
        script_template('k{}'.format(org), 'kafka.service', vars_file, 'autogen_start_kafka{}.yml'.format(org))
        script_template('fabric-ca{}'.format(org), 'fabricca.service', vars_file, 'autogen_start_fabricca{}.yml'.format(org))
        script_template('orderer{}'.format(org), 'orderer.service', vars_file, 'autogen_start_orderer{}.yml'.format(org))

        script_template('orderer{}'.format(org), 'orderer.service', vars_file, 'autogen_start_orderer{}.yml'.format(org))
        for peer in range(0, peer_count[org]):
            script_template('peer{}.org{}'.format(peer, org), 'peer.service', vars_file, 'autogen_start_peer{}org{}.yml'.format(peer, org))


def main():
    '''parse cmdline args and print script'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--peer_count',
                        nargs='+',
                        type=int,
                        help='number of peers per org')
    parser.add_argument('-v', '--vars_file', help='ansible vars_file location')
    args = parser.parse_args()

    script_yml(args.peer_count, args.vars_file)
    script_start(args.peer_count)


if __name__ == '__main__':
    main()
