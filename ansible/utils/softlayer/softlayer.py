'''generate softlayer playbook'''

import argparse


def general():
    '''generate generic vm info'''
    template_general = '''---
- name: "create softlayer vms"
  sl_vm:
    hostname: "{{ item.hostname }}"
    domain: "{{ item.domain }}"
    datacenter: "{{ item.datacenter }}"
    tags: "{{ item.tags }}"
    cpus: "{{ item.cpus }}"
    memory: "{{ item.memory }}"
    disks: [100]
    os_code: "{{ item.os_code }}"
    ssh_keys: "{{ item.ssh_keys }}"
    nic_speed: 1000
    hourly: yes
    private: no
    dedicated: no
    local_disk: yes
    wait: no
  with_items:
'''

    print(template_general)


def build():
    '''generate info for build vm'''
    template_build = '''# build
    - hostname: "build"
      domain: "{{ sl_domain }}"
      datacenter: "{{ sl_datacenter }}"
      tags: "{{ sl_tag }},build"
      cpus: "{{ sl_cpus_peer }}"
      memory: "{{ sl_ram_peer }}"
      os_code: "{{ sl_os }}"
      ssh_keys: ["{{ sl_sshkey }}"]
'''

    print(template_build)


def peer(peer_num, org_num):
    '''generate info for each peer vm'''
    template_peer = '''# peer{p}.org{o}
    - hostname: "peer{p}.org{o}"
      domain: "{{{{ sl_domain }}}}"
      datacenter: "{{{{ sl_datacenter }}}}"
      tags: "{{{{ sl_tag }}}},peer{p}org{o}"
      cpus: "{{{{ sl_cpus_peer }}}}"
      memory: "{{{{ sl_ram_peer }}}}"
      os_code: "{{{{ sl_os }}}}"
      ssh_keys: ["{{{{ sl_sshkey }}}}"]
'''

    print(template_peer.format(p=peer_num, o=org_num))


def orderer(org_num):
    '''generate info for each orderer vm'''
    template_orderer = '''# ordererOrg{o}
    - hostname: "orderer{o}"
      domain: "{{{{ sl_domain }}}}"
      datacenter: "{{{{ sl_datacenter }}}}"
      tags: "{{{{ sl_tag }}}},ordererOrg{o}"
      cpus: "{{{{ sl_cpus }}}}"
      memory: "{{{{ sl_ram }}}}"
      os_code: "{{{{ sl_os }}}}"
      ssh_keys: ["{{{{ sl_sshkey }}}}"]
'''

    print(template_orderer.format(o=org_num))


def zookeeper(org_num):
    '''generate info for each zookeeper vm'''
    template_zookeeper = '''# zookeeperOrg{o}
    - hostname: "z{o}"
      domain: "{{{{ sl_domain }}}}"
      datacenter: "{{{{ sl_datacenter }}}}"
      tags: "{{{{ sl_tag }}}},zookeeper{o}"
      cpus: "{{{{ sl_cpus }}}}"
      memory: "{{{{ sl_ram }}}}"
      os_code: "{{{{ sl_os }}}}"
      ssh_keys: ["{{{{ sl_sshkey }}}}"]
'''

    print(template_zookeeper.format(o=org_num))


def kafka(org_num):
    '''generate info for each kafka vm'''
    template_kafka = '''# kafkaOrg{o}
    - hostname: "k{o}"
      domain: "{{{{ sl_domain }}}}"
      datacenter: "{{{{ sl_datacenter }}}}"
      tags: "{{{{ sl_tag }}}},kafkaOrg{o}"
      cpus: "{{{{ sl_cpus }}}}"
      memory: "{{{{ sl_ram }}}}"
      os_code: "{{{{ sl_os }}}}"
      ssh_keys: ["{{{{ sl_sshkey }}}}"]
'''

    print(template_kafka.format(o=org_num))


def fabric_ca(org_num):
    '''generate info for each fabric-ca vm'''
    template_fabricca = '''# fabricCAOrg{o}
    - hostname: "fabric-ca{o}"
      domain: "{{{{ sl_domain }}}}"
      datacenter: "{{{{ sl_datacenter }}}}"
      tags: "{{{{ sl_tag }}}},fabricCAOrg{o}"
      cpus: "{{{{ sl_cpus }}}}"
      memory: "{{{{ sl_ram }}}}"
      os_code: "{{{{ sl_os }}}}"
      ssh_keys: ["{{{{ sl_sshkey }}}}"]
'''

    print(template_fabricca.format(o=org_num))


def cli(org_num):
    '''generate info for each cli vm'''
    template_cli = '''# cli{o}
    - hostname: "cli{o}"
      domain: "{{{{ sl_domain }}}}"
      datacenter: "{{{{ sl_datacenter }}}}"
      tags: "{{{{ sl_tag }}}},cli{o}"
      cpus: "{{{{ sl_cpus }}}}"
      memory: "{{{{ sl_ram }}}}"
      os_code: "{{{{ sl_os }}}}"
      ssh_keys: ["{{{{ sl_sshkey }}}}"]
'''

    print(template_cli.format(o=org_num))


def main():
    '''parse cmdline args and print role'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--peer_count',
                        nargs='+',
                        type=int,
                        help='number of peers per org')
    args = parser.parse_args()

    general()
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


if __name__ == '__main__':
    main()
