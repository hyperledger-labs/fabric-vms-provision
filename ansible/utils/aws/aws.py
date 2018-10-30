'''generate aws role'''
import argparse


SECURITY_GROUP = '''
- name: create group
  ec2_group:
    name: '{{ group }}'
    description: fabric security group
    region: '{{ region }}'
    aws_access_key: '{{ aws_access_key }}'
    aws_secret_key: '{{ aws_secret_key }}'
    rules:
  register: creategroup

- name: update group
  ec2_group:
    name: '{{ group }}'
    description: fabric security group
    region: '{{ region }}'
    aws_access_key: '{{ aws_access_key }}'
    aws_secret_key: '{{ aws_secret_key }}'
    rules:
      - proto: tcp
        from_port: 22
        to_port: 22
        cidr_ip: 0.0.0.0/0
      - proto: tcp
        ports:
          - 22
          - 2181
          - 2182
          - 2183
          - 7050
          - 7051
          - 7053
          - 7054
          - 9092
          - 9093
        group_id: '{{ creategroup.group_id }}'
  register: secgroup
- name: print secgroup
  debug: var=secgroup
'''


TEMPLATE = '''
- name: launch {vmtype} instance
  ec2:
    key_name: '{{{{ keypair }}}}'
    group: '{{{{ group }}}}'
    instance_type: '{{{{ instance_type }}}}'
    image: '{{{{ image }}}}'
    wait: true
    region: '{{{{ region }}}}'
    aws_access_key: '{{{{ aws_access_key }}}}'
    aws_secret_key: '{{{{ aws_secret_key }}}}'
  register: '{vmtype}'
- name: tag {vmtype} image
  ec2_tag:
    region: '{{{{ region }}}}'
    resource: '{{{{ {vmtype}.instance_ids[0] }}}}'
    state: present
    tags:
      Class: fabric
      Type: {vmtype}
      Host: {host}
      FQDN: '{host}.{{{{ domain }}}}'
- name: print {vmtype}
  debug: var={vmtype}
'''

WAIT = '''
- name: wait for ssh
  wait_for:
    host: '{{ item }}'
    port: 22
    delay: 5
    sleep: 5
    timeout: 320
    state: started
  with_items:'''


def secgroup():
    print(SECURITY_GROUP)


def build():
	print(TEMPLATE.format(vmtype='build', host='build'))


def peer(peer_num, org_num):
    vmtype = 'peer{}org{}'.format(peer_num, org_num)
    host = 'peer{}.org{}'.format(peer_num, org_num)
    print(TEMPLATE.format(vmtype=vmtype, host=host))


def orderer(org_num):
    vmtype = 'ordererOrg{}'.format(org_num)
    host = 'orderer{}'.format(org_num)
    print(TEMPLATE.format(vmtype=vmtype, host=host))


def zookeeper(org_num):
    vmtype = 'z{}'.format(org_num)
    host = 'z{}'.format(org_num)
    print(TEMPLATE.format(vmtype=vmtype, host=host))


def kafka(org_num):
    vmtype = 'k{}'.format(org_num)
    host = 'k{}'.format(org_num)
    print(TEMPLATE.format(vmtype=vmtype, host=host))


def fabric_ca(org_num):
    vmtype = 'fabricCAOrg{}'.format(org_num)
    host = 'fabric-ca{}'.format(org_num)
    print(TEMPLATE.format(vmtype=vmtype, host=host))


def cli(org_num):
    vmtype = 'cli{}'.format(org_num)
    host = 'cli{}'.format(org_num)
    print(TEMPLATE.format(vmtype=vmtype, host=host))


def wait(args):
    print(WAIT)
    print("   - '{{ build.instances[0].public_ip }}'")
    org_count = len(args.peer_count)
    for oid in range(0, org_count):
        for pid in range(0, args.peer_count[oid]):
            print("   - '{{{{ peer{}org{}.instances[0].public_ip }}}}'".format(pid, oid))
        print("   - '{{{{ ordererOrg{}.instances[0].public_ip }}}}'".format(oid))
        print("   - '{{{{ z{}.instances[0].public_ip }}}}'".format(oid))
        print("   - '{{{{ k{}.instances[0].public_ip }}}}'".format(oid))
        print("   - '{{{{ fabricCAOrg{}.instances[0].public_ip }}}}'".format(oid))
        print("   - '{{{{ cli{}.instances[0].public_ip }}}}'".format(oid))


def main():
    '''parse cmdline args and print role'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--peer_count',
                        nargs='+',
                        type=int,
                        help='number of peers per org')
    args = parser.parse_args()

    secgroup()
    build()

    org_count = len(args.peer_count)
    for oid in range(0, org_count):
        for pid in range(0, args.peer_count[oid]):
            peer(pid, oid)
        orderer(oid)
        zookeeper(oid)
        kafka(oid)
        fabric_ca(oid)
        cli(oid)

    wait(args)


if __name__ == '__main__':
    main()
