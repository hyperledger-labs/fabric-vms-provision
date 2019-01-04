'''generate gce role'''
import argparse


GCE_TEMPLATE_INTRO = '''---
- name: create multiple instances
  gce:
    instance_names: "{{ item.name }}"
    tags: "{{ item.tag }}"
    zone: "{{ zone }}"
    machine_type: "{{ machine_type }}"
    image: "{{ image }}"
    state: present
    service_account_email: "{{ service_account_email }}"
    credentials_file: "{{ credentials_file }}"
    project_id: "{{ project_id }}"
  with_items:'''


GCE_TEMPLATE_FINISH = '''  register: gce

- name: Wait for SSH for instances
  wait_for:
    delay: 1
    host: "{{ item.instance_data[0].public_ip }}"
    port: 22
    state: started
    timeout: 30
  with_items: "{{ gce.results }}"
'''


def gce(args):
    print(GCE_TEMPLATE_INTRO)
    names(args)
    print(GCE_TEMPLATE_FINISH)


def names(args):
    template = '''    - {{ name: {name}, tag: '{tag}-{{{{ domain }}}}' }}'''

    print(template.format(name='build', tag='build'))
    org_count = len(args.peer_count)
    for oid in range(0, org_count):
        for pid in range(0, args.peer_count[oid]):
            n = 'peer{}org{}'.format(pid, oid)
            t = 'peer{}-org{}'.format(pid, oid)
            print(template.format(name=n, tag=t))
        o = 'orderer{}'.format(oid)
        print(template.format(name=o, tag=o))

        z = 'z{}'.format(oid)
        print(template.format(name=z, tag=z))

        k = 'k{}'.format(oid)
        print(template.format(name=k, tag=k))

        f = 'fabricca{}'.format(oid)
        print(template.format(name=f, tag=f))

        c = 'cli{}'.format(oid)
        print(template.format(name=c, tag=c))


def main():
    '''parse cmdline args and print role'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--peer_count',
                        nargs='+',
                        type=int,
                        help='number of peers per org')
    args = parser.parse_args()

    gce(args)


if __name__ == '__main__':
    main()
